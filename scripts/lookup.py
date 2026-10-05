"""Offline lookup of mission recipes, tools, agents, and NVIDIA skill metadata."""
import argparse
import json
from pathlib import Path
import re
ROOT=Path(__file__).resolve().parents[1]

def load_entries(root=ROOT):
    base=root/'docs/catalog'
    data=json.loads((base/'skills-index.json').read_text())
    entries=[]
    for file,kind in [('recipes-index.json','recipe'),('tools-index.json','tool'),('agents-index.json','agent')]:
        entries.extend(dict(e,kind=kind) for e in json.loads((base/file).read_text()))
    for s in data['skills']:
        words=' '.join(data.get('navigation',{}).get('domains',{}).get(d,{}).get('keywords','') for d in s.get('domains',[]))
        entries.append(dict(s,kind='skill',keywords=words))
    return entries

def search(entries,query='',kind=None,domain=None,function=None,limit=5):
    tokens=re.findall(r'[\w-]+',query.casefold())
    ranked=[]
    for e in entries:
        if kind and e['kind']!=kind:continue
        if domain and domain not in e.get('domains',[]):continue
        if function and function not in e.get('functions',[]):continue
        name=(e['name']+' '+e.get('folder','')).casefold()
        keywords=e.get('keywords','').casefold()
        haystack=' '.join([name,keywords,e.get('description',''),*e.get('categories',[])]).casefold()
        scores=[(12 if token==name or token==e['id'].split(':')[-1] else 6 if token in name else 4 if token in keywords else 1 if token in haystack else 0) for token in tokens]
        # OR matching retains useful results when Korean particles or a long prompt occur.
        if tokens and not any(scores):continue
        score=sum(scores)+(2 if e['kind']=='recipe' else 0)
        ranked.append((score,e))
    return [e for _,e in sorted(ranked,key=lambda pair:(-pair[0],pair[1]['id']))[:limit]]

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('query',nargs='?',default='')
    p.add_argument('--kind',choices=['recipe','tool','agent','skill'])
    p.add_argument('--domain');p.add_argument('--function');p.add_argument('--show')
    p.add_argument('--limit',type=int,default=5)
    a=p.parse_args();entries=load_entries()
    if not 1<=a.limit<=50:p.error('limit must be 1..50')
    if a.show:
        found=[e for e in entries if e['id']==a.show]
    else:found=search(entries,a.query,a.kind,a.domain,a.function,a.limit)
    if not found:
        print(json.dumps({'matches':[],'note':'필터를 풀거나 영어 제품명으로 검색하세요. 이 결과는 지원 기능이 없다는 판정이 아닙니다.'},ensure_ascii=False));raise SystemExit(1)
    if not a.show:
        keys=['id','name','kind','description','domains','functions','guide','quickstart','github_url','install','runtime_status','verification','contract','contract_section','schema','fixtures','preview']
        found=[{k:(v[:220]+'…' if k=='description' and len(v)>220 else v) for k,v in row.items() if k in keys} for row in found]
    print(json.dumps(found,ensure_ascii=False,indent=2))
