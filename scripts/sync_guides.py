"""Synchronize staged guide pairs without overwriting unstaged work."""
import argparse
import json
from pathlib import Path
import subprocess

def git(root,*args):
    return subprocess.run(['git','-C',str(root),*args],capture_output=True)

def guide_case_errors(root,pairs):
    root=Path(root)
    excluded={'.git','.venv','node_modules','__pycache__','reference-skills','.backups'}
    errors=[]
    for path in root.rglob('*.md'):
        if set(path.relative_to(root).parts)&excluded:continue
        canonical={'agents.md':'AGENTS.md','claude.md':'CLAUDE.md'}.get(path.name.casefold())
        if canonical and path.name!=canonical:
            errors.append(str(path.relative_to(root))+': reserved guide filename must be '+canonical)
    for pair in pairs:
        for name in pair:
            path=root/name
            if path.exists() and path.name not in {p.name for p in path.parent.iterdir()}:
                errors.append(name+': actual filename case does not match configured path')
    return errors

def synchronize(root,check=False):
    root=Path(root).resolve()
    pairs=json.loads((root/'scripts/guide-pairs.json').read_text())
    casing=guide_case_errors(root,pairs)
    if casing:raise ValueError('\n'.join(casing))
    staged=set(git(root,'diff','--cached','--name-only','-z').stdout.decode().split('\0'))
    plans=[];errors=[]
    def working(name):
        p=root/name
        if p.is_symlink():raise ValueError('Symlink guide requires manual review: '+name)
        return p.read_bytes() if p.exists() else None
    def indexed(name):
        r=git(root,'show',':'+name)
        return r.stdout if r.returncode==0 else None
    for left,right in pairs:
        for name in (left,right):
            p=root/name
            if not p.resolve().is_relative_to(root):raise ValueError('Guide path escapes repository')
        a,b=working(left),working(right)
        if a is None and b is None:continue
        if check:
            if a is None or b is None or a!=b:errors.append(left+' / '+right+': different or missing')
            continue
        sides=[n for n in (left,right) if n in staged]
        if len(sides)==2:
            if a is None or b is None or a!=b or a!=indexed(left) or b!=indexed(right):
                errors.append(left+' / '+right+': both staged differ or contain unstaged edits')
        elif len(sides)==1:
            source=sides[0];target=right if source==left else left
            content=indexed(source);current=working(source);target_index=indexed(target);target_work=working(target)
            if content is None or content!=current:
                errors.append(source+': staged deletion or partial staging; resolve manually')
            elif target_index is not None and target_work!=target_index:
                errors.append(target+': unstaged edits/deletion; refusing overwrite')
            elif target_index is None and target_work is not None and target_work!=content:
                errors.append(target+': different untracked file; refusing overwrite')
            elif target_work!=content or target_index!=content:
                plans.append((target,content))
        elif a is None or b is None or a!=b:
            errors.append(left+' / '+right+': no staged direction; stage the chosen source')
    if errors:raise ValueError('\n'.join(errors))
    for target,content in plans:
        dest=root/target;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(content)
        r=git(root,'add','--',target)
        if r.returncode:raise ValueError('Could not stage synchronized guide: '+target)
    return len(plans)

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--check',action='store_true');a=p.parse_args()
    result=git(Path.cwd(),'rev-parse','--show-toplevel')
    if result.returncode:p.exit(2,'Not a Git repository\n')
    try:n=synchronize(result.stdout.decode().strip(),a.check)
    except (ValueError,OSError) as e:p.exit(1,str(e)+'\n')
    print('Guide pairs OK' if a.check else f'Synchronized {n} guide file(s)')
