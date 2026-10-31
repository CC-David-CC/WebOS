#!/usr/bin/env python3
"""Explicit root-only isolated systemd rollback exercise; never touches live units."""
import os
from pathlib import Path
import subprocess
import sys
import tempfile

ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'active-system'))
from browser_service import audit_switch

UNIT=Path('/etc/systemd/system/codi-browser-audit-fixture.service')
NAME=UNIT.name
OFF=b'[Unit]\nDescription=Codi audit fixture\n[Service]\nType=oneshot\nRemainAfterExit=yes\nExecStart=/usr/bin/true\n'
ON=b'[Unit]\nDescription=Codi audit fixture\n[Service]\nType=oneshot\nRemainAfterExit=yes\nEnvironment=CODI_AUDIT_FIXTURE=on\nExecStart=/usr/bin/true\n'
BAD=b'[Unit]\nDescription=Codi audit fixture\n[Service]\nType=oneshot\nRemainAfterExit=yes\nExecStart=/usr/bin/false\n'

def command(*args,check=True):return subprocess.run(args,check=check,capture_output=True,text=True,timeout=30)
def restart():command('systemctl','daemon-reload');command('systemctl','restart',NAME)
def check():command('systemctl','is-active','--quiet',NAME)
def validate(policy,unit):
    import json
    assert isinstance(json.loads(policy)['serverAuditEnabled'],bool)
    assert unit in (OFF,ON,BAD)
    with tempfile.TemporaryDirectory(prefix='codi-audit-verify-') as folder:
        p=Path(folder)/NAME;p.write_bytes(unit);command('systemd-analyze','verify',str(p))

def main():
    if sys.argv!=[sys.argv[0],'--run'] or os.geteuid()!=0:raise ValueError('Root and explicit --run required')
    if UNIT.exists() or UNIT.is_symlink():raise ValueError('Fixture unit already exists')
    with tempfile.TemporaryDirectory(prefix='codi-audit-systemd-fixture-',dir='/run') as folder:
        policy=Path(folder)/'policy.json';journal=Path(folder)/'journal.json';original=b'{"serverAuditEnabled": false, "blacklist": ["example.com"]}\n';policy.write_bytes(original);policy.chmod(0o600)
        try:
            fd=os.open(UNIT,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o644)
            with os.fdopen(fd,'wb') as f:f.write(OFF)
            restart();check()
            result=audit_switch.switch(policy,UNIT,journal,expected_unit=OFF,candidate_unit=ON,enabled=True,validate=validate,restart=restart,check=check)
            assert result['status']=='enabled' and UNIT.read_bytes()==ON
            before=policy.read_bytes()
            try:audit_switch.switch(policy,UNIT,journal,expected_unit=ON,candidate_unit=BAD,enabled=False,validate=validate,restart=restart,check=check)
            except subprocess.CalledProcessError:pass
            else:raise AssertionError('Failed service unexpectedly succeeded')
            assert policy.read_bytes()==before and UNIT.read_bytes()==ON and not journal.exists();check()
            def interrupt():raise SystemExit('simulated interruption')
            try:audit_switch.switch(policy,UNIT,journal,expected_unit=ON,candidate_unit=OFF,enabled=False,validate=validate,restart=interrupt,check=check)
            except SystemExit:pass
            else:raise AssertionError('Interruption not simulated')
            assert journal.is_file()
            assert audit_switch.recover(policy,UNIT,journal,restart=restart,check=check)['status']=='rolled-back'
            assert policy.read_bytes()==before and UNIT.read_bytes()==ON and not journal.exists();check()
            print('PASS isolated systemd enable, failed restart rollback, and interrupted transition recovery')
        finally:
            command('systemctl','stop',NAME,check=False)
            if UNIT.is_symlink() or (UNIT.exists() and UNIT.read_bytes() not in (OFF,ON,BAD)):raise ValueError('Fixture unit changed independently; manual cleanup required')
            UNIT.unlink(missing_ok=True);command('systemctl','daemon-reload',check=False);command('systemctl','reset-failed',NAME,check=False)

if __name__=='__main__':main()
