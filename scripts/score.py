"""Aggregate explicit human ratings; unknown gates can never pass."""
import argparse
import json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]

def calculate(card, rubric):
    if card.get('rubric_version') != rubric['version']:
        raise ValueError('루브릭 버전 불일치')
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
        result = calculate(json.loads(args.scorecard.read_text()), json.loads((ROOT/'docs/evaluation/rubric.json').read_text()))
    except (ValueError, KeyError, TypeError, OSError) as exc:
        parser.exit(2, f'채점 오류: {exc}\n')
    print(json.dumps(result, ensure_ascii=False, indent=2))
