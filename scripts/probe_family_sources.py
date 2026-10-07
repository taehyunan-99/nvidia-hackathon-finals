"""Read-only Seoul sample/authenticated and official detail checks; network is opt-in."""
import argparse
from datetime import datetime, timezone, timedelta
import hashlib
from html.parser import HTMLParser
import json
import os
from pathlib import Path
import re
import shlex
import urllib.error
import urllib.request

SERVICE = 'tvYeyakCOllect'
SAMPLE_URL = f'http://openapi.seoul.go.kr:8088/sample/json/{SERVICE}/1/5/'
HTTPS_BASE = 'https://openapi.seoul.go.kr:443'
HTTP_BASE = 'http://openapi.seoul.go.kr:8088'
ROOT = Path(__file__).resolve().parents[1]
DETAIL_BASE = 'https://yeyak.seoul.go.kr/web/reservation/selectReservView.do?rsv_svc_id='
SAMPLE_IDS = ['S260919140130025643', 'S260226152742370024', 'S260226153543290596']
MAX_BYTES = 2_000_000


def source_key(path=ROOT / '.env'):
    name = 'SEOUL_OPEN_DATA_API_KEY'
    if name in os.environ:
        value = os.environ[name].strip()
    else:
        value = ''
        if path.is_file():
            for line in path.read_text(encoding='utf-8-sig').splitlines():
                key, sep, raw = line.partition('=')
                if sep and key.strip() == name:
                    parsed = shlex.split(raw, comments=True)
                    value = parsed[0] if len(parsed) == 1 else ''
    if not re.fullmatch(r'[A-Za-z0-9]+', value) or value == 'sample':
        raise ValueError('A valid SEOUL_OPEN_DATA_API_KEY is required')
    return value


class PageText(HTMLParser):
    def __init__(self):
        super().__init__()
        self.parts = []
        self.hidden = 0

    def handle_starttag(self, tag, attrs):
        if tag in {'script', 'style'}:
            self.hidden += 1

    def handle_endtag(self, tag):
        if tag in {'script', 'style'}:
            self.hidden = max(0, self.hidden - 1)

    def handle_data(self, data):
        if not self.hidden and data.strip():
            self.parts.append(re.sub(r'\s+', ' ', data.strip()))


class SameHostRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        from urllib.parse import urlsplit
        previous, target = urlsplit(req.full_url), urlsplit(newurl)
        if target.netloc != previous.netloc or target.scheme != previous.scheme:
            raise ValueError('Unexpected redirect')
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def fetch(url):
    request = urllib.request.Request(url, headers={'User-Agent': 'FamilyCulturePreflight/1.0'})
    opener = urllib.request.build_opener(SameHostRedirect())
    with opener.open(request, timeout=25) as response:
        raw = response.read(MAX_BYTES + 1)
        if len(raw) > MAX_BYTES:
            raise ValueError('Response exceeds limit')
        return raw, response.headers.get_content_charset() or 'utf-8'


def inspect_api(raw):
    data = json.loads(raw)
    body = data.get(SERVICE, {})
    code = body.get('RESULT', data.get('RESULT', {})).get('CODE')
    rows = body.get('row', [])
    empty = (code in {'INFO-000', 'INFO-200'} and isinstance(rows, list) and not rows
             and (code == 'INFO-200' or 'row' in body))
    valid = code == 'INFO-000' and isinstance(rows, list) and bool(rows)
    if valid:
        valid = all(isinstance(row, dict) and row.get('SVCID') and row.get('SVCNM') for row in rows)
    fields = ['SVCID', 'SVCNM', 'MAXCLASSNM', 'MINCLASSNM', 'SVCSTATNM',
              'USETGTINFO', 'SVCOPNBGNDT', 'SVCOPNENDDT', 'RCPTBGNDT', 'RCPTENDDT']
    return {'status': 'ok' if valid else 'empty' if empty else 'invalid_response', 'api_code': code,
            'rows': len(rows) if isinstance(rows, list) else None,
            'total_services': body.get('list_total_count'),
            'samples': [{field: row.get(field) for field in fields} for row in rows[:3]] if valid else [],
            'has_detail_html': any(bool(row.get('DTLCONT')) for row in rows) if valid else False}


def inspect_detail(raw, encoding):
    page = raw.decode(encoding)
    parser = PageText()
    parser.feed(page)
    text = '\n'.join(parser.parts)
    markers = ['서비스대상', '이용대상', '이용기간', '접수기간', '예약마감', '접수중',
               '초등', '보호자', '미취학', '동반', '일요일', '온라인']
    excerpts = [line[:350] for line in parser.parts if any(marker in line for marker in markers)]
    detail_present = '이용기간' in text and '접수기간' in text
    return {'status': 'ok' if detail_present else 'detail_unverified',
            'condition_excerpts': excerpts[:16],
            'bytes': len(raw), 'sha256': hashlib.sha256(raw).hexdigest()}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--live', action='store_true')
    parser.add_argument('--authenticated', action='store_true', help='Read the Seoul key from environment or local .env')
    parser.add_argument('--api-transport', choices=['http', 'https'], help='Default: HTTP sample, HTTPS authenticated')
    parser.add_argument('--allow-http-key', action='store_true', help='Explicitly permit the documented plaintext key transport')
    parser.add_argument('--output', type=Path)
    parser.add_argument('--service-id', action='append')
    args = parser.parse_args()
    transport = args.api_transport or ('https' if args.authenticated else 'http')
    if args.allow_http_key and (not args.authenticated or transport != 'http'):
        parser.error('--allow-http-key requires --authenticated --api-transport http')
    if args.authenticated and transport == 'http' and not args.allow_http_key:
        parser.error('Authenticated HTTP requires explicit --allow-http-key; HTTPS is the default')
    ids = args.service_id or SAMPLE_IDS
    if len(ids) > 3 or any(not re.fullmatch(r'S\d{18}', item) for item in ids):
        parser.error('Provide at most three official service IDs')
    if not args.live:
        print(json.dumps({'mode': 'dry-run', 'http_requests': 0, 'sample_key_only': not args.authenticated,
                          'api_transport': transport,
                          'planned_requests': 1 + len(ids)}))
        return
    secret = ''
    if args.authenticated:
        try:
            secret = source_key()
        except (OSError, ValueError):
            parser.error('Unable to load a valid SEOUL_OPEN_DATA_API_KEY')
    api_base = HTTPS_BASE if transport == 'https' else HTTP_BASE
    api_url = f'{api_base}/{secret or "sample"}/json/{SERVICE}/1/5/'
    if args.output and args.output.exists():
        parser.error('Output exists; choose a fresh directory')
    if args.output:
        args.output.mkdir(parents=True)
    result = {'mode': 'live', 'execution_boundary': 'development_host',
              'queried_at': datetime.now(timezone(timedelta(hours=9))).isoformat(),
              'sample_key_only': not args.authenticated, 'api_transport': transport,
              'http_requests': 0, 'sources': []}
    checks = [('api', api_url)] + [(item, DETAIL_BASE + item) for item in ids]
    for name, url in checks:
        result['http_requests'] += 1
        item = {'id': name, 'url': url.replace(secret, '[redacted]') if secret else url}
        try:
            raw, encoding = fetch(url)
            if secret:
                raw = raw.replace(secret.encode('ascii'), b'[redacted]')
            item.update(inspect_api(raw) if name == 'api' else inspect_detail(raw, encoding))
            if args.output:
                suffix = '.json' if name == 'api' else '.html'
                (args.output / (name + suffix)).write_bytes(raw)
        except urllib.error.HTTPError as exc:
            item.update(status='http_error', http_status=exc.code)
        except (OSError, ValueError, LookupError, TypeError, AttributeError):
            item.update(status='unavailable_or_invalid_response')
        result['sources'].append(item)
    if args.output:
        (args.output / 'observations.json').write_text(
            json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'mode': 'live', 'sample_key_only': not args.authenticated,
                      'api_transport': transport,
                      'http_requests': result['http_requests'],
                      'sources': [{key: item[key] for key in ['id', 'status', 'api_code', 'rows'] if key in item}
                                  for item in result['sources']]}, ensure_ascii=False))
    if any(item['status'] not in {'ok', 'empty'} for item in result['sources']):
        raise SystemExit(1)


if __name__ == '__main__':
    main()
