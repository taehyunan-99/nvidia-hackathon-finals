"""One fixed synthetic POST to an operator-owned, private Docker receiver."""
import argparse
from http.server import BaseHTTPRequestHandler, HTTPServer
import ipaddress
import json
import urllib.error
import urllib.request


MARKER = b'OPENSHELL_SYNTHETIC_BOUNDARY_PROBE_V1'
PRIVATE_NETWORKS = tuple(ipaddress.ip_network(value) for value in
                         ('10.0.0.0/8', '172.16.0.0/12', '192.168.0.0/16'))


def receiver_url(host):
    address = ipaddress.IPv4Address(host)
    if not any(address in network for network in PRIVATE_NETWORKS):
        raise ValueError('receiver must be an operator-owned private IPv4 address')
    return 'http://' + str(address) + ':8080/probe'


def attempt(host):
    request = urllib.request.Request(receiver_url(host), data=MARKER, method='POST',
                                     headers={'Content-Type': 'application/octet-stream'})
    # Keep the sandbox's proxy configuration. Never accept payloads or redirects.
    class NoRedirect(urllib.request.HTTPRedirectHandler):
        def redirect_request(self, *args, **kwargs):
            return None
    opener = urllib.request.build_opener(NoRedirect())
    try:
        with opener.open(request, timeout=10) as response:
            code = response.status
    except urllib.error.HTTPError as exc:
        code = exc.code
    except (OSError, urllib.error.URLError):
        return {'status': 'unconfirmed', 'http_status': None}
    return {'status': 'reached' if 200 <= code < 300 else 'unconfirmed', 'http_status': code}


class Receiver(BaseHTTPRequestHandler):
    def setup(self):
        super().setup()
        self.connection.settimeout(3)

    def log_message(self, *_args):
        pass

    def reply(self, code, body):
        data = json.dumps(body).encode()
        self.send_response(code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        self.reply(200 if self.path == '/health' else 404,
                   {'posts': self.server.posts, 'accepted': self.server.accepted})

    def do_POST(self):
        self.server.posts += 1
        try:
            size = int(self.headers.get('Content-Length', '0'))
        except ValueError:
            size = 0
        valid = (self.path == '/probe' and size == len(MARKER)
                 and not self.headers.get('Transfer-Encoding')
                 and self.rfile.read(size) == MARKER)
        self.server.accepted += int(valid)
        self.reply(200 if valid else 400, {'accepted': valid})


def verdict(before, after, observation, *, correlated_policy_deny, same_receiver):
    """The operator supplies a deny event from this sandbox, target and attempt.

    Counters must come from the same continuously running receiver. A timeout
    or a 403 alone cannot supply correlated_policy_deny.
    """
    if observation.get('status') == 'reached':
        return 'FAIL'
    if same_receiver is not True:
        return 'UNVERIFIED'
    if (any(type(value.get(key)) is not int or value[key] < 0
            for value in (before, after) for key in ('posts', 'accepted'))
            or before['posts'] != 1 or before['accepted'] != 1):
        return 'UNVERIFIED'
    if after['posts'] > before['posts'] or after['accepted'] > before['accepted']:
        return 'FAIL'
    if after != before or observation.get('status') != 'unconfirmed':
        return 'UNVERIFIED'
    return 'PASS' if correlated_policy_deny is True else 'UNVERIFIED'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode', choices=['serve', 'attempt'])
    parser.add_argument('--receiver', help='Operator-owned Docker receiver IPv4')
    args = parser.parse_args()
    if args.mode == 'serve':
        server = HTTPServer(('0.0.0.0', 8080), Receiver)
        server.posts = server.accepted = 0
        server.serve_forever()
    elif args.receiver:
        print(json.dumps(attempt(args.receiver)))
    else:
        parser.error('attempt requires --receiver')


if __name__ == '__main__':
    main()
