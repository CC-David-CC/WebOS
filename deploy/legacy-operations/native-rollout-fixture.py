"""Actual installed fixture for the native checkpoint/code-switch orchestration."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

def check(run, stage, release, python, config_path, tool, sudo):
    parent = stage / 'rollout-backups'
    sudo('mkdir', '-m', '0700', parent)
    legacy = stage / 'rollout-legacy'
    sudo('cp', '-a', ROOT / '.build/releases/connected-preview-20261022-r1', legacy)
    sudo('chown','-R','root:root',legacy)
    sudo('/usr/bin/python3','-B','-c','from pathlib import Path;import sys;p=Path(sys.argv[1]);[(f.chmod(0o755 if f.is_dir() else 0o644)) for f in [p,*p.rglob("*")]]',legacy)
    # Deliberately exercise the retained profile8 with its original RAM cookie,
    # including its RAM-only cookie. This is an owned disposable fixture only.
    tool('upgrade', '--release', legacy, '--python', python)
    instance = json.loads(sudo('cat', config_path).stdout)['instance']
    assert str(stage) == '/srv/' + instance and instance.startswith('codi-persistent-')
    secret = stage / ('guest-cookie-' + instance) / 'secret'
    sudo('rm', '--', secret)
    driver = '''import importlib.util,json,pathlib,sys
from unittest.mock import patch
source,config_file,script,target,python,backups,action,fault=map(str,sys.argv[1:])
source=pathlib.Path(source);sys.path.insert(0,str(source))
spec=importlib.util.spec_from_file_location('rollout_operator',source/'scripts/manage-services.py');op=importlib.util.module_from_spec(spec);sys.modules[spec.name]=op;spec.loader.exec_module(op)
spec=importlib.util.spec_from_file_location('rollout_check',script);rollout=importlib.util.module_from_spec(spec);sys.modules[spec.name]=rollout;spec.loader.exec_module(rollout)
config_path=pathlib.Path(config_file)
class ProcessDied(BaseException):pass
def phase(name):
 if name==fault:raise ProcessDied('SIMULATED_DEATH_'+name)
with op.locked(config_path):
 if action=='recover':value=rollout.recover(op,config_path)
 else:
  original=op.atomic
  def interrupted(path,*args,**kwargs):
   original(path,*args,**kwargs)
   if fault=='inner-unit' and pathlib.Path(path).parent==pathlib.Path('/etc/systemd/system'):raise ProcessDied('SIMULATED_DEATH_inner-unit')
  with patch.object(op,'atomic',interrupted):value=rollout.upgrade(op,config_path,pathlib.Path(target),pathlib.Path(python),pathlib.Path(backups),phase)
 print(json.dumps(value))
 if value['status']=='candidate-failed-rolled-back':raise SystemExit(1)
'''
    def invoke(target, fault='', action='upgrade', check=True):
        return sudo(python, '-B', '-c', driver, release, config_path,
                    ROOT / 'scripts/native-rollout.py', target, python, parent,
                    action, fault, check=check, timeout=180)
    def current():
        return json.loads(sudo('cat', config_path).stdout)
    def complete():
        assert sudo('test', '-e', config_path.parent / 'native-rollout.json', check=False).returncode
        assert sudo('test', '-e', config_path.parent / 'maintenance.json', check=False).returncode
        assert all(value['ActiveState']=='active' and int(value['MainPID'])>0 for value in tool('status')['units'].values())
    initial = json.loads(invoke(release).stdout)
    assert initial['status']=='upgraded' and initial['guestCookiePreserved'] and initial['checkpointGuestPidPreserved']
    assert initial['keysAuthorityAndExistingAccountsPreserved'] and not initial['dataRestored'];complete()
    pids = tool('status')['units']
    expected = json.loads(sudo('/usr/bin/python3','-B','-c','import hashlib,json,sys;print(json.dumps(hashlib.sha256(open(sys.argv[1],"rb").read()).hexdigest()))',release/'connected-release.json').stdout)
    cli = sudo(python,'-B',ROOT/'scripts/native-rollout.py','upgrade','--operator',release/'scripts/manage-services.py','--operator-manifest-sha256',expected,'--config',config_path,'--release',release,'--python',python,'--backup-parent',parent)
    assert json.loads(cli.stdout)['status']=='already-current'
    assert json.loads(invoke(release).stdout)['status']=='already-current'
    assert tool('status')['units']==pids
    # Early interrupted stop/checkpoint must resume the old roles while keeping
    # the exact existing guest process. A second rollout must refuse the journal.
    alternate = stage / 'alternate'
    evidence=[]
    for fault in ['prepared', 'roles-stopped', 'checkpointed', 'roles-resumed']:
        guest = tool('status')['units']['guest']['MainPID']
        child = invoke(alternate, fault=fault, check=False)
        assert child.returncode and 'SIMULATED_DEATH_'+fault in child.stderr, child.stderr
        pending = invoke(alternate, check=False)
        assert pending.returncode and 'native rollout is pending' in pending.stderr, pending.stderr
        result = json.loads(invoke(alternate, action='recover').stdout)
        assert result['status']=='interrupted-rollout-resumed-before' and result['guestCookiePreserved']
        assert tool('status')['units']['guest']['MainPID']==guest;complete();evidence.append(fault)
    # Abrupt death after an actual unit replacement leaves both journals. The
    # existing operator recovers code, then the outer wrapper restores roles.
    child = invoke(alternate, fault='inner-unit', check=False)
    assert child.returncode and 'SIMULATED_DEATH_inner-unit' in child.stderr
    result = json.loads(invoke(alternate, action='recover').stdout)
    assert result['status']=='interrupted-rollout-resumed-before' and result['guestCookiePreserved'];complete()
    # A committed code switch must be kept if death happens before outer clear.
    child = invoke(alternate, fault='code-returned', check=False)
    assert child.returncode and 'SIMULATED_DEATH_code-returned' in child.stderr
    assert current()['release']==str(alternate)
    result = json.loads(invoke(alternate, action='recover').stdout)
    assert result['status']=='committed-rollout-recovered' and result['guestCookiePreserved'];complete()
    # Actual failing issuer startup automatically reverts to the current code,
    # preserving accounts and the persistent guest credential.
    child = invoke(stage / 'bad-start', check=False)
    assert child.returncode==1, child.stderr
    result = json.loads(child.stdout)
    assert result['status']=='candidate-failed-rolled-back' and result['guestCookiePreserved']
    assert result['release']==str(alternate) and result['keysAuthorityAndExistingAccountsPreserved'];complete()
    return {'status':'PASS', 'actualLegacyToPersistentCookieProfileMigration':True,
            'targetProfileVersion':json.loads((release/'connected-release.json').read_text())['version'],
            'coherentCheckpointKeepsGuestPidAndCookie':True,
            'accountsAndAuthorityPreservedWithoutRestore':True, 'noOpPreservesPids':True, 'actualAuthenticatedCli':True,
            'actualEarlyInterruptionRecovery':evidence,
            'pendingOuterJournalRefusesAnotherRollout':True,
            'actualInnerUnitReplacementRecovered':True,
            'committedCodeKeptAfterOuterInterruption':True,
            'failedIssuerStartupRevertsCodeAndKeepsCookie':True,
            'allThreeRolesRunningAndJournalsCleared':True}
