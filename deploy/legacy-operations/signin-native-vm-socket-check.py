#!/usr/bin/env python3
"""Real direct sockets under the installed worker UIDs in the private VM.

Bypasses the Ethernet filter deliberately to exercise the independent installed
kernel boundary. Destinations are controlled fixture IPs; no live host changes.
"""
import hashlib
import importlib.util
import json
from pathlib import Path
import shlex
import subprocess
import time

ROOT=Path(__file__).resolve().parent.parent
PROBE=r'''
import json,os,socket,struct,sys
from pathlib import Path
v=json.load(sys.stdin);out={}
for name,host,port,kind in v['probes']:
 try:
  with socket.socket(socket.AF_INET,socket.SOCK_DGRAM if kind in ('ping','dns') else socket.SOCK_STREAM,socket.IPPROTO_ICMP if kind=='ping' else 0) as s:
   s.settimeout(.5)
   if kind=='tcp':s.connect((host,port));ok=True
   elif kind=='ping':s.sendto(struct.pack('!BBHHH',8,0,0,123,1)+b'signin-uid-probe',(host,0));ok=s.recv(256)[0]==0
   else:
    query=b'\x73\x31\x01\x00\x00\x01\x00\x00\x00\x00\x00\x00'+b'\x0ccodi-fixture\x04test\x00\x00\x01\x00\x01'
    s.sendto(query,(host,port));data=s.recv(1024);ok=data[:2]==b'\x73\x31' and data[-4:]==socket.inet_aton('1.1.1.2')
   out[name]={'ok':ok}
 except OSError as error:out[name]={'ok':False,'errno':error.errno}
status=dict(line.split(':',1) for line in Path('/proc/self/status').read_text().splitlines())
assert os.getuid()==v['uid'] and int(status['CapEff'],16)==0 and status['NoNewPrivs'].strip()=='1'
print(json.dumps({'uid':os.getuid(),'effectiveCapabilities':0,'noNewPrivileges':True,'results':out}))
'''
REMOTE=r'''
import hashlib,json,subprocess,sys
from pathlib import Path
v=json.load(sys.stdin);c=json.loads(Path('/etc/codi-native-fixture/managed.json').read_text());b=json.loads(Path(c['guestNetwork']['configFile']).read_text())
assert b['policy']['version']=='codi-guest-egress-policy/2' and b['policy']['anonymousInternet']=='deny'
args=[c['python'],'-I','-B',b['operatorRelease']+'/scripts/manage-guest-network.py','status','--config-dir',str(Path(c['guestNetwork']['configFile']).parent)]
def status():
 r=json.loads(subprocess.check_output(args,text=True));assert r['active'] and r['kernelMatches'] and not r['guardFault'];return r
def counters():
 r=json.loads(subprocess.check_output(['/usr/sbin/nft','-j','list','table','inet','codi_guest_egress'],text=True));return {role:sum(e.get('counter',{}).get('packets',0) for row in r['nftables'] if row.get('rule',{}).get('chain')==role for e in row['rule']['expr']) for role in ['anonymous','registered']}
before=status();start=counters();witnesses={}
for role in ['anonymous','registered','unrelated']:
 uid=b['roles'][role]['uid'] if role in b['roles'] else 65432
 assert uid>0 and (role!='unrelated' or uid not in [b['frontendUID'],*(p['uid'] for p in b['roles'].values())])
 probes=[['other-public-ping','1.1.1.2',0,'ping'],['own-public-ping','1.1.1.1',0,'ping'],['other-public-http','1.1.1.2',80,'tcp'],['other-public-https','1.1.1.2',443,'tcp'],['own-public-http','1.1.1.1',80,'tcp'],['fixed-public-dns','1.1.1.3',53,'dns'],['private-lan','10.222.0.1',80,'tcp'],['host-loopback','127.0.0.1',8118,'tcp'],['unapproved-ssh','1.1.1.2',22,'tcp']]
 value=json.loads(subprocess.check_output(['/usr/bin/setpriv','--reuid='+str(uid),'--regid=1001','--clear-groups','--bounding-set=-all','--no-new-privs','/usr/bin/python3','-I','-B','-c',v['probe']],input=json.dumps({'uid':uid,'probes':probes}),text=True))
 for name,result in value['results'].items():
  expected=role=='unrelated' or role=='registered' and name in ['other-public-ping','own-public-ping','other-public-http','other-public-https','own-public-http','fixed-public-dns']
  assert result['ok']==expected,(role,name,result,expected)
 witnesses[role]=value
end=counters();after=status();assert end['anonymous']>=start['anonymous']+9 and end['registered']>start['registered']
assert {k:p['MainPID'] for k,p in before['units'].items() if k.endswith('.service')}=={k:p['MainPID'] for k,p in after['units'].items() if k.endswith('.service')}
print(json.dumps({'status':'PASS','workerPolicySHA256':b['policySHA256'],'witnesses':witnesses,'counterDeltas':{k:end[k]-start[k] for k in start},'guardAndWorkerPIDsUnchanged':True,'installedGuardHealthy':True,'liveWebhostChanged':False,'hostFirewallChanged':False}))
'''

if __name__=='__main__':
    spec=importlib.util.spec_from_file_location('signin_sockets_vm',ROOT/'scripts/prepare-native-network-vm.py');vm=importlib.util.module_from_spec(spec);spec.loader.exec_module(vm);vm.status()
    result={'status':'FAIL'}
    try:
        p=subprocess.run([*vm.ssh_args(),'/usr/bin/python3 -I -B -c '+shlex.quote(REMOTE)],input=json.dumps({'probe':PROBE}),text=True,capture_output=True,timeout=60)
        if p.returncode:raise RuntimeError(p.stderr[-2800:])
        result=json.loads(p.stdout)
    finally:
        result['sourceSHA256']=hashlib.sha256(Path(__file__).read_bytes()).hexdigest();out=ROOT/'.build/checks/signin-native-vm-socket-result.json'
        if out.exists():out.rename(out.with_name('signin-native-vm-socket-before-'+str(time.time_ns())+'.json'))
        out.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
