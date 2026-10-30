#!/usr/bin/env python3
"""Inspect the published native22/24 desktop and preserved data; fetch public bytes.

No service restart, authority renewal, data restore or hosting mutation. Root
inspection uses the protected publisher and its original pre-upgrade receipt.
Browser flow and independent-WAN acceptance are separate evidence.
"""
import argparse
from concurrent.futures import ThreadPoolExecutor
import datetime
import hashlib
import json
from pathlib import Path
import shlex
import subprocess
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
APPROVED_PINS = {'115f7a79f5a74a6ba7afe8657beaad8dfbb0970f098345cf8b446daf2ec1fba0',
                 '5ad8cefa2de56378b76fafdbdd3c35f4dfc738104d286577adcf8b6b6accd1b0',
                 'a5d5a90767f4d8cc68054470a39394853835670bdc8decd11ad4afe3f9ae0d07',
                 '9537a6b6d4ab7074512d48e13c46121282980e7197a7aaf3b1c3f7ddc8199f6a',
                 'ba89487b3ea3fbca334abd3cc8f3467b8dd604bab51a141ed221236a4c1871f5'}
REMOTE = r'''
import datetime,fcntl,hashlib,importlib.util,json,os,pathlib,sqlite3,subprocess,sys
P=pathlib.Path;sha=lambda p:hashlib.sha256(P(p).read_bytes()).hexdigest()
publisher=P('/srv/codi-connected/publishers/d08b9f7b4137db482577ecc0ac5df619cf62a9678e52a4dd554d575df8a0ce88/publish-hosted-peer.py')
assert sha(publisher)=='d08b9f7b4137db482577ecc0ac5df619cf62a9678e52a4dd554d575df8a0ce88'
s=importlib.util.spec_from_file_location('hosted_live_publisher',publisher);m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
if '__EXPECTED_NATIVE_MANIFEST__'=='ba89487b3ea3fbca334abd3cc8f3467b8dd604bab51a141ed221236a4c1871f5':m.OPERATOR_DIR=P('/srv/codi-rooms/operators/53aa99303600f942a6f40b63718e26f2e73d78bffa0c458ba3d6bebb83a034fc')
with (m.HOST/'.controller.lock').open('rb') as hosting:
 fcntl.flock(hosting,fcntl.LOCK_EX|fcntl.LOCK_NB);m.protected(m.CONTROL);c=json.loads(m.CONTROL.read_bytes())
 assert c['manifestSHA256']=='__EXPECTED_NATIVE_MANIFEST__' and c['basePath']=='' and c['origin']=='https://ksu.codes' and c['instance']=='codi-ksu-hidden'
 release=P(c['release']);assert sha(release/'connected-release.json')==c['manifestSHA256']
 assert sha(release/'scripts/manage-services.py')=='__EXPECTED_MANAGEMENT_SHA__'
 op=m.module('hosted_live_native_status',release/'scripts/manage-services.py')
 with op.locked(m.CONTROL):
  op.load(m.CONTROL);op.ready(c,op.ROLES)
  assert not any((m.CONTROL.parent/n).exists() for n in ['site-cutover.json','maintenance.json','native-rollout.json','guest-signin-migration.json'])
 manager=m.room_manager()
 with manager.locked():health=manager.health(manager.load())
 assert m.hosting_pins()==m.NEW_PINS
 common,_=m.hosting_modules();assert common.caddy(common.load(),'production')==P('/etc/caddy/Caddyfile').read_text()
 value={'state':m.capture(c),'roomHealth':health,'hostingPins':m.hosting_pins()}
receipt=P('/srv/codi-connected/hosted-peer-inspect-1792890782972029188-result.json')
assert sha(receipt)=='43fb53090747c89c43f9b64012416a75a54a21fdf5ad36a1b3f184e860b98e5f'
before=json.loads(receipt.read_bytes())['state'];now=value['state']
for name in ['keys','cookie','fileConfig','filesPIDs','website','prototypeManifest','blog']:assert now[name]==before[name],name
for name in ['accounts','users','permissions']:assert set(before[name])<=set(now[name]),name
for name,pin in before['documents'].items():assert now['documents'].get(name)==pin
for name in ['issuerKeyId','rootKeyId','realm','serviceKeyId','rootRevision']:assert now['authorityBinding'][name]==before['authorityBinding'][name],name
assert now['authorityBinding']['publisherRevision']>=before['authorityBinding']['publisherRevision']
release=P(c['release']);manifest=json.loads((release/'connected-release.json').read_bytes())
assert len(manifest['files'])==__EXPECTED_FILES__
for name,record in manifest['files'].items():
 p=release/name;assert not p.is_symlink() and p.is_file() and record=={'bytes':p.stat().st_size,'sha256':sha(p)},name
website=P(now['website']);prototype=website/'public/desktop';pm=json.loads((prototype/'release.json').read_bytes());assert len(pm['files'])==133
for name,record in pm['files'].items():
 p=prototype/name;assert record=={'bytes':p.stat().st_size,'sha256':sha(p)},name
cfg=json.loads((prototype/'config.json').read_bytes());assert cfg['identity']['mode']=='local-development' and not cfg['identity'].get('apiBase') and not cfg.get('guestNetwork')
state=P(c['stateRoot']);sys.path[:0]=[str(release),str(release/'codiserver-server-v0.3.0')]
from steward.protocol import jose
seed=jose.inspect(json.loads((state/'steward/provision.json').read_bytes())['seed'],'codi-seed/1',32768)[1]
assert seed['revision']==3 and seed['exp']>__import__('time').time()
from origin_service import network_management
native_spec=importlib.util.spec_from_file_location('hosted_live_native',release/'scripts/manage-services.py');op=importlib.util.module_from_spec(native_spec);sys.modules[native_spec.name]=op;native_spec.loader.exec_module(op)
guard=network_management.Binding(op,c,c['guestNetwork']).run('status');assert guard['active'] and guard['kernelMatches'] and not guard['guardFault'] and not guard['bootEnabled']
assert sha('/etc/codi-relay/ksu/managed.json')=='5ab3e23016cd673146f1c6925aac0826368a4eff54b0fabdb9a28d7276c998a4' and P('/proc/sys/net/ipv4/ip_forward').read_text().strip()=='0'
native_pids={role:int(op.systemctl('show',op.unit(c,role),'-p','MainPID','--value')) for role in op.ROLES}
for role,pid in native_pids.items():
 assert pid>0 and op.systemctl('show',op.unit(c,role),'-p','UnitFileState','--value').strip()=='disabled'
 ps=dict(line.split(':',1) for line in P('/proc',str(pid),'status').read_text().splitlines());assert int(ps['Uid'].split()[0])>0 and int(ps['CapEff'],16)==0 and ps['NoNewPrivs'].strip()=='1'
assert op.systemctl('show',op.unit(c,'issuer-bootstrap'),'-p','MainPID','--value').strip()=='0'
health=value['roomHealth'];assert health['status']=='PASS' and health['privateNetworkNamespace'] and health['emptyCapabilities'] and not health['bootEnabled']
room_config=json.loads(P('/etc/codi-rooms/ksu/managed.json').read_bytes());assert room_config['manifestSHA256']=='__EXPECTED_ROOM_WORKER__'
smoke=json.loads(P('/home/dflanag3/webhost-sites/reports/private/hosted-peer-native21-smoke.json').read_bytes());assert len(smoke['sites'])==10 and all(v['result']=='PASS' for v in smoke['sites'].values())
print(json.dumps({'status':'PASS','nativeManifestSHA256':c['manifestSHA256'],'nativeConfigSHA256':sha(m.CONTROL),'nativePIDs':native_pids,'filePIDs':now['filesPIDs'],'nativeUnitsDisabledForBoot':True,'verifiedReleaseFiles':__EXPECTED_FILES__,'keysRealmCookieAndOriginalAccountsPreserved':True,'originalAccountCount':len(before['accounts']),'currentAccountCount':len(now['accounts']),'originalPermissionsAndDocumentsPreserved':True,'originalDocumentCount':len(before['documents']),'rootRevision':3,'rootExpiresAt':datetime.datetime.fromtimestamp(seed['exp'],datetime.timezone.utc).isoformat(),'publisherRevision':now['authorityBinding']['publisherRevision'],'prototypeManifestSHA256':now['prototypeManifest'],'prototypeFiles':pm['files'],'prototypeBackendFree':True,'websiteRelease':now['website'],'blogSHA256':now['blog'],'hostingPins':value['hostingPins'],'roomHealth':health,'roomWorkerManifestSHA256':room_config['manifestSHA256'],'all10SiteSmoke':'PASS','registeredOnlyEgressPolicyUnchanged':True,'guestKernelGuardHealthy':True,'relayConfigUnchanged':True,'forwardingDisabled':True,'servicesRestarted':False,'privateStateExported':False}))
'''


def fetch(path):
    with urllib.request.urlopen('https://ksu.codes/' + path, timeout=30) as response:
        return response.read(), response.geturl()


def run(release):
    pin = hashlib.sha256((release/'connected-release.json').read_bytes()).hexdigest()
    assert pin in APPROVED_PINS
    bootstrap = "import json,os,pathlib,sys;c=json.loads(pathlib.Path('/etc/codi-connected/ksu/managed.json').read_text());code=sys.stdin.read();os.execv(c['python'],[c['python'],'-I','-B','-c',code])"
    child = subprocess.run(['ssh', '-o', 'BatchMode=yes', 'box-webhost', 'sudo', '-n', '/usr/bin/python3', '-I', '-B', '-c', shlex.quote(bootstrap)], input=REMOTE.replace('__EXPECTED_NATIVE_MANIFEST__', pin).replace('__EXPECTED_MANAGEMENT_SHA__', hashlib.sha256((release/'scripts/manage-services.py').read_bytes()).hexdigest()).replace('__EXPECTED_FILES__', '660' if pin.startswith('ba89487b') else '615' if pin.startswith('9537a6b6') else '571').replace('__EXPECTED_ROOM_WORKER__', '3a6d3c5184e52858abe324e37fd4ca410f66d7d289468efe6f169352d347727b' if pin.startswith('ba89487b') else '3907eac6785bc4ad6ca02436949539d0d06de9cdbf78b51f0b96e2d40d6a7a85'), capture_output=True, text=True, timeout=180)
    if child.returncode:
        raise ValueError(child.stderr[-5000:] or child.stdout[-3000:])
    value = json.loads(child.stdout)
    assert value['nativeManifestSHA256'] == pin
    def prototype(record):
        name, expected = record
        body, _ = fetch('desktop/' + name)
        assert expected == {'bytes': len(body), 'sha256': hashlib.sha256(body).hexdigest()}, name
    with ThreadPoolExecutor(max_workers=6) as pool:
        list(pool.map(prototype, value.pop('prototypeFiles').items()))
    for name in ['index.html', 'assets/desktop/network-release.json', 'assets/desktop/offline-worker.js']:
        body, _ = fetch(name)
        assert body == (release/name).read_bytes(), name
    blog, url = fetch('blog/')
    assert url == 'https://ksu.codes/blog/' and hashlib.sha256(blog).hexdigest() == value['blogSHA256']
    for old in ['hidden', 'hidden/']:
        body, url = fetch(old)
        assert url == 'https://ksu.codes/' and body == (release/'index.html').read_bytes()
    value.update(defaultPublicTLS=True, publicPrototypeFilesVerified=133, publicNativeAssetsMatched=3, publicBlogBytesPreserved=True, hiddenRedirectsToActualRoot=True, observedAt=datetime.datetime.now(datetime.timezone.utc).isoformat(), sourceSHA256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(), wholeGoalComplete=False)
    return value


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--release', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    assert not args.output.exists()
    try:
        result = run(args.release.resolve())
    except Exception as error:
        result = {'status': 'FAIL', 'error': str(error), 'wholeGoalComplete': False}
    args.output.write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps({key: result.get(key) for key in ['status', 'error', 'nativeManifestSHA256', 'publicPrototypeFilesVerified', 'rootExpiresAt', 'wholeGoalComplete']}))
    raise SystemExit(0 if result['status'] == 'PASS' else 1)
