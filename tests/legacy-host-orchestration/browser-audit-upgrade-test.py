#!/usr/bin/env python3
"""Test the audit-disabled runtime upgrade transaction with fake service calls."""
import hashlib
import importlib.util
from pathlib import Path
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'active-system'))
from browser_service import audit_switch
spec=importlib.util.spec_from_file_location('audit_upgrade',ROOT/'active-system/scripts/upgrade-browser-audit-runtime.py')
upgrade=importlib.util.module_from_spec(spec);spec.loader.exec_module(upgrade)

class UpgradeTest(unittest.TestCase):
    def test_routed_readiness_is_retried_after_systemd_starts(self):
        attempts=[]
        def check():
            attempts.append(1)
            if len(attempts)<3:raise ValueError('socket not ready')
        with patch.object(upgrade.time,'sleep',return_value=None):upgrade.wait_check(SimpleNamespace(check=check))
        self.assertEqual(len(attempts),3)

    def run_upgrade(self,fail=False,exercise=False):
        with tempfile.TemporaryDirectory(prefix='codi-audit-upgrade-test-') as folder:
            root=Path(folder);unit=root/'unit';dest=root/'policy';host=root/'host.lock';lock=root/'policy.lock';journal=root/'journal';backup=root/'backup'
            old=b'old-id old-id\n';new=b'new-id new-id\n';unit.write_bytes(old);dest.write_text('{}');host.touch();lock.touch()
            state={'restarts':0}
            def restart():
                state['restarts']+=1
                if fail and state['restarts']==1:raise RuntimeError('simulated restart failure')
            policy=SimpleNamespace(load=lambda _:SimpleNamespace(server_audit_enabled=False))
            renderer=SimpleNamespace(render=lambda **_:new.decode())
            operator=SimpleNamespace(imports=lambda:(audit_switch,renderer,policy),protected=lambda *a,**k:None,protected_parents=lambda *_:None,restart=restart,check=lambda:None,VENV='a',ISSUER='b',POLICY='c')
            replacements={'UNIT':unit,'DEST':dest,'HOST_LOCK':host,'POLICY_LOCK':lock,'JOURNAL':journal,'BACKUP':backup,'OLD':'old-id','NEW':'new-id','OLD_UNIT':hashlib.sha256(old).hexdigest(),'NEW_UNIT':hashlib.sha256(new).hexdigest()}
            with patch.multiple(upgrade,**replacements),patch.object(upgrade,'operator',return_value=operator),patch.object(upgrade.os,'geteuid',return_value=0),patch.object(upgrade.socket,'gethostname',return_value='box-webhost'),patch.object(upgrade.subprocess,'run',return_value=SimpleNamespace(stdout='')),patch.object(sys,'argv',['upgrade','exercise' if exercise else 'apply']):
                if fail:
                    with self.assertRaisesRegex(RuntimeError,'restart failure'):upgrade.main()
                    self.assertEqual(unit.read_bytes(),old);self.assertEqual(state['restarts'],2)
                elif exercise:
                    upgrade.main();self.assertEqual(unit.read_bytes(),old);self.assertEqual(state['restarts'],2)
                else:
                    upgrade.main();self.assertEqual(unit.read_bytes(),new);self.assertEqual(state['restarts'],1)
                saved=backup.with_name('codi-browser-relay-before-audit-runtime-exercise.service') if exercise else backup
                self.assertEqual(saved.read_bytes(),old);self.assertFalse(journal.exists());self.assertEqual(dest.read_text(),'{}')
    def test_apply_keeps_policy_and_backups_unit(self):self.run_upgrade()
    def test_failed_restart_restores_prior_unit(self):self.run_upgrade(fail=True)
    def test_exercise_restores_prior_unit(self):self.run_upgrade(exercise=True)

if __name__=='__main__':unittest.main(verbosity=2)
