#!/usr/bin/env python3
"""Prepare root/publisher plans against existing VM state without applying them."""
import hashlib,importlib.util,json,shlex,subprocess,tarfile,time
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
def run():
 spec=importlib.util.spec_from_file_location('mount_preflight_vm',ROOT/'scripts/upgrade-signin-native-vm.py');vm=importlib.util.module_from_spec(spec);spec.loader.exec_module(vm)
 vm.vm.status();before=vm.runtime();assert before['manifestSHA256'] in ['6fbca9e61a02008c32b917e2db5cb8805271b2f6300d97338ea976532cd97200','b109768a09f1276047d74616d722f212bb12e261ff437fd1d1a6cccd4963b8cc']
 files=['mount_operator/__init__.py','mount_operator/authority.py'];records={n:{'bytes':(ROOT/n).stat().st_size,'sha256':hashlib.sha256((ROOT/n).read_bytes()).hexdigest()} for n in files}
 key=hashlib.sha256(json.dumps(records,sort_keys=True,separators=(',',':')).encode()).hexdigest();destination='/srv/codi-network-fixture/tools/mount-authority-'+key[:16]
 archive=ROOT/'.build/checks'/('mount-authority-'+key+'.tar')
 with tarfile.open(archive,'w') as out:
  for name in files:out.add(ROOT/name,arcname=name,recursive=False)
 command='mkdir '+shlex.quote(destination)+' && tar -xf - -C '+shlex.quote(destination)+' && chown -R root:root '+shlex.quote(destination)+' && chmod -R go-w '+shlex.quote(destination)
 # Owned fixture source staging; no service/config/private state is changed.
 exists=subprocess.run([*vm.vm.ssh_args(),'test -e '+shlex.quote(destination)],capture_output=True,timeout=10)
 if exists.returncode not in (0,1):raise RuntimeError('Cannot inspect existing VM source staging')
 if exists.returncode==1:
  with archive.open('rb') as stream:subprocess.run([*vm.vm.ssh_args(),command],stdin=stream,check=True,timeout=30)
 code=r'''import hashlib,json,os,pwd,subprocess,sys
from pathlib import Path
records=RECORDS;overlay=Path(OVERLAY);cpath=Path('/etc/codi-native-fixture/managed.json');c=json.loads(cpath.read_text());release=Path(c['release'])
for n,r in records.items():
 p=overlay/n;s=p.stat();assert not p.is_symlink() and s.st_uid==0 and not s.st_mode&0o022 and r=={'bytes':s.st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
sys.path[:0]=[str(overlay),str(release)];from mount_operator import authority as m;from steward.root_authority import RootAuthority;from steward.publisher import PublisherState
state=Path(c['stateRoot']);a=RootAuthority(state/'operator/root');old=a.provision();old_revision=m.provision(old)[0]['revision'];plan=m.prepare(a,'',seconds=86400,minimum_revision=old_revision)
assert a.provision()==old
staged=PublisherState(state/'operator/staging/steward-private/provisioned/ledger');stage_before=m.publisher_row(staged);stage_plan=m.publisher_plan(staged,plan,allow_unbound=True);assert m.publisher_row(staged)==stage_before
child="import json,sys;sys.path[:0]=sys.argv[1:3];from mount_operator import authority as m;from steward.publisher import PublisherState;p=PublisherState(sys.argv[3]);before=m.publisher_row(p);r=m.publisher_plan(p,json.load(sys.stdin));assert m.publisher_row(p)==before;print(json.dumps({'revision':before[3],'seedRevision':before[1],'preparedRootRevision':r['after'][1],'counterRetained':r['before'][3:]==r['after'][3:]}))"
uid=(state/'steward/ledger/publisher.sqlite3').stat().st_uid;user=pwd.getpwuid(uid).pw_name
r=subprocess.run(['runuser','-u',user,'--',c['python'],'-I','-B','-c',child,str(overlay),str(release),str(state/'steward/ledger')],input=json.dumps(plan),capture_output=True,text=True,timeout=20);assert r.returncode==0,r.stderr[-2000:]
assert a.provision()==old and hashlib.sha256(cpath.read_bytes()).hexdigest()==CONFIG_SHA
print(json.dumps({'status':'PASS','scope':'Existing installed private VM authority and both owner-separated publisher ledgers accept readonly root-mount plans; no plan applied.','runtimePublisher':json.loads(r.stdout),'stagingPublisherCounterPreserved':stage_plan['before'][3:]==stage_plan['after'][3:],'oldEndpoint':old['endpoint'],'newEndpoint':plan['after']['endpoint'],'newAPIBase':plan['after']['identity_policy']['apiBase'],'rootKeyAndRealmPreserved':old['root_key']==plan['after']['root_key'] and old['realm']==plan['after']['realm'],'servicesChanged':False,'liveWebhostChanged':False,'overlay':str(overlay)}))
'''.replace('RECORDS',repr(records)).replace('OVERLAY',repr(destination))
 config_sha=vm.remote("sha256sum /etc/codi-native-fixture/managed.json").split()[0];code=code.replace('CONFIG_SHA',repr(config_sha));result=json.loads(vm.remote('/srv/codi-network-fixture/venv/bin/python -I -B -c '+shlex.quote(code)))
 assert vm.runtime()==before
 result['sourceSHA256']={n:r['sha256'] for n,r in records.items()};return result
if __name__=='__main__':
 result={'status':'FAIL'}
 try:result.update(run())
 finally:
  result['scriptSHA256']=hashlib.sha256(Path(__file__).read_bytes()).hexdigest();out=ROOT/'.build/checks/mount-authority-vm-preflight-result.json'
  if out.exists():out.rename(out.with_name(out.stem+'-before-'+str(time.time_ns())+'.json'))
  out.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
