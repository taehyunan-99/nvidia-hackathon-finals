import contextlib
import io
import json
import unittest
from unittest.mock import patch
import urllib.request

from probe_family_sources import SERVICE, SameHostRedirect, inspect_api, inspect_detail, main


class SourceProbeTests(unittest.TestCase):
    def test_dry_run_never_uses_network(self):
        with patch('sys.argv', ['probe_family_sources.py']), patch('probe_family_sources.fetch') as fetch:
            with contextlib.redirect_stdout(io.StringIO()):
                main()
            fetch.assert_not_called()

    def test_api_error_is_not_success_or_zero_candidates(self):
        result = inspect_api(json.dumps({'RESULT': {'CODE': 'ERROR-500'}}))
        self.assertEqual(result['status'], 'invalid_response')
        self.assertEqual(result['api_code'], 'ERROR-500')

    def test_rows_without_source_identity_are_not_accepted(self):
        raw = json.dumps({SERVICE: {'RESULT': {'CODE': 'INFO-000'}, 'row': [{'SVCNM': 'Example'}]}})
        self.assertEqual(inspect_api(raw)['status'], 'invalid_response')

    def test_periods_are_preserved_separately(self):
        row = {'SVCID': 'test', 'SVCNM': 'Example', 'RCPTBGNDT': '2026-09-01',
               'SVCOPNBGNDT': '2026-10-01', 'DTLCONT': 'conditions'}
        raw = json.dumps({SERVICE: {'RESULT': {'CODE': 'INFO-000'}, 'row': [row]}})
        result = inspect_api(raw)
        self.assertEqual(result['status'], 'ok')
        self.assertEqual(result['samples'][0]['RCPTBGNDT'], '2026-09-01')
        self.assertEqual(result['samples'][0]['SVCOPNBGNDT'], '2026-10-01')

    def test_error_page_cannot_supply_fake_conditions_from_script(self):
        raw = '<html>Unavailable<script>이용기간 접수기간</script></html>'.encode('utf-8')
        self.assertEqual(inspect_detail(raw, 'utf-8')['status'], 'detail_unverified')

    def test_redirect_cannot_switch_hosts(self):
        req = urllib.request.Request('https://yeyak.seoul.go.kr/test')
        with self.assertRaises(ValueError):
            SameHostRedirect().redirect_request(req, None, 302, '', {}, 'https://example.com/')


if __name__ == '__main__':
    unittest.main()
