#!/usr/bin/env python3
"""Protected native15 rollout/checkpoint and actual interruption in retained VM."""
import hashlib
import importlib.util
import json
from pathlib import Path
import shlex
import subprocess
import time

ROOT=Path(__file__).resolve().parent.parent
CONTROL='/etc/codi-native-fixture/managed.json';STAGE='/srv/codi-network-fixture'
SHA='5fad3b77a5b3f982345c7bd959789509634076059c0b94403f2148146744fcb8'
R4=STAGE+'/candidate-'+SHA[:16];R3=STAGE+'/candidate-d9fa78abbd45224e'

def run():
    s=importlib.util.spec_from_file_location('signin_rollout_vm',ROOT/'scripts/prepare-native-network-vm.py');vm=importlib.util.module_from_spec(s);s.loader.exec_module(vm);vm.status();checks=[]
    def remote(command,*,input=None,check=True):return subprocess.run([*vm.ssh_args(),command],input=input,text=True,capture_output=True,check=check,timeout=180)
    file=STAGE+'/tools/signin-native-rollout.py';raw=(ROOT/'scripts/native-rollout.py').read_text()
    remote('cat > '+file,input=raw);remote('chmod 0644 '+file)
    pin=hashlib.sha256(raw.encode()).hexdigest();assert remote('sha256sum '+file).stdout.split()[0]==pin
    remote('test -d '+STAGE+'/signin-rollout-backups || mkdir -m 0700 '+STAGE+'/signin-rollout-backups')
    def snapshot():return json.loads(remote(STAGE+'/venv/bin/python -I -B '+STAGE+'/tools/signin-native-vm-migration-check.py --snapshot').stdout)
    before=snapshot();assert before['manifestSHA256']==SHA and all(before['pids'].values())
    code='''import importlib.util,json,os,sys
from pathlib import Path
assert Path('/var/lib/codi-fixture-ready').exists()
p=Path(OPERATOR);s=importlib.util.spec_from_file_location('signin_rollout_op',p);op=importlib.util.module_from_spec(s);sys.modules[s.name]=op;s.loader.exec_module(op)
s=importlib.util.spec_from_file_location('signin_rollout',Path(CONTROLLER));controller=importlib.util.module_from_spec(s);s.loader.exec_module(controller)
with op.locked(Path(CONTROL)):
 from origin_service import signin_migration
 signin_migration.guard(op,Path(CONTROL),'upgrade')
 def phase(name):
  if name=='checkpointed':os._exit(87)
 c=op.load(Path(CONTROL));controller.upgrade(op,Path(CONTROL),Path(TARGET),Path(c['python']),Path(BACKUPS),phase=phase)
'''.replace('OPERATOR',repr(R4+'/scripts/manage-services.py')).replace('CONTROLLER',repr(file)).replace('CONTROL',repr(CONTROL)).replace('TARGET',repr(R3)).replace('BACKUPS',repr(STAGE+'/signin-rollout-backups'))
    interrupted=remote('/srv/codi-network-fixture/venv/bin/python -I -B -c '+shlex.quote(code),check=False)
    assert interrupted.returncode==87,interrupted.stderr[-2400:];checks.append('actual process death after coherent checkpoint')
    middle=snapshot();assert middle['pids']['guest']==before['pids']['guest'] and middle['pids']['issuer']==middle['pids']['steward']==0
    checks.append('checkpoint retains guest process and strict guest backend')
    blocked_args=[STAGE+'/venv/bin/python','-I','-B',R4+'/scripts/manage-services.py','migrate-guest-signin','--config',CONTROL,'--network-operator',STAGE+'/signin-operator-5c51d2c86c214519','--network-worker',STAGE+'/signin-worker-9f9106e682e51bd5','--network-config-directory','/etc/codi-guest-network/wont-create']
    blocked=remote(shlex.join(blocked_args),check=False);assert blocked.returncode!=0 and 'Finish pending native code rollout' in blocked.stderr
    checks.append('pending code rollout fences guest policy migration before any new config')
    common=[STAGE+'/venv/bin/python','-I','-B',file,'recover','--operator',R4+'/scripts/manage-services.py','--operator-manifest-sha256',SHA,'--config',CONTROL]
    recovery=json.loads(remote(shlex.join(common)).stdout);assert recovery['status']=='interrupted-rollout-resumed-before' and recovery.get('dataRestored') is False,recovery
    recovered=snapshot();assert all(recovered['pids'].values()) and recovered['manifestSHA256']==SHA
    checks.append('explicit recovery resumes current code without restoring account state')
    transitions=[]
    for target in [R3,R4]:
        command=[STAGE+'/venv/bin/python','-I','-B',file,'upgrade','--operator',R4+'/scripts/manage-services.py','--operator-manifest-sha256',SHA,'--config',CONTROL,'--release',target,'--python',STAGE+'/venv/bin/python','--backup-parent',STAGE+'/signin-rollout-backups']
        value=json.loads(remote(shlex.join(command)).stdout);assert value['status']=='upgraded' and value['guestCookiePreserved'] and value['checkpointGuestPidPreserved'] and not value['dataRestored'];transitions.append(value)
    after=snapshot();assert after['manifestSHA256']==SHA and after['guestPolicyVersion']=='codi-guest-egress-policy/2' and all(after['pids'].values())
    assert before['keysAccountDBCookieSHA256']==after['keysAccountDBCookieSHA256'] and before['fixturePrivateFilesSHA256']==after['fixturePrivateFilesSHA256'] and before['permissionsLogicalSHA256']==after['permissionsLogicalSHA256']
    for role in ['files','filesProxy']:assert before['pids'][role]==after['pids'][role]
    checks.append('two actual native15 code changes retain strict policy keys accounts cookie files permissions and file PIDs')
    return {'status':'PASS','scope':__doc__,'checks':checks,'before':before,'after':after,'checkpointRecovery':recovery,'transitions':transitions,'controllerSHA256':pin,'liveWebhostChanged':False,'hostFirewallChanged':False}

if __name__=='__main__':
    result={'status':'FAIL'}
    try:result=run()
    finally:
        result['sourceSHA256']=hashlib.sha256(Path(__file__).read_bytes()).hexdigest();p=ROOT/'.build/checks/signin-native-vm-rollout-result.json'
        if p.exists():p.rename(p.with_name('signin-native-vm-rollout-before-'+str(time.time_ns())+'.json'))
        p.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
