"""Fixed test workload: stdin JSON -> allowed output file; no model/network."""
import errno
import hashlib
import json
import os
from pathlib import Path
import sys


OUTPUT = "/hackathon/output/result.json"


def boundary():
    # Image contains world-readable controls; never read or log their contents.
    outcomes = {}
    for name, path in [("restricted", "/hackathon/restricted/control.txt"),
                       ("secrets", "/hackathon/secrets/control.txt")]:
        try:
            fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW)
        except OSError as exc:
            outcomes[name] = "denied" if exc.errno in (errno.EACCES, errno.EPERM) else "inconclusive"
        else:
            os.close(fd)
            outcomes[name] = "not_denied"
    print(json.dumps(outcomes))
    return 0 if all(v == "denied" for v in outcomes.values()) else 1


def main():
    operation = sys.argv[1]
    if operation == "boundary":
        return boundary()
    if operation == "run":
        payload = json.loads(sys.stdin.buffer.read(4096))
        text = payload["text"]
        if set(payload) != {"text"} or not isinstance(text, str) or not 0 < len(text.encode()) <= 512:
            return 1
        # A real allow-read check precedes the output write.
        if Path("/hackathon/input/control.txt").read_text() != "PUBLIC_CONTROL\n":
            return 1
        result = {"text": text, "sha256": hashlib.sha256(text.encode()).hexdigest()}
        fd = os.open(OUTPUT, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
        with os.fdopen(fd, "w") as stream:
            json.dump(result, stream, ensure_ascii=False)
        return 0
    if operation == "result":
        fd = os.open(OUTPUT, os.O_RDONLY | os.O_NOFOLLOW)
        with os.fdopen(fd, "r") as stream:
            value = stream.read(4097)
        if len(value.encode()) > 4096:
            return 1
        print(value)
        return 0
    return 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (OSError, ValueError, KeyError, TypeError, IndexError):
        # Avoid payload, forbidden file content, or traceback leakage.
        sys.exit(1)
