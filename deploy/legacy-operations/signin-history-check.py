#!/usr/bin/env python3
"""Real root-owned large-history compatibility/count/size guards in retained VM.

Creates only a temporary root-owned fixture directory. Does not edit or truncate
actual history. The real 65,780-byte history is retained for explicit recovery.
"""
import hashlib
import importlib.util
import json
from pathlib import Path
import shlex
import subprocess

ROOT=Path(__file__).resolve().parent.parent
REMOTE=r'''
import importlib.util,json,sys,tempfile
from pathlib import Path
release=Path('/srv/codi-network-fixture/candidate-5fad3b77a5b3f982');s=importlib.util.spec_from_file_location('history_op',release/'scripts/manage-services.py');op=importlib.util.module_from_spec(s);sys.modules[s.name]=op;s.loader.exec_module(op)
from origin_service import deployment,network_management,files_management,turn_management
config=json.loads(Path('/etc/codi-native-fixture/managed.json').read_text());checks=[]
with tempfile.TemporaryDirectory(prefix='history-bound-',dir='/srv/codi-network-fixture') as d:
 folder=Path(d)
 for module,name,version in [(deployment,'code-history.json','codi-code-history/1'),(network_management,'network-history.json','codi-network-history/1'),(files_management,'files-history.json','codi-files-history/1'),(turn_management,'turn-history.json','codi-turn-history/1')]:
  file=folder/name;rows=[{'id':format(i,'032x'),'before':config,'after':config,'activeRoles':['issuer','steward','guest'],'outcome':'applied','detail':'x'*1400,'completed':i} for i in range(16)]
  value={'version':version,'instance':config['instance'],'entries':rows}
  op.atomic(file,(json.dumps(value,indent=2)+'\n').encode());assert file.stat().st_size>65536
  assert module.history(op,config,folder/'managed.json')==value;checks.append(name+': 16 valid records beyond 64 KiB retained and readable')
  value['entries'].append(rows[0]);op.atomic(file,json.dumps(value).encode())
  try:module.history(op,config,folder/'managed.json')
  except ValueError:checks.append(name+': 17 records still refused')
  else:raise AssertionError('Entry count limit relaxed')
  value['entries']=rows[:16];value['entries'][0]['detail']='x'*4194304
  op.atomic(file,json.dumps(value).encode())
  try:module.history(op,config,folder/'managed.json')
  except ValueError as error:
   assert 'ownership/type/bounds' in str(error),str(error)
   checks.append(name+': oversized valid JSON refused before parsing')
  else:raise AssertionError('Byte bound missing')
assert not folder.exists()
print(json.dumps({'status':'PASS','checks':checks,'temporaryFixtureRemoved':True,'actualHistoryModified':False,'liveWebhostChanged':False}))
'''
if __name__=='__main__':
    s=importlib.util.spec_from_file_location('history_vm',ROOT/'scripts/prepare-native-network-vm.py');vm=importlib.util.module_from_spec(s);s.loader.exec_module(vm);vm.status()
    r=subprocess.run([*vm.ssh_args(),'/srv/codi-network-fixture/venv/bin/python -I -B -c '+shlex.quote(REMOTE)],capture_output=True,text=True,timeout=60)
    if r.returncode:raise RuntimeError(r.stderr[-2400:])
    result=json.loads(r.stdout);result['sourceSHA256']=hashlib.sha256(Path(__file__).read_bytes()).hexdigest();(ROOT/'.build/checks/signin-history-result.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
