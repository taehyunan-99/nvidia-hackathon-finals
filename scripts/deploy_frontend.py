#!/usr/bin/env python3
"""Explicit manual Docker deployment; no Git or background deployment trigger."""
import argparse
import json
import os
from pathlib import Path
import secrets
import shlex
import subprocess
import tempfile
import time

ROOT = Path(__file__).resolve().parents[1]
STATE = ROOT / "runs/duru-deployment.json"


def run(args, **kwargs):
    return subprocess.run(args, check=True, **kwargs)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--api-origin", help="HTTPS hostname for the live API origin")
    parser.add_argument("--init", action="store_true", help="Connect existing CloudFront to Duru on first deployment")
    parser.add_argument("--ssh-key", required=True)
    parser.add_argument("--known-hosts", required=True)
    parser.add_argument("--host-key-alias", required=True)
    parser.add_argument("--profile", default="her2-dev")
    parser.add_argument("--region", default="ap-northeast-2")
    args = parser.parse_args()

    def aws(*command):
        result = run(["aws", "--profile", args.profile, "--region", args.region, *command,
                      "--output", "json"], capture_output=True, text=True)
        return json.loads(result.stdout) if result.stdout.strip() else {}

    def save():
        STATE.parent.mkdir(parents=True, exist_ok=True)
        fd = os.open(STATE, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
        with os.fdopen(fd, "w") as stream:
            json.dump(state, stream, indent=2)

    if STATE.exists():
        state = json.loads(STATE.read_text())
    else:
        if not args.init:
            parser.error("First deployment requires --init; local deployment state is missing")
        state = {"instance": "i-0a6dced25ec8152c1", "token": secrets.token_hex(32)}
        save()
    instance = aws("ec2", "describe-instances", "--instance-ids", state["instance"])["Reservations"][0]["Instances"][0]
    if instance["State"]["Name"] != "running":
        parser.error("Existing EC2 must be running; this command does not create/start instances")
    host = instance["PublicIpAddress"]
    ssh_options = ["-i", str(Path(args.ssh_key).resolve()), "-o", "BatchMode=yes", "-o", "IdentitiesOnly=yes",
                   "-o", "StrictHostKeyChecking=yes", "-o", f"HostKeyAlias={args.host_key_alias}",
                   "-o", f"UserKnownHostsFile={Path(args.known_hosts).resolve()}", "-o", "ConnectTimeout=10"]
    ssh = ["ssh", *ssh_options, f"ec2-user@{host}"]
    run([*ssh, "sudo docker version --format '{{.Server.Version}}'"])
    image = f"duru-frontend:{time.time_ns()}"
    run(["docker", "build", "--platform", "linux/amd64", "-f", "frontend/Dockerfile", "-t", image, "."], cwd=ROOT)
    with tempfile.TemporaryDirectory(prefix="duru-deploy-") as directory:
        archive = Path(directory) / "image.tar"
        run(["docker", "save", "-o", str(archive), image])
        env = Path(directory) / "origin.env"
        map_values = dict(line.split("=", 1) for line in (ROOT / "frontend/.env.local").read_text().splitlines()
                          if line.strip() and not line.startswith("#") and "=" in line)
        map_id = map_values.get("NAVER_MAP_CLIENT_ID", "").strip().strip("\"'")
        if not map_id or not map_id.isalnum(): parser.error("Missing or invalid NAVER_MAP_CLIENT_ID")
        env.write_text(f"DURU_ORIGIN_TOKEN={state['token']}\nNAVER_MAP_CLIENT_ID={map_id}\n")
        env.chmod(0o600)
        run([*ssh, "mkdir -p ~/duru-upload && chmod 700 ~/duru-upload"])
        run(["scp", *ssh_options, str(archive), str(env), f"ec2-user@{host}:duru-upload/"])
    remote = r'''set -eu
sudo install -d -m 700 /opt/duru
sudo install -m 600 ~/duru-upload/origin.env /opt/duru/origin.env
sudo docker load -i ~/duru-upload/image.tar >/dev/null
rm ~/duru-upload/image.tar ~/duru-upload/origin.env
sudo docker network inspect duru-edge >/dev/null 2>&1 || sudo docker network create duru-edge >/dev/null
if ! sudo docker network inspect duru-edge --format '{{range .Containers}}{{.Name}} {{end}}' | grep -qw bio3-web-1; then
    sudo docker network connect duru-edge bio3-web-1
fi
image=IMAGE
sudo docker run -d --name duru-candidate --add-host host.docker.internal:host-gateway --env-file /opt/duru/origin.env -p 127.0.0.1:18081:80 "$image" >/dev/null
trap 'sudo docker rm -f duru-candidate >/dev/null 2>&1 || true' EXIT
sleep 2
curl -fsS http://127.0.0.1:18081/healthz >/dev/null
sudo docker rm -f duru-candidate >/dev/null
trap - EXIT
if sudo docker container inspect duru-frontend >/dev/null 2>&1; then
    sudo docker rm -f duru-rollback >/dev/null 2>&1 || true
    sudo docker stop duru-frontend >/dev/null
    sudo docker rename duru-frontend duru-rollback
fi
sudo docker run -d --name duru-frontend --add-host host.docker.internal:host-gateway --restart unless-stopped --network duru-edge --env-file /opt/duru/origin.env -p 127.0.0.1:8080:80 "$image" >/dev/null
sleep 2
if ! curl -fsS http://127.0.0.1:8080/healthz >/dev/null; then
    sudo docker rm -f duru-frontend >/dev/null
    if sudo docker container inspect duru-rollback >/dev/null 2>&1; then
        sudo docker rename duru-rollback duru-frontend
        sudo docker start duru-frontend >/dev/null
    fi
    exit 1
fi
sudo python3 - <<'PY'
import json, pathlib, subprocess
mounts = json.loads(subprocess.check_output(['docker', 'inspect', 'bio3-web-1', '--format', '{{json .Mounts}}']))
source = pathlib.Path(next(m['Source'] for m in mounts if m['Destination'] == '/etc/caddy/Caddyfile'))
text = source.read_text()
backup = pathlib.Path('/opt/duru/original.Caddyfile')
if not backup.exists():
    backup.write_text(text)
    backup.chmod(0o600)
if '# Duru frontend route' not in text:
    token = pathlib.Path('/opt/duru/origin.env').read_text().strip().split('=', 1)[1]
    route = '\n    # Duru frontend route\n    @duru header X-Duru-Origin ' + token + '\n    handle @duru {\n        reverse_proxy duru-frontend:80\n    }\n'
    text = text.replace(':80 {', ':80 {' + route, 1)
    candidate = pathlib.Path('/opt/duru/proxy.caddy')
    candidate.write_text(text)
    candidate.chmod(0o600)
    subprocess.run(['docker', 'cp', str(candidate), 'bio3-web-1:/tmp/duru.caddy'], check=True, stdout=subprocess.DEVNULL)
    subprocess.run(['docker', 'exec', 'bio3-web-1', 'caddy', 'validate', '--config', '/tmp/duru.caddy', '--adapter', 'caddyfile'], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    source.write_text(text)
    subprocess.run(['docker', 'exec', 'bio3-web-1', 'caddy', 'reload', '--config', '/etc/caddy/Caddyfile', '--adapter', 'caddyfile'], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
PY
sudo docker ps --filter name=duru-frontend --format '{{.Names}} {{.Status}}'
'''.replace("IMAGE", shlex.quote(image))
    run([*ssh, "bash -s"], input=remote, text=True)

    if args.init:
        state.update(distribution="E39KLZ3QCHMW5G", domain="d25wpps17lj0dn.cloudfront.net")
        current = aws("cloudfront", "get-distribution-config", "--id", state["distribution"])
        config = current["DistributionConfig"]
        if "previous_cloudfront" not in state:
            state["previous_cloudfront"] = json.loads(json.dumps(config))
            save()
        origin = {"Id": "duru-ec2", "DomainName": instance["PublicDnsName"], "OriginPath": "",
                  "CustomHeaders": {"Quantity": 1, "Items": [{"HeaderName": "X-Duru-Origin", "HeaderValue": state["token"]}]},
                  "CustomOriginConfig": {"HTTPPort": 80, "HTTPSPort": 443, "OriginProtocolPolicy": "http-only",
                                         "OriginSslProtocols": {"Quantity": 1, "Items": ["TLSv1.2"]},
                                         "OriginReadTimeout": 30, "OriginKeepaliveTimeout": 5}}
        config["Origins"]["Items"] = [o for o in config["Origins"]["Items"] if o["Id"] != "duru-ec2"] + [origin]
        config["Origins"]["Quantity"] = len(config["Origins"]["Items"])
        config.update(Enabled=True, DefaultRootObject="index.html", Comment="Duru frontend - explicit manual Docker deployment")
        behavior = config["DefaultCacheBehavior"]
        behavior.update(TargetOriginId="duru-ec2", ViewerProtocolPolicy="redirect-to-https",
                        AllowedMethods={"Quantity": 2, "Items": ["GET", "HEAD"], "CachedMethods": {"Quantity": 2, "Items": ["GET", "HEAD"]}},
                        CachePolicyId="4135ea2d-6df8-44a3-9df3-4b5a84be39ad", Compress=True)
        behavior.pop("OriginRequestPolicyId", None)
        aws("cloudfront", "update-distribution", "--id", state["distribution"], "--if-match", current["ETag"],
            "--distribution-config", json.dumps(config))
        save()
    if "distribution" not in state:
        parser.error("Container deployed; rerun with --init to finish CloudFront setup")
    if args.api_origin:
        current = aws("cloudfront", "get-distribution-config", "--id", state["distribution"])
        config = current["DistributionConfig"]
        api_origin = {"Id": "duru-api", "DomainName": args.api_origin, "OriginPath": "",
            "CustomHeaders": {"Quantity": 1, "Items": [{"HeaderName": "X-Duru-Origin", "HeaderValue": state["token"]}]},
            "CustomOriginConfig": {"HTTPPort": 80, "HTTPSPort": 443, "OriginProtocolPolicy": "https-only",
                "OriginSslProtocols": {"Quantity": 1, "Items": ["TLSv1.2"]}, "OriginReadTimeout": 60, "OriginKeepaliveTimeout": 5}}
        config["Origins"]["Items"] = [o for o in config["Origins"]["Items"] if o["Id"] != "duru-api"] + [api_origin]
        config["Origins"]["Quantity"] = len(config["Origins"]["Items"])
        behavior = {**config["DefaultCacheBehavior"], "PathPattern": "/api/*", "TargetOriginId": "duru-api", "ViewerProtocolPolicy": "https-only",
            "SmoothStreaming": False, "AllowedMethods": {"Quantity": 7, "Items": ["GET", "HEAD", "OPTIONS", "PUT", "PATCH", "POST", "DELETE"],
                "CachedMethods": {"Quantity": 2, "Items": ["GET", "HEAD"]}}, "Compress": True,
            "CachePolicyId": "4135ea2d-6df8-44a3-9df3-4b5a84be39ad",
            "OriginRequestPolicyId": "b689b0a8-53d0-40ab-baf2-68738e2966ac",
            "TrustedSigners": {"Enabled": False, "Quantity": 0}, "TrustedKeyGroups": {"Enabled": False, "Quantity": 0}}
        items = [b for b in config.get("CacheBehaviors", {}).get("Items", []) if b["PathPattern"] != "/api/*"]
        config["CacheBehaviors"] = {"Quantity": len(items)+1, "Items": [behavior]+items}
        aws("cloudfront", "update-distribution", "--id", state["distribution"], "--if-match", current["ETag"],
            "--distribution-config", json.dumps(config))
        state["api_origin"] = args.api_origin
        save()
    current = aws("cloudfront", "get-distribution-config", "--id", state["distribution"])
    origin = next(o for o in current["DistributionConfig"]["Origins"]["Items"] if o["Id"] == "duru-ec2")
    if origin["DomainName"] != instance["PublicDnsName"]:
        origin["DomainName"] = instance["PublicDnsName"]
        aws("cloudfront", "update-distribution", "--id", state["distribution"], "--if-match", current["ETag"],
            "--distribution-config", json.dumps(current["DistributionConfig"]))
    aws("cloudfront", "create-invalidation", "--distribution-id", state["distribution"], "--paths", "/*")
    state["image"] = image
    save()
    print(f"Manual deployment submitted: https://{state['domain']}/ (verify after CloudFront propagation)")


if __name__ == "__main__":
    try:
        main()
    except subprocess.CalledProcessError as error:
        # AWS config arguments can contain origin secrets; never print error.cmd.
        if error.stderr:
            message = error.stderr.split("Encoded authorization failure message:", 1)[0]
            if STATE.exists():
                message = message.replace(json.loads(STATE.read_text())["token"], "[redacted]")
            print(message.strip()[:1500])
        raise SystemExit(f"Deployment step failed (exit {error.returncode}); existing deployment state retained") from None
