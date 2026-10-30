#!/usr/bin/env python3
"""Actual native enable/disable/process-death recovery inside the private VM.

Uses sealed native12 and external operator packages, real systemd/kernel and
actual os._exit interruptions. Never touches live webhost or host firewall.
"""
import argparse
import asyncio
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import socket
import sqlite3
import ssl
import subprocess
import sys
import time
from aiohttp import ClientSession,ClientTimeout,CookieJar,WSMsgType

ROOT=Path(__file__).resolve().parent.parent;STAGE=Path('/srv/codi-network-fixture');CONTROL=Path('/etc/codi-native-fixture/managed.json');PYTHON=STAGE/'venv/bin/python'
def module(name,file):
    spec=importlib.util.spec_from_file_location(name,file);value=importlib.util.module_from_spec(spec);sys.modules[name]=value;spec.loader.exec_module(value);return value
def run(args,check=True,**kwargs):
    result=subprocess.run(list(map(str,args)),capture_output=True,text=True,timeout=180,**kwargs)
    if check and result.returncode:raise RuntimeError((result.stderr or result.stdout)[-3000:])
    return result
def fault(point,disable):
    if os.geteuid()!=0 or not Path('/var/lib/codi-fixture-ready').exists():raise ValueError('Private VM fixture only')
    op=module('vm_native_transition',STAGE/'native/scripts/manage-services.py')
    from origin_service import network_management as network
    with op.locked(CONTROL):
        config=op.load(CONTROL);value=None if disable else network.policy(op,config,Path('/etc/codi-guest-network/fixture/managed.json'),STAGE/'guest-operator')
        atomic=op.atomic;binding_run=network.Binding.run;ready=op.ready
        def interrupted_atomic(file,raw,*args,**kwargs):
            atomic(file,raw,*args,**kwargs)
            if point=='config' and Path(file)==CONTROL:os._exit(87)
            if Path(file)==CONTROL.parent/'maintenance.json' and point=='journal-'+json.loads(raw)['phase']:os._exit(87)
        def interrupted_binding(self,action):
            result=binding_run(self,action)
            if point=='backend' and action=='start':os._exit(87)
            return result
        def interrupted_ready(c,roles):
            ready(c,roles)
            if point in ('issuer-ready','guest-ready') and roles==[point.removesuffix('-ready')]:os._exit(87)
        op.atomic=interrupted_atomic;network.Binding.run=interrupted_binding;op.ready=interrupted_ready
        if point=='committed':network.clear=lambda *a:os._exit(87)
        print(json.dumps(network.configure(op,config,CONTROL,value)))
def snapshot():
    config=json.loads(CONTROL.read_text());state=Path(config['stateRoot'])
    names=[state/'issuer/state/accounts.sqlite3',state/'issuer/state/issuer.pem',state/'steward/service.pem',state/'operator/root/root.pem',state.parent/('guest-cookie-'+config['instance'])/'secret']
    keys={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in names}
    files={str(p.relative_to('/srv/codi-files-fixture')):hashlib.sha256(p.read_bytes()).hexdigest() for p in Path('/srv/codi-files-fixture/users').rglob('*') if p.is_file()}
    usage={}
    for role in ['anonymous','registered']:
        with sqlite3.connect('/var/lib/codi-guest-network-fixture/'+role+'/usage.sqlite3') as db:usage[role]=db.execute('SELECT subject,window,bytes,packets FROM usage ORDER BY subject,window').fetchall()
    pids={}
    for role in ['issuer','guest','steward']:
        pids[role]=int(run(['systemctl','show',config['instance']+'-'+role+'.service','-p','MainPID','--value']).stdout)
    for role,unit in [('files','codi-files-network-fixture.service'),('filesProxy','codi-files-network-fixture-proxy.service')]:pids[role]=int(run(['systemctl','show',unit,'-p','MainPID','--value']).stdout)
    backend=config.get('guestNetwork')
    worker_operator=Path(backend['operatorRelease']) if backend else STAGE/'guest-operator'
    worker_config=Path(backend['configFile']).parent if backend else Path('/etc/codi-guest-network/fixture')
    worker=json.loads(run([PYTHON,'-I','-B',worker_operator/'scripts/manage-guest-network.py','status','--config-dir',worker_config]).stdout)
    unit='codi-net-network-fixture-anonymous.service' if config.get('guestNetwork') else config['instance']+'-guest.service';pid=int(run(['systemctl','show',unit,'-p','MainPID','--value']).stdout)
    children=[int(v) for v in Path('/proc/'+str(pid)+'/task/'+str(pid)+'/children').read_text().split()] if pid else []
    print(json.dumps({'configVersion':config['version'],'keysAndAccountDBSHA256':keys,'privateFixtureFileSHA256':files,'usage':usage,'pids':pids,'worker':worker,'anonymousQEMUChildren':children,'nativeJournalPresent':(CONTROL.parent/'maintenance.json').exists()}))

async def host():
    vm=module('lifecycle_vm',ROOT/'scripts/prepare-native-network-vm.py');vm.status();remote_file=STAGE/'tools/native-network-vm-lifecycle-check.py'
    run([*vm.ssh_args(),'cat > '+str(remote_file)],input=Path(__file__).read_text())
    def remote(command,check=True):return run([*vm.ssh_args(),command],check=check)
    def snap():return json.loads(remote(str(PYTHON)+' -I -B '+str(remote_file)+' --snapshot').stdout)
    def tool(action,options='',check=True):return remote(str(PYTHON)+' -I -B '+str(STAGE/'native/scripts/manage-services.py')+' '+action+' --config '+str(CONTROL)+' '+options,check=check)
    def configure(enabled):return json.loads(tool('configure-guest-network','--network-config /etc/codi-guest-network/fixture/managed.json --network-operator '+str(STAGE/'guest-operator') if enabled else '--disable').stdout)
    baseline=snap();assert baseline['configVersion']=='codi-managed-instance/5' and baseline['worker']['active'];checks=[];continuity=[];steady_pids={role:baseline['pids'][role] for role in ['steward','files','filesProxy']}
    def passed(name):checks.append(name);print(json.dumps({'phase':name}),flush=True)
    def preserved(after):
        assert after['keysAndAccountDBSHA256']==baseline['keysAndAccountDBSHA256'];assert after['privateFixtureFileSHA256']==baseline['privateFixtureFileSHA256']
        for role in ['steward','files','filesProxy']:assert after['pids'][role]==steady_pids[role],role
        for role in ['anonymous','registered']:
            current={(row[0],row[1]):row[2:] for row in after['usage'][role]}
            for row in baseline['usage'][role]:assert (row[0],row[1]) in current and all(a>=b for a,b in zip(current[(row[0],row[1])],row[2:])),(role,row,current)
    before=snap();refused=tool('upgrade','--release '+str(STAGE/'legacy11')+' --python '+str(PYTHON),check=False);assert refused.returncode and 'below profile12' in refused.stderr;assert snap()['pids']==before['pids'];passed('real native11 downgrade refused before running PID changes')
    assert configure(False)['status']=='network-configured';off=snap();assert not off['worker']['active'] and not off['worker']['kernelMatches'];preserved(off);passed('real disable stops workers and removes their owned table before legacy relay readiness')
    for point in ['journal-prepared','config','backend','issuer-ready','guest-ready']:
        crashed=remote(str(PYTHON)+' -I -B '+str(remote_file)+' --fault '+point,check=False);assert crashed.returncode==87,(point,crashed.stderr)
        interrupted=snap();assert interrupted['nativeJournalPresent'];assert tool('start','--roles guest',check=False).returncode
        recovered=json.loads(tool('recover-operation').stdout);assert recovered['status']=='interrupted-network-rolled-back'
        after=snap();assert after['configVersion']=='codi-managed-instance/4' and not after['worker']['active'] and not after['worker']['kernelMatches'] and not after['nativeJournalPresent'];preserved(after);passed('real process exit at '+point+' recovers prior policy without restoring data or usage')
    installed=json.loads(remote('cat '+str(STAGE/'installed-result.json')).stdout);certificate=remote('cat /etc/codi-fixture-tls/cert.pem').stdout;context=ssl.create_default_context(cadata=certificate);origin=installed['publicOrigin'];mac=bytes.fromhex('022215000001');arp=bytes([255])*6+mac+b'\x08\x06'+b'\0\x01\x08\0\x06\x04\0\x01'+mac+socket.inet_aton('10.86.0.2')+bytes(6)+socket.inet_aton('10.86.0.1')
    async def committed_wire(disable):
        crashed=await asyncio.to_thread(remote,str(PYTHON)+' -I -B '+str(remote_file)+' --fault committed'+(' --disable' if disable else ''),False);assert crashed.returncode==87,crashed.stderr
        async with ClientSession(timeout=ClientTimeout(total=30),cookie_jar=CookieJar(unsafe=True),trust_env=False) as client:
            async with client.get(origin+'/hidden/',ssl=context) as response:assert response.status==200;await response.read()
            async with client.ws_connect(origin.replace('https:','wss:')+'/hidden/guest-network',ssl=context,headers={'Origin':origin},max_msg_size=16384) as wire:
                async def actual_arp():
                    await wire.send_bytes(arp);reply=await asyncio.wait_for(wire.receive(),5);assert reply.type==WSMsgType.BINARY and reply.data[12:14]==b'\x08\x06' and reply.data[20:22]==b'\0\2'
                await actual_arp();before=await asyncio.to_thread(snap);assert before['anonymousQEMUChildren'] and before['nativeJournalPresent']
                recovered=json.loads((await asyncio.to_thread(tool,'recover-operation')).stdout);assert recovered['status']=='committed-network-recovered';after=await asyncio.to_thread(snap)
                assert before['pids']==after['pids'] and before['anonymousQEMUChildren']==after['anonymousQEMUChildren'] and not after['nativeJournalPresent'];await actual_arp();preserved(after)
                continuity.append({'mode':'disabled' if disable else 'enabled','nativePIDs':after['pids'],'sameQEMUChildren':after['anonymousQEMUChildren'],'samePublicWebSocketAndActualARP':True})
        await asyncio.sleep(.1)
    await committed_wire(False);passed('committed enabled recovery retains actual QEMU PID and public WebSocket/ARP')
    before=snap();assert configure(True)['status']=='network-already-current' and snap()['pids']==before['pids'];passed('real repeated enable is a no-op')
    crashed=remote(str(PYTHON)+' -I -B '+str(remote_file)+' --fault config --disable',check=False);assert crashed.returncode==87;assert json.loads(tool('recover-operation').stdout)['status']=='interrupted-network-rolled-back';assert snap()['worker']['active'];preserved(snap());passed('real interrupted disable restores enabled policy and preserves saved files')
    await committed_wire(True);passed('committed disabled recovery retains actual legacy QEMU PID and public WebSocket/ARP')
    account=snap()['keysAndAccountDBSHA256'];assert json.loads(tool('upgrade','--release '+str(STAGE/'legacy11')+' --python '+str(PYTHON)).stdout)['status']=='upgraded';assert json.loads(tool('rollback').stdout)['status']=='rolled-back';code_after=snap();assert code_after['keysAndAccountDBSHA256']==account
    # Code transitions deliberately restart all native roles. Subsequent policy
    # and guard checks must preserve the steward PID established by that upgrade.
    assert code_after['pids']['steward']>0;steady_pids['steward']=code_after['pids']['steward'];preserved(code_after);passed('disabled policy permits real native11 switch and native12 rollback without restoring account/key/cookie state')
    configure(True);before=snap();remote('systemctl kill --kill-whom=main --signal=KILL codi-net-network-fixture-guard.service')
    deadline=time.monotonic()+15
    while time.monotonic()<deadline:
        state=snap()
        if state['pids']['guest']==0 and all(int(v.get('MainPID','0'))==0 for n,v in state['worker']['units'].items() if n.endswith('.service')):break
        await asyncio.sleep(.1)
    else:raise AssertionError('Guard death did not stop actual frontend and workers')
    assert json.loads(tool('start','--roles guest').stdout)['status']=='started';after=snap();assert after['worker']['active'] and after['worker']['kernelMatches'] and after['pids']['guest']>0;assert after['pids']['issuer']==before['pids']['issuer'];preserved(after);passed('actual guard SIGKILL stops frontend/workers and native guest start recovers kernel protection without restarting issuer/steward/files')
    return {'status':'PASS','scope':__doc__,'checks':checks,'committedWireContinuity':continuity,'nativeManifestSHA256':installed['nativeSHA256'],'finalConfigVersion':after['configVersion'],'finalWorkerStatus':after['worker'],'keyAccountCookieAndPrivateFileStatePreserved':True,'usageCountersNeverReset':True,'actualProcessExitAndGuardDeath':True,'hostFirewallChanged':False,'liveWebhostChanged':False}

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--fault');parser.add_argument('--disable',action='store_true');parser.add_argument('--snapshot',action='store_true');args=parser.parse_args()
    if args.fault:fault(args.fault,args.disable)
    elif args.snapshot:snapshot()
    else:
        result={'status':'FAIL','scope':__doc__}
        try:result.update(asyncio.run(host()))
        finally:
            result['sha256']={'scripts/native-network-vm-lifecycle-check.py':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()};output=ROOT/'.build/checks/native-network-vm-lifecycle-result.json'
            if output.exists():output.rename(output.with_name('native-network-vm-lifecycle-before-'+str(time.time_ns())+'.json'))
            output.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
