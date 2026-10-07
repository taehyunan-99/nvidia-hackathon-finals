"""Synthetic boundary probes. Run only in the dedicated harness image."""
import argparse
import errno
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import uuid
import urllib.error
import urllib.request


ROOT = Path('/hackathon')
CONTROLS = ('input', 'restricted', 'secrets')

CHILD_CODE = '''import errno, json, os, sys
from pathlib import Path
root = Path(sys.argv[1])
checks = {}
for name, flags in [('input', os.O_WRONLY), ('restricted', os.O_RDONLY), ('secrets', os.O_RDONLY)]:
    try:
        fd = os.open(root / name / 'control.txt', flags)
    except OSError as exc:
        checks[name + '_child'] = {'status': 'denied' if exc.errno in (errno.EACCES, errno.EPERM) else 'inconclusive', 'errno': exc.errno}
    else:
        os.close(fd)
        checks[name + '_child'] = {'status': 'not_denied'}
print(json.dumps({'uid': os.geteuid(), 'checks': checks}))
'''


def child_checks():
    names = {'input_child', 'restricted_child', 'secrets_child'}
    try:
        result = subprocess.run([sys.executable, '-I', '-c', CHILD_CODE, str(ROOT)],
                                capture_output=True, text=True, timeout=10)
        data = json.loads(result.stdout) if result.returncode == 0 else {}
        checks = data.get('checks', {}) if isinstance(data, dict) else {}
        if (isinstance(data, dict) and isinstance(checks, dict)
                and data.get('uid') == os.geteuid() and set(checks) == names
                and all(isinstance(row, dict) and row.get('status') in
                        {'denied', 'inconclusive', 'not_denied'}
                        and (row['status'] != 'denied' or row.get('errno') in
                             (errno.EACCES, errno.EPERM)) for row in checks.values())):
            return checks
    except (OSError, ValueError, subprocess.TimeoutExpired):
        pass
    return {name: {'status': 'inconclusive'} for name in sorted(names)}


def denied_open(path, flags):
    """Never read forbidden content or truncate a file, even if policy fails."""
    try:
        fd = os.open(path, flags)
    except OSError as exc:
        return {'status': 'denied' if exc.errno in (errno.EACCES, errno.EPERM)
                else 'inconclusive', 'errno': exc.errno}
    os.close(fd)
    return {'status': 'not_denied'}


def inventory():
    """Outside OpenShell, prove controls exist and DAC permits the operations."""
    checks = {}
    for name in CONTROLS:
        path = ROOT / name / 'control.txt'
        checks[name] = path.is_file() and denied_open(path, os.O_RDWR)['status'] == 'not_denied'
    for name in ('restricted', 'secrets'):
        link = ROOT / 'output' / ('link-' + name)
        checks['link-' + name] = link.is_symlink() and link.resolve() == (ROOT / name / 'control.txt').resolve()
    return {'scope': 'fixture_inventory', 'passed': all(checks.values()), 'checks': checks}


def probe():
    checks = {}
    original = None
    try:
        original = hashlib.sha256((ROOT / 'input/control.txt').read_bytes()).digest()
        checks['input_read'] = {'status': 'allowed' if
            (ROOT / 'input/control.txt').read_text() == 'PUBLIC_CONTROL\n' else 'inconclusive'}
        output = ROOT / 'output' / ('probe-' + uuid.uuid4().hex + '.json')
        with output.open('x') as stream:
            stream.write('{"synthetic": true}\n')
        checks['output_write_read'] = {'status': 'allowed' if
            json.loads(output.read_text()) == {'synthetic': True} else 'inconclusive'}
        output.unlink()
    except OSError as exc:
        checks['allowed_io'] = {'status': 'inconclusive', 'errno': exc.errno}
    checks['input_write'] = denied_open(ROOT / 'input/control.txt', os.O_WRONLY)
    for name in ('restricted', 'secrets'):
        checks[name + '_read'] = denied_open(ROOT / name / 'control.txt', os.O_RDONLY)
        checks[name + '_write'] = denied_open(ROOT / name / 'control.txt', os.O_WRONLY)
        checks[name + '_symlink'] = denied_open(ROOT / 'output' / ('link-' + name), os.O_RDONLY)
        checks[name + '_traversal'] = denied_open(ROOT / 'input' / '..' / name / 'control.txt', os.O_RDONLY)
    checks.update(child_checks())
    try:
        unchanged = original is not None and original == hashlib.sha256(
            (ROOT / 'input/control.txt').read_bytes()).digest()
        checks['input_preserved'] = {'status': 'allowed' if unchanged else 'inconclusive'}
    except OSError:
        checks['input_preserved'] = {'status': 'inconclusive'}
    expected = {'input_read': 'allowed', 'output_write_read': 'allowed',
                'input_preserved': 'allowed'}
    passed = os.geteuid() != 0 and all(
        result['status'] == expected.get(name, 'denied') for name, result in checks.items())
    return {'scope': 'filesystem_observation', 'uid': os.geteuid(),
            'passed': passed, 'checks': checks,
            'requires': ['matching_image_inventory', 'effective_policy', 'runtime_enforcement_logs']}


def network():
    # No task data, credential, body, or user-selected destination is transmitted.
    # A timeout, DNS error, or remote HTTP 403 cannot prove an OpenShell denial.
    request = urllib.request.Request('https://example.com/', method='HEAD')
    try:
        with urllib.request.urlopen(request, timeout=10) as response:
            status = response.status
    except urllib.error.HTTPError as exc:
        status = exc.code
    except (OSError, urllib.error.URLError):
        return {'scope': 'network_observation', 'status': 'inconclusive',
                'requires': ['correlated_runtime_deny_event', 'controlled_receiver_check']}
    return {'scope': 'network_observation', 'status': 'inconclusive' if status == 403 else 'not_denied',
            'http_status': status,
            'requires': ['correlated_runtime_deny_event', 'controlled_receiver_check']}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode', choices=['inventory', 'filesystem', 'network'])
    args = parser.parse_args()
    result = {'inventory': inventory, 'filesystem': probe, 'network': network}[args.mode]()
    print(json.dumps(result, sort_keys=True))
    return 0 if result.get('passed') else 2


if __name__ == '__main__':
    raise SystemExit(main())
