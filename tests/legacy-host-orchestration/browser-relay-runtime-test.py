#!/usr/bin/env python3
"""Verify source-only runtime export and rejection of mutations."""
import importlib.util
import hashlib
import os
import select
import subprocess
import sys
import json
from pathlib import Path
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]
def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module
builder=load('runtime_builder',ROOT/'active-system/scripts/build-browser-relay-runtime.py')
runner=load('runtime_runner',ROOT/'active-system/scripts/serve-browser-relay.py')

class Runtime(unittest.TestCase):
    def test_optional_audit_is_disabled_by_default_and_requires_private_credential(self):
        from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
        from cryptography.hazmat.primitives import serialization
        with tempfile.TemporaryDirectory(prefix='codi-audit-mode-') as folder:
            root=Path(folder);policy=root/'policy.json';source=ROOT/'apps/system/browser/relay/policy.json'
            value=json.loads(source.read_text());policy.write_text(json.dumps(value));key=root/'key';database=root/'events.sqlite3'
            self.assertIsNone(runner.optional_audit(policy,database,key));self.assertFalse(database.exists());self.assertFalse(key.exists())
            value['serverAuditEnabled']=True;policy.write_text(json.dumps(value))
            with self.assertRaisesRegex(ValueError,'requires'):runner.optional_audit(policy,None,None)
            key.write_bytes(Ed25519PrivateKey.generate().private_bytes(serialization.Encoding.Raw,serialization.PrivateFormat.Raw,serialization.NoEncryption()));key.chmod(0o644)
            with self.assertRaisesRegex(ValueError,'private'):runner.optional_audit(policy,database,key)
            key.chmod(0o600);append=runner.optional_audit(policy,database,key)
            result=append({'subject':'user:test','source':'203.0.113.1','destination':'example.com','port':443,'event':'opened'})
            self.assertEqual(result['seq'],1);self.assertTrue(database.is_file())
            import sqlite3
            with sqlite3.connect(database) as db:db.execute("UPDATE events SET record='{}' WHERE seq=1")
            with self.assertRaisesRegex(ValueError,'chain changed'):runner.optional_audit(policy,database,key)

    def test_exact_runtime_and_tampering(self):
        with tempfile.TemporaryDirectory(prefix='codi-browser-export-') as folder:
            dest=Path(folder)/'runtime';result=builder.build(dest);old_root=runner.ROOT;runner.ROOT=dest/'active-system'
            try:
                self.assertEqual(runner.verify_runtime(result['manifestSHA256'])['sourceCommit'],result['sourceCommit'])
                with self.assertRaises(ValueError):runner.verify_runtime('0'*64)
                if os.getuid()!=0:
                    with self.assertRaises(ValueError):runner.verify_runtime(result['manifestSHA256'],require_root=True)
                target=dest/'apps/system/browser/relay/wisp.py';target.chmod(0o664)
                with self.assertRaises(ValueError):runner.verify_runtime(result['manifestSHA256'])
                target.chmod(0o644)
                target=dest/'apps/system/browser/relay/wisp.py';original=target.read_bytes();target.write_bytes(original+b'\n# changed\n')
                with self.assertRaises(ValueError):runner.verify_runtime(result['manifestSHA256'])
                target.write_bytes(original);extra=dest/'extra.py';extra.write_text('unexpected')
                with self.assertRaises(ValueError):runner.verify_runtime(result['manifestSHA256'])
                extra.unlink();link=dest/'bad-link';link.symlink_to(target)
                with self.assertRaises(ValueError):runner.verify_runtime(result['manifestSHA256'])
                link.unlink();self.assertEqual(runner.verify_runtime(result['manifestSHA256'])['version'],'codi-browser-relay-runtime/1')
            finally:runner.ROOT=old_root

    def test_exported_process_starts_only_with_exact_pin(self):
        from cryptography.hazmat.primitives.asymmetric import ec
        from codiauth import jose
        with tempfile.TemporaryDirectory(prefix='codi-browser-exec-') as folder:
            root=Path(folder);dest=root/'runtime';result=builder.build(dest)
            key=ec.generate_private_key(ec.SECP256R1());issuer=root/'issuer.json'
            issuer.write_text(json.dumps({'mode':'server','issuer':'https://ksu.codes','authorityKeys':[{'kid':'fixture','jwk':jose.public_jwk(key)}]}));issuer.chmod(0o600)
            domain=root/'domain.json';domain.write_bytes((ROOT/'apps/system/browser/relay/policy.json').read_bytes());domain.chmod(0o600)
            access=root/'access.json';access.write_bytes((ROOT/'active-system/network_policy/default.json').read_bytes());access.chmod(0o600)
            socketdir=root/'socket';socketdir.mkdir(mode=0o750);sock=socketdir/'relay.sock'
            command=[sys.executable,'-I','-B',str(dest/'active-system/scripts/serve-browser-relay.py'),'--origin','https://ksu.codes','--runtime-manifest-sha256',result['manifestSHA256'],'--issuer-policy',str(issuer),'--issuer-policy-sha256',hashlib.sha256(issuer.read_bytes()).hexdigest(),'--policy-sha256','a'*64,'--destination-policy',str(domain),'--access-policy',str(access),'--socket',str(sock),'--proxy-uid',str(os.getuid()),'--proxy-gid',str(os.getgid())]
            bad=subprocess.run([('0'*64 if item==result['manifestSHA256'] else item) for item in command],capture_output=True,text=True,timeout=10)
            self.assertNotEqual(bad.returncode,0);self.assertFalse(sock.exists())
            process=subprocess.Popen(command,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
            try:
                ready,_,_=select.select([process.stdout],[],[],10);self.assertTrue(ready,'Runtime failed to report readiness')
                self.assertIn('ready',process.stdout.readline());self.assertTrue(sock.is_socket())
            finally:
                process.terminate();stdout,stderr=process.communicate(timeout=10)
            self.assertEqual(process.returncode,0,stderr);self.assertFalse(sock.exists())

if __name__=='__main__':unittest.main(verbosity=2)
