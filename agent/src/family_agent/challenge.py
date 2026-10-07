"""Draft-only challenge tools. All reads run in the same OpenShell worker."""
import json
import os
import re
from pathlib import Path
from pydantic import BaseModel, ConfigDict, Field
from family_minimum.runtime import Runtime


class Draft(BaseModel):
    model_config = ConfigDict(extra='forbid', strict=True)
    action: str
    draft: str = Field(min_length=1, max_length=16000)
    citations: list[dict[str, str]] = Field(min_length=1, max_length=30)
    uncertainties: list[str] = Field(max_length=20)


class ChallengeRuntime(Runtime):
    def __init__(self, ledger, model, key, request, additional='', input_root='/hackathon/input', **kwargs):
        super().__init__(ledger, model, key, **kwargs)
        if set(request) != {'request_id', 'task'} or not re.fullmatch(r'[A-Za-z0-9_.:-]+', request['request_id']):
            raise ValueError('invalid_request')
        if not isinstance(request['task'], str) or not 1 <= len(request['task']) <= 8000 or len(additional) > 2000:
            raise ValueError('invalid_task')
        self.request_id, self.root = request['request_id'], Path(input_root)
        self.query = json.dumps({'task': request['task'], 'additional_condition': additional,
            'authority': 'draft_only; no sending, reservation, payment or upload'}, ensure_ascii=False)
        self.paths, self.reads, self.tool_steps = {}, {}, 0

    def tool(self, name, argument):
        with self.lock:
            if self.closed or self.steps >= self.policy.max_steps: raise ValueError('run_closed_or_step_limit')
            self.budget._wait(0)
            self.tool_steps += 1
            if self.tool_steps > self.policy.max_steps: raise ValueError('tool_step_limit')
            if name == 'search_input':
                if not isinstance(argument, str) or len(argument) > 100: raise ValueError('invalid_query')
                paths = []
                for directory, dirs, files in os.walk(self.root, followlinks=False):
                    dirs[:] = sorted(d for d in dirs if not Path(directory, d).is_symlink())
                    for filename in sorted(files):
                        path = Path(directory, filename)
                        if path.is_symlink() or path.suffix.lower() not in ('.md', '.txt', '.json', '.csv'): continue
                        if len(paths) >= 64: break
                        relative = path.relative_to(self.root).as_posix()
                        paths.append(relative)
                self.paths = {f'input-{i}': p for i, p in enumerate(sorted(paths))}
                result = {'status': 'ok' if paths else 'empty', 'coverage': 'bounded',
                    'sources': [{'source_id': key, 'path': path} for key, path in self.paths.items()
                                if not argument or argument.lower() in path.lower()]}
            elif name == 'read_input':
                ids = argument.split(',')
                if len(ids) > 8 or any(key not in self.paths for key in ids): raise ValueError('unobserved_source')
                result = {'status': 'ok', 'documents': []}
                for key in ids:
                    if key not in self.reads:
                        # Open every component relative to the input dir without following links.
                        fd = os.open(self.root, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
                        try:
                            components = self.paths[key].split('/')
                            for part in components[:-1]:
                                child = os.open(part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=fd)
                                os.close(fd); fd = child
                            file_fd = os.open(components[-1], os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=fd)
                            try:
                                import stat
                                if not stat.S_ISREG(os.fstat(file_fd).st_mode): raise ValueError('not_regular')
                                raw = os.read(file_fd, 10001)
                                if len(raw) > 10000: raise ValueError('input_size_limit')
                                self.reads[key] = raw.decode('utf-8')
                            finally: os.close(file_fd)
                        finally: os.close(fd)
                    result['documents'].append({'source_id': key, 'path': self.paths[key],
                        'text': self.reads[key], 'lines': [{'number': i+1, 'text': text} for i, text in enumerate(self.reads[key].splitlines())], 'trust': 'untrusted_source_data'})
            else: raise ValueError('unknown_tool')
            self.events.append({'kind': 'tool', 'name': name, 'status': result['status'],
                'source_ids': ids if name == 'read_input' else list(self.paths)})
            return result

    def validate(self, text):
        draft = Draft.model_validate_json(text)
        if draft.action not in ('finish_results', 'finish_hold'): raise ValueError('draft_only_action')
        for cite in draft.citations:
            sid = cite.get('source_id')
            if sid not in self.reads:
                sid = next((key for key in self.reads if self.paths[key] == sid), None)
            if sid is None: raise ValueError('unobserved_source')
            cite['source_id'] = sid
            if set(cite) == {'source_id', 'line'}:
                lines = self.reads[sid].splitlines()
                if not cite['line'].isdigit() or not 1 <= int(cite['line']) <= len(lines): raise ValueError('invalid_line')
                cite['quote'] = lines[int(cite.pop('line')) - 1]
            if set(cite) != {'source_id', 'quote'} or not cite['quote'].strip(): raise ValueError('invalid_citation')
            if cite['source_id'] not in self.reads or cite['quote'] not in self.reads[cite['source_id']]:
                raise ValueError('ungrounded_citation')
        return {'schema_version': 'challenge-agent-v1', 'request_id': self.request_id,
            **draft.model_dump(), 'mode': 'live', 'authority': 'draft_only',
            'sources': {key: self.paths[key] for key in self.reads}, 'events': self.events,
            'physical_model_requests': self.budget.count}

    def failed(self, error_code):
        result = self.limited('execution_failed:' + error_code)
        result['action'] = 'finish_failed'
        return result

    def limited(self, reason):
        return {'schema_version': 'challenge-agent-v1', 'request_id': self.request_id,
            'action': 'finish_limited', 'mode': 'live', 'reason': reason, 'draft': '',
            'citations': [], 'uncertainties': ['미완료: 확인한 자료만으로 결과를 확정할 수 없습니다.'],
            'events': self.events, 'physical_model_requests': self.budget.count}
