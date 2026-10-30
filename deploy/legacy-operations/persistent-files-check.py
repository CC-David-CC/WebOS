#!/usr/bin/env python3
"""Actual disposable installed file units, migration recovery, custody and HTTP.

Uses a unique locked fixture account, /srv tree and /run systemd units; no live
webhost or actual account storage is touched. Every installed operator/worker
input is checked before execution. Cleanup removes only this fixture's state.
"""
import argparse
import asyncio
import base64
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import secrets
import shutil
import signal
import socket
import subprocess
import sys
import tempfile
import threading
import time

ROOT=Path(__file__).resolve().parent.parent;sys.path.insert(0,str(ROOT))
spec=importlib.util.spec_from_file_location('installed_files_http',ROOT/'scripts/gateway-http-check.py');http=importlib.util.module_from_spec(spec);spec.loader.exec_module(http)
from origin_service.http_server import BoundedServer,QuietHandler
from aiohttp import ClientSession,ClientTimeout,ClientError

def command(args,check=True,**kwargs):
    result=subprocess.run(list(map(str,args)),check=False,capture_output=True,text=True,timeout=90,**kwargs)
    if check and result.returncode:raise RuntimeError(result.stderr or result.stdout)
    return result
def sudo(*args,**kwargs):return command(['sudo','-n',*args],**kwargs)
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()

async def main(worker_source,operator_source,report):
    token=secrets.token_hex(4);instance='codi-files-check-'+token;user='codi-file-fixture-'+token
    stage=Path('/srv')/instance;units=[instance+'.service',instance+'-proxy.service',instance+'-proxy.socket']
    worker=stage/'worker';operator=stage/'operator';python=stage/'venv/bin/python';control=stage/'control'
    state=stage/'state';data=stage/'files';checks=[];created=False;user_created=False;group_created=False;server=None;thread=None;client=None
    def tool(action,*options,check=True):
        value=sudo(python,'-I','-B',operator/'scripts/manage-user-files.py',action,'--config-dir',control,*options,check=check)
        return json.loads(value.stdout) if check else value
    def states():return tool('status')['units']
    def wait(fn,seconds=30):
        end=time.monotonic()+seconds;last=None
        while time.monotonic()<end:
            try:
                value=fn()
                if value:return value
            except (OSError,ValueError,AssertionError,subprocess.SubprocessError) as error:last=error
            time.sleep(.1)
        raise AssertionError('Installed file readiness timeout: '+str(last))
    def passed(label):checks.append(label);print(json.dumps({'milestone':label}),flush=True)
    with tempfile.TemporaryDirectory(prefix='codi-installed-files-') as temporary:
        root=Path(temporary)
        try:
            server=BoundedServer(('127.0.0.1',0),QuietHandler);origin='http://127.0.0.1:'+str(server.server_port)
            public=root/'public';public.mkdir();(public/'index.html').write_text('Disposable installed files fixture')
            issuer=http.Service(http.Config(root/'issuer',public,origin=origin,rate_per_minute=1000));server.set_app(http.GatewayAuthority(issuer))
            thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
            policy=root/'policy.json';policy.write_text(json.dumps(issuer.config()['identity']));policy.chmod(0o644)
            with socket.socket() as sock:sock.bind(('127.0.0.1',0));port=sock.getsockname()[1]
            sudo('mkdir','-m','0755',stage);created=True
            sudo('cp','-a',worker_source,worker);sudo('cp','-a',operator_source,operator);sudo('cp','-a',ROOT/'.venv',stage/'venv')
            sudo('chown','-R','root:root',stage);sudo('chmod','-R','go-w',stage)
            sudo('groupadd','--system',user);group_created=True
            sudo('useradd','--system','--gid',user,'--home-dir','/nonexistent','--no-create-home','--shell','/usr/sbin/nologin',user);user_created=True
            for folder in [state,data]:sudo('install','-d','-m','0700','-o',user,'-g',user,folder)
            sudo('install','-m','0644',policy,stage/'policy-input.json')
            # The retained foundation predates the auth/traffic extension. Seed
            # a fixture home and a deliberately revoked permission to preserve.
            seed='''import sys,time,uuid
from pathlib import Path
sys.path.insert(0,sys.argv[1])
from gateway_service.user_store import UserStore
from gateway_service.policy import Principal
s=UserStore(sys.argv[2],sys.argv[3]);p=Principal('user:'+str(uuid.UUID(int=1)),'bootstrap','registered',{},int(time.time())+3600)
s.ensure_user(p);s.put(p,'retained.txt',b'retained private fixture');s.set_permission(p.sub,'delete',False)
'''
            sudo('/usr/sbin/runuser','-u',user,'--',python,'-I','-B','-c',seed,worker,state,data)
            metadata=json.loads((worker/'files-service.json').read_text());worker_pin=sha(worker/'files-service.json')
            assert worker_pin==report['workerManifestSHA256']
            for name,value in metadata['files'].items():assert value=={'bytes':(worker/name).stat().st_size,'sha256':sha(worker/name)}
            assert sha(operator/'file-operator.json')==report['operatorManifestSHA256']
            options=['--instance',instance,'--user',user,'--release',worker,'--manifest-sha256',worker_pin,'--python',python,'--state-root',state,'--data-root',data,'--issuer-policy',stage/'policy-input.json','--port',port,'--unit-dir','/run/systemd/system']
            bad_policy=root/'private-field.json';bad=json.loads(policy.read_text());bad['authorityKeys'][0]['jwk']['d']='not-an-actual-secret';bad_policy.write_text(json.dumps(bad))
            sudo('install','-m','0644',bad_policy,stage/'policy-input.json')
            try:assert tool('configure',*options,check=False).returncode!=0
            finally:sudo('install','-m','0644',policy,stage/'policy-input.json')
            passed('credential/private-key fields refused before public policy custody or unit installation')
            # A real process death before managed.json exists must still be
            # recoverable through the normal CLI/instance lock.
            configure_die='''import os,sys
sys.path.insert(0,sys.argv[1]);from file_service.operator import Manager
m=Manager(sys.argv[2]);options=__import__('json').loads(sys.argv[3])
m.apply=lambda value:os._exit(56)
with m.locked(options['instance']):m.configure(**options)
'''
            options_json={'instance':instance,'user':user,'release':str(worker),'manifest_sha256':worker_pin,'python':str(python),'state_root':str(state),'data_root':str(data),'issuer_policy':str(stage/'policy-input.json'),'port':port,'unit_dir':'/run/systemd/system'}
            configured=sudo(python,'-I','-B','-c',configure_die,operator,control,json.dumps(options_json),check=False);assert configured.returncode==56
            assert not sudo('test','-e',control/'managed.json',check=False).returncode==0
            assert tool('start',check=False).returncode!=0
            assert tool('recover')['status']=='configuration-recovered'
            assert tool('configure',*options)['status']=='already-configured'
            assert all(v['ActiveState']=='inactive' and v['UnitFileState']=='static' for v in states().values())
            passed('actual interrupted initial configuration recovers through normal CLI, static units and idempotent setup')
            # Startup cannot implicitly create authorization/usage tables.
            denied=tool('start',check=False);assert denied.returncode!=0
            assert all(v['ActiveState'] in ('inactive','failed') for v in states().values())
            passed('missing explicit migration refuses startup and stops partial availability')
            # Exit the actual root migration process after the actual worker
            # initializer, leaving a durable journal rather than a fake flag.
            die='''import os,sys
sys.path.insert(0,sys.argv[1]);from file_service.operator import Manager
m=Manager(sys.argv[2])
with m.locked():m.initialize(lambda phase:os._exit(55) if phase=='initialized' else None)
'''
            died=sudo(python,'-I','-B','-c',die,operator,control,check=False);assert died.returncode==55
            assert tool('start',check=False).returncode!=0
            recovered=tool('recover');assert recovered['existingBindingsAndACLsPreserved'] and not recovered['dataRestored']
            assert sudo('cat',data/'users/00000000000000000000000000000001/retained.txt').stdout=='retained private fixture'
            passed('actual migration process death blocks lifecycle and recovers forward, preserving home/ACL and backup')
            started=tool('start');assert started['status']=='started'
            before=states();assert all(v['UnitFileState']=='static' for v in before.values())
            assert tool('configure',*options)['status']=='already-configured' and states()==before
            assert tool('initialize',check=False).returncode!=0
            passed('real private listener/proxy ready, no-op setup keeps PIDs, running migration refused')
            # Inspect actual identities/namespaces/capabilities and kernel routes.
            pids={name:int(before[name]['MainPID']) for name in units[:2]}
            inspect='''import json,os,pathlib,sys
out={}
for label,pid in json.loads(sys.argv[1]).items():
 s=dict(line.split(':',1) for line in pathlib.Path('/proc',str(pid),'status').read_text().splitlines())
 assert int(s['CapEff'],16)==0 and s['NoNewPrivs'].strip()=='1'
 uid=set(map(int,s['Uid'].split()));assert len(uid)==1 and 0 not in uid
 out[label]={'pid':pid,'uid':next(iter(uid)),'netns':os.readlink('/proc/'+str(pid)+'/ns/net')}
assert len({v['uid'] for v in out.values()})==2 and len({v['netns'] for v in out.values()})==1
assert next(iter(out.values()))['netns']!=os.readlink('/proc/self/ns/net')
print(json.dumps(out))
'''
            report['processes']=json.loads(sudo('/usr/bin/python3','-I','-B','-c',inspect,json.dumps(pids)).stdout)
            probe='''import errno,json,socket,sys
def test(host,port):
 with socket.socket() as s:s.settimeout(1);return s.connect_ex((host,port))
values={'internet':test('1.1.1.1',443),'privateLAN':test('10.0.0.1',443),'hostIssuer':test('127.0.0.1',int(sys.argv[1]))}
assert values['internet']==values['privateLAN']==errno.ENETUNREACH and values['hostIssuer']==errno.ECONNREFUSED
print(json.dumps(values))
'''
            report['kernelNetworkProbe']=json.loads(sudo('nsenter','-t',pids[units[0]],'-n','/usr/bin/python3','-I','-B','-c',probe,server.server_port).stdout)
            passed('different unprivileged users, zero capabilities, private namespace and actual host/LAN/Internet denial')
            client=ClientSession(timeout=ClientTimeout(total=60),trust_env=False)
            helpers=http.HTTP();helpers.origin=origin;helpers.gateway_url='http://127.0.0.1:'+str(port);helpers.client=client
            a,key=await helpers.enter('installed_'+token)
            raw=http.jose.dumps({'resource':'my-files','operation':'create','path':'note.txt','data':base64.b64encode(b'persist through real unit restart').decode()})
            status,_,headers=await helpers.authorize(a,key,raw);assert status==200
            assert (await helpers.post('/gateway/use',{},gateway=True,headers=headers,raw=raw))[0]==200
            b,bkey=await helpers.enter('other_'+token)
            assert (await helpers.rpc(b,bkey,'read','note.txt'))[0]==404
            anonymous,anonkey=await helpers.enter(None)
            assert (await helpers.authorize(anonymous,anonkey,raw))[0]==403
            passed('actual signed HTTP through installed proxy, stable private files and account/anonymous refusal')
            old=int(states()[units[0]]['MainPID']);sudo('kill','-KILL',old)
            # Keep the event loop available to the live issuer while waiting for
            # real automatic restart and proxy namespace replacement.
            deadline=time.monotonic()+30
            while True:
                try:
                    async with client.get(helpers.gateway_url+'/healthz',headers={'Host':origin[7:]}) as response:
                        if response.status==200 and int(states()[units[0]]['MainPID']) not in (0,old):break
                except (OSError,asyncio.TimeoutError,ClientError):pass
                if time.monotonic()>deadline:raise AssertionError('Worker/proxy did not recover after SIGKILL')
                await asyncio.sleep(.2)
            assert (await helpers.post('/gateway/use',{},gateway=True,headers=headers,raw=raw))[0]==401
            assert base64.b64decode((await helpers.rpc(a,key,'read','note.txt'))[1]['data'])==b'persist through real unit restart'
            report['automaticRestart']={'beforePID':old,'afterPID':int(states()[units[0]]['MainPID'])}
            passed('actual SIGKILL automatic worker/proxy recovery preserves file and durable one-use replay refusal')
            unit=Path('/run/systemd/system')/units[0];original=unit.read_bytes();changed=root/'changed.service';changed.write_bytes(original+b'\n# unmanaged fixture change\n')
            sudo('install','-m','0644',changed,unit)
            try:assert tool('start',check=False).returncode!=0
            finally:
                unchanged=root/'original.service';unchanged.write_bytes(original);sudo('install','-m','0644',unchanged,unit);sudo('systemctl','daemon-reload')
            policy_installed=control/'issuer-policy.json';original_policy=sudo('cat',policy_installed).stdout
            changed_policy=root/'changed-policy.json';changed_policy.write_text(original_policy+' ')
            sudo('install','-m','0644',changed_policy,policy_installed)
            try:assert tool('start',check=False).returncode!=0
            finally:sudo('install','-m','0644',stage/'policy-input.json',policy_installed)
            passed('unit and pinned issuer policy drift refused without replacing retained data')
            override=Path('/run/systemd/system')/(units[0]+'.d')
            sudo('mkdir',override);override_text=root/'override.conf';override_text.write_text('[Service]\nMemoryMax=512M\n');sudo('install','-m','0644',override_text,override/'override.conf')
            try:assert tool('start',check=False).returncode!=0
            finally:sudo('rm','-rf',override);sudo('systemctl','daemon-reload')
            passed('unmanaged systemd drop-in refused before lifecycle changes')
            assert tool('stop')['status']=='stopped'
            database=state/'permissions.sqlite3';retained=state/'permissions.retained'
            sudo('mv',database,retained)
            try:
                assert tool('start',check=False).returncode!=0
                assert sudo('test','-e',database,check=False).returncode==1
            finally:sudo('mv',retained,database)
            passed('missing retained permission database refuses before any empty replacement')
            migrated=tool('initialize');assert migrated['existingBindingsAndACLsPreserved']
            tool('start')
            # Synchronous root tooling blocked this test event loop while old
            # pooled sockets closed. Let its reader process the actual EOF.
            await asyncio.sleep(.1)
            assert base64.b64decode((await helpers.rpc(a,key,'read','note.txt'))[1]['data'])==b'persist through real unit restart'
            passed('explicit offline reinitialization is idempotent and retained server file survives stop/start')
            report.update(status='PASS',checks=checks,instance=instance,bootEnabled=False,liveSiteTouched=False)
        finally:
            if client:await client.close()
            if server:
                await asyncio.to_thread(server.shutdown)
                if thread:thread.join(2)
                server.server_close()
            if created:
                sudo('systemctl','stop',*reversed(units),check=False)
                for name in units:sudo('rm','-f',Path('/run/systemd/system')/name)
                sudo('systemctl','daemon-reload');sudo('systemctl','reset-failed',*units,check=False)
                sudo('rm','-rf',stage)
                if user_created:sudo('userdel',user)
                if group_created:sudo('groupdel',user,check=False)
                assert not stage.exists()
                for name in units:assert not (Path('/run/systemd/system')/name).exists()
                report['fixtureCleanupCompleted']=True

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--worker-release',type=Path,required=True);parser.add_argument('--operator-release',type=Path,required=True);args=parser.parse_args()
    worker=args.worker_release.resolve();operator=args.operator_release.resolve()
    report={'status':'FAIL','scope':'Actual local installed isolated units, explicit SQLite migration, process death/recovery and signed HTTP; no public deployment/WAN claim','workerManifestSHA256':sha(worker/'files-service.json'),'operatorManifestSHA256':sha(operator/'file-operator.json')}
    try:asyncio.run(main(worker,operator,report))
    finally:
        report['sha256']={name:sha(ROOT/name) for name in ['file_service/operator.py','scripts/manage-user-files.py','scripts/export-file-operator.py','scripts/persistent-files-check.py','scripts/gateway-http-check.py']}
        output=ROOT/'.build/checks/persistent-files-result.json'
        if output.exists() and json.loads(output.read_text()).get('status')=='FAIL':output.rename(output.with_name('persistent-files-before-'+str(time.time_ns())+'.json'))
        output.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
