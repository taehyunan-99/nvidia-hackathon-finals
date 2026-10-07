import asyncio
import json


class ConnectionRejected(ValueError):
    def __init__(self, code, observation=None):
        super().__init__(code)
        self.observation = observation or {'agent_connected': False, 'model_requests': 0, 'events': []}


def create_runtime(packet, input_root, settings):
    from family_agent.challenge import ChallengeRuntime
    from .runtime import load_policy

    class ObservedRuntime(ChallengeRuntime):
        def tool(self, name, argument):
            self.events.append({'kind': 'tool_attempt', 'name': name, 'status': 'running'})
            try:
                if name == 'read_input':
                    return self.read_inputs(argument)
                return super().tool(name, argument)
            except Exception as exc:
                self.events.append({'kind': 'tool', 'name': name, 'status': 'failed',
                                    'error_code': type(exc).__name__})
                raise

        def read_inputs(self, argument):
            from .challenge_files import InputFiles
            with self.lock:
                if self.closed or self.steps >= self.policy.max_steps:
                    raise ValueError('run_closed_or_step_limit')
                self.budget._wait(0)
                self.tool_steps += 1
                if self.tool_steps > self.policy.max_steps:
                    raise ValueError('tool_step_limit')
                ids = argument.split(',')
                if len(ids) > 8 or any(source_id not in self.paths for source_id in ids):
                    raise ValueError('unobserved_source')
                files = InputFiles(self.root)
                result = {'status': 'ok', 'documents': []}
                try:
                    for source_id in ids:
                        if source_id not in self.reads:
                            document = files.read(self.paths[source_id])
                            if document['bytes'] > 10000:
                                raise ValueError('input_size_limit')
                            self.reads[source_id] = document['text']
                        text = self.reads[source_id]
                        result['documents'].append({'source_id': source_id, 'path': self.paths[source_id],
                            'text': text, 'lines': [{'number': index + 1, 'text': line}
                                                    for index, line in enumerate(text.splitlines())],
                            'trust': 'untrusted_source_data'})
                finally:
                    files.close()
                self.events.append({'kind': 'tool', 'name': 'read_input', 'status': 'ok', 'source_ids': ids})
                return result

    return ObservedRuntime(
        ledger=settings.get('MODEL_DAILY_LEDGER'), model=settings.get('MODEL_ID'),
        key=settings.get('NVIDIA_API_KEY'), policy=load_policy(settings),
        request={'request_id': packet['request_id'], 'task': packet['request']},
        additional=packet['additional_conditions'], input_root=input_root)


def run_agent(packet, input_root, settings):
    if settings.get('MODEL_LEDGER_RECONCILED') != 'yes':
        raise ConnectionRejected('ledger_not_reconciled')
    if not all(settings.get(name) for name in ['MODEL_DAILY_LEDGER', 'MODEL_ID', 'NVIDIA_API_KEY']):
        raise ConnectionRejected('missing_model_configuration')
    runtime = None
    try:
        from family_agent.run import execute
        runtime = create_runtime(packet, input_root, settings)
        result = asyncio.run(execute(runtime, 'challenge-workflow.yml', runtime.query))
        if (not isinstance(result, dict) or result.get('schema_version') != 'challenge-agent-v1'
                or result.get('request_id') != packet['request_id']
                or result.get('action') not in {'finish_results', 'finish_hold', 'finish_limited', 'finish_failed'}):
            raise ConnectionRejected('invalid_agent_result')
        if not runtime.closed:
            raise ConnectionRejected('agent_not_stopped')
        if not isinstance(result.get('events'), list) or not all(isinstance(event, dict) for event in result['events']):
            raise ConnectionRejected('invalid_agent_events')
        if type(result.get('physical_model_requests')) is not int or result['physical_model_requests'] < 0:
            raise ConnectionRejected('invalid_request_count')
        result['sources'] = {key: runtime.paths[key] for key in runtime.reads}
        json.dumps(result, ensure_ascii=False, allow_nan=False)
        return result
    except ConnectionRejected as exc:
        if runtime is not None:
            exc.observation = {'agent_connected': True, 'model_requests': runtime.budget.count,
                               'events': runtime.events}
        raise
    except Exception:
        observation = ({'agent_connected': True, 'model_requests': runtime.budget.count,
                        'events': runtime.events} if runtime is not None else None)
        raise ConnectionRejected('agent_execution_failed', observation) from None
    finally:
        if runtime is not None:
            runtime.close()


def connected_result(prepared, result):
    actions = {'finish_results': 'completed', 'finish_hold': 'needs_confirmation',
               'finish_limited': 'limited', 'finish_failed': 'failed'}
    status = actions[result['action']]
    events = [event for event in prepared['events'] if event['kind'] != 'result']
    events.extend(result['events'])
    events.append({'kind': 'result', 'name': 'agent_result', 'status': status})
    run_id = prepared['run_id']
    sources = result.get('sources', {})
    cited = {citation['source_id'] for citation in result.get('citations', [])}
    used = prepared['used_sources'] + [
        {'source_id': source_id, 'path': path, 'usage': 'cited' if source_id in cited else 'read_not_cited'}
        for source_id, path in sources.items()]
    return {**prepared, 'status': status, 'code': result['action'],
            'message': '공통 에이전트 실행 결과입니다. 실제 정책 집행은 별도 검증이 필요합니다.',
            'agent_connected': True, 'execution_mode': 'live',
            'model_requests': result['physical_model_requests'], 'agent_result': result,
            'used_sources': used,
            'unread_sources': [path for path in prepared['packet']['available_source_ids']
                               if path not in sources.values()],
            'events': [{**event, 'run_id': run_id, 'seq': seq}
                       for seq, event in enumerate(events, start=1)]}
