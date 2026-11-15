#!/usr/bin/env python3
"""Test candidate routes through real Caddy and a real official runtime."""
import importlib.util,json,select,socket,subprocess,sys,tempfile,time,urllib.error,urllib.request
from pathlib import Path
from cryptography.hazmat.primitives.asymmetric import ec
ROOT=Path(__file__).resolve().parents[2];sys.path[:0]=[str(ROOT),str(ROOT/'codiserver-server-v0.3.0'),str(ROOT/'.build/official-hosting-candidate-r1/ops')]
from codiauth import jose
import common
def port():
 with socket.socket() as s:s.bind(('127.0.0.1',0));return s.getsockname()[1]
with tempfile.TemporaryDirectory(prefix='official-ingress-') as tmp:
 folder=Path(tmp);state=folder/'state';subprocess.run([sys.executable,str(ROOT/'scripts/official-admin.py'),'--state',str(state),'init'],check=True,capture_output=True);front=port();backend=port();origin='http://127.0.0.1:'+str(front)
 policy={'mode':'server','issuer':origin,'authorityKeys':[{'kid':'fixture','jwk':jose.public_jwk(ec.generate_private_key(ec.SECP256R1()))}]};(folder/'policy.json').write_text(json.dumps(policy))
 runtime=subprocess.Popen([sys.executable,str(ROOT/'scripts/run-official-runtime.py'),'--database',str(state/'official.sqlite'),'--ledger',str(state/'access.sqlite'),'--issuer-policy',str(folder/'policy.json'),'--port',str(backend)],stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True);caddy=None
 try:
  assert select.select([runtime.stdout],[],[],15)[0] and json.loads(runtime.stdout.readline())['port']==backend
  for prefix in ('','/hidden'):
   lines=common.official_routes({'codi_official':True},prefix);routes='\n'.join(lines).replace('127.0.0.1:8145','127.0.0.1:'+str(backend));config=folder/'Caddyfile';config.write_text('{\n admin off\n auto_https off\n}\n'+origin+' {\n'+routes+'\n handle {\n respond "Not found" 404\n }\n}\n')
   caddy=subprocess.Popen(['/tmp/codi-official-caddy-fixture','run','--config',str(config),'--adapter','caddyfile'],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
   def get(path):
    try:
     with urllib.request.urlopen(origin+path,timeout=2) as r:return r.status,json.load(r)
    except urllib.error.HTTPError as e:return e.code,None
   end=time.monotonic()+10
   while True:
    try:status,value=get(prefix+'/official-directory?after=&limit=1');break
    except OSError:
     if caddy.poll() is not None or time.monotonic()>end:raise
     time.sleep(.1)
   assert status==200 and value['items']==[];assert get(prefix+'/internal/official-health')[0]==404;assert get(prefix+'/official-history/extra')[0]==404
   caddy.terminate();caddy.wait(timeout=10);caddy=None
  print('PASS: real Caddy proxies root and mounted official directory; health and undeclared paths unavailable')
 finally:
  if caddy:caddy.terminate();caddy.wait(timeout=10)
  runtime.terminate();runtime.wait(timeout=10);runtime.stdout.close();runtime.stderr.close()
