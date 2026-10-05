"""Two-request NIM tool-calling check; dry-run unless --live is explicit."""
import argparse
import json
import os
from pathlib import Path
import time
import urllib.error
import urllib.request

def request(base,key,payload,timeout=30):
    req=urllib.request.Request(base.rstrip('/')+'/chat/completions',data=json.dumps(payload).encode(),headers={'Authorization':'Bearer '+key,'Content-Type':'application/json'})
    with urllib.request.urlopen(req,timeout=timeout) as response:return json.load(response)

def probe(send,model):
    tools=[{'type':'function','function':{'name':'add','description':'Add two integers.','parameters':{'type':'object','properties':{'a':{'type':'integer'},'b':{'type':'integer'}},'required':['a','b'],'additionalProperties':False}}}]
    messages=[{'role':'user','content':'Call add with a=17 and b=25. After its result return only JSON with the key result.'}]
    first=send({'model':model,'messages':messages,'tools':tools,'tool_choice':'auto','temperature':0,'max_tokens':256})
    message=first['choices'][0]['message'];calls=message.get('tool_calls',[])
    if len(calls)!=1 or calls[0]['function']['name']!='add':raise ValueError('Expected exactly one add tool call')
    args=json.loads(calls[0]['function']['arguments'])
    if set(args)!={'a','b'} or any(type(v) is not int for v in args.values()) or args!={'a':17,'b':25}:raise ValueError('Tool arguments did not match the test input')
    value=args['a']+args['b']
    messages += [{'role':'assistant','content':message.get('content'),'tool_calls':calls},{'role':'tool','tool_call_id':calls[0]['id'],'content':json.dumps({'result':value})}]
    second=send({'model':model,'messages':messages,'temperature':0,'max_tokens':128})
    result=json.loads(second['choices'][0]['message']['content'])
    if result!={'result':42} or type(result['result']) is not int:raise ValueError('Final JSON result failed independent validation')
    return {'mode':'live','model':model,'http_requests':2,'tool':'add','arguments':args,'tool_result':value,'final_result':result,'passed':True}

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--live',action='store_true');p.add_argument('--output',type=Path);a=p.parse_args()
    model=os.getenv('MODEL_ID','');key=os.getenv('NVIDIA_API_KEY','');base=os.getenv('MODEL_BASE_URL','https://integrate.api.nvidia.com/v1')
    if not a.live:
        print(json.dumps({'mode':'dry-run','model_configured':bool(model),'key_present':bool(key),'http_requests':0,'live_command':'python3 scripts/probe_nim.py --live --output runs/nim-probe.json'}));raise SystemExit()
    if not model or not key:p.error('MODEL_ID and NVIDIA_API_KEY must be set; values are not printed')
    if not base.startswith('https://'):p.error('Only HTTPS endpoints are supported by this probe')
    if a.output and a.output.exists():p.error('Output exists; choose a fresh run file')
    started=time.monotonic()
    try:
        result=probe(lambda payload:request(base,key,payload),model)
    except urllib.error.HTTPError as exc:p.exit(1,f'HTTP {exc.code}; response body and credentials omitted\n')
    except (ValueError,KeyError,IndexError,TypeError,OSError):p.exit(1,'Probe failed: transport or response validation; no secrets logged\n')
    result['duration_ms']=round((time.monotonic()-started)*1000)
    if a.output:
        a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,ensure_ascii=False,indent=2))
