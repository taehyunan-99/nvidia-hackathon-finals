from dataclasses import replace
from datetime import datetime, timezone
from pathlib import Path
import sqlite3
import tempfile
import unittest
import urllib.error
from unittest.mock import Mock
from model_policy import Budget, load_policy, reserve_daily, retry_delay


class PolicyTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(); self.path = Path(self.tmp.name)/'daily.sqlite3'
        self.now = 0
    def tearDown(self): self.tmp.cleanup()
    def sleep(self, seconds): self.now += seconds
    def budget(self, sender, **settings):
        return Budget(sender, policy=replace(load_policy(), **settings), daily_path=self.path,
                      clock=lambda: self.now, sleep=self.sleep)

    def test_run_limit_allows_forty_and_stops_before_forty_one(self):
        sender=Mock(return_value={}); b=self.budget(sender)
        for _ in range(40): b({})
        with self.assertRaises(ValueError): b({})
        self.assertEqual(sender.call_count,40)

    def test_deadline_reserves_request_timeout(self):
        sender=Mock(); b=self.budget(sender); self.now=841
        with self.assertRaises(ValueError): b({})
        sender.assert_not_called()

    def test_shared_daily_limit_survives_new_run(self):
        sender=Mock(return_value={})
        self.budget(sender,daily_request_limit=1)({})
        with self.assertRaises(ValueError): self.budget(sender,daily_request_limit=1)({})
        self.assertEqual(sender.call_count,1)

    def test_new_run_preserves_request_spacing(self):
        b=self.budget(Mock(return_value={}),request_limit=1)
        b({});b.start_run();b({})
        self.assertEqual(b.count,1);self.assertEqual(self.now,15)

    def test_day_rolls_at_korean_midnight(self):
        reserve_daily(self.path,1,datetime(2026,10,6,14,59,tzinfo=timezone.utc))
        with self.assertRaises(ValueError): reserve_daily(self.path,1,datetime(2026,10,6,14,59,tzinfo=timezone.utc))
        reserve_daily(self.path,1,datetime(2026,10,6,15,0,tzinfo=timezone.utc))

    def test_429_retries_count_as_physical_requests(self):
        error=urllib.error.HTTPError('https://example.invalid',429,'limited',{'Retry-After':'35'},None)
        sender=Mock(side_effect=[error,error,{}]); b=self.budget(sender)
        self.assertEqual(b({}),{})
        self.assertEqual(b.count,3); self.assertEqual(sender.call_count,3)
        self.assertEqual(self.now,95)
        with sqlite3.connect(self.path) as conn:self.assertEqual(conn.execute('SELECT used FROM requests').fetchone()[0],3)

    def test_retry_stops_at_three_attempts(self):
        error=urllib.error.HTTPError('https://example.invalid',429,'limited',{},None)
        sender=Mock(side_effect=error); b=self.budget(sender)
        with self.assertRaises(urllib.error.HTTPError): b({})
        self.assertEqual(sender.call_count,3)

    def test_retry_cannot_bypass_run_limit(self):
        error=urllib.error.HTTPError('https://example.invalid',429,'limited',{},None)
        sender=Mock(side_effect=error); b=self.budget(sender,request_limit=1)
        with self.assertRaises(ValueError): b({})
        self.assertEqual(sender.call_count,1)

    def test_long_retry_after_is_not_shortened(self):
        self.assertIsNone(retry_delay(0,'121',120))
        error=urllib.error.HTTPError('https://example.invalid',429,'limited',{'Retry-After':'121'},None)
        sender=Mock(side_effect=error)
        with self.assertRaises(urllib.error.HTTPError): self.budget(sender)({})
        self.assertEqual(sender.call_count,1);self.assertEqual(self.now,0)

    def test_unrelated_provider_errors_are_not_retried(self):
        for status in [401,403,500]:
            sender=Mock(side_effect=urllib.error.HTTPError('https://example.invalid',status,'error',{},None))
            with self.assertRaises(urllib.error.HTTPError):self.budget(sender)({})
            self.assertEqual(sender.call_count,1)

    def test_positive_overrides_and_deadline_consistency(self):
        self.assertEqual(load_policy({'NEMOTRON_REQUEST_LIMIT':'50'}).request_limit,50)
        for settings in [{'NEMOTRON_REQUEST_LIMIT':'0'},{'MAX_RUNTIME_SECONDS':'30'}]:
            with self.assertRaises(ValueError):load_policy(settings)


if __name__=='__main__':unittest.main()
