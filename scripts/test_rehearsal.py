import json
from pathlib import Path
import unittest
from unittest.mock import Mock
from rehearsal import CASES, TOOLS, assert_result, evidence, run
from lookup import load_entries, search

ROOT = Path(__file__).resolve().parents[1]


class RehearsalTests(unittest.TestCase):
    def test_observation_changes_next_tool(self):
        existing = run('existing'); supplement = run('supplement')
        calls = lambda r: [e['tool'] for e in r['events'] if e['kind'] == 'tool' and e['status'] == 'running']
        self.assertEqual(calls(existing), ['check_existing'])
        self.assertEqual(calls(supplement), ['check_existing', 'collect_more'])
        self.assertEqual(existing['status'], 'completed')
        self.assertEqual(supplement['status'], 'completed')

    def test_missing_and_conflicting_evidence_stay_partial(self):
        for case in ['hold', 'conflict']:
            with self.subTest(case=case):
                r = run(case)
                self.assertEqual(r['status'], 'partial')
                self.assertIsNone(r['artifact'])
                self.assertTrue(r['evidence'])

    def test_failed_tool_is_bounded_and_keeps_observations(self):
        r = run('failure')
        self.assertEqual(r['status'], 'failed')
        self.assertEqual(sum(e['error_code'] == 'timeout' for e in r['events']), 2)
        self.assertIsNone(r['artifact'])
        self.assertEqual(len(r['evidence']), 1)

    def test_retry_recovers_without_duplicate_evidence(self):
        r = run('retry')
        self.assertEqual(r['status'], 'completed')
        self.assertEqual(sum(e['error_code'] == 'timeout' for e in r['events']), 1)
        self.assertEqual(len(r['evidence']), 2)

    def test_premature_completion_rejected(self):
        r = run('existing', decide=lambda _: ('complete', '근거 없음'))
        self.assertEqual(r['status'], 'failed'); self.assertIsNone(r['artifact'])

    def test_unapproved_tool_never_executes(self):
        tool = Mock()
        r = run('existing', decide=lambda _: ('shell', 'not allowed'), tools={'shell': tool})
        tool.assert_not_called(); self.assertEqual(r['status'], 'failed')

    def test_step_budget_stops_loop(self):
        r = run('existing', decide=lambda _: ('check_existing', 'again'), max_steps=1)
        self.assertEqual(r['status'], 'partial'); self.assertIsNone(r['artifact'])

    def test_call_budget_stops_repeated_tool(self):
        tool = Mock(return_value=[])
        r = run('existing', decide=lambda _: ('check_existing', 'again'), tools={'check_existing': tool})
        self.assertEqual(tool.call_count, 2); self.assertEqual(r['status'], 'failed')

    def test_malformed_tool_outputs_cannot_complete(self):
        for bad in [None, 'wrong', [{}], [None], [evidence('same'), evidence('same')]]:
            with self.subTest(bad=bad):
                r = run('existing', tools={**TOOLS, 'check_existing': lambda *_: bad})
                self.assertEqual(r['status'], 'partial'); self.assertIsNone(r['artifact'])

    def test_dangling_evidence_reference_rejected(self):
        r = run('existing'); r['events'][0]['evidence_ids'] = ['missing']
        with self.assertRaises(ValueError): assert_result(r)

    def test_fixtures_match_current_runner(self):
        fixtures = json.loads((ROOT/'docs/playbooks/examples/research/fixtures.json').read_text())
        self.assertEqual(set(fixtures), set(CASES))
        for key in CASES:
            self.assertEqual(fixtures[key]['run'], run(key))
            self.assertEqual(fixtures[key]['run']['http_requests'], 0)
            self.assertEqual(fixtures[key]['run']['mode'], 'mock')


class DiscoveryTests(unittest.TestCase):
    def test_research_route_reaches_contract_fixture_and_preview(self):
        entries = load_entries()
        for query in ['조사 비교', '입출력', 'schema']:
            row = search(entries, query, kind='recipe', limit=1)[0]
            self.assertEqual(row['id'], 'recipe:research')
            for key in ['guide', 'quickstart', 'contract', 'fixtures', 'preview']:
                self.assertTrue((ROOT/row[key]).is_file(), key)
            by_id = {e['id']: e for e in entries}
            self.assertIn(row['agent_id'], by_id)
            for tool_id in row['tool_ids']: self.assertIn(tool_id, by_id)
            for folder in row['skill_folders']:
                self.assertTrue(any(e.get('folder') == folder for e in entries))

    def test_function_authoring_skill_found_with_build_filter(self):
        rows = search(load_entries(), 'nat-tools-and-functions', kind='skill', domain='agents', function='build')
        self.assertEqual(rows[0]['folder'], 'nat-tools-and-functions')


if __name__ == '__main__': unittest.main()
