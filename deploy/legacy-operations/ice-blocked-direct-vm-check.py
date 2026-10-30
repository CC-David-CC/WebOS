#!/usr/bin/env python3
"""Prove real TURN/TLS fallback with UDP blocked for the VM's browser UID.

The same actual public desktop, v86, shared pool, chat and chess run in two
owned Chrome profiles. Only a dedicated UID's UDP (except DNS) is dropped in
the existing private VM. No host/webhost rules or public services change.
"""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import shlex
import subprocess
import tarfile
import time

ROOT=Path(__file__).resolve().parent.parent
spec=importlib.util.spec_from_file_location('blocked_direct_vm',ROOT/'scripts/upgrade-native-network-vm.py')
vm=importlib.util.module_from_spec(spec);spec.loader.exec_module(vm)
INSIDE=r'''
import hashlib,json,os,pathlib,pwd,subprocess,time,urllib.request
P=pathlib.Path;inputs=json.load(__import__('sys').stdin)
assert os.geteuid()==0 and P('/var/lib/codi-fixture-ready').is_file()
installed=json.loads(P('/srv/codi-network-fixture/ice-browser-installed.json').read_text());user=pwd.getpwnam('codi-ice-browser')
assert user.pw_uid==installed['browserUID'] and user.pw_uid>0
test=P('/srv/codi-network-fixture/ice-browser-check');unit='codi-ice-browser-fixture.service';table='codi_ice_browser_test'
def run(args,**kw):
 result=subprocess.run(list(map(str,args)),capture_output=True,text=True,timeout=45,**kw)
 if result.returncode:raise RuntimeError(result.stderr[-3000:] or result.stdout[-3000:])
 return result.stdout
assert not subprocess.run(['nft','list','table','inet',table],capture_output=True).returncode==0,'Prior test rules exist; inspect before rerunning'
assert run(['systemctl','show',unit,'-p','MainPID','--value']).strip()=='0'
for name,record in inputs['files'].items():
 p=test/name;assert p.is_file() and not p.is_symlink() and hashlib.sha256(p.read_bytes()).hexdigest()==record
for p in [test,*test.rglob('*')]:os.chown(p,user.pw_uid,user.pw_gid)
service_started=False;rules_added=False
try:
 run(['systemd-run','--unit',unit,'--collect','--uid',user.pw_name,'--gid',str(user.pw_gid),'--property=NoNewPrivileges=yes','--property=WorkingDirectory='+user.pw_dir,'--setenv=HOME='+user.pw_dir,installed['driver'],'--port=19515','--allowed-ips=127.0.0.1'])
 service_started=True
 for _ in range(100):
  try:
   with urllib.request.urlopen('http://127.0.0.1:19515/status',timeout=1) as r:ready=json.load(r)['value']['ready']
   if ready:break
  except OSError:pass
  time.sleep(.1)
 else:raise ValueError('Owned VM ChromeDriver did not become ready')
 rules='table inet '+table+' { chain output { type filter hook output priority -10; policy accept; meta skuid '+str(user.pw_uid)+' meta l4proto udp udp dport != 53 counter drop comment "owned browser direct UDP blocked"; }; }\n'
 run(['nft','-c','-f','-'],input=rules)
 run(['nft','-f','-'],input=rules);rules_added=True
 command=['runuser','-u',user.pw_name,'--','/usr/bin/python3','-B','scripts/owned-tls-discovery-check.py','--url','https://ksu.codes/hidden/','--public-tls','--require-trust','test-server','--chrome-binary',installed['browser'],'--expected-server-policy',inputs['serverPolicy'],'--expect-relay-protocol','tls','--output','.build/checks/blocked-direct-result.json']
 if inputs['preflight']:command+=['--test-native-policy','all']
 with (test/'browser-run.log').open('w') as log:child=subprocess.run(command,cwd=test,stdout=log,stderr=subprocess.STDOUT,timeout=500)
 counters=json.loads(run(['nft','-j','list','table','inet',table]))
 values=[part['counter'] for item in counters['nftables'] if 'rule' in item for part in item['rule']['expr'] if 'counter' in part]
 assert values and sum(v['packets'] for v in values)>0,'No actual packets were blocked'
 proof=json.loads((test/'.build/checks/blocked-direct-result.json').read_text())
 assert child.returncode==0 and proof['status']=='PASS',{'exit':child.returncode,'error':proof.get('error')}
 assert not proof['clientForcedRelay'] and proof['defaultCertificateTrust'] and proof['onlyOwnedPeersInvited']
 assert all(w['localCandidateType']==w['remoteCandidateType']=='relay' and w['localRelayProtocol']=='tls' and set(w['nativeIcePolicies'])=={'all'} for w in proof['witnesses'])
 assert proof['bidirectionalRTC'] and proof['separateRoomChatAndMoves'] and proof['pgnExportMatchesAcrossPeersAndExcludesChat'] and proof['guestAndIdentityPreserved'] and all(proof['disposed'])
 result={'status':'PASS','scope':'Actual public HTTPS desktop in two Chrome profiles in the private VM; real UID-filtered UDP drops and native ICE all select relay/relay TLS without forcing relay; no independent WAN/NAT claim','preflightOnly':inputs['preflight'],'publicPolicyAllVerified':not inputs['preflight'],'nativePolicyAll':True,'clientForcedRelay':False,'kernelBlockedPackets':sum(v['packets'] for v in values),'kernelBlockedBytes':sum(v['bytes'] for v in values),'browserUID':user.pw_uid,'browserVersion':installed['browserVersion'],'proof':proof,'hostFirewallChanged':False,'webhostChanged':False,'independentWANVerified':False,'physicalAndroidVerified':False}
finally:
 if rules_added:run(['nft','delete','table','inet',table])
 if service_started:run(['systemctl','stop',unit])
 assert subprocess.run(['nft','list','table','inet',table],capture_output=True).returncode!=0
 assert run(['systemctl','show',unit,'-p','MainPID','--value']).strip()=='0'
result['vmRulesAndOwnedDriverCleaned']=True
print(json.dumps(result))
'''

def run(server_policy,preflight):
    vm.vm.status();before=vm.runtime()
    files=['scripts/owned-tls-discovery-check.py',*['network/'+p.name for p in sorted((ROOT/'network').glob('*.mjs'))]]
    records={name:hashlib.sha256((ROOT/name).read_bytes()).hexdigest() for name in files}
    archive=vm.vm.FOLDER/'ice-browser-source.tar.gz'
    with tarfile.open(archive,'w:gz') as out:
        for name in files:out.add(ROOT/name,arcname=name)
    target='/srv/codi-network-fixture/ice-browser-check'
    vm.remote('mkdir -p '+target+'/.build/checks')
    with archive.open('rb') as source:subprocess.run([*vm.vm.ssh_args(),'tar -xzf - -C '+target],stdin=source,check=True,timeout=30)
    result=subprocess.run([*vm.vm.ssh_args(),'/usr/bin/python3 -I -B -c '+shlex.quote(INSIDE)],input=json.dumps({'files':records,'serverPolicy':server_policy,'preflight':preflight}),capture_output=True,text=True,timeout=600)
    if result.returncode:raise RuntimeError(result.stderr[-6000:] or result.stdout[-6000:])
    proof=json.loads(result.stdout);assert before==vm.runtime(),'Private native processes/release must remain unchanged'
    proof['vmNativeReleaseAndProcessesUnchanged']=True
    proof['sha256']={'scripts/ice-blocked-direct-vm-check.py':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),**records}
    return proof

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--preflight',action='store_true');a=p.parse_args()
    value={'status':'FAIL','scope':__doc__,'preflightOnly':a.preflight}
    try:value.update(run('relay' if a.preflight else 'all',a.preflight))
    finally:
        output=ROOT/'.build/checks'/('ice-blocked-direct-vm-preflight-result.json' if a.preflight else 'ice-blocked-direct-vm-result.json')
        if output.exists():output.rename(output.with_name(output.stem+'-before-'+str(time.time_ns())+'.json'))
        output.write_text(json.dumps(value,indent=2)+'\n');print(json.dumps(value,indent=2))
