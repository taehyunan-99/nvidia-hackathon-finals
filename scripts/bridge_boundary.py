"""Operator-only check on Brev: pre-existing synthetic controls, then Landlock deny."""
import json
import os
import subprocess


def main():
    binary = os.environ["BRIDGE_OPENSHELL_BIN"]
    version = subprocess.run([binary, "--version"], capture_output=True, text=True, timeout=5)
    if version.returncode or version.stdout.strip() != "openshell 0.1.2":
        raise SystemExit("requires the verified OpenShell 0.1.2 deployment")
    image = os.environ["BRIDGE_IMAGE"]
    # Non-root identity and file permissions must allow access without OpenShell.
    existence = subprocess.run([
        "docker", "run", "--rm", "--network", "none", "--cap-drop", "ALL",
        "--security-opt", "no-new-privileges", "--label", "nvidia-finals-purpose=aws-brev-bridge",
        image, "python3", "-c",
        "import os; from pathlib import Path; "
        "assert os.getuid()==1000; "
        "assert all(Path('/hackathon/'+p+'/control.txt').is_file() "
        "and os.access('/hackathon/'+p+'/control.txt',os.R_OK) "
        "for p in ['restricted','secrets'])"
    ], capture_output=True, text=True, timeout=30)
    if existence.returncode:
        raise SystemExit("control existence/readability unverified")
    checked = subprocess.run([
        binary, "--gateway", os.environ["BRIDGE_GATEWAY"], "sandbox", "exec",
        "-n", os.environ["BRIDGE_BOUNDARY_SANDBOX"], "--no-tty", "--timeout", "10",
        "--", "python3", "/opt/bridge/worker.py", "boundary"
    ], capture_output=True, text=True, timeout=15)
    expected = {"restricted": "denied", "secrets": "denied"}
    if checked.returncode or json.loads(checked.stdout) != expected:
        raise SystemExit("sandbox deny unverified; forbidden content was not read")
    print(json.dumps({"controls_exist_and_readable": True, "sandbox_open_denied": expected}))


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, KeyError, subprocess.TimeoutExpired):
        raise SystemExit("boundary check unverified; raw output suppressed")
