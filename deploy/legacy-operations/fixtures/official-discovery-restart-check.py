#!/usr/bin/env python3
"""Real runtime exits on discovery change and loads replacement on restart."""
import json,select,socket,subprocess,sys,tempfile,urllib.request
from pathlib import Path
from cryptography.hazmat.primitives.asymmetric import ec
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'codiserver-server-v0.3.0'));from codiauth import jose
with tempfile.TemporaryDirectory(prefix='official-discovery-') as temp:
 root=Path(temp);state=root/'state';subprocess.run([sys.executable,str(ROOT/'scripts/official-admin.py'),'--state',str(state),'init'],check=True,capture_output=True)
 with socket.socket() as s:s.bind(('127.0.0.1',0));port=s.getsockname()[1]
 def identity(kid):return {'mode':'server','issuer':'http://127.0.0.1:8091','authorityKeys':[{'kid':kid,'jwk':jose.public_jwk(ec.generate_private_key(ec.SECP256R1()))}]}
 discovery=root/'discovery.json';first=identity('first');second=identity('second');discovery.write_text(json.dumps({'identity':first}))
 def start():
  child=subprocess.Popen([sys.executable,str(ROOT/'scripts/run-official-runtime.py'),'--database',str(state/'official.sqlite'),'--ledger',str(state/'access.sqlite'),'--issuer-discovery',str(discovery),'--port',str(port)],stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
  assert select.select([child.stdout],[],[],15)[0] and json.loads(child.stdout.readline())['status']=='ready';return child
 def health():
  request=urllib.request.Request('http://127.0.0.1:'+str(port)+'/internal/official-health',headers={'Host':'127.0.0.1:8091'})
  with urllib.request.urlopen(request,timeout=3) as response:return json.load(response)['identity']
 child=start()
 try:
  assert health()==first;discovery.write_text(json.dumps({'identity':second}));assert child.wait(timeout=8)!=0;child.stdout.close();child.stderr.close();child=start();assert health()==second
 finally:
  if child.poll() is None:child.terminate();child.wait(timeout=10)
  child.stdout.close();child.stderr.close()
print('PASS: actual runtime restarts onto changed discovery identity (restart supervised by fixture)')
