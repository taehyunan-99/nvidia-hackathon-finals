"""Aggregate explicit human ratings; unknown gates can never pass."""
import argparse
import json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]

RUBRIC_FILES = {
    'finals-v1': 'rubric.json',
    'agent-v2': 'agent-rubric.json',
    'frontend-v2': 'frontend-rubric.json',
    'integration-v2': 'integration.json',
}

def load_rubric(version):
    if version not in RUBRIC_FILES:
        raise ValueError('지원하지 않는 루브릭 버전')
    return json.loads((ROOT/'docs/evaluation'/RUBRIC_FILES[version]).read_text())

def validate_rubric(rubric):
    if rubric.get('profile') and set(rubric['gate_conditions']) != set(rubric['gates']):
        raise ValueError('관문 조건 불일치')
    if len(rubric['gates']) != len(set(rubric['gates'])):
        raise ValueError('중복 관문')
    if rubric.get('profile') == 'integration':
        if 'criteria' in rubric:
            raise ValueError('통합 관문에 점수 항목을 넣을 수 없음')
        return
    rows = rubric['criteria']
    if len(rows) != len({r['id'] for r in rows}):
        raise ValueError('중복 채점 항목')
    if any(type(r['weight']) is not int or r['weight'] <= 0 for r in rows) or sum(r['weight'] for r in rows) != 100:
        raise ValueError('가중치는 양의 정수이며 합계 100이어야 함')
    if rubric.get('profile'):
        if any(set(r['anchors']) != {'0','1','2','3','4'} for r in rows):
            raise ValueError('0~4 관찰 기준 필요')

def has_evidence(row):
    values = row.get('evidence')
    return isinstance(values, list) and bool(values) and all(isinstance(e, str) and e.strip() for e in values)

def check_metadata(card):
    for key in ('subject', 'revision', 'environment'):
        if not isinstance(card.get(key), str) or not card[key].strip():
            raise ValueError(f'{key}: 대상·버전·환경 식별 필요')

def check_gates(card, rubric):
    if set(card.get('gates', {})) != set(rubric['gates']):
        raise ValueError('관문 누락 또는 알 수 없는 관문')
    blocking = []
    for key, row in card['gates'].items():
        if not isinstance(row, dict):
            raise ValueError(f'{key}: 관문 객체 필요')
        if row['status'] not in {'pass','fail','unknown'}:
            raise ValueError(f'{key}: pass/fail/unknown 필요')
        if not isinstance(row.get('note'), str) or not row['note'].strip():
            raise ValueError(f'{key}: 판정 이유 또는 다음 확인 필요')
        if row['status'] != 'unknown' and not has_evidence(row):
            raise ValueError(f'{key}: 통과/실패 근거 필요')
        if row['status'] != 'pass':
            blocking.append(f"{key}: {row['status']}")
    return blocking

def calculate_area(card, rubric):
    criteria = {r['id']: r for r in rubric['criteria']}
    if set(card.get('criteria', {})) != set(criteria):
        raise ValueError('채점 항목 누락 또는 알 수 없는 항목')
    if any(not isinstance(row, dict) for row in card['criteria'].values()):
        raise ValueError('항목별 채점 객체 필요')
    mode = card.get('assessment_mode')
    if mode not in {*rubric['mode_caps'], 'mixed'}:
        raise ValueError('design/mock/replay/live/mixed 평가 모드 필요')
    blocking = check_gates(card, rubric)
    score, unknown, low = 0, 0, []
    if any(r['rating'] is not None for r in card['criteria'].values()) or any(r['status'] != 'unknown' for r in card['gates'].values()):
        check_metadata(card)
    for key, spec in criteria.items():
        row = card['criteria'][key]
        rating = row['rating']
        if not isinstance(row.get('note'), str) or not row['note'].strip():
            raise ValueError(f'{key}: 판정 이유 또는 다음 확인 필요')
        if rating is None:
            unknown += spec['weight']
            continue
        if type(rating) is not int or not 0 <= rating <= 4:
            raise ValueError(f'{key}: 정수 0~4 또는 null 필요')
        caps = {'design':1, 'implementation':2, 'observed':4}
        level = row.get('evidence_level')
        evidence_mode = row.get('evidence_mode')
        if evidence_mode not in rubric['mode_caps'] or (mode != 'mixed' and evidence_mode != mode):
            raise ValueError(f'{key}: 항목 근거 모드와 평가 모드 불일치')
        if level not in caps or rating > min(caps[level], rubric['mode_caps'][evidence_mode]):
            raise ValueError(f'{key}: 평가 모드/관측 근거 수준을 넘는 등급')
        if not has_evidence(row):
            raise ValueError(f'{key}: 근거 목록 필요')
        score += spec['weight'] * rating / 4
        if rating < rubric['minimum_rating']:
            low.append(key)
    ready = score >= rubric['readiness_target'] and not unknown and not low and not blocking
    return {**{k: card.get(k) for k in ('subject','revision','environment','assessment_mode')},
            'rubric_version':rubric['version'], 'profile':rubric['profile'], 'score':score,
            'maximum':100, 'unassessed_weight':unknown, 'below_minimum':low,
            'blocking_gates':blocking, 'area_ready':ready, 'official_score':False}

def calculate_integration(card, rubric, assessments):
    validate_rubric(rubric)
    if card.get('rubric_version') != rubric['version'] or rubric.get('profile') != 'integration':
        raise ValueError('통합 루브릭 버전 불일치')
    blocking = check_gates(card, rubric)
    check_metadata(card)
    if card.get('assessment_mode') not in {'design','mock','replay','live'}:
        raise ValueError('평가 모드 필요')
    if set(assessments) != {'agent','frontend'}:
        raise ValueError('에이전트·프런트 평가 모두 필요')
    for profile, result in assessments.items():
        if result.get('profile') != profile or result.get('rubric_version') != f'{profile}-v2':
            raise ValueError('다른 영역/구버전 평가 혼합 불가')
        if any(result.get(k) != card[k] for k in ('subject','revision','environment')):
            raise ValueError('통합 대상·버전·환경 불일치')
    return {'subject':card['subject'], 'rubric_version':rubric['version'],
            'area_scores':{k:v['score'] for k,v in assessments.items()},
            'blocking_gates':blocking,
            'product_ready':card['assessment_mode'] == 'live' and not blocking and all(v['area_ready'] for v in assessments.values()),
            'official_score':False}

def calculate(card, rubric):
    if not isinstance(card, dict):
        raise ValueError('채점표 객체 필요')
    validate_rubric(rubric)
    if card.get('rubric_version') != rubric['version']:
        raise ValueError('루브릭 버전 불일치')
    if rubric.get('profile') == 'integration':
        raise ValueError('통합 평가는 두 영역 채점표가 필요함')
    if rubric.get('profile'):
        return calculate_area(card, rubric)
    criteria = {r['id']: r for r in rubric['criteria']}
    if set(card.get('criteria', {})) != set(criteria):
        raise ValueError('채점 항목 누락 또는 알 수 없는 항목')
    if set(card.get('gates', {})) != set(rubric['gates']):
        raise ValueError('관문 누락 또는 알 수 없는 관문')
    score, unknown = 0, 0
    for key, spec in criteria.items():
        row = card['criteria'][key]
        rating = row['rating']
        if rating is None:
            unknown += spec['weight']
            continue
        if type(rating) is not int or not 0 <= rating <= 4:
            raise ValueError(f'{key}: 정수 0~4 또는 null 필요')
        evidence = row.get('evidence')
        if not isinstance(evidence, list) or not evidence or not all(isinstance(e, str) and e.strip() for e in evidence):
            raise ValueError(f'{key}: 근거 목록 필요')
        score += spec['weight'] * rating / 4
    blocking = []
    for key, row in card['gates'].items():
        if row['status'] not in {'pass', 'fail', 'unknown'}:
            raise ValueError(f'{key}: pass/fail/unknown 필요')
        if row['status'] == 'pass':
            evidence = row.get('evidence')
            if not isinstance(evidence, list) or not evidence or not all(isinstance(e, str) and e.strip() for e in evidence):
                raise ValueError(f'{key}: 통과 근거 필요')
        else:
            blocking.append(f"{key}: {row['status']}")
    ready = score >= rubric['readiness_target'] and not unknown and not blocking
    return {'subject':card.get('subject'), 'score':score, 'maximum':100, 'unassessed_weight':unknown, 'blocking_gates':blocking, 'internal_ready':ready, 'official_score':False}

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('scorecard', type=Path)
    args = parser.parse_args()
    try:
        card = json.loads(args.scorecard.read_text())
        rubric = load_rubric(card.get('rubric_version'))
        if rubric.get('profile') == 'integration':
            refs = card.get('assessments', {})
            if set(refs) != {'agent','frontend'}:
                raise ValueError('에이전트·프런트 평가 파일 모두 필요')
            assessments = {}
            for profile, reference in refs.items():
                area = json.loads((args.scorecard.parent/reference).read_text())
                assessments[profile] = calculate(area, load_rubric(area.get('rubric_version')))
            result = calculate_integration(card, rubric, assessments)
        else:
            result = calculate(card, rubric)
    except (ValueError, KeyError, TypeError, OSError) as exc:
        parser.exit(2, f'채점 오류: {exc}\n')
    print(json.dumps(result, ensure_ascii=False, indent=2))
