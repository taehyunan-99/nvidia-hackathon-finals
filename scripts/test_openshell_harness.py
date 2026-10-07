"""Regression tests for false-positive security evidence."""
import errno
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import subprocess
from types import SimpleNamespace

from openshell_harness import probe


class BoundaryTests(unittest.TestCase):
    def test_child_attempts_do_not_read_or_modify_unprotected_controls(self):
        with tempfile.TemporaryDirectory() as root, patch.object(probe, 'ROOT', Path(root)):
            for name in probe.CONTROLS:
                (Path(root) / name).mkdir()
                (Path(root) / name / 'control.txt').write_text('synthetic unchanged')
            checks = probe.child_checks()
            self.assertEqual(len(checks), 3)
            self.assertTrue(all(row['status'] == 'not_denied' for row in checks.values()))
            for name in probe.CONTROLS:
                self.assertEqual((Path(root) / name / 'control.txt').read_text(), 'synthetic unchanged')

    def test_child_failure_is_inconclusive(self):
        for error in (OSError('hidden'), subprocess.TimeoutExpired('hidden', 10)):
            with patch.object(probe.subprocess, 'run', side_effect=error):
                self.assertTrue(all(row['status'] == 'inconclusive'
                                    for row in probe.child_checks().values()))

    def test_malformed_child_result_is_inconclusive(self):
        for raw in ('[]', '{"checks":[]}', 'not-json', '{}'):
            with patch.object(probe.subprocess, 'run', return_value=SimpleNamespace(returncode=0, stdout=raw)):
                self.assertTrue(all(row['status'] == 'inconclusive'
                                    for row in probe.child_checks().values()))

    def test_missing_file_is_not_denial(self):
        with tempfile.TemporaryDirectory() as root:
            self.assertEqual(probe.denied_open(Path(root) / 'missing', os.O_RDONLY),
                             {'status': 'inconclusive', 'errno': errno.ENOENT})

    def test_readable_file_is_failure_without_content_read(self):
        with tempfile.TemporaryDirectory() as root:
            path = Path(root) / 'control'
            path.write_text('do not read or change')
            self.assertEqual(probe.denied_open(path, os.O_WRONLY), {'status': 'not_denied'})
            self.assertEqual(path.read_text(), 'do not read or change')

    def test_denial_errnos_only(self):
        for number in (errno.EPERM, errno.EACCES, errno.ELOOP, errno.EIO):
            with patch.object(probe.os, 'open', side_effect=OSError(number, 'hidden')):
                self.assertEqual(probe.denied_open('/unused', os.O_RDONLY)['status'],
                                 'denied' if number in (errno.EPERM, errno.EACCES) else 'inconclusive')

    def test_unprotected_fixture_cannot_pass(self):
        with tempfile.TemporaryDirectory() as root, patch.object(probe, 'ROOT', Path(root)):
            for name in probe.CONTROLS + ('output',):
                (Path(root) / name).mkdir()
            for name in probe.CONTROLS:
                (Path(root) / name / 'control.txt').write_text('PUBLIC_CONTROL\n')
            for name in ('restricted', 'secrets'):
                (Path(root) / 'output' / ('link-' + name)).symlink_to(Path(root) / name / 'control.txt')
            self.assertTrue(probe.inventory()['passed'])
            self.assertFalse(probe.probe()['passed'])

    def test_transport_failure_is_not_policy_proof(self):
        with patch.object(probe.urllib.request, 'urlopen', side_effect=TimeoutError()):
            self.assertEqual(probe.network()['status'], 'inconclusive')


if __name__ == '__main__':
    unittest.main()
