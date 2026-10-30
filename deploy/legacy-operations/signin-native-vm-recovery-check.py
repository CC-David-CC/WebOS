#!/usr/bin/env python3
"""Resume the real interrupted policy migration using sealed corrected code.

The retained before snapshot and failed attempt are evidence; no VM, account,
file, key, permission or usage state is rolled back to make this test pass.
"""
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shlex
import subprocess
import sys
import time

ROOT=Path(__file__).resolve().parent.parent
CONTROL=Path('/etc/codi-native-fixture/managed.json')
RECOVERY=Path('/srv/codi-network-fixture/candidate-eb5afef8c41cc7d7')
RECOVERY_SHA='eb5afef8c41cc7d7373545921d99551fde0cd100d8798e5d22a98e809ce3d8c0'

def module(name,file):
    spec=importlib.util.spec_from_file_location(name,file);m=importlib.util.module_from_spec(spec);sys.modules[name]=m;spec.loader.exec_module(m);return m

def phase(point):
    if os.geteuid()!=0 or not Path('/var/lib/codi-fixture-ready').exists():raise ValueError('Private fixture only')
    raw=(RECOVERY/'connected-release.json').read_bytes();assert hashlib.sha256(raw).hexdigest()==RECOVERY_SHA
    manifest=json.loads(raw)
    for name,r in manifest['files'].items():
        p=RECOVERY/name;assert not p.is_symlink() and p.stat().st_uid==0 and not p.stat().st_mode&0o022 and r=={'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
    op=module('sealed_signin_recovery',RECOVERY/'scripts/manage-services.py')
    from origin_service import signin_migration
    def interrupted(name):
        if name==point:os._exit(87)
    with op.locked(CONTROL):result=signin_migration.advance(op,CONTROL,phase=interrupted)
    print(json.dumps(result))

def host():
    vm=module('signin_recovery_vm',ROOT/'scripts/prepare-native-network-vm.py');vm.status();checks=[];observed=[]
    def remote(command,*,input=None,check=True):return subprocess.run([*vm.ssh_args(),command],input=input,capture_output=True,text=True,check=check,timeout=120)
    helper=Path('/srv/codi-network-fixture/tools/signin-native-vm-recovery-check.py')
    remote('cat > '+str(helper),input=Path(__file__).read_text());remote('chmod 0644 '+str(helper))
    python='/srv/codi-network-fixture/venv/bin/python';original='/srv/codi-network-fixture/tools/signin-native-vm-migration-check.py'
    def snap():return json.loads(remote(shlex.join([python,'-I','-B',original,'--snapshot'])).stdout)
    before=json.loads((ROOT/'.build/checks/signin-migration-before-snapshot.json').read_text())
    def check(label,value):assert value,label;checks.append(label);print(json.dumps({'phase':label}),flush=True)
    prior=(ROOT/'.build/checks/signin-native-vm-migration-check.log').read_text()
    for earlier in ['prepared','disabled','unit-removed:codi-net-network-fixture-guard.service']:
        assert '"phase": "actual process interruption at '+earlier+'"' in prior
        assert '"phase": "native Start refuses incomplete migration at '+earlier+'"' in prior
    state=snap();check('continues same interrupted migration and retained private data',state['migrationPhase']=='disabled' and state['pids']['issuer']==state['pids']['guest']==0 and state['keysAccountDBCookieSHA256']==before['keysAccountDBCookieSHA256'])
    progress=ROOT/'.build/checks/signin-migration-recovery-progress.json'
    for point in ['units-removed','configured','bound','completed']:
        result=remote(shlex.join([python,'-I','-B',str(helper),'--phase',point]),check=False)
        if result.returncode!=87:
            (ROOT/'.build/checks/signin-recovery-phase-error.txt').write_text(result.stderr)
            raise AssertionError((point,result.returncode,result.stderr[-2600:]))
        check('actual corrected-code process interruption at '+point,True)
        state=snap();observed.append({'interruptedAt':point,'snapshot':state})
        if point!='completed':check('issuer/guest remain stopped at '+point,state['pids']['issuer']==state['pids']['guest']==0)
        c=json.loads(remote('cat '+str(CONTROL)).stdout)
        rejected=remote(shlex.join([python,'-I','-B',str(Path(c['release'])/'scripts/manage-services.py'),'start','--config',str(CONTROL),'--roles','guest']),check=False)
        check('normal Start refuses incomplete migration at '+point,rejected.returncode!=0 and 'migration pending' in rejected.stderr)
        check('steward and private file PIDs unchanged at '+point,all(state['pids'][role]==before['pids'][role] for role in ['steward','files','filesProxy']))
        progress.write_text(json.dumps({'checks':checks,'snapshots':observed},indent=2)+'\n')
    result=json.loads(remote(shlex.join([python,'-I','-B',str(RECOVERY/'scripts/manage-services.py'),'recover-guest-signin','--config',str(CONTROL)])).stdout)
    after=snap()
    check('explicit sealed recovery finishes strict target and clears journals',result['status']=='guest-signin-migrated' and after['migrationPhase'] is None and not after['innerJournalPresent'] and after['guestPolicyVersion']=='codi-guest-egress-policy/2')
    check('keys account DB cookie private files and permission rows preserved',before['keysAccountDBCookieSHA256']==after['keysAccountDBCookieSHA256'] and before['fixturePrivateFilesSHA256']==after['fixturePrivateFilesSHA256'] and before['permissionsLogicalSHA256']==after['permissionsLogicalSHA256'])
    for role,rows in before['usage'].items():
        indexed={(r[0],r[1]):r[2:] for r in after['usage'][role]}
        for row in rows:assert (row[0],row[1]) in indexed and all(a>=b for a,b in zip(indexed[(row[0],row[1])],row[2:]))
    check('durable counters retained without reset',True)
    check('three native roles and file services online',all(after['pids'].values()))
    return {'status':'PASS','scope':__doc__,'checks':checks,'before':before,'after':after,'correctedCodeFaultSnapshots':observed,'earlierFaultsInRetainedAttempt':['prepared','disabled','unit-removed:codi-net-network-fixture-guard.service'],
            'retainedAttemptLogSHA256':hashlib.sha256((ROOT/'.build/checks/signin-native-vm-migration-check.log').read_bytes()).hexdigest(),'recoveryManifestSHA256':RECOVERY_SHA,'result':result,'liveWebhostChanged':False,'hostFirewallChanged':False,'browserGuestChainTested':False}

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--phase');args=parser.parse_args()
    if args.phase:phase(args.phase)
    else:
        result={'status':'FAIL'}
        try:result=host()
        finally:
            result['sourceSHA256']=hashlib.sha256(Path(__file__).read_bytes()).hexdigest();p=ROOT/'.build/checks/signin-native-vm-recovery-result.json'
            if p.exists():p.rename(p.with_name('signin-native-vm-recovery-before-'+str(time.time_ns())+'.json'))
            p.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
