"""Refresh official skill metadata; requires PyYAML, never installs skills."""
import argparse
import concurrent.futures
import hashlib
import json
from datetime import datetime
from zoneinfo import ZoneInfo
from pathlib import Path
import urllib.request
import yaml

ROOT = Path(__file__).resolve().parents[1]
PINS = {'NVIDIA/skills': '0e0d506f4eb67204a62586ac5f19df3cb7ad9b1f',
        'NVIDIA/NeMo-Agent-Toolkit': 'c7e1162a1c7ff18bbd797e090a56cad97c281c92'}

def fetch(url):
    with urllib.request.urlopen(url, timeout=30) as r:
        return r.read()

def build():
    result, coverage = [], []
    for repo, revision in PINS.items():
        tree = json.loads(fetch(f'https://api.github.com/repos/{repo}/git/trees/{revision}?recursive=1'))
        if tree.get('truncated'):
            raise ValueError('Incomplete upstream tree: ' + repo)
        paths = sorted(x['path'] for x in tree['tree'] if x['path'].startswith('skills/') and x['path'].endswith('/SKILL.md'))
        groups = {}
        if repo == 'NVIDIA/skills':
            grouping = json.loads(fetch(f'https://raw.githubusercontent.com/{repo}/{revision}/skills.sh.json'))
            for group in grouping['groupings']:
                for name in group['skills']:
                    groups.setdefault(name, []).append(group['title'])
        def entry(path):
            data = fetch(f'https://raw.githubusercontent.com/{repo}/{revision}/{path}')
            text = data.decode('utf-8-sig')
            if not text.startswith('---'):
                raise ValueError('Missing frontmatter: ' + path)
            front = yaml.safe_load(text.split('---', 2)[1])
            name = front['name']
            folder = path.split('/')[-2]
            if not isinstance(name, str) or not isinstance(front.get('description'), str):
                raise ValueError('Invalid name/description: ' + path)
            branch = 'develop' if repo.endswith('Toolkit') else 'main'
            return {'id': f'skill:{repo.lower()}/{name}', 'name': name, 'folder': folder,
                    'description': front['description'].strip(),
                    'categories': groups.get(folder, groups.get(name, ['Agent Toolkit' if repo.endswith('Toolkit') else 'Unassigned'])),
                    'repository': repo, 'revision': revision, 'path': path,
                    'github_url': f'https://github.com/{repo}/blob/{revision}/{path}',
                    'current_url': f'https://github.com/{repo}/tree/{branch}/'+path.removesuffix('/SKILL.md'),
                    'sha256': hashlib.sha256(data).hexdigest(), 'license': str(front.get('license', 'see repository')),
                    'compatibility': str(front.get('compatibility', 'see SKILL.md and product prerequisites')),
                    'install': f'npx skills add {repo} --skill {name} --agent codex --agent claude-code',
                    'verification': 'metadata-read; not installed or runtime-tested'}
        with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
            entries = list(pool.map(entry, paths))
        ids = [x['id'] for x in entries]
        if len(ids) != len(set(ids)):
            raise ValueError('Duplicate declared skill name in ' + repo)
        result.extend(entries)
        coverage.append({'repository': repo, 'revision': revision, 'scope': 'skills/**/SKILL.md',
                         'expected': len(paths), 'indexed': len(entries), 'missing': [], 'tree_truncated': False})
    return {'schema_version': 1, 'checked_at': datetime.now(ZoneInfo('Asia/Seoul')).date().isoformat(), 'sources': coverage, 'skills': result}

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true', help='Replace local pinned metadata snapshot')
    args = parser.parse_args()
    result = build()
    if args.write:
        dest = ROOT/'docs/catalog/skills-index.json'
        dest.write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n')
        from classify_skills import generate
        generate(ROOT)
    print(json.dumps({'sources': result['sources'], 'total': len(result['skills']), 'written': args.write}, indent=2))
