import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from score import calculate, calculate_integration, load_rubric, validate_rubric

ROOT = Path(__file__).resolve().parents[1]

class SplitScoreTest(unittest.TestCase):
    def card(self, profile, rating=4):
        card = json.loads((ROOT/f'docs/evaluation/templates/{profile}-scorecard.json').read_text())
        card.update(subject='test-product', revision='fixture-revision', environment='local-fixture', assessment_mode='live')
        for row in card.get('criteria', {}).values():
            row.update(rating=rating, evidence_level='observed', evidence_mode='live', evidence=['fixture://observed-check'], note='Synthetic scorer test only')
        for row in card['gates'].values():
            row.update(status='pass', evidence=['fixture://gate-check'], note='Synthetic scorer test only')
        return card

    def results(self):
        return {p:calculate(self.card(p), load_rubric(p+'-v2')) for p in ('agent','frontend')}

    def test_separate_full_scores(self):
        for profile, result in self.results().items():
            self.assertEqual(result['score'], 100)
            self.assertTrue(result['area_ready'])
            self.assertEqual(result['profile'], profile)
            self.assertNotIn('product_ready', result)

    def test_unknown_is_not_zero_or_renormalized(self):
        card = self.card('agent'); card['criteria']['agency']['rating'] = None
        result = calculate(card, load_rubric('agent-v2'))
        self.assertEqual((result['score'], result['unassessed_weight']), (75,25))
        self.assertFalse(result['area_ready'])
        card['criteria']['agency']['rating'] = 0
        result = calculate(card, load_rubric('agent-v2'))
        self.assertEqual((result['score'], result['unassessed_weight']), (75,0))
        self.assertIn('agency', result['below_minimum'])

    def test_high_total_cannot_hide_weak_criterion(self):
        card = self.card('frontend');card['criteria']['responsiveness']['rating'] = 0
        result = calculate(card, load_rubric('frontend-v2'))
        self.assertEqual(result['score'],95)
        self.assertFalse(result['area_ready'])

    def test_mock_agent_cannot_claim_observed_live_quality(self):
        card = self.card('agent');card['assessment_mode'] = 'mock'
        for row in card['criteria'].values():row['evidence_mode']='mock'
        with self.assertRaises(ValueError):calculate(card, load_rubric('agent-v2'))
        for row in card['criteria'].values():row['rating'] = 2
        result = calculate(card, load_rubric('agent-v2'))
        self.assertEqual(result['score'],50)
        self.assertFalse(result['area_ready'])

    def test_mock_frontend_can_be_area_ready_but_not_product_ready(self):
        card = self.card('frontend');card['assessment_mode'] = 'mock'
        for row in card['criteria'].values():row['evidence_mode']='mock'
        results = self.results();results['frontend'] = calculate(card, load_rubric('frontend-v2'))
        self.assertTrue(results['frontend']['area_ready'])
        integration = self.card('integration');integration['gates']['live_path']['status']='unknown'
        result = calculate_integration(integration, load_rubric('integration-v2'), results)
        self.assertFalse(result['product_ready'])
        self.assertNotIn('score',result)

    def test_static_evidence_and_modes_limit_ratings(self):
        for profile in ('agent','frontend'):
            for level in ('design','implementation'):
                card = self.card(profile)
                next(iter(card['criteria'].values()))['evidence_level'] = level
                with self.assertRaises(ValueError):calculate(card, load_rubric(profile+'-v2'))
            card = self.card(profile);card['assessment_mode']='design'
            with self.assertRaises(ValueError):calculate(card, load_rubric(profile+'-v2'))
        card = self.card('agent');card['assessment_mode']='replay'
        with self.assertRaises(ValueError):calculate(card,load_rubric('agent-v2'))

    def test_mixed_modes_are_bounded_per_criterion(self):
        card=self.card('agent');card['assessment_mode']='mixed'
        card['criteria']['correctness'].update(evidence_mode='mock',rating=2)
        result=calculate(card,load_rubric('agent-v2'))
        self.assertEqual(result['score'],90)
        self.assertFalse(result['area_ready'])
        card['criteria']['correctness']['rating']=4
        with self.assertRaises(ValueError):calculate(card,load_rubric('agent-v2'))
        card['criteria']['correctness']['rating']=2
        card['assessment_mode']='live'
        with self.assertRaises(ValueError):calculate(card,load_rubric('agent-v2'))

    def test_invalid_numeric_ratings(self):
        for rating in (-1,5,True,3.5,'4'):
            card=self.card('agent');card['criteria']['goal']['rating']=rating
            with self.assertRaises(ValueError):calculate(card,load_rubric('agent-v2'))

    def test_evidence_reasons_and_identity_required(self):
        for key in ('subject','revision','environment'):
            card=self.card('frontend');card[key]=''
            with self.assertRaises(ValueError):calculate(card,load_rubric('frontend-v2'))
        for field, value in [('evidence',[]),('evidence',[' ']),('note','')]:
            card=self.card('frontend');card['criteria']['design'][field]=value
            with self.assertRaises(ValueError):calculate(card,load_rubric('frontend-v2'))
        card=self.card('agent');card['gates']['action_boundary'].update(status='fail',evidence=[])
        with self.assertRaises(ValueError):calculate(card,load_rubric('agent-v2'))

    def test_missing_extra_and_cross_profile_rejected(self):
        card=self.card('agent');del card['criteria']['agency']
        with self.assertRaises(ValueError):calculate(card,load_rubric('agent-v2'))
        card=self.card('agent');card['criteria']['pitch']=copy.deepcopy(card['criteria']['goal'])
        with self.assertRaises(ValueError):calculate(card,load_rubric('agent-v2'))
        with self.assertRaises(ValueError):calculate(self.card('agent'),load_rubric('frontend-v2'))
        with self.assertRaises(ValueError):load_rubric('../../other')

    def test_rubric_integrity(self):
        for profile in ('agent','frontend'):
            rubric=load_rubric(profile+'-v2');validate_rubric(rubric)
            broken=copy.deepcopy(rubric);broken['criteria'][0]['weight']+=1
            with self.assertRaises(ValueError):validate_rubric(broken)
            broken=copy.deepcopy(rubric);broken['criteria'][1]['id']=broken['criteria'][0]['id']
            with self.assertRaises(ValueError):validate_rubric(broken)
            broken=copy.deepcopy(rubric);del broken['criteria'][0]['anchors']['3']
            with self.assertRaises(ValueError):validate_rubric(broken)

    def test_all_integration_gates_block_independently(self):
        rubric=load_rubric('integration-v2');results=self.results()
        self.assertTrue(calculate_integration(self.card('integration'),rubric,results)['product_ready'])
        for gate in rubric['gates']:
            for status in ('unknown','fail'):
                card=self.card('integration');card['gates'][gate]['status']=status
                self.assertFalse(calculate_integration(card,rubric,results)['product_ready'])

    def test_integration_mismatch_and_incomplete_area(self):
        rubric=load_rubric('integration-v2');card=self.card('integration')
        for key in ('subject','revision','environment'):
            results=self.results();results['agent'][key]='different'
            with self.assertRaises(ValueError):calculate_integration(card,rubric,results)
        results=self.results();results['agent']['rubric_version']='finals-v1'
        with self.assertRaises(ValueError):calculate_integration(card,rubric,results)
        results=self.results();results['agent']['area_ready']=False
        self.assertFalse(calculate_integration(card,rubric,results)['product_ready'])
        card['assessment_mode']='mock'
        self.assertFalse(calculate_integration(card,rubric,self.results())['product_ready'])

    def test_cli_recalculates_both_cards_and_preserves_legacy(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory)
            for profile in ('agent','frontend','integration'):
                (root/f'{profile}-scorecard.json').write_text(json.dumps(self.card(profile)))
            def invoke(path):return subprocess.run([sys.executable,str(ROOT/'scripts/score.py'),str(path)],capture_output=True,text=True)
            result=invoke(root/'integration-scorecard.json')
            self.assertEqual(result.returncode,0,result.stderr)
            self.assertTrue(json.loads(result.stdout)['product_ready'])
            card=self.card('agent');card['gates']['bounded_execution']['status']='fail'
            (root/'agent-scorecard.json').write_text(json.dumps(card))
            self.assertFalse(json.loads(invoke(root/'integration-scorecard.json').stdout)['product_ready'])
            result=invoke(ROOT/'docs/evaluation/legacy/templates/bio3-scorecard.json')
            self.assertEqual(json.loads(result.stdout)['score'],73.75)

    def test_templates_unknown_and_markdown_matches_numeric_source(self):
        for profile in ('agent','frontend'):
            rubric=load_rubric(profile+'-v2')
            card=json.loads((ROOT/f'docs/evaluation/templates/{profile}-scorecard.json').read_text())
            result=calculate(card,rubric)
            self.assertEqual(result['unassessed_weight'],100)
            self.assertFalse(result['area_ready'])
            document=(ROOT/f'docs/evaluation/{profile}-rubric.md').read_text()
            for row in rubric['criteria']:
                self.assertIn(f"{row['id']} · {row['label']} / {row['weight']}",document)
                for grade in ('2','3','4'):self.assertIn(row['anchors'][grade],document)

if __name__=='__main__':unittest.main()
