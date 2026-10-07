"""AWS operator check: drop a POST response, kill the tunnel, retry the SAME key."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import socket
import subprocess
import time
import urllib.request


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--key", required=True)
    args = parser.parse_args()
    if not args.key.replace("-", "").isalnum() or len(args.key) > 64:
        raise SystemExit("invalid test key")
    token = Path(os.environ["BRIDGE_TOKEN_FILE"]).read_text().strip()
    body = json.dumps({"text": "bridge-check"}).encode()
    headers = {"Authorization": "Bearer " + token, "X-Job-Owner": "aws-trial",
               "Idempotency-Key": args.key, "Content-Type": "application/json"}
    raw = ("POST /jobs HTTP/1.1\r\nHost: 127.0.0.1\r\n" +
           "\r\n".join(k + ": " + v for k, v in headers.items()) +
           "\r\nContent-Length: " + str(len(body)) + "\r\nConnection: close\r\n\r\n").encode() + body
    with socket.create_connection(("127.0.0.1", 28080), timeout=10) as stream:
        stream.sendall(raw)
        # A response byte proves the server handled the POST. Discard all status,
        # body and job identity, rather than assuming sendall reached the server.
        if not stream.recv(1):
            raise SystemExit("first POST admission unverified")
    subprocess.run(["systemctl", "kill", "--kill-who=main", "-s", "KILL",
                    "bridge-tunnel.service"], check=True, capture_output=True)
    disconnected = False
    for _ in range(20):
        time.sleep(0.1)
        try:
            with socket.create_connection(("127.0.0.1", 28080), timeout=0.5):
                pass
        except OSError:
            disconnected = True
            break
    if not disconnected:
        raise SystemExit("tunnel disconnect not observed")

    def request(path, data=None):
        req = urllib.request.Request("http://127.0.0.1:28080" + path, headers=headers, data=data)
        with urllib.request.urlopen(req, timeout=5) as response:
            return response.status, json.load(response)

    recovered = None
    for _ in range(45):
        try:
            status, recovered = request("/jobs", body)
            break
        except (OSError, ValueError):
            time.sleep(1)
    if recovered is None or status != 200:
        raise SystemExit("lost response recovery did not return the prior job")
    job_id = recovered["job_id"]
    for _ in range(90):
        _, recovered = request("/jobs/" + job_id)
        if recovered["state"] in ["succeeded", "failed", "unknown"]:
            break
        time.sleep(1)
    if (recovered["state"] != "succeeded" or
            recovered["result"] != {"text": "bridge-check",
                                    "sha256": hashlib.sha256(b"bridge-check").hexdigest()}):
        raise SystemExit("recovered execution/result unverified")
    status, repeated = request("/jobs", body)
    if status != 200 or repeated["job_id"] != job_id:
        raise SystemExit("recovered retry did not preserve identity")
    print(json.dumps({"job_id": job_id, "state": "succeeded", "response_dropped": True,
                      "tunnel_disconnect_observed": True, "auto_recovered": True,
                      "same_key_same_job": True}))


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, KeyError, subprocess.CalledProcessError):
        raise SystemExit("recovery check unverified; retain the SAME key")
