import copy
import json
from datetime import datetime
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[2]
CONTRACTS = ROOT / 'docs/catalog/contracts'


def merge(base, patch):
    if not isinstance(patch, dict):
        return copy.deepcopy(patch)
    result = copy.deepcopy(base) if isinstance(base, dict) else {}
    for key, value in patch.items():
        result[key] = merge(result.get(key), value)
    return result


def materialize(base, case):
    result = merge(base, case['patch'])
    for path in case.get('omit_paths', []):
        parts = path.split('.')
        parent = result
        for key in parts[:-1]:
            parent = parent[key]
        parent.pop(parts[-1], None)
    return result


def definition_validator(schema, name):
    return Draft202012Validator({**schema, '$ref': '#/$defs/' + name}, format_checker=FormatChecker())


def integrity_error(data):
    evidence = data['evidence']
    if any(row['candidate_id'] != data['candidate_id'] for row in evidence):
        return 'candidate_evidence_mismatch'
    if any(row['source_id'] not in data['trusted_source_ids'] for row in evidence):
        return 'untrusted_source'
    ids = {row['id'] for row in evidence}
    if len(ids) != len(evidence) or any(not set(fact['evidence_ids']) <= ids for fact in data['facts']):
        return 'invalid_evidence_reference'
    bounds = [child['age_years'] for child in (data['conditions']['children'] or [])]
    bounds.append(data['conditions']['guardians'])
    bounds.extend(fact['value'] for fact in data['facts'] if fact['field'] == 'allowed_age_range')
    if any(row and row['maximum'] is not None and row['minimum'] > row['maximum'] for row in bounds):
        return 'invalid_range'
    for fact in data['facts']:
        if fact['field'] in {'operating_period', 'booking_period'}:
            value = fact['value']
            if datetime.fromisoformat(value['start']) > datetime.fromisoformat(value['end']):
                return 'invalid_range'
    return None


def main():
    schema = json.loads((CONTRACTS / 'family-v1.schema.json').read_text(encoding='utf-8'))
    fixtures = json.loads((CONTRACTS / 'family-v1.cases.json').read_text(encoding='utf-8'))
    Draft202012Validator.check_schema(schema)
    check_input = definition_validator(schema, 'validation_input')
    check_input.validate(fixtures['base_input'])
    definition_validator(schema, 'validation_output').validate(fixtures['baseline_output'])
    assert integrity_error(fixtures['base_input']) is None
    baseline = fixtures['baseline_expectation']['checks']
    reason_codes = set(schema['$defs']['check']['properties']['reason_code']['enum'])
    negative = 0
    for case in fixtures['validation_cases']:
        data = materialize(fixtures['base_input'], case)
        errors = list(check_input.iter_errors(data))
        actual_error = 'schema_error' if errors else integrity_error(data)
        expected = case['expected']
        assert actual_error == expected.get('error'), (case['id'], actual_error, expected.get('error'))
        if actual_error:
            negative += 1
            assert expected['overall'] is None
            continue
        checks = {**baseline, **expected['checks']}
        overall = 'unsuitable' if 'unsuitable' in checks.values() else 'unknown' if 'unknown' in checks.values() else 'suitable'
        assert expected['overall'] == overall, case['id']
        assert set(expected['preferred_actions']) <= set(expected['allowed_actions']), case['id']
        assert set(expected['reason_codes'].values()) <= reason_codes, case['id']
    all_cases = fixtures['validation_cases'] + fixtures['agent_and_resume_cases']
    assert len({case['id'] for case in all_cases}) == len(all_cases)
    resume_count = 0
    for case in fixtures['agent_and_resume_cases']:
        if 'schema' in case:
            definition_validator(schema, case['schema']).validate(case['input'])
            resume_count += 1
    print(json.dumps({'contract': 'family-v1', 'schema_definitions': len(schema['$defs']),
        'validation_cases': len(fixtures['validation_cases']), 'intentional_invalid_inputs': negative,
        'agent_and_resume_cases': len(fixtures['agent_and_resume_cases']), 'resume_shapes_checked': resume_count,
        'family_verdict_implementation_tested': False}, ensure_ascii=False))


if __name__ == '__main__':
    main()
