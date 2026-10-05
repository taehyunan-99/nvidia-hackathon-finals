"""Download one pinned official skill directory as reference data, never execute it."""
import argparse
import hashlib
import json
from pathlib import Path,PurePosixPath
import shutil
import tempfile
import urllib.request
ROOT=Path(__file__).resolve().parents[1]

def safe_path(path):
    p=PurePosixPath(path)
    if p.is_absolute() or '..' in p.parts or '\\' in path:raise ValueError('Unsafe upstream path')
    return p

def download(skill,dest):
    repo,revision=skill['repository'],skill['revision']
    if repo not in {'NVIDIA/skills','NVIDIA/NeMo-Agent-Toolkit'}:raise ValueError('Repository not allowlisted')
    prefix=str(safe_path(skill['path']).parent)+'/'
    dest=Path(dest);target=dest/skill['folder']
    if target.exists():raise ValueError('Destination exists; refusing to overwrite: '+str(target))
    def get(url):
        with urllib.request.urlopen(url,timeout=30) as r:return r.read()
    tree=json.loads(get(f'https://api.github.com/repos/{repo}/git/trees/{revision}?recursive=1'))
    if tree.get('truncated'):raise ValueError('Incomplete upstream tree')
    files=[x for x in tree['tree'] if x['type']=='blob' and (x['path'].startswith(prefix) or ('/' not in x['path'] and x['path'].upper().startswith(('LICENSE','NOTICE'))))]
    dest.mkdir(parents=True,exist_ok=True)
    staging=Path(tempfile.mkdtemp(prefix='.skill-',dir=dest))
    try:
        hashes={}
        for f in files:
            if f['mode']=='120000':raise ValueError('Symlink needs manual review: '+f['path'])
            safe_path(f['path'])
            rel=f['path'][len(prefix):] if f['path'].startswith(prefix) else '_upstream_licenses/'+f['path']
            out=staging/safe_path(rel);out.parent.mkdir(parents=True,exist_ok=True)
            b=get(f'https://raw.githubusercontent.com/{repo}/{revision}/{f["path"]}')
            digest=hashlib.sha256(b).hexdigest()
            if rel=='SKILL.md' and digest!=skill['sha256']:raise ValueError('Pinned SKILL.md hash mismatch')
            out.write_bytes(b);out.chmod(0o755 if f['mode']=='100755' else 0o644);hashes[rel]=digest
        if not (staging/'SKILL.md').is_file():raise ValueError('Missing SKILL.md')
        manifest={'repository':repo,'revision':revision,'files':hashes,'mode':'reference-only; no software executed'}
        (staging/'download-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
        if target.exists():raise ValueError('Destination appeared during download')
        staging.rename(target)
        return {'directory':str(target),'files':len(hashes),'revision':revision,'installed':False}
    finally:
        if staging.exists():shutil.rmtree(staging)

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('skill');p.add_argument('--dest',required=True,type=Path);a=p.parse_args()
    data=json.loads((ROOT/'docs/catalog/skills-index.json').read_text())['skills']
    matches=[s for s in data if a.skill in (s['name'],s['folder'],s['id'])]
    if len(matches)!=1:p.error('Skill missing or ambiguous; use the full ID from lookup.py')
    try:print(json.dumps(download(matches[0],a.dest),ensure_ascii=False,indent=2))
    except (ValueError,OSError) as exc:p.exit(2,f'Download failed: {exc}\n')
