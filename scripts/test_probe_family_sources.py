import contextlib
import io
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import urllib.request

from probe_family_sources import SERVICE, SameHostRedirect, inspect_api, inspect_detail, main, source_key


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

    def test_empty_response_is_distinct_from_api_error(self):
        for code in ['INFO-000', 'INFO-200']:
            raw = json.dumps({SERVICE: {'RESULT': {'CODE': code}, 'row': []}})
            self.assertEqual(inspect_api(raw)['status'], 'empty')
        self.assertEqual(inspect_api(json.dumps({'RESULT': {'CODE': 'INFO-200'}}))['status'], 'empty')
        self.assertEqual(inspect_api(json.dumps({'RESULT': {'CODE': 'INFO-000'}}))['status'], 'invalid_response')

    def test_authenticated_dry_run_never_reads_key_or_uses_network(self):
        with patch('sys.argv', ['probe_family_sources.py', '--authenticated']), \
                patch('probe_family_sources.source_key') as key, patch('probe_family_sources.fetch') as fetch:
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                main()
            key.assert_not_called()
            fetch.assert_not_called()
            self.assertEqual(json.loads(output.getvalue())['api_transport'], 'https')

    def test_authenticated_http_requires_explicit_opt_in(self):
        with patch('sys.argv', ['probe_family_sources.py', '--authenticated', '--api-transport', 'http']), \
                patch('probe_family_sources.fetch') as fetch, contextlib.redirect_stderr(io.StringIO()):
            with self.assertRaises(SystemExit):
                main()
            fetch.assert_not_called()

    def test_env_key_overrides_file_and_empty_env_does_not_fall_back(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / '.env'
            path.write_text('SEOUL_OPEN_DATA_API_KEY="FileKey123" # local\n', encoding='utf-8')
            with patch.dict(os.environ, {}, clear=True):
                self.assertEqual(source_key(path), 'FileKey123')
            with patch.dict(os.environ, {'SEOUL_OPEN_DATA_API_KEY': 'EnvKey456'}):
                self.assertEqual(source_key(path), 'EnvKey456')
            with patch.dict(os.environ, {'SEOUL_OPEN_DATA_API_KEY': ''}):
                with self.assertRaises(ValueError):
                    source_key(path)

    def test_authenticated_output_redacts_url_and_echoed_key(self):
        secret = 'SyntheticKey123'
        row = {'SVCID': 'test', 'SVCNM': secret, 'DTLCONT': secret}
        raw = json.dumps({SERVICE: {'RESULT': {'CODE': 'INFO-000'}, 'row': [row]}}).encode()
        page = '이용기간 접수기간'.encode()
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / 'result'
            args = ['probe_family_sources.py', '--live', '--authenticated', '--output', str(target)]
            with patch('sys.argv', args), patch('probe_family_sources.source_key', return_value=secret), \
                    patch('probe_family_sources.fetch', side_effect=[(raw, 'utf-8')] + [(page, 'utf-8')] * 3):
                output = io.StringIO()
                with contextlib.redirect_stdout(output):
                    main()
            self.assertNotIn(secret, output.getvalue())
            for path in target.iterdir():
                self.assertNotIn(secret.encode(), path.read_bytes())
            observations = json.loads((target / 'observations.json').read_text(encoding='utf-8'))
            self.assertIn('[redacted]', observations['sources'][0]['url'])

    def test_http_error_never_exposes_request_url(self):
        secret = 'SyntheticKey123'
        error = urllib.error.HTTPError(f'https://openapi.seoul.go.kr/{secret}', 403, secret, {}, None)
        with patch('sys.argv', ['probe_family_sources.py', '--live', '--authenticated']), \
                patch('probe_family_sources.source_key', return_value=secret), \
                patch('probe_family_sources.fetch', side_effect=error):
            output = io.StringIO()
            with contextlib.redirect_stdout(output), self.assertRaises(SystemExit):
                main()
            self.assertNotIn(secret, output.getvalue())
            self.assertTrue(all(item['status'] == 'http_error' for item in json.loads(output.getvalue())['sources']))

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
