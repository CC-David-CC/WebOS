#!/usr/bin/env python3
"""Actual native socket probes under the three installed guest UIDs in the VM.

Bypasses the Ethernet parser to test independent kernel enforcement. Public and
private destinations are controlled VM listeners; root first proves each exists.
No live webhost or host firewall changes. No credentials leave the private VM.
"""
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import pwd
import socket
import ssl
import struct
import subprocess
import sys
import time

ROOT=Path(__file__).resolve().parent.parent;STAGE=Path('/srv/codi-network-fixture')
def run(args,**kwargs):
    r=subprocess.run(list(map(str,args)),capture_output=True,text=True,timeout=120,**kwargs)
    if r.returncode:raise RuntimeError((r.stderr or r.stdout)[-3000:])
    return r.stdout
def probe(value,ca):
    kind,address,port=value['kind'],value['address'],value.get('port')
    try:
        if kind in ('tcp','tls'):
            with socket.create_connection((address,port),timeout=1) as connected:
                if kind=='tls':
                    with ssl.create_default_context(cadata=ca).wrap_socket(connected,server_hostname=address):pass
            return True
        if kind=='dns':
            packet=b'\x12\x34\x01\x00\x00\x01\x00\x00\x00\x00\x00\x00\x04codi\x07fixture\x04test\x00\x00\x01\x00\x01'
            with socket.socket(socket.AF_INET,socket.SOCK_DGRAM) as udp:
                udp.settimeout(1);udp.sendto(packet,(address,53));reply,_=udp.recvfrom(4096);return reply[:2]==packet[:2] and socket.inet_aton('1.1.1.2') in reply
        packet=struct.pack('!BBHHH',8,0,0,1234,1)+b'CODI-UID-PROBE'
        if len(packet)%2:packet+=b'\0'
        checksum=sum(struct.unpack('!'+str(len(packet)//2)+'H',packet));checksum=(checksum&65535)+(checksum>>16);checksum=(checksum&65535)+(checksum>>16);packet=packet[:2]+struct.pack('!H',~checksum&65535)+packet[4:]
        with socket.socket(socket.AF_INET,socket.SOCK_DGRAM,socket.IPPROTO_ICMP) as icmp:
            icmp.settimeout(1);icmp.sendto(packet,(address,0));return icmp.recv(4096)[0]==0
    except OSError:return False
def child():
    value=json.load(sys.stdin);status=dict(line.split(':',1) for line in Path('/proc/self/status').read_text().splitlines())
    result={'uid':os.getuid(),'gid':os.getgid(),'effectiveCapabilities':int(status['CapEff'],16),'noNewPrivileges':status['NoNewPrivs'].strip()=='1','results':[{**item,'connected':probe(item,value['certificate'])} for item in value['probes']]}
    print(json.dumps(result))
def inside():
    if os.geteuid()!=0 or not Path('/var/lib/codi-fixture-ready').exists():raise ValueError('Private VM root fixture only')
    config=json.loads(Path('/etc/codi-native-fixture/managed.json').read_text());assert config['version']=='codi-managed-instance/5'
    backend=json.loads(Path(config['guestNetwork']['configFile']).read_text());python=STAGE/'venv/bin/python';certificate=Path('/etc/codi-fixture-tls/cert.pem').read_text()
    worker=lambda action:json.loads(run([python,'-I','-B',STAGE/'guest-operator/scripts/manage-guest-network.py',action,'--config-dir','/etc/codi-guest-network/fixture']))
    before=worker('status');assert before['active'] and before['kernelMatches'] and not before['guardFault']
    definitions=[('own HTTP','tcp','1.1.1.1',80),('own HTTPS','tls','1.1.1.1',443),('other HTTP','tcp','1.1.1.2',80),('other HTTPS','tls','1.1.1.2',443),('private10','tcp','10.222.0.1',80),('private172','tcp','172.22.0.1',80),('private192','tcp','192.168.222.1',80),('metadata','tcp','169.254.169.254',80),('own SSH port','tcp','1.1.1.1',22),('other SSH port','tcp','1.1.1.2',22),('issuer socket','tcp','127.0.0.1',8118),('file proxy socket','tcp','127.0.0.1',8140),('new frontend socket','tcp','127.0.0.1',8132),('IPv6 loopback SSH','tcp','::1',22),('own echo','icmp','1.1.1.1',None),('other echo','icmp','1.1.1.2',None),('private echo','icmp','10.222.0.1',None),('pinned DNS','dns','1.1.1.3',53)]
    probes=[{'name':name,'kind':kind,'address':address,'port':port} for name,kind,address,port in definitions]
    # Match the worker's unprivileged ping GID/capability context for references;
    # root GID0 is deliberately outside this VM's ping_group_range.
    reference_uid=65534;assert reference_uid not in [backend['frontendUID'],*[v['uid'] for v in backend['roles'].values()]]
    reference=json.loads(run(['setpriv','--reuid='+str(reference_uid),'--regid=1001','--clear-groups','--bounding-set=-all','--no-new-privs',python,'-I','-B',Path(__file__),'--child'],input=json.dumps({'certificate':certificate,'probes':probes})))
    assert reference['uid']==reference_uid and reference['gid']==1001 and reference['effectiveCapabilities']==0 and reference['noNewPrivileges']
    references={v['name']:v['connected'] for v in reference['results']};assert all(references.values()),references
    witnesses={}
    for role,user in [('anonymous','codi-net-anonymous'),('registered','codi-net-registered'),('frontend','codi-guest')]:
        uid=pwd.getpwnam(user).pw_uid;result=json.loads(run(['setpriv','--reuid='+str(uid),'--regid=1001','--clear-groups','--bounding-set=-all','--no-new-privs',python,'-I','-B',Path(__file__),'--child'],input=json.dumps({'certificate':certificate,'probes':probes})))
        assert result['uid']==uid and result['gid']==1001 and result['effectiveCapabilities']==0 and result['noNewPrivileges']
        for value in result['results']:
            allowed=value['name']=='issuer socket' if role=='frontend' else value['name'] in ('other HTTP','other HTTPS','other echo','pinned DNS') or role=='registered' and value['name'] in ('own HTTP','own HTTPS','own echo')
            assert value['connected']==allowed,(role,value)
            value['expectedAllowed']=allowed
        witnesses[role]=result
    after=worker('status');assert before==after,'Protection or service PIDs changed during probes'
    nft=json.loads(run(['nft','-j','list','table','inet','codi_guest_egress']));denials={}
    for entry in nft['nftables']:
        rule=entry.get('rule',{})
        if any('reject' in e for e in rule.get('expr',[])):
            denials.setdefault(rule['chain'],0)
            denials[rule['chain']]+=sum(e.get('counter',{}).get('packets',0) for e in rule['expr'])
    assert all(denials.get(role,0)>0 for role in ['anonymous','registered','frontend']),denials
    print(json.dumps({'status':'PASS','scope':__doc__,'rootControlledListenerReferences':references,'unfilteredReferenceContext':{k:reference[k] for k in ['uid','gid','effectiveCapabilities','noNewPrivileges']},'uidWitnesses':witnesses,'actualRejectCounters':denials,'installedKernelPolicyVerified':True,'servicesPreserved':True,'hostFirewallChanged':False,'liveWebhostChanged':False},indent=2))
if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--inside',action='store_true');parser.add_argument('--child',action='store_true');args=parser.parse_args()
    if args.child:child()
    elif args.inside:inside()
    else:
        spec=importlib.util.spec_from_file_location('boundary_vm',ROOT/'scripts/prepare-native-network-vm.py');vm=importlib.util.module_from_spec(spec);spec.loader.exec_module(vm);vm.status();file=STAGE/'tools/native-network-vm-boundary-check.py'
        run([*vm.ssh_args(),'cat > '+str(file)],input=Path(__file__).read_text());result={'status':'FAIL','scope':__doc__}
        try:result.update(json.loads(run([*vm.ssh_args(),str(STAGE/'venv/bin/python')+' -I -B '+str(file)+' --inside'])))
        finally:
            result['sha256']={'scripts/native-network-vm-boundary-check.py':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()};output=ROOT/'.build/checks/native-network-vm-boundary-result.json'
            if output.exists():output.rename(output.with_name('native-network-vm-boundary-before-'+str(time.time_ns())+'.json'))
            output.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
