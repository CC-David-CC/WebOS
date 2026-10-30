#!/usr/bin/env python3
"""Actual retained VM HTTPS root ingress and real xterm/v86 touch acceptance.

Only the owned fixture ingress unit is changed; production hosting is untouched.
The fixture reads the real native mount instead of rewriting / into /hidden/.
"""
import copy,hashlib,importlib.util,json,shlex,subprocess,time
from pathlib import Path
from types import SimpleNamespace
from urllib.parse import urlsplit

ROOT=Path(__file__).resolve().parent.parent


def module(name,path):
    spec=importlib.util.spec_from_file_location(name,path);value=importlib.util.module_from_spec(spec);spec.loader.exec_module(value);return value


def run():
    vm=module('root_browser_vm',ROOT/'scripts/upgrade-signin-native-vm.py');before=vm.runtime()
    cycle=json.loads((ROOT/'.build/checks/mount-native-vm-cycle-result.json').read_text());assert cycle['status']=='PASS' and cycle['finalBasePath']==''
    raw=(ROOT/'scripts/native-network-vm-services.py').read_bytes();source_pin=hashlib.sha256(raw).hexdigest()
    code=r'''import hashlib,json,pathlib,subprocess,sys,time,urllib.request,ssl
P=pathlib.Path;v=json.load(sys.stdin);source=bytes.fromhex(v['sourceHex']);assert hashlib.sha256(source).hexdigest()==v['sourceSHA256'];sys.path[:0]=[v['overlay'],v['release']]
from mount_operator.coordinator import load_operator
op=load_operator(v['release'],v['nativeSHA256']);control=P('/etc/codi-native-fixture/managed.json');unit=P('/etc/systemd/system/codi-fixture-ingress.service');destination=P('/srv/codi-network-fixture/tools')/('native-root-ingress-'+v['sourceSHA256']+'.py')
expected=('[Service]\nType=exec\nExecStart=/srv/codi-network-fixture/venv/bin/python -I -B /srv/codi-network-fixture/tools/native-network-vm-services.py --certificate /etc/codi-fixture-tls/cert.pem --key /etc/codi-fixture-tls/key.pem --legacy-release /srv/codi-network-fixture/candidate-abb67a1f7a2e718c\nEnvironment=PYTHONDONTWRITEBYTECODE=1\n').encode()
after=expected.replace(b'/srv/codi-network-fixture/tools/native-network-vm-services.py',str(destination).encode()).replace(b'\nEnvironment=',b' --native-config /etc/codi-native-fixture/managed.json\nEnvironment=')
with op.locked(control):
 c=op.load(control);assert c['basePath']=='' and not (control.parent/'maintenance.json').exists()
 pids=lambda:{r:int(op.systemctl('show',op.unit(c,r),'-p','MainPID','--value')) for r in op.ROLES}
 native_before=pids();current=op.read_owned(unit,0,0o644);assert current in [expected,after]
 if destination.exists():assert op.read_owned(destination,0,0o644,1048576)==source
 else:op.atomic(destination,source,0o644)
 backup=destination.with_suffix('.before.service')
 if backup.exists():assert op.read_owned(backup,0,0o644)==expected
 else:op.atomic(backup,expected,0o644)
 changed=current!=after
 if changed:
  op.systemctl('stop',unit.name);op.atomic(unit,after,0o644);op.systemctl('daemon-reload');op.systemctl('start',unit.name)
 context=ssl._create_unverified_context();deadline=time.monotonic()+20
 while True:
  try:
   with urllib.request.urlopen('https://127.0.0.1:8443/fixture-health',context=context,timeout=2) as r:assert json.load(r)['status']=='ok'
   break
  except (OSError,ValueError):
   if time.monotonic()>deadline:raise
   time.sleep(.1)
 assert native_before==pids();pid=int(op.systemctl('show',unit.name,'-p','MainPID','--value'));assert str(destination).encode() in P('/proc',str(pid),'cmdline').read_bytes()
 print(json.dumps({'status':'PASS','scope':'Owned private fixture root ingress only; readiness uses its local self-signed listener, browser SPKI checked separately','sourceSHA256':v['sourceSHA256'],'unitSHA256':hashlib.sha256(after).hexdigest(),'previousUnitSHA256':hashlib.sha256(expected).hexdigest(),'fixtureIngressPID':pid,'fixtureIngressRestarted':changed,'nativePIDsUnchanged':True,'nativeBasePath':'','productionHostingChanged':False}))
'''
    payload={'sourceHex':raw.hex(),'sourceSHA256':source_pin,'overlay':cycle['overlay'],'release':before['release'],'nativeSHA256':before['manifestSHA256']}
    remote=subprocess.run([*vm.vm.ssh_args(),'/srv/codi-network-fixture/venv/bin/python -I -B -c '+shlex.quote(code)],input=json.dumps(payload),capture_output=True,text=True,timeout=180)
    if remote.returncode:raise ValueError(remote.stderr[-6000:] or remote.stdout[-6000:])
    ingress=json.loads(remote.stdout);(ROOT/'.build/checks/mount-root-vm-ingress-result.json').write_text(json.dumps(ingress,indent=2)+'\n')
    installed=json.loads(vm.remote('cat /srv/codi-network-fixture/installed-result.json'))
    suite=module('root_terminal_browser',ROOT/'scripts/xterm-browser-check.py');original=suite.call;paths=set()
    def call(path,data=None,method=None):
        if path=='/session':
            data=copy.deepcopy(data);options=data['capabilities']['alwaysMatch'];options.setdefault('goog:loggingPrefs',{})['performance']='ALL';args=options['goog:chromeOptions']['args'];assert not any('ignore-certificate' in x for x in args);args.append('--ignore-certificate-errors-spki-list='+installed['fixtureSPKI'])
        if method=='DELETE' and path.startswith('/session/'):
            for row in original(path+'/log',{'type':'performance'}):
                message=json.loads(row['message'])['message']
                if message['method']!='Network.requestWillBeSent':continue
                url=urlsplit(message['params']['request']['url'])
                if url.netloc==urlsplit(installed['publicOrigin']).netloc:paths.add(url.path)
        return original(path,data,method)
    suite.call=call;result=suite.browser(SimpleNamespace(origin=installed['publicOrigin'],base=''))
    assert len(result['checks'])==38 and vm.runtime()==before
    assert '/' in paths and '/config.json' in paths and not any(p=='/hidden' or p.startswith('/hidden/') for p in paths)
    return result|{'scope':__doc__,'fixtureIngress':ingress,'actualRootURL':installed['publicOrigin']+'/','nativeManifestSHA256':before['manifestSHA256'],'fixtureSPKIOnly':True,'liveWebhostChanged':False,'sameOriginRequestPaths':sorted(paths),'noHiddenDependencyObserved':True,'suiteSourceSHA256':hashlib.sha256((ROOT/'scripts/xterm-browser-check.py').read_bytes()).hexdigest()}


if __name__=='__main__':
    result={'status':'FAIL'}
    try:result.update(run())
    finally:
        result['scriptSHA256']=hashlib.sha256(Path(__file__).read_bytes()).hexdigest();out=ROOT/'.build/checks/mount-root-browser-result.json'
        if out.exists():out.rename(out.with_name(out.stem+'-before-'+str(time.time_ns())+'.json'))
        out.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
