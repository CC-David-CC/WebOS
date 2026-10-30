#!/usr/bin/env python3
"""Exercise pinned mount backend adapters against installed VM services, readonly."""
import hashlib,importlib.util,json,shlex,subprocess,tarfile,time
from pathlib import Path

ROOT=Path(__file__).resolve().parent.parent


def stage(vm):
    files=[str(p.relative_to(ROOT)) for p in sorted((ROOT/'mount_operator').glob('*.py'))]
    files.append('scripts/migrate-desktop-mount.py')
    records={n:{'bytes':(ROOT/n).stat().st_size,'sha256':hashlib.sha256((ROOT/n).read_bytes()).hexdigest()} for n in files}
    key=hashlib.sha256(json.dumps(records,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    destination='/srv/codi-network-fixture/tools/mount-'+key[:16]
    archive=ROOT/'.build/checks'/('mount-tools-'+key+'.tar')
    with tarfile.open(archive,'w') as out:
        for n in files:out.add(ROOT/n,arcname=n,recursive=False)
    r=subprocess.run([*vm.vm.ssh_args(),'test -e '+shlex.quote(destination)],capture_output=True,timeout=15)
    if r.returncode not in (0,1):raise ValueError('Cannot inspect existing mount tool staging')
    if r.returncode==1:
        with archive.open('rb') as stream:
            subprocess.run([*vm.vm.ssh_args(),'mkdir '+shlex.quote(destination)+' && tar -xf - -C '+shlex.quote(destination)+' && chown -R root:root '+shlex.quote(destination)+' && chmod -R go-w '+shlex.quote(destination)],stdin=stream,check=True,timeout=30)
    for n,r in records.items():
        assert vm.remote('sha256sum '+shlex.quote(destination+'/'+n)).split()[0]==r['sha256']
    return destination,records


def run():
    spec=importlib.util.spec_from_file_location('mount_backend_vm',ROOT/'scripts/upgrade-signin-native-vm.py');vm=importlib.util.module_from_spec(spec);spec.loader.exec_module(vm)
    before=vm.runtime();assert before['manifestSHA256']=='3071d17fa17666e2d9317e96e2e9a79d629e2a16be2e44b9afb0ed9947efd211'
    overlay,records=stage(vm)
    code=r'''
import copy,hashlib,json,pathlib,subprocess,sys,time
P=pathlib.Path;overlay=P(OVERLAY);c=json.loads(P('/etc/codi-native-fixture/managed.json').read_text());sha=lambda p:hashlib.sha256(P(p).read_bytes()).hexdigest();checks=[]
policy=json.loads((P(c['stateRoot'])/'public/origin-discovery.json').read_text())['identity'];policy={**policy,'apiBase':'/api/v1'}
for name,r in RECORDS.items():
 p=overlay/name;s=p.stat();assert not p.is_symlink() and s.st_uid==0 and not s.st_mode&0o022 and r=={'bytes':s.st_size,'sha256':sha(p)}
def args(kind):
 b=c['userFiles' if kind=='files' else 'guestNetwork']
 return [c['python'],'-I','-B',str(overlay/'mount_operator/backends.py'),'--kind',kind,'--config-dir',str(P(b['configFile']).parent),'--operator',b['operatorRelease'],'--operator-sha256',b['operatorManifestSHA256'],'--config-sha256',b['configSHA256']]
def call(p,value):
 p.stdin.write(json.dumps(value)+'\n');p.stdin.flush();line=p.stdout.readline(1048577)
 if not line:raise ValueError(p.stderr.read()[-2000:])
 return json.loads(line)
for kind in ['files','guest']:
 p=subprocess.Popen(args(kind),stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
 try:
  result=call(p,{'action':'prepare','basePath':'','issuerPolicy':policy});assert result['ok'],result;plan=result['value'];assert plan['after']['basePath']==''
  checks.append(kind+': real installed operator derives root config/settings/units')
  assert call(p,{'action':'validate','plan':plan})['ok'];checks.append(kind+': exact prepared plan validates')
  for name,mutate in [
    ('changed port/UID',lambda q:q['after'].__setitem__('uid' if kind=='files' else 'frontendUID',9999)),
    ('arbitrary output',lambda q:q['files'].__setitem__('/etc/passwd',{'before':'','after':'bad','mode':420})),
    ('issuer trust',lambda q:q['policyAfter'].__setitem__('issuer','https://evil.invalid')),
    ('new preimage',lambda q:q['before'].__setitem__('origin','https://evil.invalid'))]:
   q=copy.deepcopy(plan);mutate(q);assert not call(p,{'action':'validate','plan':q})['ok'];checks.append(kind+': refuses '+name)
  raw_before={path:sha(path) for path in plan['files']}
  refused=call(p,{'action':'apply','plan':plan});assert not refused['ok'],refused
  assert raw_before=={path:sha(path) for path in plan['files']};checks.append(kind+': active-service edits refused before any metadata write')
  competing=subprocess.run(args(kind),input=json.dumps({'action':'prepare','basePath':'','issuerPolicy':policy})+'\n',capture_output=True,text=True,timeout=20)
  assert competing.returncode!=0 and 'operation is in progress' in competing.stderr;checks.append(kind+': competing operator lock refused')
 finally:
  p.stdin.close();p.wait(timeout=15);assert p.returncode==0,p.stderr.read()
 again=subprocess.run(args(kind),input=json.dumps({'action':'prepare','basePath':'','issuerPolicy':policy})+'\n',capture_output=True,text=True,timeout=30)
 assert again.returncode==0 and json.loads(again.stdout)['ok'];checks.append(kind+': EOF releases locks for subsequent inspection')
print(json.dumps({'status':'PASS','checks':checks,'overlay':str(overlay),'servicesChanged':False,'metadataChanged':False,'liveWebhostChanged':False}))
'''.replace('OVERLAY',repr(overlay)).replace('RECORDS',repr(records))
    result=json.loads(vm.remote('/srv/codi-network-fixture/venv/bin/python -I -B -c '+shlex.quote(code)))
    assert vm.runtime()==before
    return result|{'sourceSHA256':records,'nativeManifestSHA256':before['manifestSHA256']}


if __name__=='__main__':
    result={'status':'FAIL'}
    try:result.update(run())
    finally:
        result['scriptSHA256']=hashlib.sha256(Path(__file__).read_bytes()).hexdigest();out=ROOT/'.build/checks/mount-backends-vm-result.json'
        if out.exists():out.rename(out.with_name(out.stem+'-before-'+str(time.time_ns())+'.json'))
        out.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
