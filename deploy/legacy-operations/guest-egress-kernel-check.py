#!/usr/bin/env python3
"""Actual nftables/direct socket checks in a disposable network namespace only.

No host firewall changes, persistent accounts/services, guest forwarding, public
traffic or live webhost mutation. Test UIDs exist only as numeric process IDs.
"""
import hashlib
import json
import os
from pathlib import Path
import secrets
import subprocess
import sys
import time

ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT))
from guest_service.egress import DENY_IPV4,EgressPolicy
POLICY=EgressPolicy(('1.1.1.1',),('1.1.1.3',))
UIDS={'anonymous':60231,'registered':60232,'frontend':60233,'unrelated':60234}

SERVER=r'''
import json,os,pathlib,socket,sys,threading,time
settings=json.loads(sys.argv[1]);stop=threading.Event();sockets=[]
def server(host,port,udp=False,v6=False):
 s=socket.socket(socket.AF_INET6 if v6 else socket.AF_INET,socket.SOCK_DGRAM if udp else socket.SOCK_STREAM)
 s.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
 if v6:s.setsockopt(socket.IPPROTO_IPV6,socket.IPV6_V6ONLY,1)
 s.bind((host,port));sockets.append(s)
 def run():
  if udp:
   while True:
    data,address=s.recvfrom(64);s.sendto(data,address)
  else:
   s.listen(32)
   while True:
    c,_=s.accept()
    with c:
     c.settimeout(2)
     try:data=c.recv(64);c.sendall(data)
     except OSError:pass
 threading.Thread(target=run,daemon=True).start()
for host,port,udp,v6 in settings['listeners']:server(host,port,udp,v6)
print(json.dumps({'ready':True,'uid':os.getuid()}),flush=True)
sys.stdin.read()
'''
PROBE=r'''
import errno,json,os,pathlib,socket,struct,sys
settings=json.loads(sys.argv[1]);results={}
for name,host,port,kind in settings['probes']:
 try:
  family=socket.AF_INET6 if ':' in host else socket.AF_INET
  s=socket.socket(family,socket.SOCK_DGRAM if kind in ('udp','icmp') else socket.SOCK_STREAM,socket.IPPROTO_ICMP if kind=='icmp' else 0)
  with s:
   s.settimeout(.35)
   if kind=='icmp':s.sendto(struct.pack('!BBHHH',8,0,0,123,1)+b'controlled-kernel-probe',(host,0));data=s.recv(256);ok=data[0]==0
   elif kind=='udp':s.connect((host,port));s.send(b'probe');ok=s.recv(64)==b'probe'
   else:s.connect((host,port));s.sendall(b'probe');ok=s.recv(64)==b'probe'
  results[name]={'ok':ok}
 except OSError as e:results[name]={'ok':False,'errno':e.errno}
status=dict(line.split(':',1) for line in pathlib.Path('/proc/self/status').read_text().splitlines())
assert os.getuid()==settings['uid'] and int(status['CapEff'],16)==0 and status['NoNewPrivs'].strip()=='1'
print(json.dumps({'uid':os.getuid(),'effectiveCapabilities':int(status['CapEff'],16),'noNewPrivileges':True,'results':results}))
'''

def run(args,**kwargs):
    return subprocess.run(list(map(str,args)),check=True,capture_output=True,text=True,timeout=40,**kwargs).stdout.strip()

def packet_checks():
    # One policy deliberately gives packet and kernel paths the same deny set.
    checks=0
    for address in ['10.0.7.84','127.0.0.1','169.254.169.254','100.64.0.1','172.16.0.1','192.168.0.1','0.0.0.0','192.0.0.9','192.88.99.2','198.18.0.1','192.0.2.1','198.51.100.1','203.0.113.1','224.0.0.1','255.255.255.255','::1']:
        for registered in [False,True]:
            for protocol,port in [('icmp-echo',None),('tcp',80),('tcp',443),('udp',53)]:
                assert not POLICY.permits(address,protocol,port,registered=registered);checks+=1
    for registered in [False,True]:
        for address in ['1.1.1.1','1.1.1.2']:
            for protocol,port in [('icmp-echo',None),('tcp',80),('tcp',443),('tcp',22),('tcp',53),('udp',53)]:
                expected=(address!='1.1.1.1' or registered) and (protocol=='icmp-echo' or protocol=='tcp' and port in (80,443))
                assert POLICY.permits(address,protocol,port,registered=registered)==expected;checks+=1
    assert POLICY.permits('1.1.1.3','udp',53,dns_proxy=True)
    assert POLICY.permits('1.1.1.3','tcp',53,dns_proxy=True)
    assert not POLICY.permits('1.1.1.2','udp',53,dns_proxy=True)
    for value in [{'version':'codi-guest-egress-policy/1','ownPublicIPv4':['127.0.0.1'],'dnsIPv4':['1.1.1.3']},
                  {'version':'codi-guest-egress-policy/1','ownPublicIPv4':['1.1.1.1'],'dnsIPv4':['1.1.1.1']},
                  {'version':'codi-guest-egress-policy/1','ownPublicIPv4':[],'dnsIPv4':['1.1.1.3']}]:
        try:POLICY.parse(value)
        except ValueError:pass
        else:raise AssertionError('Invalid policy accepted')
    assert POLICY.parse(POLICY.value())==POLICY
    for values in [dict(anonymous_uid=0,registered_uid=2,frontend_uid=3),dict(anonymous_uid=1,registered_uid=1,frontend_uid=3),dict(anonymous_uid=1,registered_uid=2,frontend_uid=3,issuer_port=8141)]:
        try:POLICY.nftables(**values)
        except ValueError:pass
        else:raise AssertionError('Invalid UID/port ownership accepted')
    return checks+9

def privileged():
    assert os.geteuid()==0
    namespace='codi-egress-'+secrets.token_hex(5);children=[];created=False
    host_ns=os.readlink('/proc/self/ns/net');host_tables=run(['nft','list','tables'])
    rules=POLICY.nftables(anonymous_uid=UIDS['anonymous'],registered_uid=UIDS['registered'],frontend_uid=UIDS['frontend'])
    result={'status':'FAIL','scope':__doc__,'packetDecisions':packet_checks(),'policySHA256':POLICY.sha256,'nftablesSHA256':hashlib.sha256(rules.encode()).hexdigest(),'hostFirewallChanged':False,'liveWebhostChanged':False}
    def ns(*args,**kwargs):return run(['ip','netns','exec',namespace,*args],**kwargs)
    def command(role,code,settings):
        uid=UIDS[role]
        return ['ip','netns','exec',namespace,'setpriv','--reuid='+str(uid),'--regid='+str(uid),'--clear-groups','--bounding-set=-all','--no-new-privs','/usr/bin/python3','-I','-B','-c',code,json.dumps(settings)]
    def start_server(role,listeners):
        settings={'listeners':listeners}
        argv=['ip','netns','exec',namespace,'/usr/bin/python3','-I','-B','-c',SERVER,json.dumps(settings)] if role=='root' else command(role,SERVER,settings)
        child=subprocess.Popen(argv,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True);children.append(child)
        import select
        ready,_,_=select.select([child.stdout],[],[],5)
        if not ready:raise AssertionError('Test server did not become ready')
        value=child.stdout.readline()
        if not value:raise AssertionError(child.stderr.read()[-1500:])
        assert json.loads(value)['ready']
    try:
        run(['ip','netns','add',namespace]);created=True
        ns('ip','link','set','lo','up')
        addresses=['1.1.1.1','1.1.1.2','1.1.1.3','10.0.7.84','172.16.0.1','192.168.1.1','169.254.169.254','100.64.0.1']
        for address in addresses:ns('ip','address','add',address+'/32','dev','lo')
        ns('sysctl','-q','-w','net.ipv4.ping_group_range=60231 60234')
        ns('nft','--check','--file','-',input=rules)
        ns('nft','--file','-',input=rules)
        listeners=[['0.0.0.0',p,False,False] for p in [22,53,80,443,8118]]
        listeners += [['0.0.0.0',53,True,False],['::1',80,False,True]]
        start_server('root',listeners)
        for role,port in [('anonymous',8141),('registered',8142),('frontend',8132)]:start_server(role,[['127.0.0.1',port,False,False]])
        common=[['own_ping','1.1.1.1',0,'icmp'],['own_http','1.1.1.1',80,'tcp'],['own_https','1.1.1.1',443,'tcp'],
                ['other_ping','1.1.1.2',0,'icmp'],['other_http','1.1.1.2',80,'tcp'],['other_https','1.1.1.2',443,'tcp'],
                ['public_ssh','1.1.1.2',22,'tcp'],['dns_udp','1.1.1.3',53,'udp'],['dns_tcp','1.1.1.3',53,'tcp'],['other_dns','1.1.1.2',53,'udp'],
                ['host_issuer','127.0.0.1',8118,'tcp'],['host_loopback','127.0.0.1',80,'tcp'],['ipv6_loopback','::1',80,'tcp']]
        common += [[name,address,80,'tcp'] for name,address in [('lan10','10.0.7.84'),('lan172','172.16.0.1'),('lan192','192.168.1.1'),('metadata','169.254.169.254'),('cgnat','100.64.0.1')]]
        extra=[['anonymous_worker','127.0.0.1',8141,'tcp'],['registered_worker','127.0.0.1',8142,'tcp'],['frontend_reply','127.0.0.1',8132,'tcp']]
        witnesses={}
        for role in ['anonymous','registered','frontend','unrelated']:
            value=json.loads(run(command(role,PROBE,{'uid':UIDS[role],'probes':common+extra})))
            for name,probe in value['results'].items():
                if role=='unrelated':expected=True
                elif role=='frontend':expected=name in ('host_issuer','anonymous_worker','registered_worker')
                else:expected=name in ('other_ping','other_http','other_https','dns_udp','dns_tcp') or role=='registered' and name in ('own_ping','own_http','own_https')
                assert probe['ok']==expected,(role,name,probe,expected)
            witnesses[role]=value
        # An unfiltered root client also checks the frontend reply-only exception.
        code='import socket;s=socket.create_connection(("127.0.0.1",8132),1);s.sendall(b"probe");assert s.recv(64)==b"probe";s.close()'
        ns('/usr/bin/python3','-I','-B','-c',code)
        installed=json.loads(ns('nft','--json','list','table','inet','codi_guest_egress'))
        counters=[item['rule']['expr'] for item in installed['nftables'] if 'rule' in item]
        assert any(e.get('counter',{}).get('packets',0)>0 for exprs in counters for e in exprs)
        result.update(status='PASS',actualKernelWitnesses=witnesses,replyOnlyControlServersWork=True,actualNftCountersAdvanced=True,unrelatedUIDUnchanged=True)
    finally:
        for child in children:
            if child.poll() is None:
                child.terminate()
                try:child.wait(3)
                except subprocess.TimeoutExpired:child.kill();child.wait(3)
        if created:run(['ip','netns','delete',namespace])
        assert namespace not in run(['ip','netns','list'])
        assert os.readlink('/proc/self/ns/net')==host_ns and run(['nft','list','tables'])==host_tables
        result['fixtureNamespaceAndProcessesCleaned']=True
        result['sha256']={name:hashlib.sha256((ROOT/name).read_bytes()).hexdigest() for name in ['guest_service/egress.py','scripts/guest-egress-kernel-check.py']}
        print(json.dumps(result,indent=2))

if __name__=='__main__':
    if os.geteuid()==0:privileged()
    else:
        child=subprocess.run(['sudo','-n','/usr/bin/python3','-I','-B',str(Path(__file__).resolve())],capture_output=True,text=True,timeout=120)
        output=ROOT/'.build/checks/guest-egress-kernel-result.json'
        if output.exists():output.rename(output.with_name('guest-egress-kernel-before-'+str(time.time_ns())+'.json'))
        try:report=json.loads(child.stdout)
        except ValueError:report={'status':'FAIL','scope':__doc__,'stderr':child.stderr[-2500:],'stdout':child.stdout[-2500:]}
        output.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
        if child.returncode:raise SystemExit(child.stderr[-3000:] or child.stdout[-3000:])
