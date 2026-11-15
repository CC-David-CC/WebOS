#!/usr/bin/env python3
"""Actual forward mount rollback and process-death recovery in the retained VM.

Tests the stopped-service/native authority transition, not public routing. Never
restores account/file data or changes the production host. Leaves VM at root.
"""
import hashlib,importlib.util,json,shlex,subprocess,time
from pathlib import Path

ROOT=Path(__file__).resolve().parent.parent
CONFIG='/etc/codi-native-fixture/managed.json'


def module(name,path):
    spec=importlib.util.spec_from_file_location(name,path);value=importlib.util.module_from_spec(spec);spec.loader.exec_module(value);return value


def run():
    vm=module('mount_cycle_vm',ROOT/'scripts/upgrade-signin-native-vm.py')
    staging=module('mount_cycle_staging',ROOT/'scripts/mount-backends-vm-check.py')
    runtime=vm.runtime();overlay,records=staging.stage(vm);checks=[];transitions=[]
    def remote(command,check=True):
        r=subprocess.run([*vm.vm.ssh_args(),command],capture_output=True,text=True,timeout=360)
        if check and r.returncode:raise ValueError(r.stderr[-6000:] or r.stdout[-6000:])
        return r
    def snapshot():
        return json.loads(remote('/srv/codi-network-fixture/venv/bin/python -I -B /srv/codi-network-fixture/tools/native-network-vm-lifecycle-check.py --snapshot').stdout)
    def cli(action,base=''):
        return shlex.join(['/srv/codi-network-fixture/venv/bin/python','-I','-B',overlay+'/scripts/migrate-desktop-mount.py',action,'--config',CONFIG,'--native-release',runtime['release'],'--native-manifest-sha256',runtime['manifestSHA256'],'--base-path',base,'--seconds','86400'])
    def inspect():
        code=r'''import hashlib,json,pathlib,sqlite3,subprocess
P=pathlib.Path;c=json.loads(P(CONFIG).read_text());state=P(c['stateRoot']);db=sqlite3.connect('file:'+str(state/'operator/root/authority.sqlite3')+'?mode=ro',uri=True);revision=db.execute('SELECT revision FROM authority WHERE id=1').fetchone()[0];db.close();j=P(CONFIG).parent/'maintenance.json'
pids={r:int(subprocess.check_output(['systemctl','show',c['instance']+'-'+r+'.service','-p','MainPID','--value'],text=True)) for r in ['issuer','steward','guest']}
file_cfg=json.loads(P(c['userFiles']['configFile']).read_text());permissions=P(file_cfg['stateRoot'])/'permissions.sqlite3';db=sqlite3.connect('file:'+str(permissions)+'?mode=ro',uri=True);tables={}
for table in ['users','permissions','gateway_auth_metadata','gateway_transfer_metadata']:
 rows=sorted(db.execute('SELECT * FROM '+table).fetchall(),key=repr);tables[table]=hashlib.sha256(repr(rows).encode()).hexdigest()
db.close();print(json.dumps({'basePath':c['basePath'],'rootRevision':revision,'rootFloor':json.loads((P(CONFIG).parent/'recovery-fence.json').read_text())['rootFloor'],'phase':json.loads(j.read_text())['phase'] if j.exists() else None,'nativePIDs':pids,'permissionTableDigests':tables}))'''.replace('CONFIG',repr(CONFIG))
        return json.loads(remote('/usr/bin/python3 -B -c '+shlex.quote(code)).stdout)
    before=snapshot();initial=inspect();assert initial['basePath']=='' and initial['phase'] is None
    def preserved():
        after=snapshot();value=inspect()
        assert before['keysAndAccountDBSHA256']==after['keysAndAccountDBSHA256']
        assert before['privateFixtureFileSHA256']==after['privateFixtureFileSHA256']
        assert initial['permissionTableDigests']==value['permissionTableDigests']
        for role,rows in before['usage'].items():
            current={(r[0],r[1]):r[2:] for r in after['usage'][role]}
            for row in rows:assert (row[0],row[1]) in current and all(a>=b for a,b in zip(current[(row[0],row[1])],row[2:]))
        assert after['worker']['active'] and after['worker']['kernelMatches'] and not after['worker']['guardFault'] and not after['nativeJournalPresent']
        assert value['rootRevision']==value['rootFloor'] and value['phase'] is None and all(value['nativePIDs'].values())
        return value
    value=json.loads(remote(cli('apply','/hidden')).stdout);transitions.append(value)
    current=preserved();assert current['basePath']=='/hidden' and current['rootRevision']>initial['rootRevision']
    checks.append('actual root-to-hidden rollback signs a higher root revision and preserves data')
    for base,phase in [('', 'authority'),('/hidden','backends'),('', 'committed')]:
        prior=current
        code=r'''import os,sys
sys.path[:0]=[OVERLAY,RELEASE]
from mount_operator.coordinator import load_operator,run
op=load_operator(RELEASE,PIN)
def hook(name):
 if name==PHASE:os._exit(87)
run(op,CONFIG,'apply',BASE,86400,hook)
'''.replace('OVERLAY',repr(overlay)).replace('RELEASE',repr(runtime['release'])).replace('PIN',repr(runtime['manifestSHA256'])).replace('PHASE',repr(phase)).replace('CONFIG',repr(CONFIG)).replace('BASE',repr(base))
        killed=remote('/srv/codi-network-fixture/venv/bin/python -I -B -c '+shlex.quote(code),False)
        assert killed.returncode==87,killed.stderr
        # A dead coordinator's helper pipes must close and release backend locks.
        wait_code=r'''import json,pathlib,time
target=TARGET.encode();end=time.monotonic()+8
while True:
 alive=[]
 for p in pathlib.Path('/proc').glob('[0-9]*/cmdline'):
  try:a=p.read_bytes().split(b'\0')
  except (OSError,ProcessLookupError):continue
  if len(a)>3 and a[3]==target:alive.append(int(p.parent.name))
 if not alive:break
 if time.monotonic()>end:raise ValueError('Dead coordinator helpers still hold pipes/locks')
 time.sleep(.1)
print(json.dumps({'helpersExited':True}))'''.replace('TARGET',repr(overlay+'/mount_operator/backends.py'))
        assert json.loads(remote('/usr/bin/python3 -B -c '+shlex.quote(wait_code)).stdout)['helpersExited']
        middle=inspect();assert middle['phase']==phase and middle['rootRevision']==prior['rootRevision']+1 and middle['rootFloor']==middle['rootRevision']
        assert all(middle['nativePIDs'].values()) if phase=='committed' else not any(middle['nativePIDs'].values())
        checks.append('actual coordinator death at '+phase+' retains journal and forward authority floor')
        for action in ['start','renew']:
            denied=remote(shlex.join(['/srv/codi-network-fixture/venv/bin/python','-I','-B',runtime['release']+'/scripts/manage-services.py',action,'--config',CONFIG]),False)
            assert denied.returncode!=0
        assert inspect()['rootRevision']==middle['rootRevision']
        checks.append('pending '+phase+' migration blocks ordinary native start and root renewal')
        result=json.loads(remote(cli('recover')).stdout);transitions.append(result)
        current=preserved();assert current['basePath']==base and current['rootRevision']==middle['rootRevision'] and result['dataRestored'] is False
        checks.append('explicit recovery at '+phase+' reuses committed signed bytes and preserves state')
    assert current['basePath']=='' and current['rootRevision']>initial['rootRevision']
    checks.append('all cycles preserve account/key/cookie files private documents permissions and monotonic usage')
    return {'status':'PASS','scope':__doc__,'checks':checks,'transitions':transitions,'initialRootRevision':initial['rootRevision'],'finalRootRevision':current['rootRevision'],'finalBasePath':current['basePath'],'preservedPrivateFiles':len(before['privateFixtureFileSHA256']),'permissionTablesPreserved':list(initial['permissionTableDigests']),'overlay':overlay,'sourceFiles':records,'liveWebhostChanged':False,'HTTPSRootBrowserTested':False}


if __name__=='__main__':
    result={'status':'FAIL'}
    try:result.update(run())
    finally:
        result['scriptSHA256']=hashlib.sha256(Path(__file__).read_bytes()).hexdigest();out=ROOT/'.build/checks/mount-native-vm-cycle-result.json'
        if out.exists():out.rename(out.with_name(out.stem+'-before-'+str(time.time_ns())+'.json'))
        out.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
