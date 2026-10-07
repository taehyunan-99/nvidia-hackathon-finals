import concurrent.futures
import hashlib
from http.server import ThreadingHTTPServer
import json
from pathlib import Path
import tempfile
import threading
import time
import unittest
import urllib.error
import urllib.request
from types import SimpleNamespace

from bridge_api import Bridge, OpenShellRunner, Store, handler_for


class FakeRunner:
    def __init__(self):
        self.available = True
        self.calls = []

    def ready(self):
        return self.available

    def run(self, job_id, payload):
        self.calls.append(job_id)
        text = json.loads(payload)["text"]
        return "succeeded", {"text": text, "sha256": hashlib.sha256(text.encode()).hexdigest()}


class BridgeTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.store = Store(Path(self.temp.name) / "jobs.sqlite3")
        self.runner = FakeRunner()
        self.bridge = Bridge(self.store, self.runner, b"test-only-" + b"a" * 32)
        self.server = ThreadingHTTPServer(("127.0.0.1", 0), handler_for(self.bridge))
        self.thread = threading.Thread(target=self.server.serve_forever)
        self.thread.start()
        self.base = "http://127.0.0.1:" + str(self.server.server_port)

    def tearDown(self):
        self.bridge.stopping.set()
        self.server.shutdown()
        self.server.server_close()
        self.thread.join()
        self.temp.cleanup()

    def request(self, path, data=None, owner="aws-test", token=True, key="request-1"):
        headers = {"X-Job-Owner": owner, "Idempotency-Key": key,
                   "Content-Type": "application/json"}
        if token:
            headers["Authorization"] = "Bearer " + (self.bridge.token.decode() if token is True else token)
        req = urllib.request.Request(self.base + path, headers=headers,
                                     data=json.dumps(data).encode() if data is not None else None)
        try:
            response = urllib.request.urlopen(req, timeout=5)
        except urllib.error.HTTPError as exc:
            response = exc
        with response:
            return response.status, json.load(response)

    def test_no_auth_and_wrong_auth_rejected_without_work(self):
        for token in [False, "wrong"]:
            self.assertEqual(self.request("/jobs", {"text": "sample"}, token=token)[0], 401)
        self.assertIsNone(self.store.claim())

    def test_same_request_concurrent_and_disconnected_retry_runs_once(self):
        with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
            results = list(pool.map(lambda _: self.request("/jobs", {"text": "sample"}), range(8)))
        ids = {data["job_id"] for _, data in results}
        self.assertEqual(len(ids), 1)
        self.assertEqual(sum(code == 202 for code, _ in results), 1)
        worker = threading.Thread(target=self.bridge.work)
        worker.start()
        job_id = ids.pop()
        try:
            for _ in range(100):
                status, data = self.request("/jobs/" + job_id)
                if data["state"] == "succeeded":
                    break
                time.sleep(0.01)
            self.assertEqual(data["state"], "succeeded")
            self.runner.available = False
            self.assertEqual(self.request("/jobs", {"text": "sample"})[1]["job_id"], job_id)
            self.assertEqual(self.runner.calls, [job_id])
            self.assertEqual(self.request("/jobs", {"text": "new"}, key="new")[0], 503)
        finally:
            self.bridge.stopping.set()
            worker.join(5)

    def test_owner_and_conflict(self):
        _, data = self.request("/jobs", {"text": "sample"})
        self.assertEqual(self.request("/jobs/" + data["job_id"], owner="other")[0], 404)
        self.assertEqual(self.request("/jobs", {"text": "changed"})[0], 409)

    def test_input_cannot_select_command_image_policy_or_path(self):
        for data in [{"text": "sample", "command": "id"}, {"image": "evil"},
                     {"text": "a" * 513}, {"text": 42}, ["sample"], {"text": ""}]:
            self.assertEqual(self.request("/jobs", data)[0], 400)
        self.assertIsNone(self.store.claim())

    def test_restarted_running_job_held_unknown_without_reexecution(self):
        _, data = self.request("/jobs", {"text": "sample"})
        self.assertIsNotNone(self.store.claim())
        reopened = Store(self.store.path)
        reopened.recover()
        self.assertEqual(reopened.get("aws-test", data["job_id"])["state"], "unknown")
        self.assertIsNone(reopened.claim())
        self.assertEqual(self.request("/jobs", {"text": "sample"})[1]["job_id"], data["job_id"])

    def test_persisted_queue_and_trial_limit(self):
        for i in range(32):
            self.assertEqual(self.request("/jobs", {"text": "sample"}, key=str(i))[0], 202)
        self.assertEqual(self.request("/jobs", {"text": "sample"}, key="overflow")[0], 429)
        reopened = Store(self.store.path)
        self.assertIsNotNone(reopened.claim())


class RunnerTests(unittest.TestCase):
    def test_sandbox_name_fits_verified_openshell_limit(self):
        runner = OpenShellRunner("openshell", "test", "image", "policy")
        calls = []
        text = "sample"
        result = {"text": text, "sha256": hashlib.sha256(text.encode()).hexdigest()}

        def command(args, payload=None, timeout=30):
            calls.append(args)
            return SimpleNamespace(returncode=0, stdout=json.dumps(result))

        runner.command = command
        self.assertEqual(runner.run("aad9cdf5cd98445fb028f44686b36edc", json.dumps({"text": text})),
                         ("succeeded", result))
        name = calls[0][calls[0].index("--name") + 1]
        self.assertLessEqual(len(name), 19)
        self.assertEqual(calls[-1], ["sandbox", "stop", name])


if __name__ == "__main__":
    unittest.main()
