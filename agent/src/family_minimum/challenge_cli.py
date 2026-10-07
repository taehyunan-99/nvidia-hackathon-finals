import argparse
import json
import os
import sys
import uuid
from pathlib import Path

from .challenge_contract import ChallengeRequest, RequestRejected, pending_result
from .challenge_files import FileRejected, InputFiles, read_task, write_result

SANDBOX_ROOT = Path('/hackathon')


def parser():
    cli = argparse.ArgumentParser(description='챌린지 CLI; 기본은 무통신 준비, run --live에서 에이전트 실행')
    cli.add_argument('--local-root', type=Path, help='TASK.md·hackathon/이 있는 로컬 레포 루트; 정책 증거 아님')
    commands = cli.add_subparsers(dest='command', required=True)
    commands.add_parser('inspect', help='허용 input 파일 목록만 확인')
    search = commands.add_parser('search', help='허용 자료 검색; 원문은 비신뢰 데이터')
    search.add_argument('query')
    search.add_argument('--offset', type=int, default=0)
    read = commands.add_parser('read', help='input 기준 상대 source ID의 원문 읽기')
    read.add_argument('source_id')
    run = commands.add_parser('run', help='요청 전달 준비와 미연결 결과 저장; 판단·추천 실행 아님')
    run.add_argument('--request', help='선택 요청 override; 기본은 패키지 TASK.md 원문')
    run.add_argument('--additional-conditions', default='')
    run.add_argument('--live', action='store_true', help='OpenShell 안에서 실제 공통 에이전트 실행')
    return cli


def main(argv=None):
    args = parser().parse_args(argv)
    mode = 'local_preparation' if args.local_root else 'sandbox_preparation'
    root = args.local_root / 'hackathon' if args.local_root else SANDBOX_ROOT
    if not root.is_absolute() or '..' in root.parts:
        return emit({'status': 'invalid_input', 'code': 'absolute_root_required'}, 2)
    request = None
    task = None
    live = args.command == 'run' and args.live
    if live and args.local_root:
        return emit({'status': 'invalid_input', 'code': 'live_requires_sandbox_root',
                     'artifact_saved': False}, 2)
    try:
        if args.command == 'run':
            if args.request is None:
                task = read_task(args.local_root if args.local_root else root)
            request = ChallengeRequest(task['text'] if task else args.request, args.additional_conditions)
        files = InputFiles(root / 'input')
        try:
            if args.command == 'inspect':
                response = {'status': 'ok', 'source_ids': files.paths()}
            elif args.command == 'search':
                response = files.search(args.query, args.offset)
            elif args.command == 'read':
                response = files.read(args.source_id)
            else:
                packet = request.packet(uuid.uuid4().hex, files.paths())
                packet['request_source'] = ({'kind': 'task_file', 'source_id': 'TASK.md',
                                             'sha256': task['sha256']} if task else {'kind': 'cli_override'})
                response = pending_result(packet, local=args.local_root is not None)
                events = []
                if task:
                    events.append({'name': 'read_task', 'source_ids': ['TASK.md'], 'status': 'completed'})
                events.append({'name': 'inspect_input', 'source_ids': [], 'status': 'completed',
                               'file_count': len(packet['available_source_ids'])})
                preparation = response['events'][0]
                response['events'] = [{'seq': index, 'run_id': packet['request_id'], 'kind': 'tool',
                                       **event} for index, event in enumerate(events, start=1)]
                response['events'].append({**preparation, 'seq': len(events) + 1})
                response['used_sources'] = [packet['request_source']] if task else []
                response['access_denials'] = []
        finally:
            files.close()
        if args.command == 'run':
            exit_code = 4
            if live:
                from .challenge_connection import ConnectionRejected, connected_result, run_agent
                try:
                    result = run_agent(packet, root / 'input', os.environ)
                    response = connected_result(response, result)
                    exit_code = {'completed': 0, 'needs_confirmation': 0, 'limited': 6, 'failed': 1}[response['status']]
                except ConnectionRejected as exc:
                    response.update(status='failed', code=str(exc),
                                    message='에이전트 실행을 완료하지 못했습니다.', execution_mode='live',
                                    agent_connected=exc.observation['agent_connected'],
                                    model_requests=exc.observation['model_requests'])
                    response['events'].extend([{**event, 'seq': len(response['events']) + index,
                                               'run_id': response['run_id']}
                                              for index, event in enumerate(exc.observation['events'], start=1)])
                    response['events'].append({'seq': len(response['events']) + 1, 'run_id': response['run_id'],
                                               'kind': 'result', 'name': 'agent_connection',
                                               'status': 'failed', 'code': str(exc)})
                    exit_code = 1
            artifact = write_result(root / 'output', response['run_id'], response)
            return emit({**response, 'artifact_saved': True, 'artifact': artifact}, exit_code)
        return emit({**response, 'execution_mode': mode, 'policy_verification': 'unverified'}, 0)
    except RequestRejected as exc:
        return emit({'status': 'invalid_input', 'code': str(exc), 'artifact_saved': False}, 2)
    except FileRejected as exc:
        return emit({'status': 'failed', 'code': str(exc), 'artifact_saved': False,
                     'policy_verification': 'unverified'}, 5)
    except OSError:
        return emit({'status': 'failed', 'code': 'filesystem_unavailable', 'artifact_saved': False,
                     'policy_verification': 'unverified'}, 5)


def emit(value, code):
    print(json.dumps(value, ensure_ascii=False, allow_nan=False))
    return code


if __name__ == '__main__':
    sys.exit(main())
