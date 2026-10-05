"""Read-only local inventory. No API calls, no environment dumps."""
import json
import os
import platform
import shutil
import subprocess

def version(binary):
    path=shutil.which(binary)
    if not path:return {'present':False}
    try:
        p=subprocess.run([path,'--version'],capture_output=True,text=True,timeout=5)
        return {'present':True,'version':(p.stdout or p.stderr).splitlines()[0][:160]}
    except (OSError,subprocess.TimeoutExpired,IndexError):return {'present':True,'version':'unverified'}
if __name__=='__main__':
    print(json.dumps({'platform':platform.system(),'machine':platform.machine(),'python':platform.python_version(),'tools':{n:version(n) for n in ['git','node','npm','uv','docker']},'credentials_present_in_process':{n:bool(os.getenv(n)) for n in ['NVIDIA_API_KEY','NGC_API_KEY']},'gpu_cli_present':bool(shutil.which('nvidia-smi')),'live_api':'not_checked','docker_daemon':'not_checked','note':'키 값과 .env는 읽지 않음. 없는 GPU CLI는 hosted API 사용을 막지 않음.'},ensure_ascii=False,indent=2))
