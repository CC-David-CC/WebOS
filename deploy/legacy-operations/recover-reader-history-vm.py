#!/usr/bin/env python3
"""Recover retained real oversize-history failure using exact native24 tooling.

Reads/writes the existing private VM; preserves both pending journal semantics,
current nonempty data, authority custody and all account/file/usage state.
No DB restore, root mint, manual history pruning or old verifier modification.
"""
import argparse
import hashlib
import importlib.util
import json
import os
import secrets
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

CONTROL=Path('/etc/codi-native-fixture/managed.json');BASE=Path('/srv/codi-room-fixture')
OLD='a2086017e7dcc87a7c1126bb7c71b62fd5ae0e7c1f94567444491850d1862a34';NEW='ba89487b3ea3fbca334abd3cc8f3467b8dd604bab51a141ed221236a4c1871f5'
OP='53aa99303600f942a6f40b63718e26f2e73d78bffa0c458ba3d6bebb83a034fc';OLD_DIR=Path('/srv/codi-network-fixture/candidate-'+OLD[:16]);NEW_DIR=Path('/srv/codi-network-fixture/candidate-'+NEW[:16]);PYTHON='/srv/codi-network-fixture/venv/bin/python'
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--result',type=Path,required=True);a=p.parse_args();assert not a.result.exists() and os.geteuid()==0
s=importlib.util.spec_from_file_location('history_recovery_composition',Path(__file__).with_name('reader-backend-transition.py'));b=importlib.util.module_from_spec(s);s.loader.exec_module(b);t=b.Transition(CONTROL,Path('/etc/codi-rooms-fixture/managed.json'),BASE/'operators'/OP,OP,NEW_DIR,NEW)

def run(args):return subprocess.check_output(list(map(str,args)),text=True,stderr=subprocess.PIPE,timeout=180)
def snapshot():return json.loads(run([PYTHON,'-I','-B','/srv/codi-network-fixture/tools/native-network-vm-lifecycle-check.py','--snapshot']))
def custody():
 c=t.read_native();root=Path(c['stateRoot'])/'operator/root';return {str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest()for p in root.rglob('*')if p.is_file()}
def refused(fn):
 try:fn()
 except (ValueError,OSError,subprocess.SubprocessError):return True
 raise AssertionError('Expected refusal')
checks=[];v=dict(status='FAIL',scope=__doc__,checks=checks,productionChanged=False,dataRestored=False,rootMinted=False)
def check(name,ok):assert ok,name;checks.append(name);print(json.dumps({'check':name}),flush=True)
try:
 before=snapshot();rootkeys=custody();jraw=t.journal.read_bytes();j=json.loads(jraw);history=CONTROL.parent/'rooms-history.json';raw=history.read_bytes();old_history=json.loads(raw);native_inner=json.loads((CONTROL.parent/'maintenance.json').read_bytes());assert len(raw)>65536 and j['controllerPin']==OLD and j['phase']=='prepared' and native_inner['version']=='codi-hosted-rooms-transition/1' and t.read_native()['manifestSHA256']==OLD
 # Actual native readers/ownership checks, with a retained copy of this real
 # 14-record history. No untrusted wrapper replaces their I/O.
 spec=importlib.util.spec_from_file_location('history_repair_native',NEW_DIR/'scripts/manage-services.py');op=importlib.util.module_from_spec(spec);sys.modules[spec.name]=op;spec.loader.exec_module(op)
 from origin_service import room_management as rooms
 with tempfile.TemporaryDirectory(prefix='reader-history-',dir=BASE/'tests')as folder:
  folder=Path(folder);file=folder/'rooms-history.json';file.write_bytes(raw);file.chmod(0o600);config=t.read_native()
  check('actual repaired native reader accepts the retained legitimate history larger than64KiB',rooms.history(op,config,folder/'managed.json')==old_history)
  first=rooms.history(op,config,folder/'managed.json');entry={'id':secrets.token_hex(16),'before':config,'after':config,'activeRoles':['issuer']};rooms.record(op,config,folder/'managed.json',entry,'reverted');saved=rooms.history(op,config,folder/'managed.json')
  expected=([x['id']for x in first['entries']]+[entry['id']])[-16:]
  check('real history writer preserves bounded prior records while appending once',[x['id']for x in saved['entries']]==expected)
  for _ in range(20):
   entry={**entry,'id':secrets.token_hex(16)};expected=(expected+[entry['id']])[-16:];rooms.record(op,config,folder/'managed.json',entry,'reverted');saved=rooms.history(op,config,folder/'managed.json');assert [x['id']for x in saved['entries']]==expected
  check('twenty further real history writes plateau at16 while retaining the latest exact IDs',len(saved['entries'])==16)
  rooms.record(op,config,folder/'managed.json',entry,'reverted');again=rooms.history(op,config,folder/'managed.json');check('repeated commit ID is kept exactly once',len(again['entries'])==16 and sum(x['id']==entry['id']for x in again['entries'])==1)
  unchanged=file.read_bytes();check('history writer refuses over4MiB before overwriting prior records',refused(lambda:rooms.write_history(op,file,{'padding':'x'*(4*1048576)})) and file.read_bytes()==unchanged)
  oversized=json.dumps({'version':first['version'],'instance':first['instance'],'entries':[],'padding':'x'*(4*1048576)}).encode();file.write_bytes(oversized)
  check('history reader refuses over4MiB bounded input',refused(lambda:rooms.history(op,config,folder/'managed.json')))
  called=[];atomic,stop=op.atomic,op.stop
  def mutation(*args,**kwargs):called.append(True);raise AssertionError('Mutation before history preflight')
  op.atomic=op.stop=mutation
  try:check('oversize-history configure refuses before a journal write or service stop',refused(lambda:rooms.configure(op,config,folder/'managed.json',None)) and not called)
  finally:op.atomic,op.stop=atomic,stop
 check('different tooling requires explicit exact previous-controller compatibility proof',refused(lambda:t.recover()) and t.journal.read_bytes()==jraw and history.read_bytes()==raw and snapshot()['pids']==before['pids'])
 recovered=t.recover(previous_controller=(OLD_DIR,OLD));after=snapshot();c,state=t.room()
 check('actual pending native binding and outer transition recover with corrected controller',recovered['status']=='interrupted-reader-backend-reverted' and recovered['originalControllerPin']==OLD and recovered['recoveryControllerPin']==NEW and not t.journal.exists() and not (CONTROL.parent/'maintenance.json').exists())
 check('current keys accounts private files and root custody are retained',after['keysAndAccountDBSHA256']==before['keysAndAccountDBSHA256'] and after['privateFixtureFileSHA256']==before['privateFixtureFileSHA256'] and custody()==rootkeys)
 check('guest steward and file service processes remain running unchanged',all(after['pids'][r]==before['pids'][r]for r in ['guest','steward','files','filesProxy']))
 check('nonempty current accepted room state and replay floors retained exactly',state==j['baseline'] and sum(row[6]for row in state['rooms'])>=2)
 check('original worker and strict binding restored without changing native code',c==j['before'] and t.read_native()==j['native'] and c['manifestSHA256']=='3907eac6785bc4ad6ca02436949539d0d06de9cdbf78b51f0b96e2d40d6a7a85')
 for role,rows in before['usage'].items():
  fresh={(r[0],r[1]):r[2:]for r in after['usage'][role]}
  for row in rows:assert all(x>=y for x,y in zip(fresh[(row[0],row[1])],row[2:]))
 check('monotonic guest usage retained',True)
 v.update(status='PASS',originalHistoryBytes=len(raw),originalHistorySHA256=hashlib.sha256(raw).hexdigest(),roomHealth=t.manager.health(c),nativePIDs=after['pids'],originalNativeManifestSHA256=OLD,recoveryControllerSHA256=NEW,originalOuterJournalSHA256=hashlib.sha256(jraw).hexdigest(),noManualHistoryPruning=True)
except Exception as error:
 import traceback;v.update(error=str(error),traceback=traceback.format_exc())
finally:a.result.write_text(json.dumps(v,indent=2)+'\n');print(json.dumps({k:v.get(k)for k in ['status','error','originalHistoryBytes','nativePIDs']}))
raise SystemExit(0 if v['status']=='PASS'else 1)
