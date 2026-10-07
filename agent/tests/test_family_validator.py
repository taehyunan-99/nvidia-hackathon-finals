import copy
import json
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'agent/src'))
sys.path.insert(0, str(ROOT / 'agent/contracts'))

from family_minimum.family_validator import ContractError, FIELDS, validate as validate_family
from check_contract import materialize
from check_validation import compare_cases


class FamilyValidationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.fixtures = json.loads((ROOT / 'docs/catalog/contracts/family-v1.cases.json').read_text(encoding='utf-8'))

    def setUp(self):
        self.data = copy.deepcopy(self.fixtures['base_input'])

    def fact(self, field):
        return next(f for f in self.data['facts'] if f['field'] == field)

    def verdict(self, field, verdict, reason):
        result = validate_family(self.data)
        self.assertEqual(result['checks'][field]['verdict'], verdict)
        self.assertEqual(result['checks'][field]['reason_code'], reason)
        self.assertEqual(result['availability'], 'unverified')
        return result

    def test_v01_to_v31_against_independent_answers(self):
        summary = compare_cases(self.fixtures)
        self.assertEqual(summary['cases'], 31)
        self.assertEqual(summary['failures'], [])

    def test_all_valid_cases_preserve_identity_evidence_and_aggregation(self):
        for case in self.fixtures['validation_cases']:
            if 'error' in case['expected']:
                continue
            with self.subTest(case=case['id']):
                data = materialize(self.fixtures['base_input'], case)
                output = validate_family(data)
                for key in ['schema_version', 'request_id', 'candidate_id', 'conditions_revision']:
                    self.assertEqual(output[key], data[key])
                for field, row in output['checks'].items():
                    evidence = list(dict.fromkeys(eid for f in data['facts']
                        if f['field'] in FIELDS[field] and f['scope_match'] != 'not_applicable'
                        for eid in f['evidence_ids']))
                    self.assertEqual(row['evidence_ids'], evidence)
                self.assertEqual(output['availability'], 'unverified')

    def test_all_cases_have_no_network_calls(self):
        with patch('urllib.request.urlopen', side_effect=AssertionError('Network forbidden')) as http, \
                patch('socket.socket', side_effect=AssertionError('Network forbidden')) as socket:
            self.assertEqual(compare_cases(self.fixtures)['failures'], [])
        http.assert_not_called()
        socket.assert_not_called()

    def test_revision_change_recomputes_and_does_not_mutate_previous_result(self):
        old = validate_family(self.data)
        self.data['conditions_revision'] = 2
        self.data['conditions']['visit_date'] = '2026-10-10'
        new = validate_family(self.data)
        self.assertEqual((old['conditions_revision'], old['overall']), (1, 'suitable'))
        self.assertEqual((new['conditions_revision'], new['overall']), (2, 'unsuitable'))

    def test_exact_baseline_output_and_input_preserved(self):
        original = copy.deepcopy(self.data)
        self.assertEqual(validate_family(self.data), self.fixtures['baseline_output'])
        self.assertEqual(self.data, original)

    def test_errors_never_generate_business_verdicts(self):
        for case in self.fixtures['validation_cases']:
            if 'error' in case['expected']:
                with self.subTest(case=case['id']):
                    with self.assertRaises(ContractError) as caught:
                        validate_family(materialize(self.fixtures['base_input'], case))
                    self.assertEqual(caught.exception.code, case['expected']['error'])

    def test_missing_family_does_not_become_eligible(self):
        self.data['conditions']['children'] = None
        self.data['conditions']['guardians'] = None
        result = validate_family(self.data)
        for field in ['age', 'grade', 'companions']:
            self.assertEqual(result['checks'][field]['reason_code'], 'missing_user_input')
        self.assertEqual(result['overall'], 'unknown')

    def test_known_child_mismatch_survives_missing_other_child(self):
        self.data['conditions']['children'] = [
            {'member_id': 'unknown', 'grade': None, 'age_years': None},
            {'member_id': 'too-young', 'grade': 'preschool', 'age_years': {'minimum': 4, 'maximum': 4}}]
        self.data['conditions']['composition_complete'] = False
        self.verdict('age', 'unsuitable', 'age_mismatch')
        self.verdict('grade', 'unsuitable', 'grade_mismatch')

    def test_unbounded_age_is_ambiguous_only_with_upper_restriction(self):
        self.data['conditions']['children'][0]['age_years'] = {'minimum': 7, 'maximum': None}
        self.verdict('age', 'unknown', 'age_range_ambiguous')
        self.fact('allowed_age_range')['value']['maximum'] = None
        self.verdict('age', 'suitable', 'matched')

    def test_age_boundaries_are_inclusive(self):
        for age in [5, 12]:
            self.data['conditions']['children'][0]['age_years'] = {'minimum': age, 'maximum': age}
            self.verdict('age', 'suitable', 'matched')

    def test_unrestricted_grade_needs_no_grade_input(self):
        self.fact('allowed_grades')['value'] = ['preschool', '1', '2', '3', '4', '5', '6', 'teen']
        self.data['conditions']['children'] = None
        self.verdict('grade', 'suitable', 'explicitly_unrestricted')

    def test_ignored_evidence_is_preserved(self):
        case = next(c for c in self.fixtures['validation_cases'] if c['id'] == 'V17')
        result = validate_family(materialize(self.data, case))
        self.assertEqual(result['ignored_evidence_ids'], ['e-conflict'])
        self.assertNotIn('e-conflict', result['checks']['age']['evidence_ids'])

    def test_wrong_target_is_unresolved(self):
        self.fact('allowed_age_range')['applies_to'] = 'session'
        self.verdict('age', 'unknown', 'scope_unresolved')

    def test_equivalent_set_claims_do_not_conflict(self):
        fact = copy.deepcopy(self.fact('allowed_grades'))
        fact['id'] = 'same-grades'
        fact['value'].reverse()
        self.data['facts'].append(fact)
        self.verdict('grade', 'suitable', 'matched')

    def test_known_party_over_cap_survives_missing_guardians(self):
        self.data['conditions']['guardians'] = None
        self.fact('participant_max')['value'] = 0
        self.verdict('companions', 'unsuitable', 'party_size_exceeded')

    def test_exact_guardian_requirement_uses_full_range(self):
        fact = self.fact('guardian_min')
        fact['field'] = 'guardian_exact'
        self.data['conditions']['guardians'] = {'minimum': 1, 'maximum': 2}
        self.verdict('companions', 'unknown', 'count_range_ambiguous')
        self.data['conditions']['guardians'] = {'minimum': 2, 'maximum': 2}
        self.verdict('companions', 'unsuitable', 'guardian_missing')

    def test_period_is_not_a_session_and_session_needs_no_period(self):
        self.data['facts'] = [f for f in self.data['facts'] if f['field'] not in {'session_dates', 'weekdays'}]
        self.verdict('visit_date', 'unknown', 'missing_source_fact')
        self.data = copy.deepcopy(self.fixtures['base_input'])
        self.data['facts'] = [f for f in self.data['facts'] if f['field'] != 'operating_period']
        self.verdict('visit_date', 'suitable', 'matched')

    def test_weekday_only_and_period_boundary(self):
        self.data['facts'] = [f for f in self.data['facts'] if f['field'] != 'session_dates']
        self.verdict('visit_date', 'suitable', 'matched')
        self.data['conditions']['visit_date'] = '2026-11-01'
        self.verdict('visit_date', 'unsuitable', 'session_mismatch')

    def test_booking_boundary_and_timezone_compare_instants(self):
        self.data['as_of'] = '2026-10-10T14:59:59Z'
        self.verdict('booking', 'suitable', 'matched')
        self.data['as_of'] = '2026-10-10T15:00:00Z'
        self.verdict('booking', 'unknown', 'conflicting_evidence')

    def test_contract_valid_lowercase_timestamp(self):
        self.data['as_of'] = '2026-10-07t05:00:00z'
        self.fact('booking_period')['value']['start'] = '2026-10-01t00:00:00z'
        self.verdict('booking', 'suitable', 'matched')

    def test_booking_cancelled_and_missing_status(self):
        self.fact('booking_status')['value'] = 'cancelled'
        self.verdict('booking', 'unsuitable', 'booking_cancelled')
        self.data['facts'] = [f for f in self.data['facts'] if f['field'] != 'booking_status']
        self.verdict('booking', 'unknown', 'missing_source_fact')

    def test_delivery_not_requested_keeps_evidence(self):
        self.data['conditions']['delivery_mode'] = None
        self.fact('delivery_mode')['value'] = 'online'
        result = self.verdict('delivery', 'suitable', 'not_requested')
        self.assertEqual(result['checks']['delivery']['evidence_ids'], ['e-delivery_mode'])

    def test_needs_distinguish_user_source_and_alternative(self):
        self.data['conditions']['visit_date'] = None
        self.fact('allowed_age_range')['value']['minimum'] = 8
        self.data['facts'] = [f for f in self.data['facts'] if f['field'] != 'allowed_grades']
        needs = validate_family(self.data)['needs']
        self.assertIn({'kind': 'user_input', 'field': 'visit_date', 'reason_code': 'missing_user_input'}, needs)
        self.assertIn({'kind': 'alternative', 'field': 'age', 'reason_code': 'age_mismatch'}, needs)
        self.assertIn({'kind': 'detail', 'field': 'grade', 'reason_code': 'missing_source_fact'}, needs)

    def test_duplicate_id_and_inverted_period_rejected(self):
        for mutation, code in [
            (lambda: self.data['facts'].append(copy.deepcopy(self.data['facts'][0])), 'invalid_evidence_reference'),
            (lambda: self.data['evidence'].append(copy.deepcopy(self.data['evidence'][0])), 'invalid_evidence_reference'),
            (lambda: self.data['conditions']['children'].append(copy.deepcopy(self.data['conditions']['children'][0])), 'schema_error'),
            (lambda: self.fact('operating_period')['value'].update(start='2026-11-01'), 'invalid_range')]:
            self.data = copy.deepcopy(self.fixtures['base_input'])
            mutation()
            with self.assertRaises(ContractError) as caught:
                validate_family(self.data)
            self.assertEqual(caught.exception.code, code)

    def test_audit_detects_three_error_categories(self):
        fixtures = copy.deepcopy(self.fixtures)
        fixtures['validation_cases'] = [copy.deepcopy(fixtures['validation_cases'][0])]
        expected = fixtures['validation_cases'][0]['expected']
        expected['checks']['age'] = 'unknown'
        self.assertEqual(compare_cases(fixtures)['mismatch_counts']['false_suitable'], 1)
        expected['checks']['age'] = 'suitable'
        fixtures['validation_cases'][0]['patch'] = {'conditions': {'visit_date': None}}
        summary = compare_cases(fixtures)
        self.assertEqual(summary['mismatch_counts']['excessive_unknown'], 2)
        expected['error'] = 'schema_error'
        self.assertEqual(compare_cases(fixtures)['mismatch_counts']['contract_error'], 1)


if __name__ == '__main__':
    unittest.main()
