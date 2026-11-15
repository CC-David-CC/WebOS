#!/usr/bin/env python3
"""Exercise actual loopback official backend health and policy matching."""
import json,select,socket,subprocess,sys,tempfile,urllib.error,urllib.request
from pathlib import Path
from cryptography.hazmat.primitives.asymmetric import ec
ROOT=Path(__file__).resolve().parents[2];sys.path[:0]=[str(ROOT),str(ROOT/'codiserver-server-v0.3.0')]
from codiauth import jose
from origin_service.official_management import check_backend
class Op:
 def read_owned(self,path,*args):return Path(path).read_bytes()
with tempfile.TemporaryDirectory(prefix='official-health-') as tmp:
 root=Path(tmp);state=root/'state';subprocess.run([sys.executable,str(ROOT/'scripts/official-admin.py'),'--state',str(state),'init'],check=True,capture_output=True)
 policy={'mode':'server','issuer':'http://127.0.0.1:8091','authorityKeys':[{'kid':'fixture','jwk':jose.public_jwk(ec.generate_private_key(ec.SECP256R1()))}]};policyfile=root/'policy.json';policyfile.write_text(json.dumps(policy));public=root/'public';public.mkdir();(public/'origin-discovery.json').write_text(json.dumps({'identity':policy}))
 with socket.socket() as s:s.bind(('127.0.0.1',0));port=s.getsockname()[1]
 p=subprocess.Popen([sys.executable,str(ROOT/'scripts/run-official-runtime.py'),'--database',str(state/'official.sqlite'),'--ledger',str(state/'access.sqlite'),'--issuer-policy',str(policyfile),'--port',str(port)],stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
 try:
  assert select.select([p.stdout],[],[],15)[0] and json.loads(p.stdout.readline())['port']==port
  config={'stateRoot':str(root),'origin':policy['issuer']};assert check_backend(Op(),config,port)
  (public/'origin-discovery.json').write_text(json.dumps({'identity':policy|{'issuer':'http://127.0.0.1:8092'}}))
  try:check_backend(Op(),config,port);raise AssertionError('wrong issuer accepted')
  except ValueError:pass
  (public/'origin-discovery.json').write_text(json.dumps({'identity':policy|{'authorityKeys':[]}}))
  try:check_backend(Op(),config,port);raise AssertionError('wrong keys accepted')
  except ValueError:pass
  try:urllib.request.urlopen('http://127.0.0.1:'+str(port)+'/internal/official-health',timeout=2);raise AssertionError('bad host accepted')
  except urllib.error.HTTPError as error:assert error.code==403
 finally:
  p.terminate();p.wait(timeout=10);p.stdout.close();p.stderr.close()
print('PASS: live loopback health accepts matching identity and rejects wrong issuer, keys and Host')
