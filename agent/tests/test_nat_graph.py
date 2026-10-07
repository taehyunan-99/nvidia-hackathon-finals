import asyncio
import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from family_minimum.runtime import Runtime, SERVICE


@unittest.skipUnless(importlib.util.find_spec('nat'), 'Requires the pinned NAT Linux environment')
class NATGraphTests(unittest.TestCase):
    def test_actual_registration_parsing_tool_and_validator(self):
        from family_minimum.run import execute
        with tempfile.TemporaryDirectory() as folder:
            replies = iter([
                'Thought: Inspect the public source.\nAction: search_experiences\nAction Input: {"query":"seoul_public_sample"}',
                'Thought: Observation contains S1.\nFinal Answer: {"status":"inspection_complete","service_ids":["S1"],"source_ids":["seoul_public_sample"]}',
            ])
            sender = Mock(side_effect=lambda _: {'choices': [{'finish_reason': 'stop', 'message': {'content': next(replies)}}]})
            fetcher = Mock(return_value=(json.dumps({SERVICE: {'RESULT': {'CODE': 'INFO-000'},
                'row': [{'SVCID': 'S1', 'SVCNM': 'TEST ONLY'}]}}).encode(), 'utf-8'))
            runtime = Runtime(Path(folder) / 'ledger.sqlite3', 'test', 'TEST_ONLY', send=sender, fetch_source=fetcher)
            now = [0]
            runtime.budget.clock = lambda: now[0]
            runtime.budget.started = 0
            runtime.budget.sleep = lambda seconds: now.__setitem__(0, now[0] + seconds)
            result = asyncio.run(execute(runtime))
            self.assertEqual(result['status'], 'inspection_complete')
            self.assertEqual(result['physical_model_requests'], 2)
            self.assertEqual(result['participation'], 'unverified')
            fetcher.assert_called_once()
            self.assertTrue(runtime.closed)
            self.assertIn('S1', json.dumps(sender.call_args.args[0]['messages']))

    def test_actual_nat_parser_retry_and_empty_source_hold(self):
        from family_minimum.run import execute
        with tempfile.TemporaryDirectory() as folder:
            replies = iter([
                'Thought: Inspect the source.\nAction: search_experiences',
                'Thought: Inspect the source.\nAction: search_experiences\nAction Input: {"query":"seoul_public_sample"}',
                'Thought: No source records.\nFinal Answer: {"status":"needs_confirmation","service_ids":[],"source_ids":["seoul_public_sample"]}',
            ])
            sender = Mock(side_effect=lambda _: {'choices': [{'finish_reason': 'stop', 'message': {'content': next(replies)}}]})
            fetcher = Mock(return_value=(json.dumps({SERVICE: {'RESULT': {'CODE': 'INFO-200'}, 'row': []}}).encode(), 'utf-8'))
            runtime = Runtime(Path(folder) / 'ledger.sqlite3', 'test', 'TEST_ONLY', send=sender, fetch_source=fetcher)
            now = [0]
            runtime.budget.clock = lambda: now[0]
            runtime.budget.started = 0
            runtime.budget.sleep = lambda seconds: now.__setitem__(0, now[0] + seconds)
            result = asyncio.run(execute(runtime))
            self.assertEqual(result['status'], 'needs_confirmation')
            self.assertEqual(result['physical_model_requests'], 3)
            self.assertEqual(runtime.steps, 3)
            fetcher.assert_called_once()


if __name__ == '__main__':
    unittest.main()
