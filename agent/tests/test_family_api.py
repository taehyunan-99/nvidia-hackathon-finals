import copy
from pathlib import Path
import sys
import threading
import time
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from fastapi.testclient import TestClient
from family_agent.api import create_app, _active_runtimes
from types import SimpleNamespace

CARDS = {'interests': ['craft'], 'grades': [], 'guardians': 'unknown', 'date': None, 'district': 'all'}


class APITests(unittest.TestCase):
    def setUp(self):
        self.calls = []
        def worker(job_id, revision, conditions):
            self.calls.append(copy.deepcopy(conditions))
            return {'request_id': job_id, 'conditions_revision': revision, 'action': 'ask_user',
                'question': {'question_id': 'q-guardians', 'request_id': job_id, 'conditions_revision': revision,
                    'field': 'guardians', 'member_id': None, 'options': [{'id': 'guardians-1', 'label': '1명'}, {'id': 'guardians-2plus', 'label': '2명 이상'}]}}
        self.client = TestClient(create_app(worker))
        self.job = self.client.post('/api/runs', json=CARDS).json()
        self.headers = {'X-Run-Owner': self.job['owner_token']}
        for _ in range(100):
            if self.client.get('/api/runs/' + self.job['run_id'], headers=self.headers).json()['status'] == 'completed': break
            time.sleep(.001)

    def answer(self, revision=1, option='guardians-2plus', request_id=None):
        return self.client.post('/api/runs/' + self.job['run_id'] + '/resume', headers=self.headers,
            json={'question_id': 'q-guardians', 'request_id': request_id or self.job['run_id'],
                'conditions_revision': revision, 'selected_option_id': option})

    def test_R01_accepted_answer_creates_new_revision(self):
        response = self.answer()
        self.assertEqual(response.status_code, 202)
        self.assertEqual(response.json()['conditions_revision'], 2)
        for _ in range(100):
            if len(self.calls) == 2: break
            time.sleep(.001)
        self.assertEqual(self.calls[-1]['guardians'], {'minimum': 2, 'maximum': None})

    def test_R02_stale_answer_rejected(self):
        self.assertEqual(self.answer(revision=2).status_code, 409)

    def test_R03_other_owner_and_request_rejected(self):
        self.assertEqual(self.client.get('/api/runs/' + self.job['run_id'], headers={'X-Run-Owner': 'other'}).status_code, 404)
        self.assertEqual(self.answer(request_id='other').status_code, 404)

    def test_R04_invented_option_rejected(self):
        self.assertEqual(self.answer(option='invented').status_code, 422)

    def test_invalid_date_and_client_trusted_fields_rejected(self):
        bad = {**CARDS, 'as_of': '2026-10-07'}
        self.assertEqual(self.client.post('/api/runs', json=bad).status_code, 422)
        # Date format errors must cross the HTTP boundary as 422, not server exceptions.
        bad = {**CARDS, 'date': 'not-a-date'}
        self.assertEqual(self.client.post('/api/runs', json=bad).status_code, 422)

    def test_running_observations_require_owner_and_keep_identity(self):
        started, release = threading.Event(), threading.Event()
        def worker(job_id, revision, conditions):
            _active_runtimes[job_id] = SimpleNamespace(events=[{'kind': 'tool', 'name': 'search_experiences', 'status': 'ok'}])
            started.set()
            try:
                release.wait(2)
                return {'request_id': job_id, 'conditions_revision': revision}
            finally:
                _active_runtimes.pop(job_id, None)
        client = TestClient(create_app(worker))
        job = client.post('/api/runs', json=CARDS).json()
        try:
            self.assertTrue(started.wait(1))
            url = '/api/runs/' + job['run_id']
            self.assertEqual(client.get(url).status_code, 404)
            state = client.get(url, headers={'X-Run-Owner': job['owner_token']}).json()
            self.assertEqual(state['status'], 'running')
            self.assertIsNone(state['result'])
            self.assertEqual(state['events'][0]['request_id'], job['run_id'])
            self.assertEqual(state['events'][0]['seq'], 1)
        finally:
            release.set()
