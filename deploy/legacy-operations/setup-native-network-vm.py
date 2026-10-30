#!/usr/bin/env python3
"""Install sealed native/worker fixtures inside the private KVM guest only."""
import argparse
import base64
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import grp
import pwd
import subprocess
import sys
import tarfile
import time

ROOT=Path(__file__).resolve().parent.parent
STAGE=Path('/srv/codi-network-fixture')
def run(args,**kwargs):
    value=subprocess.run(list(map(str,args)),capture_output=True,text=True,timeout=180,**kwargs)
    if value.returncode:raise RuntimeError((value.stderr or value.stdout)[-3000:])
    return value.stdout
def sha(file):return hashlib.sha256(file.read_bytes()).hexdigest()
def write(file,value,mode=0o600):
    file.write_text(json.dumps(value,indent=2)+'\n');file.chmod(mode)
def inside(public_port,resume_files=False):
    if os.geteuid()!=0 or not Path('/var/lib/codi-fixture-ready').is_file() or not (STAGE/'input.json').is_file() or type(public_port) is not int or not 1024<=public_port<=65535:raise ValueError('Only the newly prepared private VM can run this installation')
    inputs=json.loads((STAGE/'input.json').read_text());native=STAGE/'native';python=STAGE/'venv/bin/python';control=Path('/etc/codi-native-fixture/managed.json');state=Path('/var/lib/codi-native-fixture')
    if control.exists() and not resume_files:raise ValueError('Retain configured VM; do not overwrite account/worker state by rerunning setup')
    for name,manifest,digest in inputs['packages']:
        if sha(STAGE/name/manifest)!=digest:raise ValueError('Uploaded package pin changed '+name)
    run(['chown','-R','root:root',STAGE]);run(['chmod','-R','go-w',STAGE])
    for name in ['native','legacy11']:
        result=run([python,'-I','-B',STAGE/name/'scripts/manage-services.py','--help'])
        if 'prepare' not in result:raise ValueError('Native CLI imports failed')
    def tool(action,*options):return json.loads(run([python,'-I','-B',native/'scripts/manage-services.py',action,'--config',control,*options]))
    origin='https://127.0.0.1:'+str(public_port);instance='codi-network-fixture';network_control=Path('/etc/codi-guest-network/fixture')
    if resume_files:
        current=json.loads(control.read_text())
        if current['version']!='codi-managed-instance/3' or current['release']!=str(native) or current['origin']!=origin or Path('/etc/codi-user-files/fixture/managed.json').exists():raise ValueError('Resume is only for the verified failure before file configuration')
        if json.loads((state/'public/origin-discovery.json').read_text())['identity']!=json.loads((STAGE/'issuer-policy.json').read_text()):raise ValueError('Preserve issuer identity during resume')
        status=json.loads(run([python,'-I','-B',STAGE/'guest-operator/scripts/manage-guest-network.py','status','--config-dir',network_control]))
        if status['active'] or status['guardFault'] or status['kernelMatches']:raise ValueError('Resume must not change an active network backend')
    else:
        run([python,'-I','-B',native/'scripts/install-service-accounts.py','--guest-gid','1001','--apply'])
        for user in ['codi-net-anonymous','codi-net-registered','codi-gateway']:
            try:who=pwd.getpwnam(user)
            except KeyError:
                run(['useradd','--system','--user-group','--home-dir','/nonexistent','--shell','/usr/sbin/nologin',user]);who=pwd.getpwnam(user)
            if not 0<who.pw_uid<1000 or who.pw_dir!='/nonexistent' or who.pw_shell!='/usr/sbin/nologin' or grp.getgrgid(who.pw_gid).gr_name!=user or os.getgrouplist(user,who.pw_gid)!=[who.pw_gid] or run(['passwd','-S',user]).split()[1]!='L':raise ValueError('Unexpected existing fixture service identity')
        for folder in ['/etc/codi-native-fixture','/etc/codi-guest-network','/etc/codi-guest-network/fixture','/etc/codi-user-files','/etc/codi-user-files/fixture','/etc/codi-fixture-tls']:Path(folder).mkdir(mode=0o755,exist_ok=True)
        run(['sysctl','-w','net.ipv4.ping_group_range=1000 1001']);assert Path('/proc/sys/net/ipv4/ip_forward').read_text().strip()=='0'
        tool('prepare','--release',native,'--python',python,'--state-root',state,'--unit-dir','/etc/systemd/system','--instance',instance,'--origin',origin,'--base-path','/hidden','--issuer-port','8118','--steward-port','8119','--guest-port','8132')
        tool('provision','--seconds','7200');tool('start','--roles','issuer','steward','guest');tool('stop','--roles','issuer','steward')
        Path('/var/lib/codi-fixture-backups').mkdir(mode=0o700);tool('backup','--output','/var/lib/codi-fixture-backups/before-network');tool('start','--roles','issuer','steward');tool('configure-turn','--disable')
        identity=json.loads((state/'public/origin-discovery.json').read_text())['identity'];write(STAGE/'issuer-policy.json',identity,0o644)
        policy={'version':'codi-guest-egress-policy/1','ownPublicIPv4':['1.1.1.1'],'dnsIPv4':['1.1.1.3']};write(STAGE/'egress-policy.json',policy,0o644)
        guest=json.loads(run([python,'-I','-B',STAGE/'guest-operator/scripts/manage-guest-network.py','configure','--config-dir',network_control,'--instance','codi-net-network-fixture','--worker',STAGE/'guest-worker','--worker-sha256',inputs['guestWorkerSHA256'],'--python',python,'--state-root','/var/lib/codi-guest-network-fixture','--issuer-policy',STAGE/'issuer-policy.json','--egress-policy',STAGE/'egress-policy.json','--base-path','/hidden']))
        assert not guest['started'] and not guest['bootEnabled']
    file_state=Path('/var/lib/codi-files-fixture');file_data=Path('/srv/codi-files-fixture')
    for folder in [file_state,file_data]:run(['install','-d','-m','0700','-o','codi-gateway','-g','codi-gateway',folder])
    seed='import sys;sys.path.insert(0,sys.argv[1]);from gateway_service.user_store import UserStore;UserStore(sys.argv[2],sys.argv[3])'
    run(['runuser','-u','codi-gateway','--',python,'-I','-B','-c',seed,STAGE/'file-worker',file_state,file_data])
    files_control=Path('/etc/codi-user-files/fixture')
    def files(action,*options):return json.loads(run([python,'-I','-B',STAGE/'file-operator/scripts/manage-user-files.py',action,'--config-dir',files_control,*options]))
    files('configure','--instance','codi-files-network-fixture','--user','codi-gateway','--release',STAGE/'file-worker','--manifest-sha256',inputs['fileWorkerSHA256'],'--python',python,'--state-root',file_state,'--data-root',file_data,'--issuer-policy',STAGE/'issuer-policy.json','--base-path','/hidden','--port','8140','--unit-dir','/etc/systemd/system');files('initialize');files('start')
    tool('configure-user-files','--gateway-config',files_control/'managed.json','--file-operator',STAGE/'file-operator')
    for address in ['1.1.1.1','1.1.1.2','1.1.1.3','10.222.0.1','172.22.0.1','192.168.222.1','169.254.169.254']:run(['ip','address','add',address+'/32','dev','lo'])
    tls=Path('/etc/codi-fixture-tls');tls.chmod(0o700)
    run(['openssl','req','-x509','-newkey','rsa:2048','-nodes','-subj','/CN=127.0.0.1','-addext','subjectAltName=IP:127.0.0.1,IP:1.1.1.1,IP:1.1.1.2','-days','2','-keyout',tls/'key.pem','-out',tls/'cert.pem']);(tls/'key.pem').chmod(0o600)
    pub=run(['openssl','x509','-in',tls/'cert.pem','-pubkey','-noout'])
    der=subprocess.run(['openssl','pkey','-pubin','-outform','DER'],input=pub.encode(),check=True,capture_output=True).stdout;spki=base64.b64encode(hashlib.sha256(der).digest()).decode()
    services='[Service]\nType=exec\nExecStart='+str(python)+' -I -B '+str(STAGE/'tools/native-network-vm-services.py')+' --certificate '+str(tls/'cert.pem')+' --key '+str(tls/'key.pem')+'\nEnvironment=PYTHONDONTWRITEBYTECODE=1\n'
    unit=Path('/etc/systemd/system/codi-fixture-ingress.service');unit.write_text(services);unit.chmod(0o644);run(['systemctl','daemon-reload']);run(['systemctl','start',unit.name])
    def pids():return {role:int(run(['systemctl','show',instance+'-'+role+'.service','-p','MainPID','--value']).strip()) for role in ['issuer','steward','guest']}
    before=pids();activated=tool('configure-guest-network','--network-config',network_control/'managed.json','--network-operator',STAGE/'guest-operator');after=pids()
    assert activated['status']=='network-configured' and activated['enabled'] and before['steward']==after['steward'] and before['guest']!=after['guest']
    status=json.loads(run([python,'-I','-B',STAGE/'guest-operator/scripts/manage-guest-network.py','status','--config-dir',network_control]));assert status['active'] and status['kernelMatches'] and not status['guardFault']
    value={'status':'PASS','scope':'Actual native12 schema4-to5 installation with sealed external controller, systemd workers/kernel and private Files inside the disposable VM; browser proof pending','nativeSHA256':inputs['nativeSHA256'],'guestWorkerSHA256':inputs['guestWorkerSHA256'],'guestOperatorSHA256':inputs['guestOperatorSHA256'],'publicOrigin':origin,'fixtureSPKI':spki,'activation':activated,'nativePIDsBefore':before,'nativePIDsAfter':after,'backendStatus':status,'hostFirewallChanged':False,'liveWebhostChanged':False}
    write(STAGE/'installed-result.json',value);print(json.dumps(value,indent=2))
def upload():
    spec=importlib.util.spec_from_file_location('private_fixture_vm',ROOT/'scripts/prepare-native-network-vm.py');vm=importlib.util.module_from_spec(spec);spec.loader.exec_module(vm);status=vm.status()
    run([*vm.ssh_args(),'test ! -e /srv/codi-network-fixture'])
    inputs=[('native',ROOT/'.build/releases/connected-network-r1','connected-release.json'),('legacy11',ROOT/'.build/releases/connected-files-r2','connected-release.json'),('guest-worker',ROOT/'.build/guest-workers/guest-wire-r1','guest-wire.json'),('guest-operator',ROOT/'.build/guest-operators/persistent-guest-r1','guest-operator.json'),('file-worker',ROOT/'.build/gateways/user-files-r4','files-service.json'),('file-operator',ROOT/'.build/file-operators/private-files-r6','file-operator.json')]
    hashes={name:sha(source/manifest) for name,source,manifest in inputs};metadata={'packages':[(name,manifest,hashes[name]) for name,source,manifest in inputs],'nativeSHA256':hashes['native'],'guestWorkerSHA256':hashes['guest-worker'],'guestOperatorSHA256':hashes['guest-operator'],'fileWorkerSHA256':hashes['file-worker']}
    payload=vm.FOLDER/'payload.tar.gz'
    with tarfile.open(payload,'w:gz',compresslevel=1) as archive:
        for name,source,manifest in inputs:archive.add(source,arcname='codi-network-fixture/'+name)
        archive.add(ROOT/'.venv',arcname='codi-network-fixture/venv')
        for name in ['setup-native-network-vm.py','native-network-vm-services.py']:archive.add(ROOT/'scripts'/name,arcname='codi-network-fixture/tools/'+name)
    with payload.open('rb') as stream:subprocess.run([*vm.ssh_args(),'tar -xzf - -C /srv'],stdin=stream,check=True,timeout=180)
    run([*vm.ssh_args(),'cat > /srv/codi-network-fixture/input.json'],input=json.dumps(metadata))
    print(json.dumps({'phase':'protected fixture packages uploaded','packages':hashes}),flush=True)
    print(run([*vm.ssh_args(),'/srv/codi-network-fixture/venv/bin/python -I -B /srv/codi-network-fixture/tools/setup-native-network-vm.py --inside --public-port '+str(status['httpsPort'])]),flush=True)
if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--inside',action='store_true');parser.add_argument('--resume-files',action='store_true');parser.add_argument('--public-port',type=int);args=parser.parse_args()
    if args.inside:inside(args.public_port,args.resume_files)
    else:upload()
