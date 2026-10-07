import json
import os
from datetime import date, datetime
from functools import lru_cache
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker


FIELDS = {
    'age': ('allowed_age_range',),
    'grade': ('allowed_grades',),
    'companions': ('guardian_min', 'guardian_exact', 'participant_max'),
    'visit_date': ('operating_period', 'session_dates', 'weekdays'),
    'booking': ('booking_status', 'booking_period'),
    'delivery': ('delivery_mode',),
    'interest': ('interest_tags',),
}


class ContractError(ValueError):
    def __init__(self, code):
        self.code = code
        super().__init__(code)


@lru_cache(maxsize=2)
def contract_validator(name):
    root = Path(os.environ.get('FAMILY_PROJECT_ROOT', Path(__file__).resolve().parents[3]))
    schema = json.loads((root / 'docs/catalog/contracts/family-v1.schema.json').read_text(encoding='utf-8'))
    return Draft202012Validator({**schema, '$ref': '#/$defs/' + name}, format_checker=FormatChecker())


def integrity_error(data):
    evidence = data['evidence']
    if any(row['candidate_id'] != data['candidate_id'] for row in evidence):
        return 'candidate_evidence_mismatch'
    if any(row['source_id'] not in data['trusted_source_ids'] for row in evidence):
        return 'untrusted_source'
    ids = {row['id'] for row in evidence}
    facts = data['facts']
    if (len(ids) != len(evidence) or len({f['id'] for f in facts}) != len(facts)
            or any(not set(f['evidence_ids']) <= ids for f in facts)):
        return 'invalid_evidence_reference'
    children = data['conditions']['children'] or []
    if len({c['member_id'] for c in children}) != len(children):
        return 'schema_error'
    bounds = [c['age_years'] for c in children] + [data['conditions']['guardians']]
    bounds.extend(f['value'] for f in facts if f['field'] == 'allowed_age_range')
    if any(b and b['maximum'] is not None and b['minimum'] > b['maximum'] for b in bounds):
        return 'invalid_range'
    for fact in facts:
        if fact['field'] in {'operating_period', 'booking_period'}:
            value = fact['value']
            if timestamp(value['start']) > timestamp(value['end']):
                return 'invalid_range'
    return None


def timestamp(value):
    return datetime.fromisoformat(value.replace('z', '+00:00'))


def check(verdict, reason='matched', evidence=()):
    return {'verdict': verdict, 'reason_code': reason, 'evidence_ids': list(dict.fromkeys(evidence))}


def canonical(value):
    if isinstance(value, list):
        return tuple(sorted(set(value)))
    if isinstance(value, dict):
        return tuple(sorted(value.items()))
    return value


class Facts:
    def __init__(self, data, condition):
        target = 'child' if condition in {'age', 'grade'} else 'family' if condition == 'companions' else 'session'
        rows = [f for f in data['facts'] if f['field'] in FIELDS[condition] and f['scope_match'] != 'not_applicable']
        self.evidence = [eid for f in rows for eid in f['evidence_ids']]
        self.values = {}
        self.problem = None
        for field in FIELDS[condition]:
            matching = [f for f in rows if f['field'] == field and f['scope_match'] == 'applicable' and f['applies_to'] == target]
            if len({canonical(f['value']) for f in matching}) > 1:
                self.problem = 'conflicting_evidence'
            if matching:
                self.values[field] = matching[0]['value']
        if any(f['scope_match'] == 'unresolved' or f['applies_to'] != target for f in rows):
            self.problem = 'scope_unresolved'

    def result(self, verdict, reason='matched'):
        return check(verdict, reason, self.evidence)


def child_check(conditions, facts, kind):
    key = FIELDS[kind][0]
    if key not in facts.values:
        return facts.result('unknown', 'missing_source_fact')
    allowed = facts.values[key]
    unrestricted = (allowed['minimum'] == 0 and allowed['maximum'] is None) if kind == 'age' else set(allowed) == {'preschool', '1', '2', '3', '4', '5', '6', 'teen'}
    if unrestricted:
        return facts.result('suitable', 'explicitly_unrestricted')
    children = conditions['children']
    if children is None:
        return facts.result('unknown', 'missing_user_input')
    missing, ambiguous = False, False
    for child in children:
        value = child['age_years' if kind == 'age' else 'grade']
        if value is None:
            missing = True
        elif kind == 'grade':
            if value not in allowed:
                return facts.result('unsuitable', 'grade_mismatch')
        else:
            low, high = value['minimum'], value['maximum']
            upper = allowed['maximum']
            if (high is not None and high < allowed['minimum']) or (upper is not None and low > upper):
                return facts.result('unsuitable', 'age_mismatch')
            if low < allowed['minimum'] or (upper is not None and (high is None or high > upper)):
                ambiguous = True
    if missing:
        return facts.result('unknown', 'missing_user_input')
    if ambiguous:
        return facts.result('unknown', 'age_range_ambiguous')
    if not conditions['composition_complete']:
        return facts.result('unknown', 'partial_composition')
    return facts.result('suitable')


def companion_check(conditions, facts):
    values = facts.values
    if not values:
        return facts.result('unknown', 'missing_source_fact')
    exact, minimum = values.get('guardian_exact'), values.get('guardian_min')
    if exact is not None and minimum is not None and exact < minimum:
        return facts.result('unknown', 'conflicting_evidence')
    guardians, children = conditions['guardians'], conditions['children']
    ambiguous, missing = False, False
    if minimum is not None or exact is not None:
        if guardians is None:
            missing = True
        else:
            low, high = guardians['minimum'], guardians['maximum']
            if minimum is not None:
                if high is not None and high < minimum:
                    return facts.result('unsuitable', 'guardian_missing')
                ambiguous |= low < minimum
            if exact is not None:
                if low > exact or (high is not None and high < exact):
                    return facts.result('unsuitable', 'guardian_missing')
                ambiguous |= low != exact or high != exact
    cap = values.get('participant_max')
    if cap is not None:
        low = (len(children) if children else 0) + (guardians['minimum'] if guardians else 0)
        if low > cap:
            return facts.result('unsuitable', 'party_size_exceeded')
        if children is None or guardians is None:
            missing = True
        elif guardians['maximum'] is None or len(children) + guardians['maximum'] > cap:
            ambiguous = True
    if missing:
        return facts.result('unknown', 'missing_user_input')
    if not conditions['composition_complete']:
        return facts.result('unknown', 'partial_composition')
    if ambiguous:
        return facts.result('unknown', 'count_range_ambiguous')
    return facts.result('suitable')


def visit_check(conditions, facts):
    visit = conditions['visit_date']
    if visit is None:
        return facts.result('unknown', 'missing_user_input')
    values = facts.values
    period = values.get('operating_period')
    if period and not period['start'] <= visit <= period['end']:
        return facts.result('unsuitable', 'session_mismatch')
    if 'session_dates' in values and visit not in values['session_dates']:
        return facts.result('unsuitable', 'session_mismatch')
    if 'weekdays' in values and date.fromisoformat(visit).isoweekday() not in values['weekdays']:
        return facts.result('unsuitable', 'session_mismatch')
    if 'session_dates' not in values and 'weekdays' not in values:
        return facts.result('unknown', 'missing_source_fact')
    return facts.result('suitable')


def booking_check(data, facts):
    status = facts.values.get('booking_status')
    if status in {'closed', 'full', 'cancelled'}:
        return facts.result('unsuitable', 'booking_' + status)
    if status is None:
        return facts.result('unknown', 'missing_source_fact')
    if status == 'unknown':
        return facts.result('unknown', 'booking_state_unknown')
    period = facts.values.get('booking_period')
    if period:
        now = timestamp(data['as_of'])
        if not timestamp(period['start']) <= now <= timestamp(period['end']):
            return facts.result('unknown', 'conflicting_evidence')
    return facts.result('suitable')


def preference_check(conditions, facts, kind):
    key = FIELDS[kind][0]
    if key not in facts.values:
        return facts.result('unknown', 'missing_source_fact')
    requested = conditions['delivery_mode' if kind == 'delivery' else 'interests']
    if kind == 'delivery' and requested is None:
        return facts.result('suitable', 'not_requested')
    if not requested:
        return facts.result('unknown', 'missing_user_input')
    matched = requested == facts.values[key] if kind == 'delivery' else bool(set(requested) & set(facts.values[key]))
    return facts.result('suitable' if matched else 'unsuitable', 'matched' if matched else kind + '_mismatch')


def validate(payload: dict) -> dict:
    data = payload
    if not contract_validator('validation_input').is_valid(data):
        raise ContractError('schema_error')
    error = integrity_error(data)
    if error:
        raise ContractError(error)
    checks = {}
    for kind in FIELDS:
        facts = Facts(data, kind)
        if facts.problem:
            result = facts.result('unknown', facts.problem)
        elif kind in {'age', 'grade'}:
            result = child_check(data['conditions'], facts, kind)
        elif kind == 'companions':
            result = companion_check(data['conditions'], facts)
        elif kind == 'visit_date':
            result = visit_check(data['conditions'], facts)
        elif kind == 'booking':
            result = booking_check(data, facts)
        else:
            result = preference_check(data['conditions'], facts, kind)
        checks[kind] = result
    verdicts = [row['verdict'] for row in checks.values()]
    overall = 'unsuitable' if 'unsuitable' in verdicts else 'unknown' if 'unknown' in verdicts else 'suitable'
    needs = []
    for field, row in checks.items():
        if row['verdict'] == 'suitable':
            continue
        reason = row['reason_code']
        if row['verdict'] == 'unsuitable':
            kinds = ['alternative']
        elif reason in {'missing_user_input', 'partial_composition', 'age_range_ambiguous', 'count_range_ambiguous'}:
            kinds = ['user_input']
        elif reason == 'missing_source_fact':
            kinds = ['detail', 'official_source']
        else:
            kinds = ['official_source']
        needs.extend({'kind': kind, 'field': field, 'reason_code': reason} for kind in kinds)
    output = {key: data[key] for key in ('schema_version', 'request_id', 'conditions_revision', 'candidate_id')}
    output.update(checks=checks, overall=overall, needs=needs,
        ignored_evidence_ids=list(dict.fromkeys(eid for f in data['facts'] if f['scope_match'] == 'not_applicable' for eid in f['evidence_ids'])),
        availability='unverified')
    contract_validator('validation_output').validate(output)
    return output
