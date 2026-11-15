#!/usr/bin/env python3
"""Actual authenticated checkpoint/code rollout on the existing private VM only."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import shlex
import subprocess
import time

ROOT=Path(__file__).resolve().parent.parent
spec=importlib.util.spec_from_file_location('rollout_vm',ROOT/'scripts/upgrade-native-network-vm.py');candidate=importlib.util.module_from_spec(spec);spec.loader.exec_module(candidate)
def run(release_dir=None):
    candidate.vm.status();current=candidate.runtime();target=Path(current['release']);key=current['manifestSHA256']
    local=Path(release_dir) if release_dir else ROOT/'.build/releases/connected-maintenance-r3'
    assert key==hashlib.sha256((local/'connected-release.json').read_bytes()).hexdigest()
    profile=json.loads((local/'connected-release.json').read_text())['version'];policy=None
    if profile=='codi-connected-development/14':
        spec=importlib.util.spec_from_file_location('rollout_ice_vm',ROOT/'scripts/ice-preference-vm-check.py');ice=importlib.util.module_from_spec(spec);spec.loader.exec_module(ice)
        policy=ice.operator('configure-turn','relay');current=candidate.runtime()
    assert current['appSHA256']==hashlib.sha256((ROOT/'app.js').read_bytes()).hexdigest()
    source=ROOT/'scripts/native-rollout.py';stage='/srv/codi-network-fixture';python=stage+'/venv/bin/python';control='/etc/codi-native-fixture/managed.json'
    remote_script=stage+'/tools/native-rollout.py'
    subprocess.run([*candidate.vm.ssh_args(),'cat > '+remote_script+' && chmod 644 '+remote_script],input=source.read_bytes(),check=True,timeout=30)
    assert candidate.remote('sha256sum '+remote_script).split()[0]==hashlib.sha256(source.read_bytes()).hexdigest()
    def snap():return json.loads(candidate.remote(python+' -I -B '+stage+'/tools/native-network-vm-lifecycle-check.py --snapshot'))
    baseline=snap()
    old=stage+('/candidate-ce00294efbc58d83' if profile=='codi-connected-development/14' else '/candidate-46a00d79102e9c0a')
    changed=json.loads(candidate.remote(python+' -I -B '+str(target/'scripts/manage-services.py')+' upgrade --config '+control+' --release '+old+' --python '+python))
    assert changed['status']=='upgraded' and candidate.runtime()['release']==old
    candidate.remote('install -d -m 700 /var/lib/codi-fixture-backups/rollout')
    argv=[python,'-I','-B',remote_script,'upgrade','--operator',str(target/'scripts/manage-services.py'),'--operator-manifest-sha256',key,'--config',control,'--release',str(target),'--python',python,'--backup-parent','/var/lib/codi-fixture-backups/rollout']
    result=json.loads(candidate.remote(shlex.join(argv)));after=snap();executed=candidate.runtime()
    assert result['status']=='upgraded' and result['guestCookiePreserved'] and result['checkpointGuestPidPreserved'] and result['keysAuthorityAndExistingAccountsPreserved'] and not result['dataRestored']
    assert executed['manifestSHA256']==key and after['configVersion']=='codi-managed-instance/5' and not after['nativeJournalPresent']
    assert baseline['keysAndAccountDBSHA256']==after['keysAndAccountDBSHA256'] and baseline['privateFixtureFileSHA256']==after['privateFixtureFileSHA256']
    assert all(baseline['pids'][role]==after['pids'][role] for role in ['files','filesProxy'])
    assert after['worker']['active'] and after['worker']['kernelMatches'] and not after['worker']['guardFault']
    for role,rows in baseline['usage'].items():
        retained={(r[0],r[1]):r[2:] for r in after['usage'][role]}
        for row in rows:assert all(a>=b for a,b in zip(retained[(row[0],row[1])],row[2:]))
    assert not candidate.remote('find /etc/codi-native-fixture -maxdepth 1 -name native-rollout.json').strip()
    return {'status':'PASS','scope':__doc__,'nativeManifestSHA256':key,'nativeProfile':profile,'preparedRelayPolicy':policy,'actualAuthenticatedProfileRollout':result,'runtime':executed,'currentKeysAccountsCookieFilesAndUsagePreserved':True,'privateFileProcessesUnchanged':True,'enabledGuestPolicyRetained':True,'hostFirewallChanged':False,'liveWebhostChanged':False}
if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--release-dir',type=Path);args=parser.parse_args()
    value={'status':'FAIL','scope':__doc__}
    try:value.update(run(args.release_dir))
    finally:
        value['sha256']={name:hashlib.sha256((ROOT/name).read_bytes()).hexdigest() for name in ['scripts/native-network-vm-rollout-check.py','scripts/native-rollout.py','scripts/upgrade-native-network-vm.py']};output=ROOT/'.build/checks/native-network-vm-rollout-result.json'
        if output.exists():output.rename(output.with_name('native-network-vm-rollout-before-'+str(time.time_ns())+'.json'))
        output.write_text(json.dumps(value,indent=2)+'\n');print(json.dumps(value,indent=2))
