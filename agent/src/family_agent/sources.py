"""Bounded public sample + official detail. No model-selected URL or credentials."""
import json
import re
import urllib.request
from datetime import datetime
from zoneinfo import ZoneInfo
from family_minimum.runtime import SAMPLE_URL, SERVICE, NoRedirect
from probe_family_sources import DETAIL_BASE, PageText
from .normalize import add_facts


def now():
    return datetime.now(ZoneInfo('Asia/Seoul')).isoformat()


def bounded_fetch(url):
    request = urllib.request.Request(url, headers={'User-Agent': 'FamilyCultureAgent/1.0'})
    with urllib.request.build_opener(NoRedirect()).open(request, timeout=25) as response:
        raw = response.read(2_000_001)
        if len(raw) > 2_000_000: raise ValueError('source_response_too_large')
        return raw, response.headers.get_content_charset() or 'utf-8'


class SeoulSources:
    def __init__(self, request_id, revision, conditions, fetcher=bounded_fetch):
        self.request_id, self.revision, self.conditions = request_id, revision, conditions
        self.fetcher, self.rows, self.calls = fetcher, {}, 0
        self.search_result = None

    def identity(self):
        return {'request_id': self.request_id, 'conditions_revision': self.revision}

    def search(self, cursor=None):
        if cursor is not None:
            raise ValueError('sample_has_no_cursor')
        if self.search_result is not None:
            return self.search_result
        self.calls += 1
        result = {**self.identity(), 'status': 'error', 'candidate_ids': [], 'next_cursor': None,
            'scope': {'district': self.conditions['district'], 'interests': self.conditions['interests'],
                'coverage': 'sample', 'pages_read': 1, 'limit_reached': True}, 'error_code': None}
        try:
            raw, _ = self.fetcher(SAMPLE_URL)
            body = json.loads(raw).get(SERVICE, {})
            if body.get('RESULT', {}).get('CODE') not in ('INFO-000', 'INFO-200'):
                raise ValueError('invalid_response')
            rows = body.get('row', [])
            if not isinstance(rows, list) or len(rows) > 5:
                raise ValueError('invalid_response')
            for row in rows:
                if not re.fullmatch(r'S\d{18}', row.get('SVCID', '')) or not isinstance(row.get('SVCNM'), str):
                    raise ValueError('invalid_record')
                # Culture services only; user interest is interpreted from source text by the agent.
                if row.get('MAXCLASSNM') != '문화체험':
                    continue
                district = self.conditions['district']
                if district != 'all' and {'jongno': '종로구', 'jung': '중구'}[district] not in row.get('AREANM', ''):
                    continue
                self.rows[row['SVCID']] = row
            result.update(status='ok' if self.rows else 'empty', candidate_ids=list(self.rows))
        except (OSError, ValueError, TypeError, AttributeError):
            self.rows.clear()
            result.update(error_code='source_unavailable_or_invalid')
        self.search_result = result
        return result

    def summaries(self):
        return [{'candidate_id': cid, 'title': row['SVCNM'], 'category': row.get('MINCLASSNM'),
                 'target_text': row.get('USETGTINFO'), 'booking_text': row.get('SVCSTATNM')}
                for cid, row in self.rows.items()]

    def detail(self, candidate_id, official=False):
        row = self.rows[candidate_id]
        source_id = ('official:' if official else 'api:') + candidate_id
        result = {**self.identity(), 'candidate_id': candidate_id, 'source_id': source_id,
            'status': 'ok', 'evidence': [], 'facts': [], 'error_code': None}
        stamp = now()
        def evidence(quote, locator):
            eid = source_id + ':e' + str(len(result['evidence']))
            result['evidence'].append({'id': eid, 'source_id': source_id, 'candidate_id': candidate_id,
                'quote': quote, 'locator': locator, 'retrieved_at': stamp})
            return eid
        def fact(field, value, quote, locator, applies='session', scope='applicable'):
            result['facts'].append({'id': source_id + ':f' + str(len(result['facts'])),
                'evidence_ids': [evidence(quote, locator)], 'applies_to': applies,
                'scope_match': scope, 'field': field, 'value': value})
        if official:
            self.calls += 1
            try:
                raw, encoding = self.fetcher(DETAIL_BASE + candidate_id)
                parser = PageText(); parser.feed(raw.decode(encoding))
                text = '\n'.join(parser.parts)
                if '이용기간' not in text or '접수기간' not in text:
                    raise ValueError('invalid_detail')
                # Full text remains untrusted; fixed excerpts are data, never instructions.
                relevant = [part for part in parser.parts if any(word in part for word in
                    ('초등', '보호자', '동반', '일요일', '온라인', '연령', '예약마감', '접수중'))]
                for i, quote in enumerate(relevant[:12]):
                    evidence(quote[:500], 'official-text:' + str(i))
            except (OSError, ValueError, UnicodeError, LookupError):
                result.update(status='error', error_code='official_source_unavailable_or_invalid')
            add_facts(result, row)
            return result
        for field in ('SVCNM', 'USETGTINFO', 'SVCSTATNM'):
            if row.get(field): evidence(str(row[field]), 'API.' + field)
        state = {'접수중': 'open', '접수종료': 'closed', '예약마감': 'full', '취소': 'cancelled'}.get(row.get('SVCSTATNM'))
        if state: fact('booking_status', state, row['SVCSTATNM'], 'API.SVCSTATNM')
        for field, start, end in [('operating_period', 'SVCOPNBGNDT', 'SVCOPNENDDT'),
                                  ('booking_period', 'RCPTBGNDT', 'RCPTENDDT')]:
            try:
                a, b = (datetime.fromisoformat(row[k]).replace(tzinfo=ZoneInfo('Asia/Seoul')) for k in (start, end))
                if a > b: continue
                value = {'start': a.date().isoformat(), 'end': b.date().isoformat()} if field == 'operating_period' else {'start': a.isoformat(), 'end': b.isoformat()}
                fact(field, value, row[start] + ' ~ ' + row[end], 'API.' + start + '+' + end)
            except (ValueError, TypeError, KeyError): pass
        parser = PageText(); parser.feed(row.get('DTLCONT') or '')
        for i, quote in enumerate(parser.parts[:12]):
            evidence(quote[:500], 'API.DTLCONT.text:' + str(i))
        add_facts(result, row)
        return result

    def card(self, candidate_id):
        row = self.rows[candidate_id]
        coordinates = None
        try:
            latitude, longitude = float(row['Y']), float(row['X'])
            if 33 <= latitude <= 39 and 124 <= longitude <= 132:
                coordinates = {'latitude': latitude, 'longitude': longitude}
        except (KeyError, ValueError, TypeError): pass
        return {'id': candidate_id, 'coordinates': coordinates, 'title': row['SVCNM'], 'place': row.get('PLACENM', ''),
            'district': row.get('AREANM', ''), 'booking_text': row.get('SVCSTATNM', ''),
            'official_url': DETAIL_BASE + candidate_id, 'operating_start': row.get('SVCOPNBGNDT'),
            'operating_end': row.get('SVCOPNENDDT'), 'cost': row.get('PAYATNM', '미확인')}
