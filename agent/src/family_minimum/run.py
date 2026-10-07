import argparse
import asyncio
import json
import logging
import os
from pathlib import Path

from .runtime import CURRENT, ROOT, Runtime, load_policy


async def execute(runtime):
    from nat.builder.workflow_builder import WorkflowBuilder
    from nat.runtime.loader import load_config
    from . import register

    token = CURRENT.set(runtime)
    try:
        config = load_config(ROOT / 'agent/workflow.yml')
        async with WorkflowBuilder.from_config(config) as builder:
            workflow = await builder.build()
            async with workflow.run('Inspect the official Seoul public sample; do not confirm participation.') as runner:
                answer = await asyncio.wait_for(runner.result(), timeout=runtime.policy.max_runtime_seconds)
        return runtime.validate(str(answer))
    finally:
        runtime.close()
        CURRENT.reset(token)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--live', action='store_true')
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    if not args.live:
        print(json.dumps({'mode': 'dry-run', 'model_requests': 0, 'source_requests': 0,
            'requires': ['dedicated OpenShell sandbox', 'provider credential', 'reconciled shared daily ledger']}))
        return 0
    if args.output is None or args.output.exists():
        parser.error('A fresh output file under /hackathon/output is required')
    output = args.output.resolve()
    if not output.is_relative_to(Path('/hackathon/output').resolve()):
        parser.error('Output must stay under /hackathon/output')
    if os.environ.get('MODEL_LEDGER_RECONCILED') != 'yes':
        parser.error('Confirm the shared daily ledger before live execution')
    logging.disable(logging.CRITICAL)
    runtime = None
    try:
        runtime = Runtime(os.environ.get('MODEL_DAILY_LEDGER'), os.environ.get('MODEL_ID'),
            os.environ.get('NVIDIA_API_KEY'), policy=load_policy(os.environ))
        result = asyncio.run(execute(runtime))
        result.update(mode='live', boundary='requires external OpenShell policy evidence')
        output.parent.mkdir(parents=True, exist_ok=True)
        with output.open('x', encoding='utf-8') as stream:
            json.dump(result, stream, ensure_ascii=False)
        print(json.dumps({'status': result['status'], 'physical_model_requests': runtime.budget.count,
            'participation': 'unverified', 'output': str(output)}))
        return 0
    except Exception as exc:
        print(json.dumps({'status': 'failed', 'error_type': type(exc).__name__,
            'physical_model_requests': runtime.budget.count if runtime else 0}))
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
