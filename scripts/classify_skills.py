"""Build small domain/task views from the single official metadata index."""
import collections
import json
from pathlib import Path
import re
ROOT=Path(__file__).resolve().parents[1]
DOMAINS={
 'knowledge':('문서·검색·지식','문서 검색 규정 rag retrieval documents knowledge'),
 'agents':('에이전트·평가·정책','에이전트 평가 정책 agent workflow guardrails evaluation'),
 'vision':('영상·이미지·비전','영상 이미지 비전 video vision image vss deepstream'),
 'speech':('음성·대화','음성 전사 대화 speech voice conversational asr tts'),
 'optimization':('경로·수학 최적화','경로 배차 일정 최적화 cuopt routing optimization solver'),
 'biology':('생명과학·의료','바이오 생명 의료 단백질 분자 biology healthcare protein molecule dicom'),
 'data':('표 데이터·분석','데이터 표 분석 csv dataframe data science cudf'),
 'robotics':('로봇·물리·시뮬레이션','로봇 물리 시뮬레이션 robotics physical simulation cosmos isaac'),
 'training':('모델 학습·조정','학습 튜닝 training finetune reinforcement'),
 'infrastructure':('배포·서빙·인프라','배포 서빙 인프라 네트워크 저장소 deploy serving infrastructure networking storage'),
 'compute':('GPU 개발·고급 계산','gpu cuda 커널 계산 compute kernel quantum gaming')}
FUNCTIONS={'discover':'탐색·선택','setup':'설치·배포','build':'구현·연결','run':'실행·사용','evaluate':'검증·평가','optimize':'성능·조정','troubleshoot':'문제 해결'}
MAP={'Agentic AI':'agents','Agent Toolkit':'agents','Cybersecurity':'agents','Vision AI':'vision','Conversational AI':'speech','Decision Optimization':'optimization','Data Science':'data','Physical AI':'robotics','Robotics':'robotics','Robotics Simulation':'robotics','Simulation and Modeling':'robotics','Training AI':'training','Inference AI':'infrastructure','Infrastructure':'infrastructure','Networking':'infrastructure','AI Storage':'infrastructure','GPU Development':'compute','Quantum Computing':'compute','Gaming':'compute'}
PATTERNS={
 'discover':r'find|discover|selection|recommender|user-guide|docs|taxonomy',
 'setup':r'install|setup|deploy|launch|bootstrap|provision|flash|init|download',
 'build':r'build|create|develop|integrat|scaffold|config|pipeline|onboard|write|convert|adapter',
 'evaluate':r'eval|test|validat|verif|check|audit|benchmark|inspect',
 'optimize':r'optimiz|perf|tuning|finetun|profile|quantiz',
 'troubleshoot':r'troubleshoot|debug|diagnos|repair|resilien',
 'run':r'run|query|ask|search|summar|generat|infer|predict|usage|api|process|extract'}

def classify(skill):
    name=skill['folder'].lower()
    domains=list(dict.fromkeys(MAP.get(c,'agents') for c in skill['categories']))
    specific=[]
    if name.startswith(('bionemo-','dicom-','digital-health-','ambient-healthcare-')):specific.append('biology')
    if name.startswith(('rag-','nemo-retriever','nemotron-retrieval')):specific.append('knowledge')
    if re.search(r'speech|asr|tts|voice|riva|pipecat',name):specific.append('speech')
    if name=='data-designer':specific.extend(['data','agents'])
    domains=list(dict.fromkeys(specific+domains))
    scores={k:len(re.findall(p,name))*5+min(2,len(re.findall(p,skill['description'].lower()))) for k,p in PATTERNS.items()}
    funcs=sorted((k for k,v in scores.items() if v>=5),key=lambda k:(-scores[k],k))[:2]
    if not funcs:funcs=[max(scores,key=scores.get)] if max(scores.values()) else ['run']
    overrides={
        'nemo-retriever':['setup','run'], 'nemo-retriever-mcp':['build','run'],
        'rag-blueprint':['setup','build','troubleshoot'],
        'nat-installation':['setup'], 'nat-workflow-creation':['build'],
        'nat-tools-and-functions':['build','evaluate'],
        'nat-agent-configuration':['discover','build'], 'nat-mcp-and-serving':['build','run'],
        'nat-evaluation':['evaluate'], 'nat-telemetry':['evaluate','troubleshoot'],
        'data-designer':['build','run'], 'nemoclaw-user-guide':['discover','setup'],
        'nemotron-policy-generator':['build','evaluate'],
        'nemotron-speech':['discover','setup','run'], 'nvidia-skill-finder':['discover'],
        'cuopt-routing-api-python':['build','run']}
    return domains,overrides.get(name,funcs)

def domain_filename(domain):
    # Avoid a case-insensitive collision with the reserved AGENTS.md guide.
    return 'agent-workflows.md' if domain == 'agents' else domain + '.md'

def generate(root=ROOT):
    path=root/'docs/catalog/skills-index.json';data=json.loads(path.read_text())
    for skill in data['skills']:
        skill['domains'],skill['functions']=classify(skill)
        skill['classification']='project-derived-from-official-category-and-metadata; reviewable'
    data['navigation']={'domains':{k:{'label':v[0],'keywords':v[1]}for k,v in DOMAINS.items()},'functions':FUNCTIONS}
    path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
    base=root/'docs/catalog/skills';base.mkdir(parents=True,exist_ok=True)
    manifest=[]
    def write(p,s):
        dest=base/p;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_text(s+'\n');manifest.append(str(dest.relative_to(root)))
    top=['# 스킬 탐색: 도메인 → 작업 목적 → 개별 스킬','','원본 정보는 [skills-index.json](../skills-index.json) 한 곳에 있다. 이 문서들은 검색용 자동 생성 뷰다. 공식 분류는 `categories`, 이 프로젝트의 도메인/작업 분류는 `domains/functions`에 구분했다. 작업 분류는 이름·설명에서 만든 탐색 보조이며 제품 지원 보증이 아니다.','','| 도메인 | 고유 스킬 수 | 바로 읽기 |','|---|---:|---|']
    for domain,(label,_) in DOMAINS.items():
        selected=[s for s in data['skills'] if domain in s['domains']]
        top.append(f'| {label} | {len(selected)} | [{domain}](domains/{domain_filename(domain)}) |')
        lines=[f'# {label}','','[전체 도메인](../README.md) · 목록은 이 도메인의 스킬만 포함한다.','','| 작업 목적 | 스킬 수 | 목록 |','|---|---:|---|']
        for function,label2 in FUNCTIONS.items():
            subset=sorted((s for s in selected if function in s['functions']),key=lambda s:s['name'])
            if not subset:continue
            links=[]
            for start in range(0,len(subset),25):
                page=start//25+1;name=f'{domain}/{function}-{page}.md';links.append(f'[{page}](../{name})')
                leaf=[f'# {label} / {label2} / {page}','','[도메인으로](../domains/'+domain_filename(domain)+')','','| 스킬 | 사용 목적 | 고정 원문 |','|---|---|---|']
                for s in subset[start:start+25]:
                    desc=' '.join(s['description'].split()).replace('|','/')
                    desc=desc[:150]+'…' if len(desc)>150 else desc
                    leaf.append(f"| `{s['name']}` | {desc} | [SKILL.md]({s['github_url']}) |")
                leaf+=['','설치/환경/실행 정보: `python3 scripts/lookup.py --show "'+subset[start]['id']+'"` 형식으로 조회한다.','공통 [확보 절차](../../../playbooks/skill-setup.md). 검색 결과가 부족하면 domain/function 필터를 풀어 전체 원문 설명에서 찾는다.']
                write(name,'\n'.join(leaf))
            lines.append(f"| {label2} (`{function}`) | {len(subset)} | {' · '.join(links)} |")
        lines+=['',f'CLI: `python3 scripts/lookup.py --domain {domain} --kind skill --limit 8`.', '기능을 더 좁히려면 `--function setup` 등 사용. 결과의 전체 사용법/참조는 선택한 스킬 원문을 읽는다.']
        write('domains/'+domain_filename(domain),'\n'.join(lines))
    top+=['','## 기능으로 바로 찾기','','`python3 scripts/lookup.py --kind skill --function evaluate --limit 8`처럼 도메인 없이 기능만 검색할 수도 있다.','각 스킬은 여러 도메인/기능에 연결될 수 있으므로 표의 합계는 고유 스킬 수와 다를 수 있다. 전체 범위는 NVIDIA/skills 398개 + NAT 11개다. 모든 NVIDIA 제품 저장소의 모든 비공개/미등록 스킬까지 포함하는 목록은 아니다.']
    write('README.md','\n'.join(top))
    oldpath=base/'generated-files.json'
    if oldpath.exists():
        for old in json.loads(oldpath.read_text()):
            p=root/old
            if old not in manifest and p.is_relative_to(base) and p.is_file():p.unlink()
    oldpath.write_text(json.dumps(manifest,indent=2)+'\n')
    return len(data['skills']),len(manifest)
if __name__=='__main__':print('skills / navigation pages:',generate())
