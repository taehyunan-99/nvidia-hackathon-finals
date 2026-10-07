import json
import sys
import tempfile
import unittest
import urllib.error
from dataclasses import replace
from pathlib import Path
from unittest.mock import Mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from family_minimum.runtime import Runtime, SERVICE
from model_policy import load_policy


def source(rows=None, code='INFO-000'):
    return json.dumps({SERVICE: {'RESULT': {'CODE': code},
        'row': rows if rows is not None else [{'SVCID': 'S1', 'SVCNM': '체험'}]}}).encode(), 'utf-8'


class RuntimeTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.sender = Mock(return_value={'choices': [{'message': {'content': 'answer'}, 'finish_reason': 'stop'}]})
        self.fetcher = Mock(return_value=source())
        self.runtime = Runtime(Path(self.temp.name) / 'ledger.sqlite3', 'test', 'TEST_ONLY',
            send=self.sender, fetch_source=self.fetcher)

    def test_source_ids_and_participation_remain_unverified(self):
        self.runtime.search('seoul_public_sample')
        result = self.runtime.validate(json.dumps({'status': 'inspection_complete',
            'service_ids': ['S1'], 'source_ids': ['seoul_public_sample']}))
        self.assertEqual(result['participation'], 'unverified')
        self.assertEqual(result['records'][0]['SVCID'], 'S1')

    def test_external_url_rejected_before_network(self):
        with self.assertRaises(ValueError):
            self.runtime.search('https://example.com/secrets')
        self.fetcher.assert_not_called()

    def test_fabricated_source_and_extra_claims_rejected(self):
        self.runtime.search('seoul_public_sample')
        for field, value in [('service_ids', ['invented']), ('source_ids', ['invented']),
                             ('participation', 'eligible'), ('service_ids', ['S1', 'S1'])]:
            result = {'status': 'inspection_complete', 'service_ids': ['S1'], 'source_ids': ['seoul_public_sample']}
            result[field] = value
            with self.assertRaises(ValueError): self.runtime.validate(json.dumps(result))

    def test_no_source_cannot_complete(self):
        with self.assertRaises(ValueError):
            self.runtime.validate('{"status":"inspection_complete","service_ids":[],"source_ids":[]}')

    def test_empty_error_and_invalid_data_do_not_complete(self):
        for response in [source([]), source(code='ERROR-300'), source([{'SVCID': 'S1'}])]:
            with self.subTest(response=response):
                self.runtime.tool_called = False
                self.fetcher.return_value = response
                self.runtime.search('seoul_public_sample')
                with self.assertRaises(ValueError):
                    self.runtime.validate('{"status":"inspection_complete","service_ids":["S1"],"source_ids":["seoul_public_sample"]}')
                result = self.runtime.validate('{"status":"needs_confirmation","service_ids":[],"source_ids":["seoul_public_sample"]}')
                self.assertEqual(result['status'], 'needs_confirmation')

    def test_duplicate_tool_is_cached_and_terminated_run_has_no_calls(self):
        first = self.runtime.search('seoul_public_sample')
        self.assertIs(first, self.runtime.search('seoul_public_sample'))
        self.fetcher.assert_called_once()
        self.runtime.close()
        for action in [lambda: self.runtime.search('seoul_public_sample'), lambda: self.runtime.model_request([])]:
            with self.assertRaises(ValueError): action()
        self.sender.assert_not_called()

    def test_parser_requests_and_provider_retries_use_same_budget(self):
        error = urllib.error.HTTPError('https://example.invalid', 429, 'limited', {}, None)
        self.sender.side_effect = [error, self.sender.return_value, self.sender.return_value]
        now = [0]
        self.runtime.budget.clock = lambda: now[0]
        self.runtime.budget.started = 0
        self.runtime.budget.sleep = lambda seconds: now.__setitem__(0, now[0] + seconds)
        self.runtime.model_request([])
        self.runtime.model_request([])
        self.assertEqual(self.runtime.budget.count, 3)
        self.assertEqual([event['physical_requests'] for event in self.runtime.events], [2, 1])
        self.assertEqual(self.sender.call_args.args[0]['max_tokens'], 1024)

    def test_step_limit_prevents_additional_physical_request(self):
        self.runtime.steps = self.runtime.policy.max_steps
        with self.assertRaises(ValueError): self.runtime.model_request([])
        self.sender.assert_not_called()

    def test_close_during_retry_wait_prevents_next_transport_request(self):
        self.sender.side_effect = urllib.error.HTTPError('https://example.invalid', 429, 'limited', {}, None)
        now = [0]
        self.runtime.budget.clock = lambda: now[0]
        self.runtime.budget.started = 0
        def close_during_wait(seconds):
            now[0] += seconds
            self.runtime.close()
        self.runtime.budget.sleep = close_during_wait
        with self.assertRaises(ValueError): self.runtime.model_request([])
        self.assertEqual(self.sender.call_count, 1)


if __name__ == '__main__':
    unittest.main()
