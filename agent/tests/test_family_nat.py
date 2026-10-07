import asyncio
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import Mock
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from family_agent.runtime import FamilyRuntime
from family_agent.sources import SeoulSources
from family_minimum.runtime import SERVICE
from test_family_agent import CID, CONDITIONS


@unittest.skipUnless(importlib.util.find_spec('nat'), 'Requires pinned NAT environment')
class FamilyNATTests(unittest.TestCase):
    def test_model_selected_tools_observation_and_hold(self):
        from family_agent.run import execute
        with tempfile.TemporaryDirectory() as folder:
            replies = iter([
                'Thought: Search relevant culture candidates.\nAction: search_experiences\nAction Input: {"cursor":null}',
                'Thought: Inspect the craft candidate.\nAction: get_experience_detail\nAction Input: {"candidate_id":"' + CID + '"}',
                'Thought: Validator unavailable, keep unknown.\nFinal Answer: ' + json.dumps({'action': 'finish_hold', 'candidate_ids': [CID], 'question_field': None, 'reason': '조건 검증기 연결 전으로 참여 적합성 미확인'}),
            ])
            sender = Mock(side_effect=lambda _: {'choices': [{'finish_reason': 'stop', 'message': {'content': next(replies)}}]})
            fetcher = Mock(return_value=(json.dumps({SERVICE: {'RESULT': {'CODE': 'INFO-000'},
                'row': [{'SVCID': CID, 'SVCNM': '솟대만들기', 'MAXCLASSNM': '문화체험'}]}}).encode(), 'utf-8'))
            sources = SeoulSources('nat-test', 1, CONDITIONS, fetcher)
            runtime = FamilyRuntime(Path(folder) / 'ledger', 'test', 'TEST_ONLY', CONDITIONS, 'nat-test',
                sources=sources, send=sender, implementation=False)
            now = [0]; runtime.budget.clock = lambda: now[0]; runtime.budget.started = 0
            runtime.budget.sleep = lambda seconds: now.__setitem__(0, now[0] + seconds)
            result = asyncio.run(execute(runtime))
            self.assertEqual(result['action'], 'finish_hold', result)
            self.assertEqual(result['physical_model_requests'], 3)
            self.assertEqual(result['candidates'][0]['validation']['overall'], 'unknown')
            self.assertIn('validator_connected', json.dumps(sender.call_args.args[0]['messages']))
            self.assertTrue(runtime.closed)

    def test_terminal_tool_stops_before_next_physical_model_call(self):
        from family_agent.run import execute
        with tempfile.TemporaryDirectory() as folder:
            replies = iter([
                'Thought: Read the craft source.\nAction: get_experience_detail\nAction Input: {"candidate_id":"' + CID + '"}',
                'Thought: Keep unconfirmed.\nAction: finish_discovery\nAction Input: ' + json.dumps({'outcome': 'hold', 'candidate_ids': [CID], 'reason': '확인 필요', 'question_field': None}),
            ])
            sender = Mock(side_effect=lambda _: {'choices': [{'finish_reason': 'stop', 'message': {'content': next(replies)}}]})
            fetcher = Mock(return_value=(json.dumps({SERVICE: {'RESULT': {'CODE': 'INFO-000'}, 'row': [
                {'SVCID': CID, 'SVCNM': '솟대만들기', 'MAXCLASSNM': '문화체험'}]}}).encode(), 'utf-8'))
            runtime = FamilyRuntime(Path(folder) / 'ledger', 'test', 'TEST_ONLY', CONDITIONS, 'terminal',
                sources=SeoulSources('terminal', 1, CONDITIONS, fetcher), send=sender, implementation=False)
            now = [0]; runtime.budget.clock = lambda: now[0]; runtime.budget.started = 0
            runtime.budget.sleep = lambda seconds: now.__setitem__(0, now[0] + seconds)
            result = asyncio.run(execute(runtime))
            self.assertEqual(result['action'], 'finish_hold', result)
            self.assertEqual(sender.call_count, 2)
            self.assertTrue(runtime.closed)

    def test_challenge_terminal_preserves_exact_quotes(self):
        from family_agent.run import execute
        from family_agent.challenge import ChallengeRuntime
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder) / 'input'; root.mkdir(); (root / 'notice.md').write_text('당일 시장 운영시간은 10시부터 14시까지입니다.')
            replies = iter([
                'Thought: Read current notice.\nAction: read_input\nAction Input: {"source_ids":["input-0"]}',
                'Thought: Submit a bounded draft.\nAction: finish_draft\nAction Input: ' + json.dumps({'outcome': 'hold', 'draft': '시장 방문은 14시 전에 마치는 초안입니다.', 'citations': [{'source_id': 'input-0', 'quote': '10시부터 14시까지'}], 'uncertainties': ['추가 조건 확인 필요']}, ensure_ascii=False),
            ])
            sender = Mock(side_effect=lambda _: {'choices': [{'finish_reason': 'stop', 'message': {'content': next(replies)}}]})
            runtime = ChallengeRuntime(Path(folder) / 'ledger', 'test', 'TEST_ONLY', {'request_id': 'common', 'task': '문화 방문 초안'}, input_root=root, send=sender)
            now = [0]; runtime.budget.clock = lambda: now[0]; runtime.budget.started = 0
            runtime.budget.sleep = lambda seconds: now.__setitem__(0, now[0] + seconds)
            result = asyncio.run(execute(runtime, 'challenge-workflow.yml', runtime.query))
            self.assertEqual(result['action'], 'finish_hold', result)
            self.assertEqual(result['citations'][0]['quote'], '10시부터 14시까지')
            self.assertEqual(sender.call_count, 2)

    def test_invalid_final_has_one_budgeted_correction(self):
        from family_agent.run import execute
        with tempfile.TemporaryDirectory() as folder:
            replies = iter([
                'Thought: Read source.\nAction: get_experience_detail\nAction Input: {"candidate_id":"' + CID + '"}',
                'Thought: Submit.\nFinal Answer: ' + json.dumps({'action': 'finish_results', 'candidate_ids': [CID], 'reason': 'invalid completion', 'question_field': None}),
                'Thought: Correct the rejected unknown recommendation.\nAction: finish_discovery\nAction Input: ' + json.dumps({'outcome': 'hold', 'candidate_ids': [CID], 'reason': '확인 필요', 'question_field': None}),
            ])
            sender = Mock(side_effect=lambda _: {'choices': [{'finish_reason': 'stop', 'message': {'content': next(replies)}}]})
            fetcher = Mock(return_value=(json.dumps({SERVICE: {'RESULT': {'CODE': 'INFO-000'}, 'row': [{'SVCID': CID, 'SVCNM': '솟대만들기', 'MAXCLASSNM': '문화체험'}]}}).encode(), 'utf-8'))
            runtime = FamilyRuntime(Path(folder) / 'ledger', 'test', 'TEST_ONLY', CONDITIONS, 'correction', sources=SeoulSources('correction', 1, CONDITIONS, fetcher), send=sender, implementation=False)
            now = [0]; runtime.budget.clock = lambda: now[0]; runtime.budget.started = 0
            runtime.budget.sleep = lambda seconds: now.__setitem__(0, now[0] + seconds)
            result = asyncio.run(execute(runtime))
            self.assertEqual(result['action'], 'finish_hold', result)
            self.assertEqual(sender.call_count, 3)
            self.assertTrue(any(e.get('status') == 'rejected' for e in result['events']))
