import unittest
from unittest.mock import patch
import urllib.error

from openshell_harness import network_probe as probe


class NetworkTests(unittest.TestCase):
    def test_public_and_metadata_targets_rejected(self):
        for host in ('example.com', '8.8.8.8', '127.0.0.1', '169.254.169.254', '::1'):
            with self.subTest(host=host), self.assertRaises(ValueError):
                probe.receiver_url(host)

    def test_fixed_synthetic_body(self):
        with patch.object(probe.urllib.request, 'build_opener') as build:
            build.return_value.open.side_effect = TimeoutError()
            self.assertEqual(probe.attempt('172.17.0.2')['status'], 'unconfirmed')
            request = build.return_value.open.call_args.args[0]
            self.assertEqual(request.data, probe.MARKER)
            self.assertEqual(request.full_url, 'http://172.17.0.2:8080/probe')
            self.assertEqual(request.get_method(), 'POST')

    def test_http_403_is_not_denial_proof(self):
        with patch.object(probe.urllib.request, 'build_opener') as build:
            build.return_value.open.side_effect = urllib.error.HTTPError('', 403, '', {}, None)
            result = probe.attempt('172.17.0.2')
        count = {'posts': 1, 'accepted': 1}
        self.assertEqual(probe.verdict(count, count, result, correlated_policy_deny=False,
                                      same_receiver=True), 'UNVERIFIED')

    def test_receiver_delivery_fails_even_with_deny_event(self):
        self.assertEqual(probe.verdict({'posts': 1, 'accepted': 1},
                                      {'posts': 2, 'accepted': 2},
                                      {'status': 'unconfirmed'}, correlated_policy_deny=True,
                                      same_receiver=True), 'FAIL')

    def test_complete_denial_evidence_passes(self):
        count = {'posts': 1, 'accepted': 1}
        self.assertEqual(probe.verdict(count, count, {'status': 'unconfirmed'},
                                      correlated_policy_deny=True, same_receiver=True), 'PASS')
        self.assertEqual(probe.verdict(count, count, {'status': 'unconfirmed'},
                                      correlated_policy_deny=True, same_receiver=False), 'UNVERIFIED')

    def test_missing_control_or_reset_is_unverified(self):
        for before, after in [({}, {}), ({'posts': 0, 'accepted': 0}, {'posts': 0, 'accepted': 0}),
                              ({'posts': 1, 'accepted': 1}, {'posts': 0, 'accepted': 0})]:
            self.assertEqual(probe.verdict(before, after, {'status': 'unconfirmed'},
                                          correlated_policy_deny=True, same_receiver=True), 'UNVERIFIED')


if __name__ == '__main__':
    unittest.main()
