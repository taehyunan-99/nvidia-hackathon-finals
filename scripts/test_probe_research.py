from copy import deepcopy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import Mock, patch
from probe_research import ModelDecision, check_expectation, config, read_input
from rehearsal import run, evidence


def tool_response(name='check_existing', arguments='{}'):
    return {'choices': [{'finish_reason': 'tool_calls', 'message': {'content': None,
            'tool_calls': [{'id': 'call-1', 'type': 'function', 'function': {'name': name, 'arguments': arguments}}]}}]}


class ModelDecisionTests(unittest.TestCase):
    def test_expected_paths_pass(self):
        for case in ['existing', 'hold']: check_expectation(run(case), case)

    def test_completed_result_with_redundant_call_is_not_a_pass(self):
        result = run('existing')
        result['events'].insert(-1, {**result['events'][1], 'tool': 'collect_more'})
        for seq, event in enumerate(result['events'], 1): event['seq'] = seq
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

    def test_all_fixture_outcomes_pass_invariant_review(self):
        for case in ['existing', 'supplement', 'hold', 'conflict', 'failure', 'retry']:
            with self.subTest(case=case): check_expectation(run(case))

    def test_new_input_schema_rejects_wrong_topic(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'input.json'
            data = {'name': 'new', 'goal': 'another topic', 'existing': [evidence('a')], 'additional': []}
            path.write_text(json.dumps(data))
            with self.assertRaises(ValueError): read_input(path)
            data['existing'] = []
            path.write_text(json.dumps(data))
            self.assertEqual(read_input(path), data)

    def test_current_permissions_are_sent_and_enforced(self):
        sent = []
        def send(payload):
            sent.append(deepcopy(payload))
            return tool_response('check_existing')
        planner = ModelDecision(send, 'test')
        with self.assertRaises(ValueError):
            planner({'allowed_actions': ['collect_more', 'hold'], 'evidence': [evidence('a')]})
        self.assertEqual([t['function']['name'] for t in sent[0]['tools']], ['collect_more'])
        self.assertEqual(json.loads(sent[0]['messages'][-1]['content'])['allowed_actions'], ['collect_more', 'hold'])

    def test_new_inputs_are_evaluated_by_observation_not_name(self):
        for value in [True, False]:
            rows = [evidence('fresh-a', value), evidence('fresh-b', value)]
            result = run('unseen-name', tools={'check_existing': lambda *_: rows})
            check_expectation(result)
            result['status'] = 'partial'; result['artifact'] = None
            with self.assertRaises(ValueError): check_expectation(result)

    def test_actual_model_adapter_stops_after_one_verified_tool(self):
        send = Mock(return_value=tool_response())
        result = run('existing', decide=ModelDecision(send, 'test'))
        self.assertEqual(send.call_count, 1)
        self.assertEqual(result['status'], 'completed')
        check_expectation(result)

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
