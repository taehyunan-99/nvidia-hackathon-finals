import argparse
import asyncio
import json
import logging
import os
from pathlib import Path
from family_minimum.runtime import CURRENT, ROOT, load_policy
from .runtime import FamilyRuntime


async def execute(runtime, workflow_file='family-workflow.yml', query=None):
    logging.disable(logging.CRITICAL)
    from nat.builder.workflow_builder import WorkflowBuilder
    from nat.runtime.loader import load_config
    from family_minimum import register as model_registration
    from . import register
    if workflow_file == 'challenge-workflow.yml':
        from . import challenge_register
    token = CURRENT.set(runtime)
    try:
        config = load_config(ROOT / 'agent' / workflow_file)
        async with WorkflowBuilder.from_config(config) as builder:
            workflow = await builder.build()
            initial = runtime.tool('search_experiences') if query is None else None
            if workflow_file == 'challenge-workflow.yml':
                task_data = json.loads(query)
                listing = runtime.tool('search_input', '')
                task_data['initial_input_listing'] = listing
                ids = [source['source_id'] for source in listing['sources']]
                total_bytes = sum((runtime.root / runtime.paths[key]).lstat().st_size for key in ids)
                if len(ids) <= 24 and total_bytes <= 32768:
                    task_data['initial_documents'] = [runtime.tool('read_input', ','.join(ids[i:i+8]))
                        for i in range(0, len(ids), 8)]
                query = json.dumps(task_data, ensure_ascii=False)
            task = query or json.dumps({'task': 'Compare relevant cultural experiences. Initial search has already executed. Use observed candidate IDs to call detail tools.',
                'conditions': runtime.conditions, 'initial_search_observation': initial}, ensure_ascii=False)
            original_task = task
            for attempt in range(2):
                async with workflow.run(task) as runner:
                    answer = await asyncio.wait_for(runner.result(), timeout=runtime.policy.max_runtime_seconds)
                try:
                    return runtime.validate(str(answer))
                except ValueError as exc:
                    runtime.events.append({'kind': 'validation', 'status': 'rejected', 'error_code': type(exc).__name__})
                    if attempt or runtime.steps >= runtime.policy.max_steps: raise
                    feedback = {'task': 'The previous final output was rejected. Call the terminal tool with only observed eligible/unknown candidate IDs; never include unsuitable candidates. Do not repeat cached source reads.',
                        'error_code': str(exc) if str(exc) in {'unverified_or_unsuitable_selection', 'unverified_recommendation', 'incomplete_search_not_empty'} else 'invalid_final_output',
                        'observed_verdicts': {key: value['overall'] for key, value in getattr(runtime, 'assessments', {}).items()},
                        'observed_sources': getattr(runtime, 'paths', {})}
                    feedback['original_task'] = json.loads(original_task)
                    if workflow_file == 'challenge-workflow.yml':
                        feedback['task'] = 'The draft/citations were rejected. Keep the original request and additional condition. Use observed source IDs and exact quotes or numbered lines, then call finish_draft. Do not repeat cached reads.'
                    task = json.dumps(feedback, ensure_ascii=False)
    except Exception as exc:
        if getattr(runtime, 'final_result', None) is not None: return runtime.final_result
        # Bounded partial observations survive invalid output, timeout and model limits.
        limits = {'Runtime limit', 'HTTP request limit', 'Daily HTTP request limit', 'Stopped or step limit reached', 'run_closed_or_step_limit', 'tool_step_limit'}
        if runtime.steps >= runtime.policy.max_steps or isinstance(exc, TimeoutError) or (isinstance(exc, ValueError) and str(exc) in limits):
            return runtime.limited('execution_limit:' + type(exc).__name__)
        return runtime.failed(type(exc).__name__)
    finally:
        runtime.close()
        CURRENT.reset(token)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--live', action='store_true')
    parser.add_argument('--request', type=Path)
    parser.add_argument('--output', type=Path)
    parser.add_argument('--challenge', action='store_true')
    parser.add_argument('--additional-condition', default='')
    args = parser.parse_args()
    if not args.live:
        print(json.dumps({'mode': 'dry-run', 'model_requests': 0, 'source_requests': 0}))
        return 0
    if not args.request or not args.output:
        parser.error('--request and --output are required')
    request = args.request.resolve()
    output = args.output.resolve()
    if not request.is_relative_to(Path('/hackathon/input')) or not output.is_relative_to(Path('/hackathon/output')) or output.exists():
        parser.error('Fresh output and request must remain in their /hackathon directories')
    if os.environ.get('MODEL_LEDGER_RECONCILED') != 'yes': parser.error('Shared daily ledger reconciliation required')
    logging.disable(logging.CRITICAL)
    try:
        if request.stat().st_size > 32768: raise ValueError('request_too_large')
        payload = json.loads(request.read_text())
        common = dict(ledger=os.environ.get('MODEL_DAILY_LEDGER'), model=os.environ.get('MODEL_ID'),
            key=os.environ.get('NVIDIA_API_KEY'), policy=load_policy(os.environ))
        if args.challenge:
            from .challenge import ChallengeRuntime
            runtime = ChallengeRuntime(**common, request=payload, additional=args.additional_condition)
            result = asyncio.run(execute(runtime, 'challenge-workflow.yml', runtime.query))
        else:
            if set(payload) != {'request_id', 'conditions_revision', 'conditions'}: raise ValueError('invalid_request')
            runtime = FamilyRuntime(**common, conditions=payload['conditions'], request_id=payload['request_id'], revision=payload['conditions_revision'])
            result = asyncio.run(execute(runtime))
        output.parent.mkdir(parents=True, exist_ok=True)
        with output.open('x') as stream: json.dump(result, stream, ensure_ascii=False)
        print(json.dumps({'action': result['action'], 'physical_model_requests': result['physical_model_requests']}))
        return 1 if result['action'] == 'finish_failed' else 0
    except Exception as exc:
        print(json.dumps({'action': 'finish_failed', 'error_code': type(exc).__name__}))
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
