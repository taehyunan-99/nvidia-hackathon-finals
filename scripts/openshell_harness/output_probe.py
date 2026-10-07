"""Synthetic collector checks; creates and removes only its own temporary tree."""
import json
import os
from pathlib import Path
import tempfile

if __package__:
    from .output import OutputRejected, collect_json
else:
    from output import OutputRejected, collect_json


def probe(root=Path('/hackathon/output')):
    checks = {}
    with tempfile.TemporaryDirectory(prefix='collection-', dir=root) as temporary:
        base = Path(temporary)
        job_id = 'a' * 32
        directory = base / job_id
        directory.mkdir()
        output = directory / 'result.json'
        raw = json.dumps({'job_id': job_id, 'result': {'text': 'synthetic'}}).encode()
        root_fd = os.open(base, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
        options = {'requester': 'owner-a', 'job_owner': 'owner-a',
                   'expected_uid': os.geteuid()}

        def check(name, expected=None, **changes):
            try:
                result = collect_json(root_fd, job_id, **(options | changes))
                checks[name] = expected is None and result == {'text': 'synthetic'}
            except OutputRejected as exc:
                checks[name] = expected is not None and str(exc) == expected

        try:
            output.write_bytes(raw)
            check('valid')
            check('other_owner', 'wrong_owner', requester='owner-b')
            check('wrong_uid', 'wrong_file_owner', expected_uid=os.geteuid() + 1)
            check('oversized', 'too_large', max_bytes=len(raw) - 1)
            output.write_text('{"job_id":"' + job_id + '","result":{},"result":{}}')
            check('duplicate_key', 'duplicate_key')
            output.write_text(json.dumps({'job_id': 'b' * 32, 'result': {}}))
            check('other_job', 'invalid_envelope')
            output.write_bytes(b'\xff')
            check('invalid_utf8', 'unreadable_or_invalid')
            output.unlink()
            check('missing', 'unreadable_or_invalid')
            target = base / 'control.json'
            target.write_bytes(raw)
            output.symlink_to(target)
            check('file_symlink', 'unreadable_or_invalid')
            output.unlink()
            os.link(target, output)
            check('hardlink', 'hardlink')
            output.unlink()
            os.mkfifo(output)
            check('fifo', 'not_regular')
            output.unlink()
            directory.rmdir()
            directory.symlink_to(base, target_is_directory=True)
            check('directory_symlink', 'unreadable_or_invalid')
        finally:
            os.close(root_fd)
    return {'scope': 'synthetic_output_collection', 'passed': all(checks.values()),
            'checks': checks, 'requires': ['trusted_job_owner_lookup',
                                         'terminated_writer', 'consumer_schema_validation']}


if __name__ == '__main__':
    result = probe()
    print(json.dumps(result, sort_keys=True))
    raise SystemExit(0 if result['passed'] else 2)
