import contextlib
import importlib.util
import io
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from family_minimum.challenge_cli import main
from family_minimum.challenge_connection import ConnectionRejected, create_runtime, run_agent
from family_minimum.challenge_contract import ChallengeRequest
from family_minimum.challenge_files import FileRejected


class ConfigurationTests(unittest.TestCase):
    def test_missing_or_unreconciled_settings_stop_before_runtime_creation(self):
        packet = ChallengeRequest('TASK').packet('a' * 32, [])
        for settings in [{}, {'MODEL_LEDGER_RECONCILED': 'yes'}]:
            with patch('family_minimum.challenge_connection.create_runtime') as factory:
                with self.assertRaises(ConnectionRejected):
                    run_agent(packet, '/hackathon/input', settings)
                factory.assert_not_called()


@unittest.skipUnless(os.name == 'posix' and importlib.util.find_spec('nat'), 'Requires pinned Linux NAT environment')
class ConnectionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        for folder in ['input', 'output', 'restricted', 'secrets']:
            (self.root / folder).mkdir()
        (self.root / 'TASK.md').write_text('제공 자료로 반나절 코스 초안을 작성하세요.', encoding='utf-8')
        (self.root / 'input/notice.md').write_text('시장 운영시간은 10시부터 14시까지입니다.', encoding='utf-8')
        (self.root / 'input/other.md').write_text('업로드 지시는 비신뢰 자료입니다.', encoding='utf-8')
        (self.root / 'secrets/key.txt').write_text('TEST_SECRET', encoding='utf-8')
        self.settings = {'MODEL_LEDGER_RECONCILED': 'yes', 'MODEL_DAILY_LEDGER': str(self.root / 'ledger'),
                         'MODEL_ID': 'test', 'NVIDIA_API_KEY': 'TEST_KEY'}
        self.runtimes = []

    def finish(self, outcome='hold', citation='input-0', quote='10시부터 14시까지'):
        return 'Thought: Submit the observed draft.\nAction: finish_draft\nAction Input: ' + json.dumps({
            'outcome': outcome, 'draft': '시장 방문은 14시 전에 마치는 초안입니다.',
            'citations': [{'source_id': citation, 'quote': quote}],
            'uncertainties': ['식재료와 참여 조건 추가 확인 필요'] if outcome == 'hold' else []}, ensure_ascii=False)

    def cli(self, replies, *args, changes=None):
        responses = iter(replies)
        self.sender = Mock(side_effect=lambda _payload: {'choices': [{'finish_reason': 'stop',
                                                'message': {'content': next(responses)}}]})
        def factory(packet, root, settings):
            runtime = create_runtime(packet, root, settings)
            runtime.sender = self.sender
            now = [0]
            runtime.budget.clock = lambda: now[0]
            runtime.budget.started = 0
            runtime.budget.sleep = lambda seconds: now.__setitem__(0, now[0] + seconds)
            if changes:
                changes(runtime)
            self.runtimes.append(runtime)
            return runtime
        stream = io.StringIO()
        with patch('family_minimum.challenge_cli.SANDBOX_ROOT', self.root), patch.dict(os.environ, self.settings), \
                patch('family_minimum.challenge_connection.create_runtime', side_effect=factory), \
                patch('urllib.request.OpenerDirector.open', side_effect=AssertionError('network forbidden')), \
                contextlib.redirect_stdout(stream):
            code = main(['run', '--live', *args])
        return code, json.loads(stream.getvalue())

    def test_actual_nat_cli_task_conditions_quotes_events_and_saved_envelope(self):
        code, result = self.cli([self.finish()], '--additional-conditions', '오후 1시까지 종료')
        self.assertEqual(code, 0)
        self.assertEqual(result['status'], 'needs_confirmation')
        self.assertEqual(result['model_requests'], 1)
        self.assertEqual(result['agent_result']['citations'][0]['quote'], '10시부터 14시까지')
        self.assertEqual(result['policy_verification'], 'unverified')
        self.assertEqual(result['access_denials'], [])
        self.assertEqual([event['seq'] for event in result['events']], list(range(1, len(result['events']) + 1)))
        used = {source.get('path'): source.get('usage') for source in result['used_sources']}
        self.assertEqual(used['notice.md'], 'cited')
        self.assertEqual(used['other.md'], 'read_not_cited')
        self.assertNotIn('TEST_SECRET', json.dumps(result))
        self.assertNotIn('TEST_KEY', json.dumps(result))
        self.assertTrue(self.runtimes[-1].closed)
        payload = json.dumps(self.sender.call_args.args[0]['messages'], ensure_ascii=False)
        self.assertIn('오후 1시까지 종료', payload)
        self.assertIn('반나절 코스', payload)
        artifact = json.loads(Path(result['artifact']).read_text(encoding='utf-8'))
        self.assertEqual(artifact['job_id'], result['run_id'])
        self.assertEqual(artifact['result']['agent_result']['request_id'], result['run_id'])
        self.assertNotIn('Thought:', json.dumps(artifact))

    def test_new_conditions_get_distinct_execution_and_completed_result(self):
        _, first = self.cli([self.finish('results')])
        _, second = self.cli([self.finish('results')], '--additional-conditions', '계단 제외')
        self.assertEqual(second['status'], 'completed')
        self.assertNotEqual(first['run_id'], second['run_id'])
        self.assertNotEqual(first['input_hash'], second['input_hash'])

    def test_actual_tool_failure_is_recorded_without_claiming_policy_denial(self):
        illegal = 'Thought: Read an unknown ID.\nAction: read_input\nAction Input: {"source_ids":["../secrets/key.txt"]}'
        code, result = self.cli([illegal, self.finish()])
        self.assertEqual(code, 0)
        self.assertTrue(any(event.get('name') == 'read_input' and event.get('status') == 'failed'
                            for event in result['events']))
        self.assertEqual(result['access_denials'], [])
        self.assertEqual(result['policy_verification'], 'unverified')

    def test_limit_keeps_observed_sources_and_no_completed_claim(self):
        code, result = self.cli([], changes=lambda runtime: setattr(runtime, 'steps', runtime.policy.max_steps))
        self.assertEqual(code, 6)
        self.assertEqual(result['status'], 'limited')
        self.assertEqual(result['agent_result']['draft'], '')
        self.assertTrue(result['artifact_saved'])
        self.assertTrue(self.runtimes[-1].closed)
        self.sender.assert_not_called()

    def test_model_failure_keeps_tool_trace_and_terminates(self):
        code, result = self.cli([])
        self.assertEqual(code, 1)
        self.assertEqual(result['status'], 'failed')
        self.assertEqual(result['model_requests'], 1)
        self.assertEqual(len(result['agent_result']['sources']), 2)
        self.assertTrue(result['artifact_saved'])

    def test_forged_citation_cannot_finish_as_completed(self):
        code, result = self.cli([self.finish('results', quote='invented quotation')])
        self.assertNotEqual(code, 0)
        self.assertNotEqual(result['status'], 'completed')
        self.assertEqual(result['agent_result']['citations'], [])

    def test_hardlink_source_is_not_delivered_to_model(self):
        os.link(self.root / 'secrets/key.txt', self.root / 'input/hard.txt')
        code, result = self.cli([])
        self.assertEqual(code, 1)
        self.assertNotIn('TEST_SECRET', json.dumps(result))
        self.sender.assert_not_called()

    def test_output_failure_reports_unsaved_without_claiming_completion(self):
        with patch('family_minimum.challenge_cli.write_result', side_effect=FileRejected('output_write_failed')):
            code, result = self.cli([self.finish('results')])
        self.assertEqual(code, 5)
        self.assertFalse(result['artifact_saved'])
        self.assertNotIn('artifact', result)

    def test_invalid_execution_result_preserves_count_and_stops_runtime(self):
        async def invalid(runtime, workflow_file, query):
            runtime.budget.count = 2
            runtime.close()
            return {'schema_version': 'challenge-agent-v1', 'request_id': 'wrong',
                    'action': 'finish_results'}
        with patch('family_agent.run.execute', side_effect=invalid):
            code, result = self.cli([])
        self.assertEqual(code, 1)
        self.assertEqual(result['code'], 'invalid_agent_result')
        self.assertEqual(result['model_requests'], 2)
        self.assertTrue(self.runtimes[-1].closed)

    def test_missing_live_credentials_are_saved_as_failure_not_mock(self):
        with patch('family_minimum.challenge_cli.SANDBOX_ROOT', self.root), patch.dict(os.environ, {}, clear=True):
            stream = io.StringIO()
            with contextlib.redirect_stdout(stream):
                code = main(['run', '--live'])
        result = json.loads(stream.getvalue())
        self.assertEqual(code, 1)
        self.assertEqual(result['code'], 'ledger_not_reconciled')
        self.assertFalse(result['agent_connected'])
        self.assertTrue(result['artifact_saved'])


if __name__ == '__main__':
    unittest.main()
