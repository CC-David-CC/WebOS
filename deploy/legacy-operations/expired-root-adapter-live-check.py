#!/usr/bin/env python3
"""Read-only check of the uninstalled managed recovery adapter against webhost."""
import hashlib,json,shlex,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
steps=(ROOT/'origin_service/expired_root_steps.py').read_text();adapter=(ROOT/'origin_service/expired_root_managed.py').read_text()
remote=r'''
import hashlib,importlib.util,json,os,sys,types
from pathlib import Path
assert os.geteuid()==0
path=Path('/etc/codi-connected/ksu/managed.json');raw=path.read_bytes();cfg=json.loads(raw);release=Path(cfg['release']);sys.path.insert(0,str(release))
spec=importlib.util.spec_from_file_location('expired_adapter_installed_operator',release/'scripts/manage-services.py');op=importlib.util.module_from_spec(spec);sys.modules[spec.name]=op;spec.loader.exec_module(op)
from origin_service import maintenance
steps=types.ModuleType('origin_service.expired_root_steps');sys.modules[steps.__name__]=steps;exec(__STEPS__,steps.__dict__)
module=types.ModuleType('expired_root_managed_uninstalled');exec(__ADAPTER__,module.__dict__)
backend=module.ManagedExpiredRoot(op,maintenance,path,config_sha256=hashlib.sha256(raw).hexdigest(),release_sha256=cfg['manifestSHA256'])
with backend.locked():
 record=backend.initial();action=backend.decide(record)
 print(json.dumps({'status':'PASS','scope':'Uninstalled managed adapter read-only coherent-state verification','nextStep':action,'baseRevision':record['checkpoint']['baseRevision'],'publisherFloor':record['publisherRevision'],'configSHA256':record['configSHA256'],'releaseSHA256':record['releaseSHA256'],'liveChanged':False,'signingPerformed':False}))
'''
if __name__=='__main__':
 bootstrap="import json,os,pathlib,sys;c=json.loads(pathlib.Path('/etc/codi-connected/ksu/managed.json').read_bytes());code=sys.stdin.read();os.execv(c['python'],[c['python'],'-I','-B','-c',code])"
 code=remote.replace('__STEPS__',repr(steps)).replace('__ADAPTER__',repr(adapter));child=subprocess.run(['ssh','-o','BatchMode=yes','-o','ConnectTimeout=5','box-webhost','sudo','-n','/usr/bin/python3','-I','-B','-c',shlex.quote(bootstrap)],input=code,text=True,capture_output=True,timeout=45)
 if child.returncode:raise RuntimeError('Read-only adapter check failed: '+child.stderr[-4000:])
 result=json.loads(child.stdout);result.update(stepsSHA256=hashlib.sha256(steps.encode()).hexdigest(),adapterSHA256=hashlib.sha256(adapter.encode()).hexdigest());out=ROOT/'.build/checks/expired-root-adapter-live-r3-result.json';assert not out.exists();out.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
