"""Single-worker MVP API. Start inside OpenShell; never fetch sources on a host proxy."""
import asyncio
from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
import os
import json
from pathlib import Path
import secrets
import threading
import time
from typing import Literal
from fastapi import FastAPI, Header, HTTPException
from jsonschema.exceptions import ValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict, Field, model_validator
from family_minimum.runtime import load_policy
from .contracts import from_cards, check
from .run import execute
from .runtime import FamilyRuntime


class Cards(BaseModel):
    model_config = ConfigDict(extra='forbid', strict=True)
    interests: list[Literal['history', 'craft', 'performance']] = Field(min_length=1, max_length=3)
    grades: list[Literal['preschool', '1', '2', '3', '4', '5', '6', 'teen']] = Field(max_length=8)
    guardians: Literal['unknown', '0', '1', '2', '2+']
    children: list[dict] | None = None
    composition_complete: bool = False
    delivery_mode: Literal['in_person', 'online'] | None = None
    date: str | None
    district: Literal['all', 'jongno', 'jung']

    @model_validator(mode='after')
    def valid_conditions(self):
        try: from_cards(self.model_dump(exclude_unset=True))
        except (ValueError, ValidationError): raise ValueError('invalid_family_conditions') from None
        return self


class Resume(BaseModel):
    model_config = ConfigDict(extra='forbid', strict=True)
    question_id: str
    request_id: str
    conditions_revision: int
    selected_option_id: str


_last_request_started = None
_active_runtimes = {}


def run_worker(runtime, job_id, revision, workflow='family-workflow.yml', query=None, request=None):
    global _last_request_started
    _active_runtimes[job_id] = runtime
    runtime.budget.last = _last_request_started
    try:
        result = asyncio.run(execute(runtime, workflow, query))
        result['conditions_revision'] = revision
        result['elapsed_seconds'] = round(runtime.budget.clock() - runtime.budget.started, 2)
        result['events'] = [{**event, 'seq': i+1, 'request_id': job_id} for i, event in enumerate(result['events'])]
        if request is not None: result['request'] = request
    finally:
        _last_request_started = runtime.budget.last
        _active_runtimes.pop(job_id, None)
    from openshell_harness.output import collect_json
    root = Path('/hackathon/output') / str(revision)
    root.mkdir(exist_ok=True)
    directory = root / job_id
    directory.mkdir()
    with (directory / 'result.json').open('x') as stream:
        json.dump({'job_id': job_id, 'result': result}, stream, ensure_ascii=False)
    root_fd = os.open(root, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    try:
        result = collect_json(root_fd, job_id, requester=job_id, job_owner=job_id, expected_uid=os.getuid())
        result['storage'] = {'status': 'collected', 'path': str(directory / 'result.json')}
        return result
    finally:
        os.close(root_fd)


def settings():
    if os.environ.get('MODEL_LEDGER_RECONCILED') != 'yes': raise ValueError('ledger_not_reconciled')
    return dict(ledger=os.environ.get('MODEL_DAILY_LEDGER'), model=os.environ.get('MODEL_ID'),
        key=os.environ.get('NVIDIA_API_KEY'), policy=load_policy(os.environ))


def live_worker(job_id, revision, conditions):
    runtime = FamilyRuntime(**settings(), conditions=conditions, request_id=job_id, revision=revision)
    return run_worker(runtime, job_id, revision)


def create_app(worker=live_worker):
    app = FastAPI(title='두루 가족 탐색 MVP')
    @app.exception_handler(ValidationError)
    async def invalid_contract(request, exc):
        return JSONResponse(status_code=422, content={'detail': 'invalid_contract'})

    jobs, lock = {}, threading.RLock()
    pool = ThreadPoolExecutor(max_workers=1, thread_name_prefix='family-agent')

    def owned(job_id, owner):
        with lock:
            job = jobs.get(job_id)
            if not job or not owner or not secrets.compare_digest(owner, job['owner']):
                raise HTTPException(404, 'not_found')
            return job

    def launch(job_id):
        job = jobs[job_id]
        revision, conditions = job['revision'], deepcopy(job['conditions'])
        def run():
            with lock:
                if job['status'] == 'cancelled': return
                job['status'] = 'running'
            try:
                result = worker(job_id, revision, conditions)
                if result.get('request_id') != job_id or result.get('conditions_revision') != revision:
                    raise ValueError('worker_identity_mismatch')
                with lock:
                    if job['status'] != 'cancelled': job.update(status='completed', result=result)
            except Exception as exc:
                with lock:
                    if job['status'] != 'cancelled': job.update(status='failed', error_code=type(exc).__name__)
        job['future'] = pool.submit(run)

    @app.get('/api/health')
    def health():
        return {'mode': 'live', 'worker': 'single', 'boundary': 'requires_operators_OpenShell_evidence'}

    def create_job(conditions, mode):
        with lock:
            for key in list(jobs):
                if jobs[key]['status'] in ('completed', 'failed', 'cancelled') and time.monotonic() - jobs[key]['created'] > 1800:
                    del jobs[key]
            if len(jobs) >= 32 or sum(j['status'] in ('queued', 'running') for j in jobs.values()) >= 4:
                raise HTTPException(429, 'worker_capacity')
            job_id, owner = secrets.token_hex(16), secrets.token_urlsafe(32)
            jobs[job_id] = {'owner': owner, 'created': time.monotonic(), 'status': 'queued',
                'revision': 1, 'conditions': conditions, 'mode': mode, 'result': None}
            launch(job_id)
        return {'run_id': job_id, 'owner_token': owner, 'conditions_revision': 1}

    @app.post('/api/runs', status_code=202)
    def start(cards: Cards):
        return create_job(from_cards(cards.model_dump(exclude_unset=True)), 'family')

    @app.get('/api/runs/{job_id}')
    def get(job_id: str, x_run_owner: str | None = Header(default=None)):
        job = owned(job_id, x_run_owner)
        with lock:
            return {'run_id': job_id, 'status': job['status'], 'conditions_revision': job['revision'],
                'result': deepcopy(job['result']), 'error_code': job.get('error_code')}

    @app.delete('/api/runs/{job_id}', status_code=202)
    def cancel(job_id: str, x_run_owner: str | None = Header(default=None)):
        job = owned(job_id, x_run_owner)
        with lock:
            job.update(status='cancelled', result=None)
            job['future'].cancel()
            runtime = _active_runtimes.get(job_id)
            if runtime: runtime.close()
        return {'status': 'cancelled'}

    @app.post('/api/runs/{job_id}/resume', status_code=202)
    def resume(job_id: str, payload: Resume, x_run_owner: str | None = Header(default=None)):
        check('resume_input', payload.model_dump())
        job = owned(job_id, x_run_owner)
        with lock:
            if payload.request_id != job_id: raise HTTPException(404, 'not_found')
            if payload.conditions_revision != job['revision']: raise HTTPException(409, 'revision_conflict')
            question = (job['result'] or {}).get('question')
            if job['status'] != 'completed' or not question or question['question_id'] != payload.question_id:
                raise HTTPException(409, 'question_not_active')
            if payload.selected_option_id not in {o['id'] for o in question['options']}:
                raise HTTPException(422, 'invalid_option')
            conditions = deepcopy(job['conditions']); value, field = payload.selected_option_id, question['field']
            if field == 'guardians': value = {'guardians-0': '0', 'guardians-1': '1', 'guardians-2plus': '2+'}[value]
            if field == 'grade':
                member = next(c for c in conditions['children'] if c['member_id'] == question['member_id'])
                member['grade'] = value
            elif field == 'guardians':
                conditions['guardians'] = {'minimum': int(value.rstrip('+')), 'maximum': None if value == '2+' else int(value)}
            elif field == 'delivery_mode': conditions['delivery_mode'] = value
            else: raise HTTPException(422, 'unsupported_question')
            check('conditions', conditions)
            job.update(conditions=conditions, revision=job['revision'] + 1, result=None, status='queued')
            launch(job_id)
        return {'run_id': job_id, 'conditions_revision': job['revision']}

    return app


app = create_app()
