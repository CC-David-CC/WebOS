#!/usr/bin/env python3
"""Run explicit pinned live-development rollout steps; never retry a mutation.

The protected remote publisher holds the hosting lock and produces an owned
receipt. This wrapper verifies that receipt's exact bytes and retains it locally.
No VM, new service, credentials, keys or actual document bodies are involved.
"""
import argparse
import hashlib
import json
from pathlib import Path
import shlex
import subprocess
import time

PUBLISHER='/srv/codi-connected/recovery-producers/cd875e7222826e24a02a8811be2668213cbe6013e7ec174a427be54b32a9c9e5/publish-recovery-producer.py'
COMMIT='e3f3127fd9205c527ec4c6c39c1101460751d845'
ACTIONS=['stage','activate-backend','rollback-backend','recover-backend','activate','rollback-native','recover-native','verify']


def run(actions):
    result={'status':'FAIL','scope':__doc__,'sourceCommit':COMMIT,'steps':[],'wholeGoalComplete':False}
    try:
        for action in actions:
            started=time.monotonic()
            remote=subprocess.run(['ssh','-o','BatchMode=yes','box-webhost','sudo','-n','/srv/codi-connected/venvs/517179c/bin/python','-I','-B',PUBLISHER,action,'--commit',COMMIT],capture_output=True,text=True,timeout=420)
            assert remote.stdout,remote.stderr[-2000:]
            summary=json.loads(remote.stdout);assert summary['action']==action
            path=Path(summary['rootReceipt']);assert path.parent==Path('/srv/codi-connected') and path.name.startswith('recovery-producer-'+action+'-') and path.name.endswith('-result.json')
            code='from pathlib import Path;import sys;sys.stdout.buffer.write(Path('+repr(str(path))+').read_bytes())'
            receipt=subprocess.run(['ssh','-o','BatchMode=yes','box-webhost','sudo','-n','/usr/bin/python3','-I','-B','-c',shlex.quote(code)],capture_output=True,check=True,timeout=30).stdout
            assert hashlib.sha256(receipt).hexdigest()==summary['rootReceiptSHA256']
            value=json.loads(receipt);assert value['action']==action and value.get('sourceCommit',COMMIT)==COMMIT
            step={'summary':summary,'receipt':value,'elapsedSeconds':round(time.monotonic()-started,3)};result['steps'].append(step)
            print(json.dumps({'action':action,'status':summary['status'],'manifestSHA256':summary.get('manifestSHA256'),'elapsedSeconds':step['elapsedSeconds'],'error':summary.get('error')}),flush=True)
            assert remote.returncode==0 and value['status']==summary['status']=='PASS',value.get('traceback',remote.stderr[-2000:])
        result['status']='PASS'
    except Exception as error:
        import traceback
        result.update(error=str(error),traceback=traceback.format_exc(),recoveryRequired='Inspect the last explicit receipt and managed journals; do not blindly resend a mutation.')
    result['sourceSHA256']=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    return result


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--actions',nargs='+',choices=ACTIONS,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();assert not a.output.exists()
    value=run(a.actions);a.output.write_text(json.dumps(value,indent=2)+'\n');print(json.dumps({'status':value['status'],'completedSteps':len(value['steps']),'error':value.get('error')}));raise SystemExit(0 if value['status']=='PASS' else 1)
