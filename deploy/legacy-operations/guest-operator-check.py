#!/usr/bin/env python3
"""Real root controller/systemd/kernel lifecycle in an isolated disposable fixture.

No live webhost, host firewall/sysctl, public route, real login or personal file
changes. Unique locked accounts, /srv roots, /run units and a private netns.
"""
import argparse
import asyncio
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import secrets
import signal
import subprocess
import sys
import tempfile
import time

ROOT=Path(__file__).resolve().parent.parent
def sha(file):return hashlib.sha256(Path(file).read_bytes()).hexdigest()
def command(args,*,check=True,**kwargs):
    value=subprocess.run(list(map(str,args)),capture_output=True,text=True,timeout=90,**kwargs)
    if check and value.returncode:raise RuntimeError(value.stderr[-2500:] or value.stdout[-2500:])
    return value
def sudo(*args,**kwargs):return command(['sudo','-n',*args],**kwargs)
def module(name,path):
    spec=importlib.util.spec_from_file_location(name,path);value=importlib.util.module_from_spec(spec);spec.loader.exec_module(value);return value

def control(stage):
    sys.path.insert(0,str(stage/'operator'));from guest_service.operator import Manager,verify_operator
    value=json.load(sys.stdin);verify_operator(stage/'operator');manager=Manager(stage/('other' if value.get('alternate') else 'control'),stage/'operator')
    def phase(name):
        if value.get('interrupt')==name:os._exit(87)
        if value.get('race')==name:
            c=manager.load(pending=True);prefix=['/usr/bin/nsenter','--net='+c['namespacePath'],'/usr/sbin/nft']
            if name=='remove-checked':subprocess.run([*prefix,'delete','table','inet','codi_guest_egress'],check=True)
            subprocess.run([*prefix,'create','table','inet','codi_guest_egress'],check=True)
    with manager.locked():
        if value['action']=='configure':result=manager.configure(**value['arguments'],phase=phase)
        elif value['action'] in ('start','stop'):result=getattr(manager,value['action'])(phase=phase)
        elif value['action']=='recover':result=manager.recover()
        else:raise ValueError('Unknown fixture operation')
    print(json.dumps(result))

async def main():
    sys.path.insert(0,str(ROOT));auth=module('guest_operator_auth',ROOT/'scripts/guest-authorization-check.py');worker_export=module('guest_operator_worker_export',ROOT/'scripts/export-guest-wire.py');operator_export=module('guest_lifecycle_export',ROOT/'scripts/export-guest-operator.py')
    token=secrets.token_hex(4);instance='codi-net-op-'+token;stage=Path('/srv')/('codi-net-operator-'+token);namespace='codi-ng-fixture-'+token;ns_path='/run/netns/'+namespace
    build=operator_export.export(ROOT/'.build/guest-operators'/('installed-check-'+token));operator_source=ROOT/'.build/guest-operators'/('installed-check-'+token)
    worker_source=ROOT/'.build/guest-workers/guest-wire-r1';worker_info=worker_export.verify(worker_source)
    worker=stage/'worker';operator=stage/'operator';python=stage/'venv/bin/python';runner=stage/'runner.py';peer_runner=stage/'peer.py';control_dir=stage/'control';state=stage/'state'
    users={role:'codi-ngf-'+short+'-'+token for role,short in [('anonymous','a'),('registered','r'),('frontend','f')]};created_users=[];unit_names=[instance+'-guard.service',*[instance+'-'+role+'.'+suffix for role in ['anonymous','registered'] for suffix in ['socket','service']]]
    created=False;ns_created=False;peers=[];checks=[];copied={};uids={};process_witnesses={}
    host_tables=sudo('nft','list','tables').stdout;host_sys={key:Path('/proc/sys/net/ipv4/'+key).read_bytes() for key in ['ping_group_range','ip_forward']};host_resolver=Path('/etc/resolv.conf').read_bytes()
    fixture=auth.Authorization();fixture.setUp();fixture.issuer.clock=time.time;fixture.t=int(time.time())
    from guest_service.egress import EgressPolicy
    fixture.policy_sha=EgressPolicy(('1.1.1.1',),('1.1.1.3',)).sha256;fixture.s=auth.GuestAuthority(fixture.issuer,fixture.policy_sha);account=fixture.enter('alice')
    def passed(label):checks.append(label);print(json.dumps({'phase':label}),flush=True)
    def ctl(action,*,check=True,**values):
        result=sudo(python,'-I','-B',runner,'--mode','control','--stage',stage,input=json.dumps({'action':action,**values}),check=check)
        return json.loads(result.stdout) if check else result
    def tool(action,*,check=True):
        result=sudo(python,'-I','-B',operator/'scripts/manage-guest-network.py',action,'--config-dir',control_dir,check=check)
        return json.loads(result.stdout) if check else result
    def config():return json.loads(sudo('cat',control_dir/'managed.json').stdout)
    def pending():return json.loads(sudo('cat',control_dir/'pending.json').stdout)
    def sysctl(*args,check=True):return sudo('systemctl',*args,check=check)
    def pid(role):return int(sysctl('show',instance+'-'+role+'.service','-p','MainPID','--value').stdout.strip())
    def children(role):
        parent=pid(role)
        return [int(v) for v in Path('/proc/'+str(parent)+'/task/'+str(parent)+'/children').read_text().split()] if parent else []
    def tables():return sudo('ip','netns','exec',namespace,'nft','list','tables').stdout
    async def wait(action,seconds=15):
        end=time.monotonic()+seconds;last=None
        while time.monotonic()<end:
            try:
                value=action()
                if value:return value
            except (OSError,ValueError,RuntimeError) as error:last=error
            await asyncio.sleep(.1)
        raise AssertionError('Controller fixture timeout: '+str(last))
    def metadata():
        code='''from pathlib import Path
import hashlib,json,sqlite3,sys
p=Path(sys.argv[1]);state=Path(sys.argv[2]);result={'secrets':{},'usage':{}}
for role in ['anonymous','registered']:
 result['secrets'][role]=hashlib.sha256((p/'credentials'/(role+'.secret')).read_bytes()).hexdigest()
 with sqlite3.connect(state/role/'usage.sqlite3') as db:result['usage'][role]=db.execute('SELECT subject,window,bytes,packets FROM usage ORDER BY subject').fetchall()
print(json.dumps(result))'''
        return json.loads(sudo('/usr/bin/python3','-I','-B','-c',code,control_dir,state).stdout)
    async def connect(role='registered'):
        secret=sudo('cat',control_dir/'credentials'/(role+'.secret')).stdout
        p=await asyncio.create_subprocess_exec('sudo','-n','setpriv','--reuid='+str(uids['frontend']),'--regid=1001','--clear-groups','--bounding-set=-all','--no-new-privs',str(python),'-I','-B',str(peer_runner),'--mode','peer',stdin=asyncio.subprocess.PIPE,stdout=asyncio.subprocess.PIPE,stderr=asyncio.subprocess.PIPE,start_new_session=True);peers.append(p)
        async def send(value):p.stdin.write((json.dumps(value)+'\n').encode());await p.stdin.drain()
        async def receive():
            value=await asyncio.wait_for(p.stdout.readline(),10)
            if not value:raise AssertionError((await p.stderr.read()).decode()[-2000:])
            return json.loads(value)
        await send({'role':role,'socket':'/run/codi-network/'+instance+'/'+role+'.sock','origin':fixture.config.origin,'secret':secret});value=await receive()
        if role=='registered':
            ch=value['challenge'];fixture.t=int(time.time());grant=fixture.authorize(account,ch);assert grant['status']==200,(grant['status'],grant['body'].get('error'));g=grant['body']['grant'];await send({'type':'codi-guest-network-auth/1','grant':g,'proof':fixture.proof(account,g,ch)});value=await receive()
        assert value['ready'];await send({'action':'arp'});assert (await receive())['arpReply'];await wait(lambda:children(role));return p,send,receive
    async def close(peer):
        p,send,receive=peer
        if p.returncode is None:await send({'action':'close'});assert (await receive())['closed'];await p.wait()
    async def interrupted(action,at):
        value=ctl(action,check=False,interrupt=at);assert value.returncode==87,(action,at,value.stderr);assert pending()['kind']==action
        return value
    def all_stopped():return all(pid(role)==0 for role in ['guard','anonymous','registered'])
    def no_kernel():return 'table inet codi_guest_egress' not in tables()
    def sentinel():return 'table inet codi_fixture_sentinel' in tables()
    try:
        sudo('mkdir','-m','0755',stage);created=True
        for source,target in [(ROOT/'.venv',stage/'venv'),(worker_source,worker),(operator_source,operator)]:sudo('cp','-a',source,target)
        sudo('cp',Path(__file__),runner);sudo('cp',ROOT/'scripts/guest-installed-worker-check.py',peer_runner);sudo('chown','-R','root:root',stage);sudo('chmod','-R','go-w',stage)
        for folder,manifest,key in [(worker,'guest-wire.json',worker_info['manifestSHA256']),(operator,'guest-operator.json',build['manifestSHA256'])]:
            assert sha(folder/manifest)==key
            for name,record in json.loads((folder/manifest).read_text())['files'].items():
                assert record=={'bytes':(folder/name).stat().st_size,'sha256':sha(folder/name)};copied[str(folder.name)+'/'+name]=record['sha256']
        passed('sealed worker and root operator copies verified before execution')
        for role,user in users.items():
            sudo('useradd','--system','--user-group','--home-dir','/nonexistent','--no-create-home','--shell','/usr/sbin/nologin',user);created_users.append(user);uids[role]=int(command(['id','-u',user]).stdout)
        sudo('ip','netns','add',namespace);ns_created=True;sudo('ip','-n',namespace,'link','set','lo','up');sudo('ip','netns','exec',namespace,'sysctl','-q','-w','net.ipv4.ping_group_range=1000 1001','net.ipv4.ip_forward=0');sudo('ip','netns','exec',namespace,'nft','add','table','inet','codi_fixture_sentinel')
        with tempfile.TemporaryDirectory() as folder:
            input_policy=Path(folder)/'issuer.json';input_policy.write_text(json.dumps(fixture.issuer.config()['identity']));sudo('install','-m','0644',input_policy,stage/'issuer-policy.json')
        arguments={'instance':instance,'worker':str(worker),'worker_sha256':worker_info['manifestSHA256'],'python':str(python),'state_root':str(state),'frontend_user':users['frontend'],'anonymous_user':users['anonymous'],'registered_user':users['registered'],'issuer_policy':str(stage/'issuer-policy.json'),'policy':{'version':'codi-guest-egress-policy/1','ownPublicIPv4':['1.1.1.1'],'dnsIPv4':['1.1.1.3']},'namespace':ns_path,'unit_dir':'/run/systemd/system','base_path':''}
        value=ctl('configure',check=False,arguments=arguments,interrupt='prepared');assert value.returncode==87,value.stderr;assert pending()['kind']=='configure';assert no_kernel();tool('recover');assert no_kernel() and all_stopped();baseline=metadata()
        passed('interrupted configure recovers the same credentials and installs inactive static units only')
        assert ctl('configure',arguments=arguments)['status']=='already-configured' and tool('stop')['status']=='already-stopped' and metadata()==baseline;passed('repeating configure and stopped lifecycle does not replace credentials or state')
        sudo('ip','netns','exec',namespace,'nft','add','table','inet','codi_guest_egress');value=tool('start',check=False);assert value.returncode!=0 and all_stopped() and 'table inet codi_guest_egress' in tables();sudo('ip','netns','exec',namespace,'nft','delete','table','inet','codi_guest_egress');passed('pre-existing kernel table is refused and retained rather than adopted')
        for at in ['prepared','kernel','guard','workers']:
            await interrupted('start',at);tool('recover');assert all_stopped() and no_kernel() and sentinel() and metadata()==baseline;passed('actual interrupted start '+at+' rolls back owned resources and preserves state')
        await interrupted('start','committed');peer=await connect();before={role:pid(role) for role in ['guard','anonymous','registered']};qemu=children('registered');result=tool('recover');assert result['status']=='committed-start-retained' and {role:pid(role) for role in before}==before and children('registered')==qemu
        assert tool('recover')['status']=='already-started' and {role:pid(role) for role in before}==before and children('registered')==qemu
        for role in ['guard','anonymous','registered']:
            status=dict(line.split(':',1) for line in sudo('cat','/proc/'+str(pid(role))+'/status').stdout.splitlines());uid=0 if role=='guard' else uids[role];gid=0 if role=='guard' else 1001;caps=1<<12 if role=='guard' else 0
            assert set(map(int,status['Uid'].split()))=={uid} and set(map(int,status['Gid'].split()))=={gid} and int(status['CapEff'],16)==caps and status['NoNewPrivs'].strip()=='1'
            process_witnesses[role]={'uid':uid,'gid':gid,'effectiveCapabilities':caps,'noNewPrivileges':True}
        passed('actual guard has only NET_ADMIN and both fixed-role workers have no capabilities')
        await peer[1]({'action':'arp'});assert (await peer[2]())['arpReply'];tool('start');await close(peer);await wait(lambda:not children('registered'));retained=metadata();assert retained['secrets']==baseline['secrets'] and retained['usage']['registered'];passed('committed interrupted start and healthy recovery retain actual live QEMU PID wire and usage')
        for at in ['units','kernel']:
            await interrupted('stop',at);tool('recover');assert all_stopped() and no_kernel() and sentinel() and metadata()==retained;passed('actual interrupted stop '+at+' completes without restoring data')
            if at=='units':tool('start')
        tool('start');peer=await connect();sudo('ip','netns','exec',namespace,'nft','delete','table','inet','codi_guest_egress');await wait(all_stopped);await peer[1]({'action':'wait_closed'});assert (await peer[2]())['closed'];await peer[0].wait();assert (control_dir/'fault.json').exists();tool('recover');assert no_kernel() and sentinel();retained=metadata();passed('continuous kernel loss guard stops actual workers QEMU and sockets and records recoverable fault')
        tool('start');peer=await connect();sudo('kill','-KILL',pid('guard'));await wait(all_stopped);await peer[1]({'action':'wait_closed'});assert (await peer[2]())['closed'];await peer[0].wait();tool('recover');assert no_kernel() and sentinel();passed('guard process SIGKILL stops dependent actual workers and is recoverable')
        tool('start');sudo('ip','netns','exec',namespace,'nft','add','chain','inet','codi_guest_egress','foreign_change');await wait(all_stopped);value=tool('recover',check=False);assert value.returncode!=0 and 'foreign_change' in sudo('ip','netns','exec',namespace,'nft','list','table','inet','codi_guest_egress').stdout
        sudo('ip','netns','exec',namespace,'nft','delete','chain','inet','codi_guest_egress','foreign_change');tool('recover');assert no_kernel() and sentinel();passed('unrecognized drift stops workers but is not deleted until the exact owned rules are restored')
        tool('start');drop=Path('/run/systemd/system')/(instance+'-registered.service.d');sudo('mkdir','-m','0755',drop)
        with tempfile.TemporaryDirectory() as folder:
            file=Path(folder)/'override.conf';file.write_text('[Service]\nMemoryMax=255M\n');sudo('install','-m','0644',file,drop/'override.conf')
        await wait(all_stopped);assert tool('recover',check=False).returncode!=0;sudo('rm',drop/'override.conf');sudo('rmdir',drop);sysctl('daemon-reload');tool('recover');assert no_kernel() and sentinel();passed('unmanaged unit drop-in stops running workers and blocks recovery until removed')
        before=metadata()
        mutation='import sqlite3,sys;db=sqlite3.connect(sys.argv[1]);db.execute("UPDATE meta SET role=?",(sys.argv[2],));db.commit();print(db.execute("SELECT role FROM meta").fetchone()[0]);db.close()'
        sudo('/usr/bin/python3','-I','-B','-c',mutation,state/'registered/usage.sqlite3','anonymous')
        value=tool('start',check=False);assert value.returncode!=0 and all_stopped() and no_kernel() and sentinel() and metadata()==before
        assert sudo('/usr/bin/python3','-I','-B','-c','import sqlite3,sys;print(sqlite3.connect(sys.argv[1]).execute("SELECT role FROM meta").fetchone()[0])',state/'registered/usage.sqlite3').stdout.strip()=='anonymous'
        sudo('/usr/bin/python3','-I','-B','-c',mutation,state/'registered/usage.sqlite3','registered');passed('genuine worker readiness failure rolls back kernel and units without resetting damaged usage')
        value=ctl('start',check=False,race='prepared');assert value.returncode!=0 and all_stopped() and 'table inet codi_guest_egress' in tables()
        sudo('ip','netns','exec',namespace,'nft','delete','table','inet','codi_guest_egress');tool('recover');assert no_kernel();passed('exclusive kernel create preserves a competing table appearing after inspection')
        tool('start');value=ctl('stop',check=False,race='remove-checked');assert value.returncode!=0 and all_stopped() and 'table inet codi_guest_egress' in tables()
        sudo('ip','netns','exec',namespace,'nft','delete','table','inet','codi_guest_egress');tool('recover');assert no_kernel();passed('kernel generation handle prevents deleting a replacement table with the same name')
        tool('start');peer=await connect();before_pids={role:pid(role) for role in ['guard','anonymous','registered']};before_qemu=children('registered')
        alternate={**arguments,'instance':'codi-net-opb-'+token,'state_root':str(stage/'state-other')}
        other_names=[alternate['instance']+'-guard.service',*[alternate['instance']+'-'+role+'.'+suffix for role in ['anonymous','registered'] for suffix in ['socket','service']]];unit_names.extend(other_names)
        ctl('configure',alternate=True,arguments=alternate);value=ctl('stop',alternate=True,check=False);after_pids={role:pid(role) for role in before_pids};after_qemu=children('registered')
        assert value.returncode!=0 and after_pids==before_pids and after_qemu==before_qemu,{'returncode':value.returncode,'error':value.stderr[-300:],'beforePids':before_pids,'afterPids':after_pids,'beforeQemu':before_qemu,'afterQemu':after_qemu}
        await peer[1]({'action':'arp'});assert (await peer[2]())['arpReply'];await close(peer);tool('stop');ctl('recover',alternate=True);assert no_kernel() and sentinel();passed('another configured controller cannot remove identical policy belonging to the live instance')
        return {'status':'PASS','scope':__doc__,'checks':checks,'workerRuntimeSHA256':worker_info['manifestSHA256'],'operatorManifestSHA256':build['manifestSHA256'],'copiedSourceSHA256':copied,'processWitnesses':process_witnesses,'actualSystemdLifecycle':True,'actualQEMUAndSignedGrants':True,'continuousKernelGuard':True,'atomicRecoveryBoundaries':True,'unrelatedFixtureTablePreserved':True,'liveWebhostChanged':False,'browserInstalledWholeChainVerified':False,'independentWANVerified':False}
    except BaseException:
        if created:
            logs={name:sudo('journalctl','-u',name,'--no-pager','-n','25',check=False).stdout for name in unit_names if name.endswith('.service')};(ROOT/'.build/checks/guest-operator-before-journal.json').write_text(json.dumps(logs,indent=2)+'\n')
        raise
    finally:
        for p in peers:
            if p.returncode is None:
                p.stdin.close()
                try:await asyncio.wait_for(p.wait(),1)
                except asyncio.TimeoutError:sudo('kill','-TERM','--','-'+str(p.pid),check=False);await asyncio.wait_for(p.wait(),5)
        for name in reversed(unit_names):sysctl('stop',name,check=False)
        for name in unit_names:
            sysctl('reset-failed',name,check=False);file=Path('/run/systemd/system')/name
            if file.exists():sudo('rm',file)
            drop=Path(str(file)+'.d')
            if drop.exists():sudo('rm','-f',drop/'override.conf');sudo('rmdir',drop)
        sysctl('daemon-reload')
        if ns_created:
            for value in sudo('ip','netns','pids',namespace).stdout.split():sudo('kill','-KILL',value,check=False)
            sudo('ip','netns','delete',namespace)
        runtime=Path('/run/codi-network')/instance
        if runtime.exists():sudo('rmdir',runtime)
        for user in reversed(created_users):
            sudo('userdel',user)
            if command(['getent','group',user],check=False).returncode==0:sudo('groupdel',user)
        if created:sudo('rm','-rf','--',stage)
        fixture.temp.cleanup()
        assert sudo('nft','list','tables').stdout==host_tables and Path('/etc/resolv.conf').read_bytes()==host_resolver and host_sys=={k:Path('/proc/sys/net/ipv4/'+k).read_bytes() for k in host_sys}
        assert not stage.exists() and namespace not in sudo('ip','netns','list').stdout and not any(Path('/run/systemd/system',name).exists() for name in unit_names)
        print(json.dumps({'phase':'fixture units accounts private roots and namespace removed; host network settings unchanged'}),flush=True)

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--mode',choices=['control']);parser.add_argument('--stage',type=Path);args=parser.parse_args()
    if args.mode=='control':control(args.stage)
    else:
        result={'status':'FAIL','scope':__doc__}
        try:result.update(asyncio.run(main()),fixtureCleanupCompleted=True,hostFirewallResolverAndSysctlsUnchanged=True)
        finally:
            names=['guest_service/operator.py','guest_service/installation.py','guest_service/usage.py','scripts/manage-guest-network.py','scripts/export-guest-operator.py','scripts/guest-operator-check.py','scripts/guest-installed-worker-check.py','scripts/guest-authorization-check.py']
            result['sha256']={name:sha(ROOT/name) for name in names};output=ROOT/'.build/checks/guest-operator-result.json'
            if output.exists():output.rename(output.with_name('guest-operator-before-'+str(time.time_ns())+'.json'))
            output.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
