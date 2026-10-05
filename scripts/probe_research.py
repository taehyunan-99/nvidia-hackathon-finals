"""Bounded live model check with two synthetic tools. Dry-run by default."""
import argparse
import json
import os
from pathlib import Path
import shlex
import time
import urllib.error
import uuid
from probe_nim import request
from rehearsal import TOPIC, run, assert_result, validate_evidence
from model_policy import Budget, ENV_FIELDS, load_policy

ROOT = Path(__file__).resolve().parents[1]
SYSTEM = '''You review synthetic evidence for the goal supplied in the current observation.
Choose only allowed_actions. The runner enforces termination after validation; do not predict hidden tool data.
Choose tools yourself from observations. check_existing retrieves existing evidence;
collect_more retrieves additional evidence when existing evidence is insufficient.
Do not collect more if two different sources already agree and validation passed.
If collection still leaves insufficient or conflicting evidence, hold the conclusion.
A tool error permits at most one retry. Never claim completion before validation passes.
When finished, return ONLY a JSON object with action (complete, hold, or fail) and
reason (one short Korean sentence). For tools use native tool calls with empty arguments.
Do not invent sources or values. This is a synthetic tool integration check, not real research.'''
TOOLS = [{'type': 'function', 'function': {'name': name, 'description': description,
          'parameters': {'type': 'object', 'properties': {}, 'additionalProperties': False}}}
         for name, description in [('check_existing', 'Retrieve existing evidence before deciding whether more is needed.'),
                                   ('collect_more', 'Collect another source when current evidence is insufficient.')]]


def config(path=ROOT / '.env'):
    values = {}
    allowed = {'NVIDIA_API_KEY', 'MODEL_ID', 'MODEL_BASE_URL', 'MODEL_DAILY_BUDGET_PATH'} | set(ENV_FIELDS)
    if path.is_file():
        for line in path.read_text().splitlines():
            key, sep, value = line.partition('=')
            if sep and key.strip() in allowed:
                parsed = shlex.split(value, comments=True)
                if parsed: values[key.strip()] = parsed[0]
    for key in allowed:
        if os.getenv(key): values[key] = os.environ[key]
    return values


class ModelDecision:
    def __init__(self, send, model, policy=None):
        self.send, self.model = send, model
        self.policy = policy or load_policy()
        self.messages = [{'role': 'system', 'content': SYSTEM}]
        self.pending = None

    def __call__(self, observation):
        if self.pending:
            self.messages.append({'role': 'tool', 'tool_call_id': self.pending,
                                  'content': json.dumps(observation, ensure_ascii=False)})
        else:
            self.messages.append({'role': 'user', 'content': json.dumps(observation, ensure_ascii=False)})
        response = self.send({'model': self.model, 'messages': self.messages,
                              'tools': [tool for tool in TOOLS if tool['function']['name'] in observation.get('allowed_actions', ['check_existing', 'collect_more'])], 'tool_choice': 'auto', 'stream': False,
                              'temperature': 1, 'top_p': 0.95, 'max_tokens': self.policy.max_output_tokens,
                              'chat_template_kwargs': {'enable_thinking': False}})
        choice = response['choices'][0]
        if choice.get('finish_reason') == 'length':
            raise ValueError('Truncated response')
        message = choice['message']
        calls = message.get('tool_calls') or []
        if calls:
            if len(calls) != 1:
                raise ValueError('Expected one tool per decision')
            call = calls[0]
            name = call['function']['name']
            if name not in observation.get('allowed_actions', ['check_existing', 'collect_more']) or json.loads(call['function']['arguments']) != {}:
                raise ValueError('Invalid tool or arguments')
            if not isinstance(call.get('id'), str) or not call['id']:
                raise ValueError('Missing tool call ID')
            self.pending = call['id']
            # Do not retain or display reasoning_content or other provider metadata.
            self.messages.append({'role': 'assistant', 'content': message.get('content'), 'tool_calls': calls})
            return name, '실제 모델이 현재 관측에서 이 도구를 선택했습니다. 선택 이유 설명은 별도로 요청하지 않았습니다.'
        final = json.loads(message['content'])
        if set(final) != {'action', 'reason'} or final['action'] not in {'complete', 'hold', 'fail'} or not isinstance(final['reason'], str) or not final['reason'].strip():
            raise ValueError('Invalid final decision')
        if final['action'] not in observation.get('allowed_actions', ['complete', 'hold', 'fail']):
            raise ValueError('Action not permitted in current state')
        return final['action'], final['reason'][:300]


def check_expectation(result, case=None):
    """Replay preconditions independently of scenario labels or an answer path."""
    assert_result(result)
    obs = {'calls': [], 'attempts': {}, 'error': None, 'validation': 'insufficient'}
    pending = None
    terminal = False

    def permitted_tool(name):
        if obs['validation'] in {'pass', 'conflict', 'invalid_output'}:
            return False
        if obs['error']:
            return name == obs['calls'][-1] and obs['attempts'][name] < 2
        if name in obs['calls']:
            return False
        return name == 'check_existing' if not obs['calls'] else name == 'collect_more'

    for event in result['events']:
        if event['kind'] == 'decision':
            if terminal and (event['label'] != '실행 제어의 종료' or event['tool']):
                raise ValueError('Decision after terminal state')
            if event['tool'] and not permitted_tool(event['tool']):
                raise ValueError('Tool selected outside state permissions')
        elif event['kind'] == 'tool':
            name = event['tool']
            if terminal:
                raise ValueError('Tool after terminal state')
            if event['status'] == 'running':
                if pending or not permitted_tool(name):
                    raise ValueError('Redundant or premature tool')
                attempt = obs['attempts'].get(name, 0) + 1
                if event['attempt'] != attempt:
                    raise ValueError('Invalid attempt')
                obs['attempts'][name] = attempt
                obs['calls'].append(name)
                pending = name
            else:
                if pending != name:
                    raise ValueError('Tool result without call')
                pending = None
                obs['error'] = event['error_code']
                if event['error_code'] == 'invalid_output':
                    obs['validation'] = 'invalid_output'
        elif event['kind'] == 'validation':
            rows = [row for row in result['evidence'] if row['id'] in event['evidence_ids']]
            if obs['validation'] != 'invalid_output':
                obs['validation'] = validate_evidence(rows, result['input']['goal'])
            if (event['status'] == 'completed') != (obs['validation'] == 'pass'):
                raise ValueError('Validation mismatch')
            terminal = obs['validation'] in {'pass', 'conflict', 'invalid_output'} or 'collect_more' in obs['calls']
    if pending:
        raise ValueError('Missing tool result')
    expected = None
    if obs['validation'] == 'pass':
        expected = 'completed'
    elif obs['validation'] in {'conflict', 'invalid_output'}:
        expected = 'partial'
    elif obs['error'] and obs['attempts'][obs['calls'][-1]] == 2:
        expected = 'failed'
    elif not obs['error'] and 'collect_more' in obs['calls']:
        expected = 'partial'
    if expected and result['status'] != expected:
        raise ValueError('Incorrect terminal outcome')
    if result['status'] == 'completed' and obs['validation'] != 'pass':
        raise ValueError('Completion without observed validation')
    # Preserve old scenario-specific diagnostics; new inputs use only invariants.
    if case is not None:
        expected = 'completed' if case == 'existing' else 'partial'
        expected_calls = ['check_existing'] if case == 'existing' else ['check_existing', 'collect_more']
        if result['status'] != expected or obs['calls'] != expected_calls:
            raise ValueError('Unexpected scenario outcome or tool path')


def read_input(path):
    """External synthetic data, never shown to the model before tool retrieval."""
    data = json.loads(path.read_text())
    if set(data) != {'name', 'goal', 'existing', 'additional'} or any(
            not isinstance(data[key], str) or not data[key] for key in ['name', 'goal']):
        raise ValueError('Invalid synthetic input')
    for key in ['existing', 'additional']:
        if validate_evidence(data[key], data['goal']) == 'invalid_output':
            raise ValueError('Invalid synthetic evidence')
    return data


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--live', action='store_true')
    parser.add_argument('--case', choices=['existing', 'hold', 'both'], default='both')
    parser.add_argument('--output', type=Path)
    parser.add_argument('--input', type=Path, help='새 합성 입력 JSON: name, goal, existing, additional')
    args = parser.parse_args()
    data = read_input(args.input) if args.input else None
    settings = config()
    policy = load_policy(settings)
    if not args.live:
        print(json.dumps({'mode': 'dry-run', 'key_present': bool(settings.get('NVIDIA_API_KEY')),
                          'model_configured': bool(settings.get('MODEL_ID')), 'max_http_requests_per_case': policy.request_limit,
                          'max_runtime_seconds_per_case': policy.max_runtime_seconds,
                          'max_output_tokens_per_request': policy.max_output_tokens,
                          'daily_request_limit': policy.daily_request_limit, 'max_steps': policy.max_steps,
                          'tools': 'two synthetic local tools', 'http_requests': 0}))
        return
    if not settings.get('NVIDIA_API_KEY') or not settings.get('MODEL_ID'):
        parser.error('NVIDIA_API_KEY and MODEL_ID required; values omitted')
    base = settings.get('MODEL_BASE_URL', 'https://integrate.api.nvidia.com/v1')
    if base != 'https://integrate.api.nvidia.com/v1':
        parser.error('This check only sends credentials to the NVIDIA hosted endpoint')
    if args.output and args.output.exists():
        parser.error('Output already exists; choose a fresh path')
    budget = Budget(lambda payload: request(base, settings['NVIDIA_API_KEY'], payload,
                                            timeout=policy.request_timeout_seconds),
                    policy=policy, daily_path=settings.get('MODEL_DAILY_BUDGET_PATH'))
    total_requests = 0
    fixtures = {}
    try:
        for case in ([data['name']] if data else (['existing', 'hold'] if args.case == 'both' else [args.case])):
            budget.start_run()
            started = time.monotonic()
            tools = {'check_existing': lambda *_: data['existing'],
                     'collect_more': lambda *_: data['additional']} if data else None
            result = run(case, decide=ModelDecision(budget, settings['MODEL_ID'], policy),
                         max_steps=policy.max_steps, tools=tools, topic=data['goal'] if data else TOPIC)
            result.update({'run_id': 'live-' + uuid.uuid4().hex[:12], 'mode': 'live',
                           'model_id': settings['MODEL_ID'], 'http_requests': budget.count,
                           'limitations': ['실제 NIM 모델 판단 + 합성 로컬 도구/자료. NAT와 실제 검색 서비스는 미연결.']})
            for event in result['events']:
                if event['kind'] == 'decision' and event['tool']:
                    event['label'] = '모델의 도구 선택'
            fixtures[case] = {'label': '실모델 · ' + case, 'run': result}
            if args.output:
                args.output.parent.mkdir(parents=True, exist_ok=True)
                args.output.write_text(json.dumps(fixtures, ensure_ascii=False, indent=2) + '\n')
            print(json.dumps({'case': case, 'status': result['status'], 'http_requests': result['http_requests'],
                              'tools': [e['tool'] for e in result['events'] if e['kind'] == 'tool' and e['status'] == 'running'],
                              'seconds': round(time.monotonic() - started, 2)}, ensure_ascii=False), flush=True)
            check_expectation(result, None if data else case)
            total_requests += budget.count
    except urllib.error.HTTPError as exc:
        parser.exit(1, f'HTTP {exc.code}; requests={total_requests + (budget.count if budget else 0)}; body and credentials omitted\n')
    except (ValueError, KeyError, IndexError, TypeError, OSError):
        parser.exit(1, f'Probe incomplete: transport, response or budget; requests={total_requests + (budget.count if budget else 0)}; details omitted\n')


if __name__ == '__main__':
    main()
