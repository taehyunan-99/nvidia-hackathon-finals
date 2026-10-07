"""Loopback-only trial job API; run on the Brev host, never in a workload."""
import argparse
import hashlib
import hmac
import json
import os
from pathlib import Path
import re
import sqlite3
import subprocess
import threading
import uuid
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer


IDENTIFIER = re.compile(r"[A-Za-z0-9_-]{1,64}\Z")
JOB_ID = re.compile(r"[a-f0-9]{32}\Z")


class Store:
    def __init__(self, path):
        self.path = str(path)
        with self.connect() as db:
            db.execute("""CREATE TABLE IF NOT EXISTS jobs (
                id TEXT PRIMARY KEY, owner TEXT NOT NULL, request_key TEXT NOT NULL,
                payload TEXT NOT NULL, state TEXT NOT NULL, result TEXT,
                UNIQUE(owner, request_key))""")

    def connect(self):
        return sqlite3.connect(self.path, timeout=5)

    def accept(self, owner, key, payload):
        with self.connect() as db:
            db.execute("BEGIN IMMEDIATE")
            row = db.execute("SELECT id, payload FROM jobs WHERE owner=? AND request_key=?",
                             (owner, key)).fetchone()
            if row:
                return row[0], False, row[1] == payload
            if db.execute("SELECT count(*) FROM jobs").fetchone()[0] >= 32:
                return None, False, False
            job_id = uuid.uuid4().hex
            db.execute("INSERT INTO jobs VALUES (?, ?, ?, ?, 'queued', NULL)",
                       (job_id, owner, key, payload))
            return job_id, True, True

    def get(self, owner, job_id):
        with self.connect() as db:
            row = db.execute("SELECT state, result FROM jobs WHERE id=? AND owner=?",
                             (job_id, owner)).fetchone()
        if row is None:
            return None
        return {"job_id": job_id, "state": row[0],
                "result": json.loads(row[1]) if row[1] else None}

    def recover(self):
        # A host crash leaves execution uncertain. Never automatically repeat it.
        with self.connect() as db:
            db.execute("UPDATE jobs SET state='unknown' WHERE state='running'")

    def claim(self):
        with self.connect() as db:
            db.execute("BEGIN IMMEDIATE")
            row = db.execute("SELECT id, payload FROM jobs WHERE state='queued' LIMIT 1").fetchone()
            if row:
                db.execute("UPDATE jobs SET state='running' WHERE id=?", (row[0],))
        return row

    def finish(self, job_id, state, result=None):
        with self.connect() as db:
            db.execute("UPDATE jobs SET state=?, result=? WHERE id=? AND state='running'",
                       (state, json.dumps(result) if result is not None else None, job_id))


class OpenShellRunner:
    def __init__(self, binary, gateway, image, policy):
        self.binary, self.gateway = binary, gateway
        self.image, self.policy = image, str(policy)

    def command(self, args, payload=None, timeout=30):
        # No shell, input-derived argv, credential auto-discovery, or raw CLI logs.
        return subprocess.run([self.binary, "--gateway", self.gateway, *args],
                              input=payload, capture_output=True, text=True, timeout=timeout)

    def ready(self):
        try:
            version = subprocess.run([self.binary, "--version"], capture_output=True,
                                     text=True, timeout=5)
            return (version.returncode == 0 and version.stdout.strip() == "openshell 0.1.2"
                    and self.command(["status"], timeout=5).returncode == 0)
        except (OSError, subprocess.TimeoutExpired):
            return False

    def run(self, job_id, payload):
        name = "bridge-" + job_id[:12]
        started = False
        try:
            created = self.command([
                "sandbox", "create", "--name", name, "--from", self.image,
                "--policy", self.policy, "--cpu", "1", "--memory", "512Mi",
                "--approval-mode", "manual", "--no-auto-providers", "--detach",
                "--", "sleep", "infinity"
            ], timeout=90)
            if created.returncode:
                return "unknown", None
            started = True
            executed = self.command([
                "sandbox", "exec", "-n", name, "--no-tty", "--timeout", "30",
                "--", "python3", "/opt/bridge/worker.py", "run"
            ], payload=payload, timeout=40)
            if executed.returncode:
                return "failed", None
            collected = self.command([
                "sandbox", "exec", "-n", name, "--no-tty", "--timeout", "10",
                "--", "python3", "/opt/bridge/worker.py", "result"
            ], timeout=15)
            if collected.returncode or len(collected.stdout.encode()) > 4096:
                return "failed", None
            result = json.loads(collected.stdout)
            expected = json.loads(payload)["text"]
            if result != {"text": expected, "sha256": hashlib.sha256(expected.encode()).hexdigest()}:
                return "failed", None
            return "succeeded", result
        except (OSError, subprocess.TimeoutExpired):
            return "unknown", None
        except (ValueError, TypeError):
            return "failed", None
        finally:
            # Only this API's own deterministic sandbox; never delete shared resources.
            if started:
                try:
                    self.command(["sandbox", "stop", name], timeout=20)
                except (OSError, subprocess.TimeoutExpired):
                    pass


class Bridge:
    def __init__(self, store, runner, token):
        self.store, self.runner, self.token = store, runner, token
        self.stopping = threading.Event()

    def work(self):
        self.store.recover()
        while not self.stopping.is_set():
            if self.runner.ready():
                row = self.store.claim()
                if row:
                    state, result = self.runner.run(*row)
                    self.store.finish(row[0], state, result)
                    continue
            self.stopping.wait(1)


def handler_for(bridge):
    class Handler(BaseHTTPRequestHandler):
        def setup(self):
            super().setup()
            self.connection.settimeout(5)

        def log_message(self, *_args):
            pass

        def respond(self, status, data):
            body = json.dumps(data, ensure_ascii=False).encode()
            self.send_response(status)
            self.send_header("Content-Type", "application/json")
            self.send_header("Cache-Control", "no-store")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def owner(self):
            supplied = self.headers.get("Authorization", "").encode()
            if not hmac.compare_digest(supplied, b"Bearer " + bridge.token):
                self.respond(401, {"error": "unauthorized"})
                return None
            owner = self.headers.get("X-Job-Owner", "")
            if not IDENTIFIER.fullmatch(owner):
                self.respond(400, {"error": "invalid_owner"})
                return None
            return owner

        def do_GET(self):
            owner = self.owner()
            if owner is None:
                return
            if self.path == "/health/live":
                self.respond(200, {"live": True})
            elif self.path == "/health/ready":
                ready = bridge.runner.ready()
                self.respond(200 if ready else 503, {"ready": ready})
            elif self.path.startswith("/jobs/") and JOB_ID.fullmatch(self.path[6:]):
                job = bridge.store.get(owner, self.path[6:])
                self.respond(200 if job else 404, job or {"error": "not_found"})
            else:
                self.respond(404, {"error": "not_found"})

        def do_POST(self):
            owner = self.owner()
            if owner is None:
                return
            if self.path != "/jobs":
                self.respond(404, {"error": "not_found"})
                return
            key = self.headers.get("Idempotency-Key", "")
            try:
                length = int(self.headers.get("Content-Length", "0"))
                if not IDENTIFIER.fullmatch(key) or not 0 < length <= 4096:
                    raise ValueError
                if self.headers.get("Content-Type") != "application/json":
                    raise ValueError
                data = json.loads(self.rfile.read(length))
                if (not isinstance(data, dict) or set(data) != {"text"}
                        or not isinstance(data["text"], str)
                        or not 0 < len(data["text"].encode()) <= 512):
                    raise ValueError
            except (ValueError, UnicodeError):
                self.respond(400, {"error": "invalid_request"})
                return
            payload = json.dumps(data, sort_keys=True, ensure_ascii=False)
            # Check durable idempotency before gateway readiness so retry works offline.
            previous = None
            with bridge.store.connect() as db:
                previous = db.execute("SELECT id FROM jobs WHERE owner=? AND request_key=?",
                                      (owner, key)).fetchone()
            if previous is None and not bridge.runner.ready():
                self.respond(503, {"error": "worker_unavailable"})
                return
            job_id, created, matches = bridge.store.accept(owner, key, payload)
            if job_id is None:
                self.respond(429, {"error": "trial_limit"})
            elif not matches:
                self.respond(409, {"error": "idempotency_conflict"})
            else:
                self.respond(202 if created else 200, bridge.store.get(owner, job_id))

    return Handler


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", type=int, default=18080)
    args = parser.parse_args()
    token_path = Path(os.environ["BRIDGE_TOKEN_FILE"])
    if token_path.stat().st_mode & 0o077:
        raise SystemExit("token file must not be accessible by group or others")
    token = token_path.read_bytes().strip()
    if len(token) < 32 or any(c < 33 or c > 126 for c in token):
        raise SystemExit("token must contain at least 32 printable ASCII bytes")
    state_dir = Path(os.environ["BRIDGE_STATE_DIR"])
    state_dir.mkdir(mode=0o700, parents=True, exist_ok=True)
    os.umask(0o077)
    runner = OpenShellRunner(os.environ["BRIDGE_OPENSHELL_BIN"],
                             os.environ["BRIDGE_GATEWAY"], os.environ["BRIDGE_IMAGE"],
                             os.environ["BRIDGE_POLICY"])
    bridge = Bridge(Store(state_dir / "jobs.sqlite3"), runner, token)
    # Second API process must not mark another active worker's job unknown.
    import fcntl
    lock = (state_dir / "worker.lock").open("w")
    fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    server = ThreadingHTTPServer(("127.0.0.1", args.port), handler_for(bridge))
    threading.Thread(target=bridge.work, daemon=True).start()
    server.serve_forever()


if __name__ == "__main__":
    main()
