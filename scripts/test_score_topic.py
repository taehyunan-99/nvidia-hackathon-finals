import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from score import calculate, load_rubric

ROOT = Path(__file__).resolve().parents[1]


class TopicScoreTest(unittest.TestCase):
    def card(self, ratings=None):
        card = json.loads((ROOT/'docs/evaluation/templates/topic-scorecard.json').read_text())
        card.update(subject='Synthetic candidate', revision='case-v1', environment='2 people / 7 hours',
                    assessed_at='2026-10-05T18:00:00+09:00', next_check='Verify actual source access')
        for row, rating in zip(card['criteria'].values(), ratings or [3]*7):
            row.update(rating=rating, evidence_level='compared', evidence=['fixture://synthetic-only'], note='Synthetic test, not actual candidate evidence')
        for row in card['gates'].values():
            row.update(status='pass', evidence=['fixture://synthetic-only'], note='Synthetic gate')
        return card

    def result(self, card):
        return calculate(card, load_rubric('topic-v1'))

    def test_representative_and_counterexamples(self):
        cases = [([3]*7, None, 75, 0, 'candidate'),
                 ([3,0,4,4,2,4,3], 'agency', 63.75, 0, 'revise'),
                 ([2,3,None,None,3,1,4], None, 43.75, 30, 'hold'),
                 ([3,3,3,0,3,1,4], 'verify', 60, 0, 'revise')]
        for ratings, failed, score, unknown, decision in cases:
            with self.subTest(ratings=ratings):
                card = self.card(ratings)
                if failed: card['gates'][failed]['status'] = 'fail'
                r = self.result(card)
                self.assertEqual((r['score'],r['unassessed_weight'],r['decision']), (score,unknown,decision))
                self.assertEqual(r['possible_range'], [score,score+unknown])
                self.assertNotIn('product_ready', r)

    def test_gate_fail_overrides_high_score_and_unknown(self):
        card = self.card([4]*7);card['gates']['mission']['status'] = 'fail'
        card['criteria']['inspect']['rating'] = None
        self.assertEqual(self.result(card)['decision'], 'exclude')
        card['gates']['mission']['status'] = 'pass';card['gates']['access']['status'] = 'fail'
        self.assertEqual(self.result(card)['decision'], 'revise')

    def test_mission_only_unknown_is_provisional_not_selected(self):
        card = self.card();card['gates']['mission']['status'] = 'unknown'
        r = self.result(card)
        self.assertEqual(r['decision'],'hold');self.assertTrue(r['provisional_candidate'])
        card['gates']['access']['status'] = 'unknown'
        self.assertFalse(self.result(card)['provisional_candidate'])

    def test_core_and_minor_minimums_cannot_be_hidden(self):
        for key, rating in [('agency',2),('inspect',1)]:
            card = self.card([4]*7);card['criteria'][key]['rating'] = rating
            r = self.result(card)
            self.assertGreater(r['score'],70);self.assertEqual(r['decision'],'revise')
            self.assertIn(key,r['below_minimum'])

    def test_selection_threshold(self):
        r=self.result(self.card([3,3,3,3,2,2,3]))
        self.assertEqual((r['score'],r['decision']),(70,'candidate'))
        r=self.result(self.card([3,3,3,3,2,2,2]))
        self.assertEqual((r['score'],r['decision']),(68.75,'revise'))

    def test_missing_evidence_metadata_and_invalid_values_rejected(self):
        edits = [lambda c:c.update(subject=''), lambda c:c.update(rubric_version='agent-v2'),
                 lambda c:c['criteria'].pop('scope'), lambda c:c['gates'].pop('scope'),
                 lambda c:c['criteria']['agency'].update(rating=True),
                 lambda c:c['criteria']['agency'].update(rating=2.5),
                 lambda c:c['criteria']['agency'].update(rating=5),
                 lambda c:c['criteria']['agency'].update(evidence=[]),
                 lambda c:c['criteria']['agency'].update(evidence_level='design'),
                 lambda c:c['criteria']['agency'].update(rating=None,note=''),
                 lambda c:c['gates']['access'].update(status='fail',evidence=[])]
        for edit in edits:
            card=self.card();edit(card)
            with self.assertRaises(ValueError): self.result(card)

    def test_unknown_and_zero_remain_distinct(self):
        card=self.card();card['criteria']['agency']['rating']=None
        self.assertEqual(self.result(card)['unassessed_weight'],25)
        card['criteria']['agency']['rating']=0
        self.assertEqual(self.result(card)['unassessed_weight'],0)

    def test_document_anchors_match_machine_rubric(self):
        text=(ROOT/'docs/evaluation/topic-selection.md').read_text()
        for spec in load_rubric('topic-v1')['criteria']:
            line=next(s for s in text.splitlines() if s.startswith('| '+spec['id']+' /'))
            cells=[s.strip() for s in line.strip('|').split('|')]
            self.assertEqual(int(cells[1]),spec['weight'])
            for n in [2,3,4]:self.assertEqual(cells[n],spec['anchors'][str(n)])

    def test_cli_and_blank_template(self):
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'card.json';path.write_text(json.dumps(self.card()))
            result=subprocess.run([sys.executable,str(ROOT/'scripts/score.py'),str(path)],capture_output=True,text=True)
            self.assertEqual(result.returncode,0,result.stderr)
            self.assertEqual(json.loads(result.stdout)['decision'],'candidate')
        blank=json.loads((ROOT/'docs/evaluation/templates/topic-scorecard.json').read_text())
        with self.assertRaises(ValueError):self.result(blank)


if __name__ == '__main__':
    unittest.main()
