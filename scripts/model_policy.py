"""Shared finals model limits. Reserve every physical request, including 429 retries."""
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
import json
import math
from pathlib import Path
import sqlite3
import time
import urllib.error

ROOT = Path(__file__).resolve().parents[1]
ENV_FIELDS = {
    'NEMOTRON_REQUEST_LIMIT': 'request_limit',
    'NEMOTRON_DAILY_REQUEST_LIMIT': 'daily_request_limit',
    'MODEL_REQUEST_INTERVAL_SECONDS': 'request_interval_seconds',
    'MODEL_REQUEST_TIMEOUT_SECONDS': 'request_timeout_seconds',
    'MODEL_MAX_OUTPUT_TOKENS': 'max_output_tokens',
    'MAX_STEPS': 'max_steps',
    'MODEL_MAX_ATTEMPTS': 'max_attempts',
    'MODEL_MAX_RETRY_WAIT_SECONDS': 'max_retry_wait_seconds',
    'MAX_RUNTIME_SECONDS': 'max_runtime_seconds',
}


@dataclass(frozen=True)
class Policy:
    request_limit: int
    daily_request_limit: int
    request_interval_seconds: int
    request_timeout_seconds: int
    max_output_tokens: int
    max_steps: int
    max_attempts: int
    max_retry_wait_seconds: int
    max_runtime_seconds: int


def load_policy(settings=None):
    data = json.loads((ROOT/'docs/playbooks/model-policy.json').read_text())
    data.pop('version')
    for env, field in ENV_FIELDS.items():
        if (settings or {}).get(env): data[field] = int(settings[env])
    if any(type(v) is not int or v < 1 for v in data.values()):
        raise ValueError('Model limits must be positive integers')
    if data['max_runtime_seconds'] < data['request_timeout_seconds']:
        raise ValueError('Runtime must cover one request timeout')
    return Policy(**data)


def reserve_daily(path, limit, now=None):
    day = (now or datetime.now(timezone(timedelta(hours=9)))).astimezone(timezone(timedelta(hours=9))).date().isoformat()
    path = Path(path); path.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(path, timeout=10) as conn:
        conn.execute('CREATE TABLE IF NOT EXISTS requests (day TEXT PRIMARY KEY, used INTEGER NOT NULL)')
        conn.execute('BEGIN IMMEDIATE')
        row = conn.execute('SELECT used FROM requests WHERE day=?', (day,)).fetchone()
        if row and row[0] >= limit: raise ValueError('Daily HTTP request limit')
        conn.execute('INSERT INTO requests VALUES (?,1) ON CONFLICT(day) DO UPDATE SET used=used+1', (day,))


def retry_delay(attempt, value, maximum):
    try: after = float(value)
    except (TypeError, ValueError):
        try: after = (parsedate_to_datetime(value) - datetime.now(timezone.utc)).total_seconds()
        except (TypeError, ValueError, OverflowError): after = 0
    if not math.isfinite(after): after = 0
    wanted = max(30 * 2 ** attempt, after)
    return wanted if wanted <= maximum else None


class Budget:
    def __init__(self, send, policy=None, daily_path=None, clock=time.monotonic, sleep=time.sleep):
        self.policy = policy or load_policy()
        self.daily_path = Path(daily_path) if daily_path is not None else ROOT/'runs/model-daily-budget.sqlite3'
        self.send, self.clock, self.sleep = send, clock, sleep
        self.started, self.last, self.count = clock(), None, 0

    def start_run(self):
        # Reset the run cap, but preserve pacing and the shared daily ledger.
        self.started, self.count = self.clock(), 0

    def _wait(self, seconds):
        remaining = self.policy.max_runtime_seconds - (self.clock() - self.started)
        if seconds + self.policy.request_timeout_seconds > remaining:
            raise ValueError('Runtime limit')
        if seconds > 0: self.sleep(seconds)

    def __call__(self, payload):
        for attempt in range(self.policy.max_attempts):
            if self.count >= self.policy.request_limit: raise ValueError('HTTP request limit')
            interval = 0 if self.last is None else max(0, self.policy.request_interval_seconds - (self.clock() - self.last))
            self._wait(interval)
            reserve_daily(self.daily_path, self.policy.daily_request_limit)
            self.count += 1
            self.last = self.clock()
            try: return self.send(payload)
            except urllib.error.HTTPError as exc:
                if exc.code != 429 or attempt + 1 >= self.policy.max_attempts: raise
                delay = retry_delay(attempt, exc.headers.get('Retry-After') if exc.headers else None,
                                    self.policy.max_retry_wait_seconds)
                if delay is None: raise
                self._wait(delay)
