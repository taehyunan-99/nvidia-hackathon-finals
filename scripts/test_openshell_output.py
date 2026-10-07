"""Exercise hostile files independently of the model and OpenShell runtime."""
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from openshell_harness.output import OutputRejected, collect_json
from openshell_harness import output_probe


class CollectionTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.job = 'a' * 32
        (self.root / self.job).mkdir()
        self.output = self.root / self.job / 'result.json'
        self.raw = json.dumps({'job_id': self.job, 'result': {'text': '문화 초안'}}).encode()
        self.output.write_bytes(self.raw)
        self.fd = os.open(self.root, os.O_RDONLY | os.O_DIRECTORY)

    def tearDown(self):
        os.close(self.fd)
        self.temporary.cleanup()

    def collect(self, **options):
        defaults = dict(requester='owner-a', job_owner='owner-a', expected_uid=os.getuid())
        return collect_json(self.fd, self.job, **(defaults | options))

    def test_valid_exact_byte_limit(self):
        self.assertEqual(self.collect(max_bytes=len(self.raw)), {'text': '문화 초안'})
        with self.assertRaisesRegex(OutputRejected, '^too_large$'):
            self.collect(max_bytes=len(self.raw) - 1)

    def test_owner_rejected_before_any_file_open(self):
        with patch('openshell_harness.output.os.open') as opened:
            with self.assertRaisesRegex(OutputRejected, '^wrong_owner$'):
                self.collect(requester='owner-b')
            opened.assert_not_called()

    def test_job_path_traversal_rejected_before_open(self):
        for value in ('../' + self.job, '/' + self.job, self.job + '/result.json', '', 'A' * 32):
            with self.subTest(value=value), patch('openshell_harness.output.os.open') as opened:
                with self.assertRaisesRegex(OutputRejected, '^invalid_job_id$'):
                    collect_json(self.fd, value, requester='a', job_owner='a', expected_uid=os.getuid())
                opened.assert_not_called()

    def test_links_never_read(self):
        target = self.root / 'private'
        target.write_text('synthetic-private')
        self.output.unlink()
        self.output.symlink_to(target)
        with patch('openshell_harness.output.os.read') as read:
            with self.assertRaises(OutputRejected):
                self.collect()
            read.assert_not_called()
        self.output.unlink()
        os.link(target, self.output)
        with patch('openshell_harness.output.os.read') as read:
            with self.assertRaisesRegex(OutputRejected, '^hardlink$'):
                self.collect()
            read.assert_not_called()

    def test_other_job_directory_symlink_rejected(self):
        self.output.unlink()
        (self.root / self.job).rmdir()
        other = self.root / ('b' * 32)
        other.mkdir()
        (other / 'result.json').write_bytes(self.raw)
        (self.root / self.job).symlink_to(other)
        with self.assertRaises(OutputRejected):
            self.collect()

    def test_fifo_and_directory_rejected_without_blocking(self):
        self.output.unlink()
        os.mkfifo(self.output)
        with self.assertRaisesRegex(OutputRejected, '^not_regular$'):
            self.collect()
        self.output.unlink()
        self.output.mkdir()
        with self.assertRaisesRegex(OutputRejected, '^not_regular$'):
            self.collect()

    def test_uid_mismatch(self):
        with self.assertRaisesRegex(OutputRejected, '^wrong_file_owner$'):
            self.collect(expected_uid=os.getuid() + 1)

    def test_envelope_and_numeric_traps(self):
        for raw in (b'[]', b'{}', b'null', b'\xff', b'{',
                    json.dumps({'job_id': 'b' * 32, 'result': {}}).encode(),
                    json.dumps({'job_id': self.job, 'result': {}, 'owner': 'a'}).encode(),
                    ('{"job_id":"' + self.job + '","result":{"x":1,"x":2}}').encode(),
                    ('{"job_id":"' + self.job + '","result":{"x":NaN}}').encode(),
                    ('{"job_id":"' + self.job + '","result":{"x":1e999}}').encode()):
            with self.subTest(raw=raw):
                self.output.write_bytes(raw)
                with self.assertRaises(OutputRejected):
                    self.collect()

    def test_growing_file_is_bounded(self):
        original_read = os.read
        def grow(fd, size):
            self.output.write_bytes(self.raw + b' ' * 1000)
            return original_read(fd, size)
        with patch('openshell_harness.output.os.read', side_effect=grow):
            with self.assertRaisesRegex(OutputRejected, '^too_large$'):
                self.collect(max_bytes=len(self.raw))

    def test_changed_file_rejected(self):
        original_read = os.read
        def change(fd, size):
            result = original_read(fd, size)
            os.utime(self.output, ns=(1, 1))
            return result
        with patch('openshell_harness.output.os.read', side_effect=change):
            with self.assertRaisesRegex(OutputRejected, '^changed_during_read$'):
                self.collect()

    def test_error_contains_no_content(self):
        self.output.write_text('SYNTHETIC_PRIVATE_PAYLOAD')
        with self.assertRaisesRegex(OutputRejected, '^unreadable_or_invalid$') as error:
            self.collect()
        self.assertNotIn('SYNTHETIC_PRIVATE', str(error.exception))

    def test_probe_is_repeatable_and_cleans_its_tree(self):
        before = set(self.root.iterdir())
        for _ in range(2):
            result = output_probe.probe(self.root)
            self.assertTrue(result['passed'], result)
            self.assertEqual(len(result['checks']), 12)
            self.assertEqual(set(self.root.iterdir()), before)


if __name__ == '__main__':
    unittest.main()
