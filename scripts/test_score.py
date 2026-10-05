import copy
import json
from pathlib import Path
import unittest
from score import calculate
R=Path(__file__).resolve().parents[1]
class ScoreTest(unittest.TestCase):
    def setUp(self):
        self.rubric=json.loads((R/'docs/evaluation/rubric.json').read_text())
        self.card=json.loads((R/'docs/evaluation/templates/scorecard.json').read_text())
    def full(self):
        c=copy.deepcopy(self.card)
        for row in c['criteria'].values():row.update(rating=4,evidence=['run/trace.json'])
        for row in c['gates'].values():row.update(status='pass',evidence=['run/check.json'])
        return c
    def test_full_ready(self):
        r=calculate(self.full(),self.rubric)
        self.assertEqual(r['score'],100);self.assertTrue(r['internal_ready'])
    def test_unknown_never_ready(self):
        c=self.full();c['gates']['live_path']['status']='unknown'
        self.assertFalse(calculate(c,self.rubric)['internal_ready'])
    def test_missing_rating_distinct_from_zero(self):
        c=self.full();c['criteria']['agency']['rating']=None
        r=calculate(c,self.rubric)
        self.assertEqual(r['unassessed_weight'],20);self.assertFalse(r['internal_ready'])
    def test_no_evidence_rejected(self):
        c=self.full();c['criteria']['quality']['evidence']=[]
        with self.assertRaises(ValueError):calculate(c,self.rubric)
    def test_invalid_rating(self):
        for rating in [-1,5,True,2.5]:
            c=self.full();c['criteria']['quality']['rating']=rating
            with self.assertRaises(ValueError):calculate(c,self.rubric)
    def test_schema_and_version(self):
        c=self.full();del c['gates']['submission']
        with self.assertRaises(ValueError):calculate(c,self.rubric)
        c=self.full();c['rubric_version']='different'
        with self.assertRaises(ValueError):calculate(c,self.rubric)
    def test_bio3_is_provisional(self):
        c=json.loads((R/'docs/evaluation/templates/bio3-scorecard.json').read_text());r=calculate(c,self.rubric)
        self.assertEqual(r['score'],73.75);self.assertFalse(r['internal_ready'])
if __name__=='__main__':unittest.main()
