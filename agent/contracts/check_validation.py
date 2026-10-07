import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'agent/src'))

from family_minimum.family_validator import ContractError, contract_validator, validate as validate_family
from check_contract import materialize


def compare_cases(fixtures):
    failures = []
    counts = dict(false_suitable=0, excessive_unknown=0, contract_error=0, other_mismatch=0)
    for case in fixtures['validation_cases']:
        expected = case['expected']
        try:
            output = validate_family(materialize(fixtures['base_input'], case))
        except ContractError as error:
            if error.code != expected.get('error'):
                counts['contract_error'] += 1
                failures.append({'case': case['id'], 'field': 'error', 'expected': expected.get('error'), 'actual': error.code})
            continue
        if expected.get('error') or not contract_validator('validation_output').is_valid(output):
            counts['contract_error'] += 1
            failures.append({'case': case['id'], 'field': 'error', 'expected': expected.get('error'), 'actual': 'business_verdict'})
            continue
        checks = {**fixtures['baseline_expectation']['checks'], **expected['checks']}
        comparisons = [(field, verdict, output['checks'][field]['verdict']) for field, verdict in checks.items()]
        comparisons.append(('overall', expected['overall'], output['overall']))
        comparisons.extend((field + '.reason_code', reason, output['checks'][field]['reason_code']) for field, reason in expected['reason_codes'].items())
        for field, wanted, actual in comparisons:
            if wanted != actual:
                category = 'false_suitable' if actual == 'suitable' else 'excessive_unknown' if actual == 'unknown' and wanted != 'unknown' else 'other_mismatch'
                counts[category] += 1
                failures.append({'case': case['id'], 'field': field, 'expected': wanted, 'actual': actual})
    return {'contract': 'family-v1', 'cases': len(fixtures['validation_cases']),
        'mismatch_counts': counts, 'failures': failures}


def main():
    fixtures = json.loads((ROOT / 'docs/catalog/contracts/family-v1.cases.json').read_text(encoding='utf-8'))
    summary = compare_cases(fixtures)
    print(json.dumps(summary, ensure_ascii=False))
    return bool(summary['failures'])


if __name__ == '__main__':
    sys.exit(main())
