"""Small, conservative source normalizer; ambiguous clauses stay as evidence."""
import re

GRADES = ['preschool', '1', '2', '3', '4', '5', '6', 'teen']


def add_facts(result, row):
    source = result['source_id']
    def add(field, value, e, applies='session', scope='applicable'):
        result['facts'].append({'id': source + ':f' + str(len(result['facts'])), 'evidence_ids': [e['id']],
            'applies_to': applies, 'scope_match': scope, 'field': field, 'value': value})
    for e in result['evidence']:
        quote = e['quote']
        # Parse exact structured target only, not a incidental body mention.
        if e['locator'] == 'API.USETGTINFO':
            target = quote.strip()
            if target in ('제한없음', '제한 없음', '누구나'):
                add('allowed_age_range', {'minimum': 0, 'maximum': None}, e, 'child')
                add('allowed_grades', GRADES, e, 'child')
            elif re.fullmatch(r'유아\(만\s*5세\s*이상\),?\s*초등학생', target):
                add('allowed_age_range', {'minimum': 5, 'maximum': None}, e, 'child')
                add('allowed_grades', GRADES[:-1], e, 'child')
            elif target == '초등학생':
                add('allowed_grades', [str(i) for i in range(1, 7)], e, 'child')
        if e['locator'] == 'API.SVCNM':
            weekdays = {'월': 1, '화': 2, '수': 3, '목': 4, '금': 5, '토': 6, '일': 7}
            match = re.search(r'매주\s*([월화수목금토일])(?:요일|\s*[)\d])', quote)
            if match: add('weekdays', [weekdays[match[1]]], e)
            tags = []
            if re.search(r'전시해설|역사|문화유산|가옥', quote): tags.append('history')
            if re.search(r'공예|솟대|장승|한지|전통.*만들', quote): tags.append('craft')
            if re.search(r'국악|전통.*공연|장구|판소리', quote): tags.append('performance')
            if tags: add('interest_tags', tags, e)
            if '온라인교육' in quote: add('delivery_mode', 'online', e)
        # Restrictions in paragraphs can refer to another session or an example.
        # Until their scope is confirmed, preserve them as unresolved, never as a pass.
        if 'DTLCONT' in e['locator'] or 'official-text' in e['locator']:
            if re.search(r'(?:대상|참여|신청).{0,30}초등|초등.{0,20}(?:대상|한정|만 참여)', quote):
                add('allowed_grades', [str(i) for i in range(1, 7)], e, 'child', 'unresolved')
            if re.search(r'연령.{0,10}제한\s*없', quote):
                add('allowed_age_range', {'minimum': 0, 'maximum': None}, e, 'child', 'unresolved')
            if re.search(r'보호자\s*(?:1인|1명)\s*(?:동반|참여)', quote):
                add('guardian_min', 1, e, 'family', 'unresolved')
