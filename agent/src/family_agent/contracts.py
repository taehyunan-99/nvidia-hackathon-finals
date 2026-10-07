"""Shared family-v1 boundary; the teammate owns eligibility computation."""
import importlib
import json
from pathlib import Path
from jsonschema import Draft202012Validator, FormatChecker
from family_minimum.runtime import ROOT

SCHEMA = json.loads((ROOT / 'docs/catalog/contracts/family-v1.schema.json').read_text())
FIELDS = ('age', 'grade', 'companions', 'visit_date', 'booking', 'delivery', 'interest')


def check(name, value):
    Draft202012Validator({**SCHEMA, '$ref': '#/$defs/' + name}, format_checker=FormatChecker()).validate(value)
    return value


def validator():
    try:
        return importlib.import_module('family_minimum.family_validator').validate
    except ModuleNotFoundError as exc:
        if exc.name != 'family_minimum.family_validator':
            raise
        return None


def assess(payload, implementation):
    check('validation_input', payload)
    if implementation is None:
        # An integration hold, never a substitute eligibility algorithm.
        result = {k: payload[k] for k in ('schema_version', 'request_id', 'conditions_revision', 'candidate_id')}
        result.update(checks={field: {'verdict': 'unknown', 'reason_code': 'missing_source_fact',
            'evidence_ids': []} for field in FIELDS}, overall='unknown', needs=[],
            ignored_evidence_ids=[], availability='unverified')
    else:
        result = implementation(json.loads(json.dumps(payload)))
    check('validation_output', result)
    for key in ('request_id', 'conditions_revision', 'candidate_id'):
        if result[key] != payload[key]:
            raise ValueError('validator_identity_mismatch')
    known = {e['id'] for e in payload['evidence']}
    verdicts = []
    for field, item in result['checks'].items():
        if not set(item['evidence_ids']) <= known:
            raise ValueError('validator_unknown_evidence')
        if item['verdict'] == 'suitable' and not item['evidence_ids']:
            if not (field == 'delivery' and item['reason_code'] == 'not_requested'
                    and payload['conditions']['delivery_mode'] is None):
                raise ValueError('validator_ungrounded_suitable')
        verdicts.append(item['verdict'])
    overall = 'unsuitable' if 'unsuitable' in verdicts else 'unknown' if 'unknown' in verdicts else 'suitable'
    if result['overall'] != overall or not set(result['ignored_evidence_ids']) <= known:
        raise ValueError('validator_inconsistent_result')
    return result


def from_cards(cards):
    # Grade selections describe kinds of children, not a complete family census.
    result = check('conditions', {'interests': cards['interests'], 'district': cards['district'],
        'children': cards['children'] if 'children' in cards else [{'member_id': f'child-{i}', 'grade': grade, 'age_years': None}
                     for i, grade in enumerate(cards['grades'])] or None,
        'composition_complete': cards.get('composition_complete', False),
        'guardians': None if cards['guardians'] == 'unknown' else
            {'minimum': int(cards['guardians'].rstrip('+')), 'maximum': None if cards['guardians'] == '2+' else int(cards['guardians'])},
        'visit_date': cards['date'], 'delivery_mode': cards.get('delivery_mode')})

    children = result['children'] or []
    if result['composition_complete'] and not children: raise ValueError('missing_complete_composition')
    if len({c['member_id'] for c in children}) != len(children): raise ValueError('duplicate_member')
    for bounds in [c['age_years'] for c in children] + [result['guardians']]:
        if bounds and bounds['maximum'] is not None and bounds['minimum'] > bounds['maximum']: raise ValueError('invalid_range')
    return result
