"""Validate local documentation, catalog coverage, guide imports and skill pairs."""
from pathlib import Path
import json
import re
from urllib.parse import unquote
from sync_guides import guide_case_errors, reference_content
R=Path(__file__).resolve().parents[1]
EXCLUDED={'.git','.venv','node_modules','__pycache__','reference-skills','.backups'}
errors=[]
def files(pattern):return (p for p in R.rglob(pattern) if not (set(p.relative_to(R).parts)&EXCLUDED))
for p in files('*.json'):
    try:json.loads(p.read_text())
    except ValueError as e:errors.append(f'{p.relative_to(R)}: {e}')
for p in files('*.md'):
    if 'assets' in p.parts and p.name.endswith('-template.md'):
        continue  # Paths here are instantiated when the skill creates a guide.
    content=re.sub(r'<!--.*?-->', '', p.read_text(), flags=re.S)
    content=re.sub(r'(?ms)^```[^\n]*\n.*?^```\s*$', '', content)
    for target in re.findall(r'\]\(([^)]+)\)',content):
        if target.startswith(('http:','https:','#','mailto:')):continue
        path=unquote(target.strip('<>').split('#')[0])
        if path and not (p.parent/path).exists():errors.append(f'{p.relative_to(R)}: {target}')
from score import RUBRIC_FILES, load_rubric, validate_rubric
for version in RUBRIC_FILES:
    try:validate_rubric(load_rubric(version))
    except (ValueError, KeyError, TypeError) as exc:errors.append(f'{version}: {exc}')
index=json.loads((R/'docs/catalog/skills-index.json').read_text());skills=index['skills']
folders={s['folder']for s in skills};ids={s['id']for s in skills}
if len(ids)!=len(skills):errors.append('duplicate skill IDs')
for source in index['sources']:
    count=sum(s['repository']==source['repository']for s in skills)
    if count!=source['expected'] or count!=source['indexed'] or source['missing'] or source['tree_truncated']:errors.append('source coverage mismatch: '+source['repository'])
for s in skills:
    if not s.get('domains') or not s.get('functions'):errors.append('unclassified: '+s['id'])
tools=json.loads((R/'docs/catalog/tools-index.json').read_text());agents=json.loads((R/'docs/catalog/agents-index.json').read_text());recipes=json.loads((R/'docs/catalog/recipes-index.json').read_text())
toolids={r['id']for r in tools};agentids={r['id']for r in agents}
for row in tools+agents+recipes:
    for name in row['skill_folders']:
        if name not in folders:errors.append(row['id']+': missing skill '+name)
    for key in ['guide','quickstart']:
        if not (R/row[key]).is_file():errors.append(row['id']+': missing '+key)
for row in recipes:
    if row['agent_id'] not in agentids or not set(row['tool_ids'])<=toolids:errors.append(row['id']+': unknown agent/tool')
pairs=json.loads((R/'scripts/guide-pairs.json').read_text())
errors.extend(guide_case_errors(R,pairs))
for a,b in pairs:
    expected=reference_content(a,b)
    if not (R/a).is_file() or not (R/b).is_file():
        errors.append(a+': guide or partner missing')
        continue
    if (R/b).read_bytes()!=(expected if expected is not None else (R/a).read_bytes()):
        errors.append(a+': import or skill-pair mismatch')
    if a.endswith('/AGENTS.md'):
        headings=re.findall(r'^## [1-7]\. ',(R/a).read_text(),re.M)
        if len(headings)!=7:errors.append(a+': needs seven sections')
for page in (R/'docs/catalog/skills').glob('*/*.md'):
    if page.parent.name=='domains':continue
    rows=[s for s in page.read_text().splitlines() if s.startswith('| `')]
    if len(rows)>25:errors.append(str(page)+': leaf exceeds 25 entries')
if errors:raise SystemExit('\n'.join(errors))
print(f'OK: {len(skills)} skills, {len(tools)} tools, {len(agents)} agent patterns, {len(recipes)} recipes, {len(pairs)} guide pairs; local links and coverage valid')
