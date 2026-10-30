#!/usr/bin/env python3
"""Actual native16 interruption, recovery, native15 rollback and re-upgrade.

Only the retained private systemd fixture is changed. The same new controller
and installed native16 operator must pass before they can be used on webhost.
No account, private-file, permission or authority data is restored.
"""
import argparse
import hashlib
import importlib.util
import json
import re
import shlex
import subprocess
import time
from pathlib import Path

ROOT=Path(__file__).resolve().parent.parent
STAGE='/srv/codi-network-fixture'
CONTROL='/etc/codi-native-fixture/managed.json'
NEW='6fbca9e61a02008c32b917e2db5cb8805271b2f6300d97338ea976532cd97200'
OLD='6789b29e7ed65ff2087e791448306ba68ab0b8bcc45ed70cdaa60a23fa404f35'

def run():
 spec=importlib.util.spec_from_file_location('routed_rollout_vm',ROOT/'scripts/upgrade-signin-native-vm.py');vm=importlib.util.module_from_spec(spec);spec.loader.exec_module(vm)
 assert vm.runtime()['manifestSHA256']==NEW
 def remote(command,check=True,input=None):return subprocess.run([*vm.vm.ssh_args(),command],check=check,input=input,capture_output=True,text=True,timeout=210)
 installed=json.loads(remote('cat '+STAGE+'/installed-result.json').stdout)
 raw=(ROOT/'scripts/native-rollout.py').read_bytes();key=hashlib.sha256(raw).hexdigest()
 tool=STAGE+'/tools/routed-rollout-'+key+'.py'
 present=remote('test -e '+tool,check=False);assert present.returncode in (0,1)
 if present.returncode==1:remote('cat > '+tool+' && chmod 0644 '+tool,input=raw.decode())
 assert remote('sha256sum '+tool).stdout.split()[0]==key
 target=STAGE+'/candidate-'+NEW[:16];old=STAGE+'/candidate-'+OLD[:16]
 remote('test -d '+old+' && test -d '+target)
 old_version=json.loads(remote('cat '+old+'/connected-release.json').stdout)['version']
 backups=STAGE+'/routed-rollout-backups';remote('test -d '+backups+' || mkdir -m 0700 '+backups)
 def snapshot():return json.loads(remote(STAGE+'/venv/bin/python -I -B '+STAGE+'/tools/native-network-vm-lifecycle-check.py --snapshot').stdout)
 before=snapshot();checks=[]
 code='''import importlib.util,os,sys
from pathlib import Path
p=Path(OPERATOR);s=importlib.util.spec_from_file_location('routed_rollout_op',p);op=importlib.util.module_from_spec(s);sys.modules[s.name]=op;s.loader.exec_module(op)
s=importlib.util.spec_from_file_location('routed_rollout_controller',CONTROLLER);controller=importlib.util.module_from_spec(s);s.loader.exec_module(controller)
with op.locked(Path(CONTROL)):
 from origin_service import signin_migration
 signin_migration.guard(op,Path(CONTROL),'upgrade')
 def phase(name):
  if name=='checkpointed':os._exit(87)
 c=op.load(Path(CONTROL));controller.upgrade(op,Path(CONTROL),Path(TARGET),Path(c['python']),Path(BACKUPS),phase=phase)
'''.replace('OPERATOR',repr(target+'/scripts/manage-services.py')).replace('CONTROLLER',repr(tool)).replace('CONTROL',repr(CONTROL)).replace('TARGET',repr(old)).replace('BACKUPS',repr(backups))
 interrupted=remote(STAGE+'/venv/bin/python -I -B -c '+shlex.quote(code),check=False)
 assert interrupted.returncode==87,interrupted.stderr
 middle=snapshot();assert middle['pids']['guest']==before['pids']['guest'] and middle['pids']['issuer']==middle['pids']['steward']==0
 checks.append('actual process death after checkpoint preserves guest and stops issuer/steward')
 common=[STAGE+'/venv/bin/python','-I','-B',tool,'recover','--operator',target+'/scripts/manage-services.py','--operator-manifest-sha256',NEW,'--config',CONTROL]
 recovered=json.loads(remote(shlex.join(common)).stdout)
 assert recovered['status']=='interrupted-rollout-resumed-before' and recovered['dataRestored'] is False,recovered
 assert vm.runtime()['manifestSHA256']==NEW
 checks.append('explicit native16 recovery resumes original code without restoring data')
 transitions=[]
 for destination,pin in [(old,OLD),(target,NEW)]:
  args=[STAGE+'/venv/bin/python','-I','-B',tool,'upgrade','--operator',target+'/scripts/manage-services.py','--operator-manifest-sha256',NEW,'--config',CONTROL,'--release',destination,'--python',STAGE+'/venv/bin/python','--backup-parent',backups]
  value=json.loads(remote(shlex.join(args)).stdout)
  assert value['status']=='upgraded' and value['guestCookiePreserved'] and value['checkpointGuestPidPreserved'] and not value['dataRestored'],value
  assert vm.runtime()['manifestSHA256']==pin
  c=json.loads(remote(shlex.join(['curl','--silent','--fail','--insecure','--pinnedpubkey','sha256//'+installed['fixtureSPKI'],'https://127.0.0.1:8443/hidden/config.json'])).stdout)
  assert (c.get('routedGroups')=={'version':'codi-routed-room/2'})==(pin==NEW or old_version=='codi-connected-development/16'),c.keys()
  transitions.append(value)
 checks.append('actual rollback and re-upgrade serve the expected native feature contract')
 after=snapshot()
 for key_name in ['keysAndAccountDBSHA256','privateFixtureFileSHA256']:assert before[key_name]==after[key_name]
 for role in ['files','filesProxy']:assert before['pids'][role]==after['pids'][role]
 for role,rows in before['usage'].items():
  current={(r[0],r[1]):r[2:] for r in after['usage'][role]}
  for row in rows:assert (row[0],row[1]) in current and all(a>=b for a,b in zip(current[(row[0],row[1])],row[2:]))
 assert after['worker']['active'] and after['worker']['kernelMatches'] and not after['worker']['guardFault'] and not after['nativeJournalPresent']
 assert remote('test ! -e /etc/codi-native-fixture/native-rollout.json').returncode==0
 checks.append('keys accounts cookies private files file-service PIDs and usage survive all transitions')
 return {'status':'PASS','checks':checks,'nativeManifestSHA256':NEW,'rollbackManifestSHA256':OLD,'controllerSHA256':key,'controllerRemotePath':tool,'transitions':transitions,'recovery':recovered,'finalRuntime':vm.runtime(),'webhostChanged':False,'dataRestored':False}

if __name__=='__main__':
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--manifest-sha256',default=NEW);parser.add_argument('--previous-manifest-sha256',default=OLD);parser.add_argument('--output',type=Path);args=parser.parse_args()
 NEW,OLD=args.manifest_sha256,args.previous_manifest_sha256
 assert all(re.fullmatch('[0-9a-f]{64}',v) for v in [NEW,OLD])
 result={'status':'FAIL'}
 try:result.update(run())
 finally:
  result['sourceSHA256']=hashlib.sha256(Path(__file__).read_bytes()).hexdigest();path=args.output or ROOT/'.build/checks/routed-native-vm-rollout-result.json'
  if path.exists():path.rename(path.with_name(path.stem+'-before-'+str(time.time_ns())+'.json'))
  path.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
