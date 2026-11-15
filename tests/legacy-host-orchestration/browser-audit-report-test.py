#!/usr/bin/env python3
"""Exercise private ledger verification and per-account/all-account totals."""
import json
import sqlite3
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'apps/system/browser'))
from relay.audit import AuditLedger

class AuditReportTest(unittest.TestCase):
    def test_existing_ledger_and_account_scope(self):
        with tempfile.TemporaryDirectory(prefix='codi-audit-report-') as folder:
            root=Path(folder);key=Ed25519PrivateKey.generate();keyfile=root/'key';keyfile.write_bytes(key.private_bytes(serialization.Encoding.Raw,serialization.PrivateFormat.Raw,serialization.NoEncryption()));keyfile.chmod(0o600)
            database=root/'events.sqlite3';ledger=AuditLedger(database,key)
            first='user:11111111-1111-4111-8111-111111111111';second='user:22222222-2222-4222-8222-222222222222'
            for subject in (first,second):ledger.append({'subject':subject,'source':'203.0.113.5','destination':'example.com','port':443,'event':'opened'})
            head=ledger.verify()['head'];command=[sys.executable,str(ROOT/'active-system/scripts/browser-audit-report.py'),'--database',str(database),'--key',str(keyfile)]
            def run(*extra):return subprocess.run([*command,*extra],capture_output=True,text=True,timeout=10)
            all_users=json.loads(run('--expected-head',head).stdout);self.assertEqual(all_users['domains'][0]['connections'],2)
            one=json.loads(run('--subject',first).stdout);self.assertEqual(one['domains'][0]['connections'],1)
            self.assertNotEqual(run('--expected-head','0'*64).returncode,0)
            self.assertNotEqual(run('--subject','user:../../bad').returncode,0)
            missing=subprocess.run([*command[:2],'--database',str(root/'missing.sqlite3'),'--key',str(keyfile)],capture_output=True,text=True,timeout=10)
            self.assertNotEqual(missing.returncode,0);self.assertFalse((root/'missing.sqlite3').exists())
            unrelated=root/'unrelated.sqlite3'
            with sqlite3.connect(unrelated) as db:db.execute('CREATE TABLE unrelated (value TEXT)')
            wrong=subprocess.run([*command[:2],'--database',str(unrelated),'--key',str(keyfile)],capture_output=True,text=True,timeout=10)
            self.assertNotEqual(wrong.returncode,0)
            with sqlite3.connect(unrelated) as db:self.assertIsNone(db.execute("SELECT name FROM sqlite_master WHERE name='events'").fetchone())

if __name__=='__main__':unittest.main(verbosity=2)
