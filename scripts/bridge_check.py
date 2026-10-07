"""Run on AWS after the server-owned SSH tunnel is active; no credentials printed."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import time
import urllib.error
import urllib.parse
import urllib.request


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", default="http://127.0.0.1:28080")
    parser.add_argument("--key", required=True, help="Keep the SAME key after a disconnect")
    args = parser.parse_args()
    parsed = urllib.parse.urlparse(args.url)
    if parsed.scheme != "http" or parsed.hostname != "127.0.0.1" or parsed.path:
        raise SystemExit("trial client requires the local SSH tunnel endpoint")
    token = Path(os.environ["BRIDGE_TOKEN_FILE"]).read_text().strip()
    expected = {"text": "bridge-check", "sha256": hashlib.sha256(b"bridge-check").hexdigest()}

    def request(path, data=None, auth=token):
        headers = {"X-Job-Owner": "aws-trial", "Idempotency-Key": args.key,
                   "Content-Type": "application/json"}
        if auth is not None:
            headers["Authorization"] = "Bearer " + auth
        req = urllib.request.Request(args.url + path, headers=headers,
                                     data=json.dumps(data).encode() if data is not None else None)
        try:
            response = urllib.request.urlopen(req, timeout=10)
        except urllib.error.HTTPError as exc:
            response = exc
        with response:
            return response.status, json.load(response)

    for auth in [None, "invalid-test-token"]:
        status, _ = request("/jobs", {"text": "bridge-check"}, auth)
        if status != 401:
            raise SystemExit("authentication rejection check failed")
    status, job = request("/jobs", {"text": "bridge-check"})
    if status not in (200, 202):
        raise SystemExit("job admission failed")
    job_id = job["job_id"]
    for _ in range(120):
        status, job = request("/jobs/" + job_id)
        if status != 200:
            raise SystemExit("job lookup failed; resume with the same key")
        if job["state"] in ["succeeded", "failed", "unknown"]:
            break
        time.sleep(1)
    if job["state"] != "succeeded" or job["result"] != expected:
        raise SystemExit("execution not verified; resume with the same key")
    status, repeated = request("/jobs", {"text": "bridge-check"})
    if status != 200 or repeated["job_id"] != job_id:
        raise SystemExit("idempotent retry check failed")
    print(json.dumps({"job_id": job_id, "state": "succeeded", "auth_rejected": True,
                      "same_key_same_job": True, "result_verified": True}))


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, KeyError):
        raise SystemExit("connection/result unverified; resume with the same key")
