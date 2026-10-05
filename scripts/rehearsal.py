"""Offline contract rehearsal: synthetic tools and a deterministic mock planner; no HTTP."""
import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CASES = {
    'existing': '기존 근거로 완료',
    'supplement': '추가 조사 후 완료',
    'hold': '자료 부족으로 보류',
    'failure': '도구 연결 실패',
    'retry': '일시 오류 후 재시도',
    'conflict': '근거 충돌로 보류',
}
TOPIC = '샘플 서비스의 로컬 실행 지원 여부'


def evidence(key, supported=True):
    return {'id': key, 'source': 'fixture://' + key, 'topic': TOPIC,
            'supported': supported, 'quote': '로컬 실행 지원' if supported else '로컬 실행 미지원'}


def check_existing(case, attempt):
    return [evidence('sample-a'), evidence('sample-b')] if case == 'existing' else [evidence('sample-a')]


def collect_more(case, attempt):
    if case == 'failure' or (case == 'retry' and attempt == 1):
        raise TimeoutError('합성 timeout: 실제 네트워크 요청 없음')
    if case == 'hold':
        return []
    return [evidence('sample-b', supported=case != 'conflict')]


TOOLS = {'check_existing': check_existing, 'collect_more': collect_more}


def read_input(path):
    """Read synthetic tool data shared by offline and live checks."""
    data = json.loads(path.read_text())
    if not isinstance(data, dict) or set(data) != {'name', 'goal', 'existing', 'additional'} or any(
            not isinstance(data[key], str) or not data[key] for key in ['name', 'goal']):
        raise ValueError('Invalid synthetic input')
    for key in ['existing', 'additional']:
        if validate_evidence(data[key], data['goal']) == 'invalid_output':
            raise ValueError('Invalid synthetic evidence')
    return data


def validate_evidence(rows, topic=TOPIC):
    """Independent fixture-domain check, not a claim of real-world source correctness."""
    if not isinstance(rows, list) or any(not isinstance(r, dict) for r in rows):
        return 'invalid_output'
    if any(set(r) != {'id', 'source', 'topic', 'supported', 'quote'} or
           not all(isinstance(r[k], str) and r[k] for k in ['id', 'source', 'topic', 'quote']) or
           type(r['supported']) is not bool or r['topic'] != topic for r in rows):
        return 'invalid_output'
    if len({r['id'] for r in rows}) != len(rows):
        return 'invalid_output'
    if len({r['supported'] for r in rows}) > 1:
        return 'conflict'
    if len({r['source'] for r in rows}) < 2:
        return 'insufficient'
    return 'pass'


def allowed_actions(observation):
    """State policy; no scenario names or expected paths are used here."""
    if observation['validation'] == 'pass':
        return ['complete']
    if observation['validation'] in {'conflict', 'invalid_output'}:
        return ['hold']
    if observation['error']:
        failed = observation['calls'][-1]
        return [failed, 'fail'] if observation['attempts'][failed] < 2 else ['fail']
    if not observation['calls']:
        return ['check_existing']
    if 'collect_more' in observation['calls']:
        return ['hold']
    return ['collect_more', 'hold']


def mock_decide(observation):
    """Deterministic test double: choose the first permitted action."""
    return observation['allowed_actions'][0], '관측에 따라 허용된 행동을 테스트용 규칙으로 선택합니다.'


def run(case, decide=mock_decide, tools=None, max_steps=6, topic=TOPIC):
    if case not in CASES and tools is None:
        raise ValueError('알 수 없는 예시')
    tools = TOOLS if tools is None else tools
    request = {'goal': topic, 'case': case, 'limits': {'max_steps': max_steps, 'max_attempts_per_tool': 2}}
    input_hash = hashlib.sha256(json.dumps(request, sort_keys=True).encode()).hexdigest()
    result = {'schema_version': 'research-v1', 'run_id': 'mock-' + input_hash[:12],
              'mode': 'mock', 'model_id': None, 'http_requests': 0, 'input_hash': input_hash,
              'input': request, 'status': 'running', 'events': [], 'evidence': [],
              'artifact': None, 'limitations': ['합성 자료·규칙 기반 mock 판단이며 모델/API/NAT 실행 근거가 아닙니다.'],
              'next_action': ''}
    obs = {'goal': topic, 'calls': [], 'attempts': {}, 'error': None,
           'validation': 'insufficient', 'evidence': []}

    def emit(kind, label, status, reason, tool=None, attempt=None, error=None, ids=None):
        result['events'].append({'seq': len(result['events']) + 1, 'kind': kind, 'label': label,
                                 'status': status, 'reason': reason, 'tool': tool, 'attempt': attempt,
                                 'error_code': error, 'evidence_ids': ids or []})

    for step in range(max_steps + 1):
        obs['allowed_actions'] = allowed_actions(obs)
        terminal = obs['allowed_actions'][0] if len(obs['allowed_actions']) == 1 and obs['allowed_actions'][0] in {'complete', 'hold', 'fail'} else None
        if terminal:
            action, reason = terminal, '실행 제어가 검증 결과와 남은 도구에 따라 종료했습니다: ' + obs['validation'] + (('; ' + obs['error']) if obs['error'] else '')
        else:
            if step == max_steps:
                result['status'] = 'partial'
                result['next_action'] = '단계 상한에 도달했습니다. 범위를 줄여 다시 실행하세요.'
                break
            action, reason = decide(deepcopy(obs))
        emit('decision', '실행 제어의 종료' if terminal else '다음 행동 선택', 'running', reason,
             tool=action if action in TOOLS else None)
        if action not in obs['allowed_actions']:
            result['status'] = 'failed'
            result['next_action'] = '현재 관측에서 허용되지 않은 행동을 수정하세요.'
            break
        if action in {'complete', 'hold', 'fail'}:
            if action == 'complete' and validate_evidence(result['evidence'], topic) != 'pass':
                result['status'] = 'failed'
                result['next_action'] = '완료 조건을 충족하지 않은 판단을 수정하세요.'
            else:
                result['status'] = {'complete': 'completed', 'hold': 'partial', 'fail': 'failed'}[action]
                result['next_action'] = {'complete': '근거를 확인하고 다음 입력을 검토하세요.',
                                         'hold': '누락되거나 충돌하는 자료를 확인한 뒤 다시 실행하세요.',
                                         'fail': '도구 연결 상태를 확인한 뒤 다시 실행하세요.'}[action]
                if action == 'complete':
                    result['artifact'] = {'summary': topic + ': ' + ('지원' if result['evidence'][0]['supported'] else '미지원'),
                                          'evidence_ids': [e['id'] for e in result['evidence']]}
            break
        if action not in TOOLS or action not in tools:
            result['status'] = 'failed'
            result['next_action'] = '허용되지 않은 도구 선택을 수정하세요.'
            break
        attempt = obs['attempts'].get(action, 0) + 1
        if attempt > 2:
            result['status'] = 'failed'
            result['next_action'] = '도구별 호출 상한에 도달했습니다.'
            break
        obs['attempts'][action] = attempt
        obs['calls'].append(action)
        emit('tool', action, 'running', '로컬 합성 도구 호출을 시작합니다.', action, attempt)
        try:
            rows = tools[action](case, attempt)
        except TimeoutError:
            obs['error'] = 'timeout'
            emit('tool', action, 'failed', '도구가 합성 timeout을 반환했습니다.', action, attempt, 'timeout')
            continue
        obs['error'] = None
        candidate = result['evidence'] + rows if isinstance(rows, list) else None
        verdict = validate_evidence(candidate, topic)
        if verdict != 'invalid_output':
            result['evidence'] = candidate
        ids = [r['id'] for r in result['evidence']]
        emit('tool', action, 'completed' if verdict != 'invalid_output' else 'failed',
             '도구 응답 수신; 결론 확정은 검증 후 가능합니다.', action, attempt,
             'invalid_output' if verdict == 'invalid_output' else None, ids)
        obs['validation'] = verdict
        obs['evidence'] = deepcopy(result['evidence'])
        emit('validation', '근거 검증', 'completed' if verdict == 'pass' else 'hold',
             {'pass': '두 출처의 주제와 값이 일치합니다.', 'insufficient': '서로 다른 두 출처가 필요합니다.',
              'conflict': '출처의 값이 서로 다릅니다.', 'invalid_output': '근거 형식 또는 식별자가 잘못되었습니다.'}[verdict], ids=ids)
    else:
        result['status'] = 'partial'
        result['next_action'] = '단계 상한에 도달했습니다. 범위를 줄여 다시 실행하세요.'
    emit('result', '실행 결과', {'completed': 'completed', 'partial': 'hold', 'failed': 'failed'}[result['status']],
         result['next_action'], ids=[r['id'] for r in result['evidence']])
    assert_result(result)
    return result


def assert_result(result):
    ids = {r['id'] for r in result['evidence']}
    if len(ids) != len(result['evidence']):
        raise ValueError('중복 근거 ID')
    for i, event in enumerate(result['events'], 1):
        if event['seq'] != i or not set(event['evidence_ids']) <= ids:
            raise ValueError('이벤트 순서 또는 근거 연결 오류')
    if result['status'] == 'completed':
        if validate_evidence(result['evidence'], result['input']['goal']) != 'pass' or not result['artifact']:
            raise ValueError('검증 전 완료 금지')
        if set(result['artifact']['evidence_ids']) != ids:
            raise ValueError('산출물 근거 불일치')
    elif result['artifact'] is not None:
        raise ValueError('보류/실패에서 확정 산출물 표시 금지')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    inputs = parser.add_mutually_exclusive_group()
    inputs.add_argument('--case', choices=CASES, default='supplement')
    inputs.add_argument('--input', type=Path, help='새 합성 입력 JSON: name, goal, existing, additional')
    inputs.add_argument('--write-fixtures', action='store_true', help='정적 화면의 예시 JSON을 명시적으로 재생성')
    args = parser.parse_args()
    if args.write_fixtures:
        target = ROOT / 'docs/playbooks/examples/research/fixtures.json'
        target.write_text(json.dumps({key: {'label': label, 'run': run(key)} for key, label in CASES.items()}, ensure_ascii=False, indent=2) + '\n')
        print(target.relative_to(ROOT))
    else:
        if args.input:
            try:
                data = read_input(args.input)
            except (ValueError, OSError):
                parser.error('Invalid synthetic input; check name, goal and evidence')
            result = run(data['name'], topic=data['goal'], tools={
                'check_existing': lambda *_: data['existing'],
                'collect_more': lambda *_: data['additional']})
        else:
            result = run(args.case)
        print(json.dumps(result, ensure_ascii=False, indent=2))
