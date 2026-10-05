from copy import deepcopy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import Mock, patch
from probe_research import ModelDecision, check_expectation, config
from rehearsal import run


def tool_response(name='check_existing', arguments='{}'):
    return {'choices': [{'finish_reason': 'tool_calls', 'message': {'content': None,
            'tool_calls': [{'id': 'call-1', 'type': 'function', 'function': {'name': name, 'arguments': arguments}}]}}]}


class ModelDecisionTests(unittest.TestCase):
    def test_expected_paths_pass(self):
        for case in ['existing', 'hold']: check_expectation(run(case), case)

    def test_completed_result_with_redundant_call_is_not_a_pass(self):
        result = run('existing')
        result['events'].insert(-1, {'kind': 'tool', 'status': 'running', 'tool': 'collect_more'})
        with self.assertRaises(ValueError): check_expectation(result, 'existing')

    def test_tool_observation_returned_to_model(self):
        observations = []
        answers = [tool_response(), {'choices': [{'finish_reason': 'stop', 'message': {'content': '{"action":"complete","reason":"검증 통과"}'}}]}]
        def send(payload):
            observations.append(deepcopy(payload)); return answers.pop(0)
        planner = ModelDecision(send, 'test-model')
        self.assertEqual(planner({})[0], 'check_existing')
        self.assertEqual(planner({'validation': 'pass', 'evidence': [{'id': 'a'}]})[0], 'complete')
        message = observations[-1]['messages'][-1]
        self.assertEqual(message['role'], 'tool'); self.assertEqual(message['tool_call_id'], 'call-1')
        self.assertEqual(json.loads(message['content'])['evidence'], [{'id': 'a'}])
        self.assertEqual(observations[-1]['max_tokens'], 1024)

    def test_unapproved_calls_and_args_rejected(self):
        for answer in [tool_response('shell'), tool_response(arguments='{"extra":1}')]:
            with self.assertRaises(ValueError): ModelDecision(lambda _: answer, 'test')({})

    def test_truncated_response_rejected(self):
        answer = tool_response(); answer['choices'][0]['finish_reason'] = 'length'
        with self.assertRaises(ValueError): ModelDecision(lambda _: answer, 'test')({})

    def test_multiple_calls_rejected(self):
        answer = tool_response(); answer['choices'][0]['message']['tool_calls'] *= 2
        with self.assertRaises(ValueError): ModelDecision(lambda _: answer, 'test')({})

    def test_reasoning_not_carried_in_messages(self):
        answer = tool_response(); answer['choices'][0]['message']['reasoning_content'] = 'private'
        planner = ModelDecision(lambda _: answer, 'test'); planner({})
        self.assertNotIn('reasoning_content', planner.messages[-1])

    def test_env_file_is_parsed_without_shell_execution(self):
        with tempfile.TemporaryDirectory() as folder, patch.dict('os.environ', {}, clear=True):
            p=Path(folder)/'.env'; p.write_text("NVIDIA_API_KEY='literal-$(not-a-command)'\nMODEL_ID=model\nUNRELATED=ignore\n")
            result=config(p)
            self.assertEqual(result['NVIDIA_API_KEY'],'literal-$(not-a-command)')
            self.assertNotIn('UNRELATED',result)


if __name__ == '__main__': unittest.main()
