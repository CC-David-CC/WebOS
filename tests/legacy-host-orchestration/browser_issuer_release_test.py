"""Run the built production-derived issuer with isolated development state."""
import json
import importlib.util
import os
from pathlib import Path
import socket
import subprocess
import sys
import tempfile
import time
import unittest
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

ROOT=Path(__file__).resolve().parents[1]
RELEASE=Path(os.environ.get('CODI_ISSUER_CANDIDATE',ROOT/'.build/browser-native-candidate/profile28-r3'))
GEO=ROOT/'active-system/.build/browser-geoip/dbip-country-lite-2026-10.mmdb'
PIN='7faf30b5457fa629acc7ffa695c15a6a8a56098ba4372412260ade478af5a537'


class CandidateIssuerTest(unittest.TestCase):
    def test_turn_preference_matches_existing_profile(self):
        baseline=ROOT/'.build/browser-native-candidate/base-release'
        if not baseline.is_dir() or not RELEASE.is_dir():self.skipTest('Candidate and baseline releases required')
        values=[]
        for root in (baseline,RELEASE):
            root=root.resolve();sys.path.insert(0,str(root))
            try:
                spec=importlib.util.spec_from_file_location('turn_test_'+root.name,root/'origin_service/turn_management.py')
                module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
                values.append(module.public_policy({'release':str(root),'turn':{'urls':['turns:turn.ksu.codes:443?transport=tcp'],'iceTransportPolicy':'all'}}))
            finally:sys.path.pop(0)
        self.assertEqual(values[0],values[1])

    def test_split_listener_configuration_and_rule_updates(self):
        if not RELEASE.is_dir() or not GEO.is_file():self.skipTest('Candidate release and local Geo-IP fixture required')
        def port():
            with socket.socket() as sock:
                sock.bind(('127.0.0.1',0));return sock.getsockname()[1]
        main,login=port(),port()
        while login==main:login=port()
        origin=f'http://127.0.0.1:{main}'
        def call(target,path, *, post=False, ip='8.8.8.8'):
            req=Request(f'http://127.0.0.1:{target}{path}',data=b'{}' if post else None,
                        headers={'Origin':origin,'Host':f'127.0.0.1:{main}',
                                 'Content-Type':'application/json','X-Codi-Client-IP':ip})
            try:
                with urlopen(req,timeout=2) as response:return response.status,response.read()
            except HTTPError as error:return error.code,error.read()
        with tempfile.TemporaryDirectory(prefix='codi-issuer-candidate-') as temporary:
            folder=Path(temporary);policy=folder/'policy.json'
            value={'version':'codi-network-access/1','incomingLogin':{'blockedCidrs':['203.0.113.0/24'],'blockedCountries':[]},'outgoing':{'blockedCidrs':[],'blockedCountries':[]}}
            policy.write_text(json.dumps(value))
            cmd=[sys.executable,'-B',str(RELEASE/'scripts/serve-connected.py'),'--port',str(main),
                 '--runtime-dir',str(folder/'runtime'),'--origin',origin,'--user-files',
                 '--browser-relay-policy-sha256',PIN,'--login-port',str(login),
                 '--login-access-policy',str(policy),'--login-geoip',str(GEO)]
            process=subprocess.Popen(cmd,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE,text=True)
            try:
                deadline=time.monotonic()+20
                while True:
                    if process.poll() is not None:self.fail('Candidate issuer exited: '+process.stderr.read())
                    try:
                        status,raw=call(main,'/config.json')
                        if status==200:break
                    except (URLError,TimeoutError,ConnectionError):pass
                    if time.monotonic()>deadline:self.fail('Candidate issuer did not start')
                    time.sleep(.1)
                config=json.loads(raw)
                self.assertEqual(config['browserRelay']['policySHA256'],PIN)
                self.assertEqual(call(main,'/api/v1/auth',post=True)[0],404)
                self.assertEqual(call(login,'/config.json')[0],404)
                self.assertEqual(call(login,'/api/v1/auth',post=True,ip='203.0.113.8')[0],403)
                self.assertNotEqual(call(login,'/api/v1/auth',post=True)[0],403)
                value['incomingLogin']['blockedCidrs'].append('8.8.8.8')
                updated=policy.with_suffix('.new');updated.write_text(json.dumps(value));updated.replace(policy)
                self.assertEqual(call(login,'/api/v1/auth',post=True)[0],403)
                # The Browser authorization handler is present, and rejects an invalid challenge.
                self.assertEqual(call(main,'/api/v1/browser-relay/challenge',post=True)[0],400)
            finally:
                process.terminate()
                try:process.wait(timeout=10)
                except subprocess.TimeoutExpired:process.kill();process.wait()
                process.stderr.close()


if __name__=='__main__':unittest.main()
