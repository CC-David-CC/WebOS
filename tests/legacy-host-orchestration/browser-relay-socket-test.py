#!/usr/bin/env python3
"""Test Browser relay's Unix peer credentials and trusted-address boundary."""
import asyncio
import importlib.util
import hashlib
import json
import signal
import sys
import os
from pathlib import Path
import tempfile
import unittest
from aiohttp import ClientSession, UnixConnector, web
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives import serialization

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('relay_runner',ROOT/'active-system/scripts/serve-browser-relay.py')
runner=importlib.util.module_from_spec(spec);spec.loader.exec_module(runner)
from codiauth import jose

class SocketBoundary(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.temp=tempfile.TemporaryDirectory(prefix='codi-browser-socket-');self.addCleanup(self.temp.cleanup)
        key=ec.generate_private_key(ec.SECP256R1())
        self.policy={'mode':'server','issuer':'https://ksu.codes','authorityKeys':[{'kid':'fixture','jwk':jose.public_jwk(key)}]}
        self.origin='https://ksu.codes';self.socket=str(Path(self.temp.name)/'relay.sock')
        self.server=None
    async def start(self,uid):
        app=runner.make_app(origin=self.origin,base_path='',issuer_policy=self.policy,policy_sha256='a'*64,
                            destination_policy=ROOT/'apps/system/browser/relay/policy.json',
                            access_policy=ROOT/'active-system/network_policy/default.json',geo=None,proxy_uid=uid)
        self.server=web.AppRunner(app,access_log=None);await self.server.setup();await web.UnixSite(self.server,self.socket).start()
    async def asyncTearDown(self):
        if self.server:await self.server.cleanup()
    async def request(self,headers):
        async with ClientSession(connector=UnixConnector(path=self.socket)) as client:
            async with client.post('http://ksu.codes/browser-relay/challenge',json={},headers=headers) as response:return response.status,await response.text()
    async def test_only_trusted_peer_with_one_valid_address_can_reach_relay(self):
        await self.start(os.getuid());headers={'Host':'ksu.codes','Origin':self.origin,'X-Codi-Client-IP':'198.51.100.5'}
        status,body=await self.request(headers);self.assertEqual(status,200,body)
        for address in ('bad','198.51.100.5, 1.1.1.1','fe80::1%eth0'):
            bad={**headers,'X-Codi-Client-IP':address};self.assertEqual((await self.request(bad))[0],403)
        missing={k:v for k,v in headers.items() if k!='X-Codi-Client-IP'};self.assertEqual((await self.request(missing))[0],403)
        self.assertEqual((await self.request({**headers,'Origin':'https://evil.invalid'}))[0],403)
    async def test_real_process_validates_pins_and_cleans_socket(self):
        folder=Path(self.temp.name);folder.chmod(0o750)
        issuer=folder/'issuer.json';issuer.write_text(json.dumps(self.policy));issuer.chmod(0o600)
        destination=folder/'destination.json';destination.write_bytes((ROOT/'apps/system/browser/relay/policy.json').read_bytes());destination.chmod(0o600)
        access=folder/'access.json';access.write_bytes((ROOT/'active-system/network_policy/default.json').read_bytes());access.chmod(0o600)
        pin=hashlib.sha256(issuer.read_bytes()).hexdigest()
        command=[sys.executable,str(ROOT/'active-system/scripts/serve-browser-relay.py'),'--origin',self.origin,'--issuer-policy',str(issuer),'--issuer-policy-sha256',pin,'--policy-sha256','a'*64,'--destination-policy',str(destination),'--access-policy',str(access),'--socket',self.socket,'--proxy-uid',str(os.getuid()),'--proxy-gid',str(os.getgid())]
        bad=await asyncio.create_subprocess_exec(*[('0'*64 if part==pin else part) for part in command],stdout=asyncio.subprocess.PIPE,stderr=asyncio.subprocess.PIPE)
        await asyncio.wait_for(bad.communicate(),10);self.assertNotEqual(bad.returncode,0);self.assertFalse(Path(self.socket).exists())
        process=await asyncio.create_subprocess_exec(*command,stdout=asyncio.subprocess.PIPE,stderr=asyncio.subprocess.PIPE)
        try:
            line=await asyncio.wait_for(process.stdout.readline(),10);self.assertIn(b'ready',line)
            self.assertEqual(Path(self.socket).stat().st_mode&0o777,0o660)
            status,_=await self.request({'Host':'ksu.codes','Origin':self.origin,'X-Codi-Client-IP':'198.51.100.5'})
            self.assertEqual(status,200)
        finally:
            if process.returncode is None:process.send_signal(signal.SIGTERM)
            await asyncio.wait_for(process.communicate(),10)
        self.assertEqual(process.returncode,0);self.assertFalse(Path(self.socket).exists())

    async def test_wrong_unix_uid_is_rejected_even_with_forged_headers(self):
        await self.start(os.getuid()+1)
        headers={'Host':'ksu.codes','Origin':self.origin,'X-Codi-Client-IP':'1.1.1.1'}
        self.assertEqual((await self.request(headers))[0],403)

    async def test_real_process_opens_private_audit_only_after_opt_in_and_restarts(self):
        folder=Path(self.temp.name);folder.chmod(0o750);private=folder/'private';private.mkdir(mode=0o700)
        issuer=folder/'issuer.json';issuer.write_text(json.dumps(self.policy));issuer.chmod(0o600)
        destination=folder/'destination.json';policy=json.loads((ROOT/'apps/system/browser/relay/policy.json').read_text());destination.write_text(json.dumps(policy));destination.chmod(0o600)
        access=folder/'access.json';access.write_bytes((ROOT/'active-system/network_policy/default.json').read_bytes());access.chmod(0o600)
        key=private/'key';key.write_bytes(Ed25519PrivateKey.generate().private_bytes(serialization.Encoding.Raw,serialization.PrivateFormat.Raw,serialization.NoEncryption()));key.chmod(0o600)
        database=private/'events.sqlite3';pin=hashlib.sha256(issuer.read_bytes()).hexdigest()
        command=[sys.executable,str(ROOT/'active-system/scripts/serve-browser-relay.py'),'--origin',self.origin,'--issuer-policy',str(issuer),'--issuer-policy-sha256',pin,'--policy-sha256','a'*64,'--destination-policy',str(destination),'--access-policy',str(access),'--socket',self.socket,'--proxy-uid',str(os.getuid()),'--proxy-gid',str(os.getgid()),'--audit-database',str(database),'--audit-key',str(key)]
        async def start_stop():
            process=await asyncio.create_subprocess_exec(*command,stdout=asyncio.subprocess.PIPE,stderr=asyncio.subprocess.PIPE)
            try:
                line=await asyncio.wait_for(process.stdout.readline(),10);self.assertIn(b'ready',line)
                self.assertEqual((await self.request({'Host':'ksu.codes','Origin':self.origin,'X-Codi-Client-IP':'198.51.100.5'}))[0],200)
            finally:
                if process.returncode is None:process.send_signal(signal.SIGTERM)
                _,stderr=await asyncio.wait_for(process.communicate(),10)
            self.assertEqual(process.returncode,0,stderr);self.assertFalse(Path(self.socket).exists())
        await start_stop();self.assertFalse(database.exists(),'Disabled mode must not create a ledger')
        policy['serverAuditEnabled']=True;destination.write_text(json.dumps(policy));await start_stop()
        self.assertTrue(database.is_file());self.assertEqual(database.stat().st_mode&0o777,0o600)
        await start_stop()  # Existing signed ledger is accepted after restart.

if __name__=='__main__':unittest.main(verbosity=2)
