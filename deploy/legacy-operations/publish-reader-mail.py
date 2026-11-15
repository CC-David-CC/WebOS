#!/usr/bin/env python3
"""Pinned KSU worker2/native25 publication; backend and native are stable checkpoints.

Root on box-webhost, exact clean Git source, unchanged hosting controller pins.
All state is retained; no authority renewal, route/port/boot change or data restore.
Backend explicit recovery uses the same composition tested in the retained VM.
"""
import argparse
import fcntl
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import socket
import sqlite3
import stat
import time

OLD='9537a6b6d4ab7074512d48e13c46121282980e7197a7aaf3b1c3f7ddc8199f6a'
NEW='46c878c394203e962680e1b09acf51cd5bdf625e5eeea3901f8664d6e2db024e'
WORKER='3a6d3c5184e52858abe324e37fd4ca410f66d7d289468efe6f169352d347727b'
OLD_WORKER='3907eac6785bc4ad6ca02436949539d0d06de9cdbf78b51f0b96e2d40d6a7a85'
OPERATOR='53aa99303600f942a6f40b63718e26f2e73d78bffa0c458ba3d6bebb83a034fc'
OLD_OPERATOR='41776629f6224f12c55e8dae011b0f2f9ca81c574530babe49a2ad50362e0d3f'
DEST=Path('/srv/codi-connected/releases/native25-'+NEW[:16]);OLD_DIR=Path('/srv/codi-connected/releases/native22-'+OLD[:16])
WORKER_DIR=Path('/srv/codi-rooms/workers')/WORKER;OLD_WORKER_DIR=Path('/srv/codi-rooms/workers')/OLD_WORKER
OPERATOR_DIR=Path('/srv/codi-rooms/operators')/OPERATOR;OLD_OPERATOR_DIR=Path('/srv/codi-rooms/operators')/OLD_OPERATOR
PUBLISHER=Path('/srv/codi-connected/publishers/d08b9f7b4137db482577ecc0ac5df619cf62a9678e52a4dd554d575df8a0ce88/publish-hosted-peer.py')
BASELINE=Path('/srv/codi-connected/hosted-peer-inspect-1792890782972029188-result.json')
# Filled from exact frozen source when this publication packet is sealed.
TRANSITION_SHA='636ddac01c1c87d5eb84284b9aa5ba592f9f97f6addc4826afe644a9bd8565a2'


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def module(name,p):
 spec=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m


def main(action,commit):
 assert os.geteuid()==0 and socket.gethostname()=='box-webhost' and re.fullmatch('[a-f0-9]{40}',commit)
 assert sha(PUBLISHER)=='d08b9f7b4137db482577ecc0ac5df619cf62a9678e52a4dd554d575df8a0ce88'
 m=module('directory_publication_retention',PUBLISHER);m.protected(PUBLISHER);m.NATIVE_DIR=DEST
 transition=Path(__file__).with_name('reader-backend-transition.py');m.protected(transition);assert sha(transition)==TRANSITION_SHA
 b=module('directory_publication_backend',transition)
 def config():
  m.protected(m.CONTROL);assert stat.S_IMODE(m.CONTROL.stat().st_mode)==0o600;c=json.loads(m.CONTROL.read_bytes())
  assert c['version']=='codi-managed-instance/5' and c['basePath']=='' and c['origin']=='https://ksu.codes' and c['instance']=='codi-ksu-hidden'
  assert c['stateRoot']=='/var/lib/codi-connected/ksu' and c['python']==str(m.PYTHON)
  assert (c['manifestSHA256'],c['release']) in [(OLD,str(OLD_DIR)),(NEW,str(DEST))]
  assert c['guestNetwork']['policySHA256']=='436096d722a1bfb42935ca817dcaaf74cec7b2856bf229a4f775cc0c7cd2c049'
  assert sha(Path(c['release'])/'connected-release.json')==c['manifestSHA256']
  assert not any((m.CONTROL.parent/n).exists()for n in ['native-rollout.json','site-cutover.json'])
  if action!='recover-backend':assert not (m.CONTROL.parent/'maintenance.json').exists() and not (m.CONTROL.parent/'reader-backend-transition.json').exists() and c.get('hostedRooms')
  return c
 def manager():return m.module('directory_rooms_operator',OPERATOR_DIR/'room_service/operator.py').Manager(m.ROOM_CONFIG)
 def backend():
  op=manager()
  with op.locked():c=op.load();return c,op.inspect(c),op.health(c)
 def usage(c):
  state=Path(json.loads(Path(c['guestNetwork']['configFile']).read_bytes())['stateRoot']);out={}
  for role in ['anonymous','registered']:
   with sqlite3.connect('file:'+str(state/role/'usage.sqlite3')+'?mode=ro',uri=True)as db:out[role]=db.execute('SELECT subject,window,bytes,packets FROM usage ORDER BY subject,window').fetchall()
  return out
 def tooling():return b.Transition(m.CONTROL,m.ROOM_CONFIG/'managed.json',OPERATOR_DIR,OPERATOR,DEST,NEW)
 def bytes_ok():
  contract=module('directory_target_contract',DEST/'origin_service/release.py');v=contract.verify(DEST);assert v['manifestSHA256']==NEW and v['files']==705
  previous=json.loads((OLD_DIR/'connected-release.json').read_bytes())['files'];new=json.loads((DEST/'connected-release.json').read_bytes())['files']
  allowed={'origin_service/release.py','origin_service/deployment.py','origin_service/turn_management.py','origin_service/room_management.py','scripts/manage-services.py'}
  assert {n for n in contract.V19_NATIVE if new[n]!=previous[n]}==allowed
  assert all(new[n]==r for n,r in previous.items()if '/apps/' in n)
  b.graph(OPERATOR_DIR,'room-operator.json',OPERATOR,b.OPERATOR_FILES);b.graph(WORKER_DIR,'room-worker.json',WORKER)
  return v
 def notice(c,fn):
  args=[m.PYTHON,'-I','-B',Path(c['release'])/'scripts/desktop-maintenance.py','--directory',Path(c['stateRoot'])/'public']
  scheduled=json.loads(m.run([*args,'scheduled','--in-seconds','10','--duration','240','--message','Development update in 10 seconds. Please save your work. Unsaved browser work is not backed up; server-saved files remain available.']))
  time.sleep(10);finished=False
  try:value=fn();finished=True;return {'scheduledNotice':scheduled,'operation':value}
  finally:
   message='Development update finished. Reload to load the new version. Unsaved browser work was not backed up.'if finished else'Development update did not finish. Recovery may be needed. Unsaved browser work was not backed up.'
   m.run([*args,'cancelled','--duration','120','--message',message])
 with (m.HOST/'.controller.lock').open('rb')as lock:
  fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB);git=lambda *args:m.run(['runuser','-u','dflanag3','--','git','-C',m.REPO,*args])
  assert git('rev-parse','HEAD')==commit and not git('status','--porcelain') and m.hosting_pins()==m.NEW_PINS
  c=config();before=m.capture(c);usage_before=usage(c);result={'status':'PASS','action':action,'sourceCommit':commit,'beforeManifestSHA256':c['manifestSHA256']}
  room_before=backend()[1]if action not in ['stage','recover-backend']else None
  if action=='stage':
   assert c['manifestSHA256']==OLD
   m.install(m.REPO/'tools/codiserver/reader-mail-native-r1/release',DEST,'connected-release.json',NEW)
   m.install(m.REPO/'tools/codiserver/reader-directory-native-r1/worker',WORKER_DIR,'room-worker.json',WORKER)
   m.install(m.REPO/'tools/codiserver/reader-directory-native-r1/operator',OPERATOR_DIR,'room-operator.json',OPERATOR)
   result['releaseVerification']=bytes_ok();bc,bs,bh=backend();assert bc['manifestSHA256']==OLD_WORKER;result.update(nativeNotActivated=True,backendNotActivated=True,backendHealth=bh)
  elif action in ['activate-backend','rollback-backend','recover-backend']:
   bytes_ok();t=tooling()
   if action=='activate-backend':result['backend']=notice(c,lambda:t.apply(WORKER_DIR,WORKER))
   elif action=='rollback-backend':
    assert c['manifestSHA256']==OLD;result['backend']=notice(c,lambda:t.apply(OLD_WORKER_DIR,OLD_WORKER,OLD_OPERATOR_DIR,OLD_OPERATOR))
   else:result['backend']=t.recover()
   result['backendHealth']=backend()[2]
  elif action in ['activate','rollback-native']:
   bytes_ok();bc,bs,bh=backend();assert bc['manifestSHA256']==WORKER and c['hostedRooms']['operatorManifestSHA256']==OPERATOR
   target=DEST if action=='activate'else OLD_DIR;expected=NEW if action=='activate'else OLD
   if c['manifestSHA256']==expected:result['native']={'status':'native-already-current','servicesRestarted':False}
   else:
    result['native']=notice(c,lambda:m.native('upgrade','--release',target,'--python',m.PYTHON));assert result['native']['operation']['status']=='upgraded'
   bc_after,bs_after,bh_after=backend();retained=m.module('directory_native_retention',OPERATOR_DIR/'room_service/operator.py').retained
   assert config()['manifestSHA256']==expected and bc_after==bc and bh_after==bh and retained(bs,bs_after)
  elif action=='verify':
   assert c['manifestSHA256']==NEW;result['releaseVerification']=bytes_ok();bc,bs,bh=backend();assert bc['manifestSHA256']==WORKER and c['hostedRooms']['operatorManifestSHA256']==OPERATOR
   result['backendHealth']=bh;result['nativeStatus']=m.native('status')
   assert sha(BASELINE)=='43fb53090747c89c43f9b64012416a75a54a21fdf5ad36a1b3f184e860b98e5f';m.preserved(json.loads(BASELINE.read_bytes())['state'],c)
   for role in ['issuer','steward','guest']:
    unit=c['instance']+'-'+role+'.service';assert m.run(['systemctl','show',unit,'-p','UnitFileState','--value'])=='disabled';pid=int(m.run(['systemctl','show',unit,'-p','MainPID','--value']));s=dict(line.split(':',1)for line in Path('/proc',str(pid),'status').read_text().splitlines());assert int(s['Uid'].split()[0])>0 and int(s['CapEff'],16)==0 and s['NoNewPrivs'].strip()=='1'
   assert m.run(['systemctl','show',c['instance']+'-issuer-bootstrap.service','-p','MainPID','--value'])=='0'
  else:raise ValueError('Unknown action')
  after=config();result['state']=m.preserved(before,after);assert m.hosting_pins()==m.NEW_PINS
  usage_after=usage(after)
  for role,rows in usage_before.items():
   current={(r[0],r[1]):r[2:]for r in usage_after[role]}
   for row in rows:assert (row[0],row[1])in current and all(a>=b for a,b in zip(current[(row[0],row[1])],row[2:]))
  if room_before is not None:
   retained=m.module('directory_retained_rooms',OPERATOR_DIR/'room_service/operator.py').retained
   assert retained(room_before,backend()[1])
  result['guestUsageFloorsPreserved']=True
  result.update(afterManifestSHA256=after['manifestSHA256'],nativeConfigSHA256=sha(m.CONTROL),hostingUnchanged=True,routerPortsChanged=False,bootPolicyChanged=False,dataRestored=False,rootMinted=False)
  return result

if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('action',choices=['stage','activate-backend','recover-backend','activate','rollback-native','rollback-backend','verify']);p.add_argument('--commit',required=True);a=p.parse_args()
 try:v=main(a.action,a.commit)
 except Exception as error:
  import traceback;v={'status':'FAIL','action':a.action,'error':str(error),'traceback':traceback.format_exc(),'recoveryRequired':'Inspect retained native/room/backend journals; no data restore'}
 receipt=Path('/srv/codi-connected')/('reader-mail-'+a.action+'-'+str(time.time_ns())+'-result.json');fd=os.open(receipt,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
 with os.fdopen(fd,'w')as stream:json.dump(v,stream,indent=2);stream.write('\n')
 print(json.dumps({'status':v['status'],'action':a.action,'rootReceipt':str(receipt),'rootReceiptSHA256':sha(receipt),'nativeManifestSHA256':v.get('afterManifestSHA256'),'error':v.get('error')}));raise SystemExit(0 if v['status']=='PASS'else 1)
