import json
import os
import threading
import time
import urllib.request
import urllib.error
from contextvars import ContextVar
from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field
from typing import Literal

ROOT = Path(os.environ.get('FAMILY_PROJECT_ROOT', Path(__file__).resolve().parents[3]))
import sys
sys.path.insert(0, str(ROOT / 'scripts'))
from model_policy import Budget, load_policy
from probe_family_sources import SAMPLE_URL, SERVICE, fetch

CURRENT = ContextVar('family_minimum_runtime')


class Inspection(BaseModel):
    model_config = ConfigDict(extra='forbid', strict=True)
    status: Literal['inspection_complete', 'needs_confirmation']
    service_ids: list[str] = Field(max_length=5)
    source_ids: list[str] = Field(max_length=1)


class Runtime:
    def __init__(self, ledger, model, key, send=None, fetch_source=fetch, policy=None):
        if not ledger or not model or not key:
            raise ValueError('Model, provider credential and reconciled daily ledger are required')
        self.policy = policy or load_policy()
        self.model, self.key = model, key
        self.fetch_source = fetch_source
        self.events, self.rows = [], []
        self.tool_called, self.closed, self.steps = False, False, 0
        self.lock = threading.RLock()
        self.sender = send or self._send
        self.budget = Budget(self._physical_send, policy=self.policy, daily_path=ledger)

    def _physical_send(self, payload):
        if self.closed:
            raise ValueError('Run closed before physical request')
        return self.sender(payload)

    def _send(self, payload):
        request = urllib.request.Request('https://integrate.api.nvidia.com/v1/chat/completions',
            data=json.dumps(payload).encode(), headers={'Authorization': 'Bearer ' + self.key,
            'Content-Type': 'application/json'}, method='POST')
        opener = urllib.request.build_opener(NoRedirect())
        with opener.open(request, timeout=self.policy.request_timeout_seconds) as response:
            data = response.read(2_000_001)
        if len(data) > 2_000_000:
            raise ValueError('Model response exceeds limit')
        return json.loads(data)

    def model_request(self, messages, stop=None):
        with self.lock:
            if self.closed or self.steps >= self.policy.max_steps:
                raise ValueError('Stopped or step limit reached')
            self.steps += 1
            payload = {'model': self.model, 'messages': messages, 'temperature': 0.0,
                'max_tokens': self.policy.max_output_tokens, 'stream': False}
            if self.model == 'nvidia/nemotron-3-super-120b-a12b':
                payload['chat_template_kwargs'] = {'enable_thinking': False}
            if stop:
                payload['stop'] = stop
            before = self.budget.count
            error = {}
            try:
                data = self.budget(payload)
                choice = data['choices'][0]
                content = choice['message']['content']
                if choice.get('finish_reason') == 'length' or not isinstance(content, str) or not content.strip():
                    raise ValueError('Invalid or truncated model response')
                return content
            except Exception as exc:
                error = {'error_code': type(exc).__name__}
                if isinstance(exc, urllib.error.HTTPError): error['http_status'] = exc.code
                raise
            finally:
                self.events.append({'kind': 'model', 'step': self.steps,
                    'physical_requests': self.budget.count - before, **error})

    def search(self, query):
        if query != 'seoul_public_sample':
            raise ValueError('Only the public sample scope is allowed')
        with self.lock:
            if self.closed:
                raise ValueError('Run is closed')
            self.budget._wait(0)
            if self.tool_called:
                return self.observation
            self.tool_called = True
            try:
                raw, _ = self.fetch_source(SAMPLE_URL)
                body = json.loads(raw)
                service = body.get(SERVICE, {})
                code = service.get('RESULT', body.get('RESULT', {})).get('CODE')
                rows = service.get('row', [])
                if code not in {'INFO-000', 'INFO-200'} or not isinstance(rows, list) or len(rows) > 5:
                    raise ValueError('Invalid source response')
                if any(not isinstance(row, dict) or not isinstance(row.get('SVCID'), str)
                       or not isinstance(row.get('SVCNM'), str) for row in rows):
                    raise ValueError('Invalid source records')
                fields = ('SVCID', 'SVCNM', 'USETGTINFO', 'SVCOPNBGNDT', 'SVCOPNENDDT',
                    'RCPTBGNDT', 'RCPTENDDT', 'SVCSTATNM')
                self.rows = [{field: row.get(field) for field in fields} for row in rows]
                self.observation = {'status': 'ok' if self.rows else 'empty', 'source_id': 'seoul_public_sample',
                    'source_url': SAMPLE_URL, 'scope': 'first five public sample records; not exhaustive',
                    'queried_at': time.time(), 'rows': self.rows,
                    'participation': 'unverified; no detail or user conditions checked'}
            except (OSError, ValueError, KeyError, TypeError):
                self.observation = {'status': 'source_error', 'source_id': 'seoul_public_sample',
                    'rows': [], 'participation': 'unverified'}
            self.events.append({'kind': 'tool', 'name': 'search_experiences',
                'status': self.observation['status'], 'source_id': 'seoul_public_sample'})
            return self.observation

    def validate(self, text):
        result = Inspection.model_validate_json(text)
        if not self.tool_called:
            raise ValueError('Final result without an observed source')
        known = {row['SVCID'] for row in self.rows}
        if len(result.service_ids) != len(set(result.service_ids)) or not set(result.service_ids) <= known:
            raise ValueError('Unobserved or duplicated service ID')
        if result.source_ids != ['seoul_public_sample']:
            raise ValueError('Missing or invented source')
        if result.status == 'inspection_complete' and (not result.service_ids or self.observation['status'] != 'ok'):
            raise ValueError('Completion without source records')
        if result.status == 'needs_confirmation' and result.service_ids:
            raise ValueError('Hold result must not imply selected records')
        return {**result.model_dump(), 'records': [row for row in self.rows if row['SVCID'] in result.service_ids],
            'participation': 'unverified', 'scope': 'public sample connectivity inspection only',
            'events': self.events, 'physical_model_requests': self.budget.count}

    def close(self):
        self.closed = True


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise ValueError('Model endpoint redirect forbidden')
