#!/usr/bin/env python3
"""Account preflight refusal tests, then idempotent validation of actual roles."""
import grp,hashlib,importlib.util,json,os,pwd,subprocess,sys,types,unittest
from pathlib import Path
from unittest.mock import patch
ROOT=Path(__file__).resolve().parent.parent
spec=importlib.util.spec_from_file_location('service_accounts',ROOT/'scripts/install-service-accounts.py');module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)

class Preflight(unittest.TestCase):
 def setUp(self):
  self.user=types.SimpleNamespace(pw_name='codi-issuer',pw_uid=997,pw_gid=984,pw_dir='/nonexistent',pw_shell='/usr/sbin/nologin')
  self.group=types.SimpleNamespace(gr_name='codi-issuer',gr_gid=984,gr_mem=[])
  self.users=[self.user];self.shadow=types.SimpleNamespace(stdout='codi-issuer:!:1:0:99999:7:::\n')
  self.patches=[patch.object(module.grp,'getgrnam',side_effect=lambda _:self.group),patch.object(module.pwd,'getpwnam',side_effect=lambda _:self.user),patch.object(module.pwd,'getpwall',side_effect=lambda:self.users),patch.object(module.os,'getgrouplist',return_value=[984]),patch.object(module.subprocess,'run',return_value=self.shadow)]
  for mock in self.patches:mock.start();self.addCleanup(mock.stop)
 def test_existing_locked_dedicated_account(self):self.assertEqual(module.validate('codi-issuer',1001),(self.user,self.group))
 def test_root_uid_refused(self):
  self.user.pw_uid=0
  with self.assertRaises(ValueError):module.validate('codi-issuer',1001)
 def test_interactive_user_uid_refused(self):
  self.user.pw_uid=1000
  with self.assertRaises(ValueError):module.validate('codi-issuer',1001)
 def test_normal_user_group_refused(self):
  self.group.gr_gid=self.user.pw_gid=1000
  with self.assertRaises(ValueError):module.validate('codi-issuer',1001)
 def test_primary_group_shared_by_other_account_refused(self):
  self.users.append(types.SimpleNamespace(pw_name='other',pw_uid=778,pw_gid=984))
  with self.assertRaises(ValueError):module.validate('codi-issuer',1001)
 def test_uid_alias_refused(self):
  self.users.append(types.SimpleNamespace(pw_name='alias',pw_uid=997,pw_gid=778))
  with self.assertRaises(ValueError):module.validate('codi-issuer',1001)
 def test_supplementary_group_refused(self):
  module.os.getgrouplist.return_value=[984,1000]
  with self.assertRaises(ValueError):module.validate('codi-issuer',1001)
 def test_group_with_explicit_member_refused(self):
  self.group.gr_mem=['other']
  with self.assertRaises(ValueError):module.validate('codi-issuer',1001)
 def test_shell_refused(self):
  self.user.pw_shell='/bin/bash'
  with self.assertRaises(ValueError):module.validate('codi-issuer',1001)
 def test_home_refused(self):
  self.user.pw_dir='/home/someone'
  with self.assertRaises(ValueError):module.validate('codi-issuer',1001)
 def test_unlocked_password_refused(self):
  self.shadow.stdout='codi-issuer:$6$redacted:1:0:99999:7:::\n'
  with self.assertRaises(ValueError):module.validate('codi-issuer',1001)
 def test_malformed_shadow_refused(self):
  self.shadow.stdout='malformed'
  with self.assertRaises(ValueError):module.validate('codi-issuer',1001)
 def test_wrong_explicit_guest_gid_refused(self):
  with self.assertRaises(ValueError):module.validate('codi-guest',1001)
 def test_missing_accounts_are_a_plan(self):
  module.grp.getgrnam.side_effect=KeyError;module.pwd.getpwnam.side_effect=KeyError
  self.assertEqual(module.validate('codi-issuer',1001),(None,None));module.subprocess.run.assert_not_called()

if __name__=='__main__':
 result=unittest.TextTestRunner(verbosity=1).run(unittest.defaultTestLoader.loadTestsFromTestCase(Preflight))
 report={'status':'FAIL','unitTests':result.testsRun,'failures':len(result.failures),'errors':len(result.errors),'scope':'Account preflight fixtures plus actual locked local account idempotence/collision; not deployed services'}
 if result.wasSuccessful():
  program=ROOT/'scripts/install-service-accounts.py';gid=grp.getgrnam('codi-guest').gr_gid
  def apply(value):return subprocess.run(['sudo','-n','/usr/bin/python3','-B',str(program),'--guest-gid',str(value),'--apply'],capture_output=True,text=True,timeout=15)
  first=apply(gid);assert first.returncode==0,first.stderr;first=json.loads(first.stdout)
  assert all(record['locked'] and not record['createdUser'] and not record['createdGroup'] for record in first['accounts'].values())
  collision=apply(os.getgid());assert collision.returncode!=0 and 'belongs to another group' in collision.stderr
  second=apply(gid);assert second.returncode==0 and json.loads(second.stdout)==first
  report.update(status='PASS',realAccounts=first['accounts'],existingAccountsNotChanged=True,realOccupiedGidRefusedBeforeMutation=True)
 report['sha256']={name:hashlib.sha256((ROOT/name).read_bytes()).hexdigest() for name in ['scripts/install-service-accounts.py','scripts/service-accounts-check.py']}
 (ROOT/'.build/checks/service-accounts-result.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
 if report['status']!='PASS':raise SystemExit(1)
