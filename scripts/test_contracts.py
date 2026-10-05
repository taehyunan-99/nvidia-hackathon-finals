import hashlib
import json
from pathlib import Path
import unittest
from lookup import load_entries, search

ROOT = Path(__file__).resolve().parents[1]


class CombinationContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.fixtures = json.loads((ROOT / 'docs/catalog/contracts/mission-fixtures.json').read_text())
        cls.recipes = json.loads((ROOT / 'docs/catalog/recipes-index.json').read_text())

    def test_every_remaining_recipe_reaches_contract_and_fixture(self):
        expected = {row['id'].split(':')[-1] for row in self.recipes} - {'research'}
        self.assertEqual(set(self.fixtures), expected)
        for recipe in self.recipes:
            if recipe['id'] == 'recipe:research': continue
            for field in ['contract', 'schema', 'fixtures']:
                self.assertTrue((ROOT / recipe[field]).is_file())
            self.assertIn('id="' + recipe['contract_section'] + '"', (ROOT / recipe['contract']).read_text())
            matches = search(load_entries(), recipe['name'], kind='recipe', limit=1)
            self.assertEqual(matches[0]['id'], recipe['id'])
            self.assertEqual(matches[0]['schema'], recipe['schema'])

    def test_partial_and_failure_never_publish_confirmed_artifact(self):
        for recipe, variants in self.fixtures.items():
            self.assertEqual(set(variants), {'completed', 'partial', 'failed'})
            for status, run in variants.items():
                with self.subTest(recipe=recipe, status=status):
                    self.assertEqual(run['status'], status)
                    self.assertEqual(run['mode'], 'mock')
                    self.assertEqual(run['http_requests'], 0)
                    self.assertIsNone(run['model_id'])
                    ids = {row['id'] for row in run['evidence']}
                    for seq, event in enumerate(run['events'], 1):
                        self.assertEqual(event['seq'], seq)
                        self.assertLessEqual(set(event['evidence_ids']), ids)
                    digest = hashlib.sha256(json.dumps(run['input'], sort_keys=True).encode()).hexdigest()
                    self.assertEqual(run['input_hash'], digest)
                    if status == 'completed':
                        self.assertLessEqual(set(run['artifact']['evidence_ids']), ids)
                        self.assertIsNotNone(run['output'])
                        self.assertEqual(run['events'][-2]['status'], 'completed')
                    else:
                        self.assertIsNone(run['artifact'])
                        self.assertTrue(run['evidence'])

    def test_routing_example_satisfies_original_constraints(self):
        run = self.fixtures['routing']['completed']; data = run['input']; result = run['output']
        route = result['routes'][0]; vehicle = data['vehicles'][0]
        orders = {row['id']: row for row in data['orders']}
        self.assertCountEqual(route['order_ids'], orders)
        self.assertEqual(len(route['order_ids']), len(set(route['order_ids'])))
        self.assertEqual(route['locations'], [vehicle['depot']] + [orders[key]['location'] for key in route['order_ids']] + [vehicle['depot']])
        self.assertEqual(route['load'], sum(row['demand'] for row in orders.values()))
        self.assertLessEqual(route['load'], vehicle['capacity'])
        costs = data['cost_matrix']; times = route['arrival_minutes']
        self.assertEqual(result['objective'], sum(costs[a][b] for a, b in zip(route['locations'], route['locations'][1:])))
        self.assertEqual(times[-1], result['objective'])
        for key, time in zip(route['order_ids'], times[1:-1]):
            start, end = orders[key]['time_window']; self.assertLessEqual(start, time); self.assertLessEqual(time, end)

    def test_allocation_example_recomputes_objective_and_bounds(self):
        run = self.fixtures['allocation']['completed']; data = run['input']
        values = {row['variable_id']: row['value'] for row in run['output']['values']}
        vector = [values[var['id']] for var in data['variables']]
        for var, value in zip(data['variables'], vector):
            self.assertLessEqual(var['lower'], value); self.assertLessEqual(value, var['upper'])
            if var['integer']: self.assertEqual(value, int(value))
        self.assertEqual(sum(a*b for a,b in zip(data['objective'], vector)), run['output']['objective'])
        for constraint in data['constraints']:
            lhs = sum(a*b for a,b in zip(constraint['coefficients'], vector))
            self.assertEqual(constraint['sense'], 'le'); self.assertLessEqual(lhs, constraint['rhs'])

    def test_media_and_partial_results_keep_their_domain_boundaries(self):
        clip = self.fixtures['video']['completed']
        for segment in clip['output']['segments']:
            self.assertLess(segment['start_seconds'], segment['end_seconds'])
            self.assertLessEqual(segment['end_seconds'], clip['input']['duration_seconds'])
        self.assertIsNone(self.fixtures['documents']['partial']['output']['items'][0]['page'])
        self.assertFalse(self.fixtures['voice']['partial']['output']['final'])
        self.assertIsNone(self.fixtures['operations']['partial']['output']['action'])
        data = self.fixtures['data']['completed']['output']
        self.assertEqual(len(data['rows']), data['row_count'])
        self.assertTrue(all(len(row) == len(data['columns']) for row in data['rows']))
        self.assertEqual(self.fixtures['biology']['completed']['output']['structures'][0]['provenance'], 'predicted')


if __name__ == '__main__': unittest.main()
