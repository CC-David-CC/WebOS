#!/usr/bin/env python3
"""Run the exact private package, post SYSTEM notices, and read its HTTP API."""
import json,os,socket,subprocess,sys,tempfile,urllib.request
from pathlib import Path
from cryptography.hazmat.primitives.asymmetric import ec
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'codiserver-server-v0.3.0'))
from codiauth import jose
package=ROOT/'.build/official-services/system-channel-r2';python=sys.executable
with tempfile.TemporaryDirectory(prefix='codi-system-package-') as directory:
 root=Path(directory);root.chmod(0o700);state=root/'state';admin=package/'scripts/official-admin.py'
 def run(action,text=None):return json.loads(subprocess.run([python,'-I','-B',str(admin),'--state',str(state),action],input=text,text=True,capture_output=True,check=True).stdout)
 run('init');info=run('system-init');first=run('system-post','First packaged system notice');second=run('system-post','Second packaged system notice');assert first['height']==1 and second['height']==2
 with socket.socket() as sock:sock.bind(('127.0.0.1',0));port=sock.getsockname()[1]
 pub=jose.public_jwk(ec.generate_private_key(ec.SECP256R1()));policy={'mode':'server','issuer':'http://127.0.0.1:'+str(port),'authorityKeys':[{'kid':'fixture','jwk':pub}]};policy_path=root/'policy.json';policy_path.write_text(json.dumps(policy))
 process=subprocess.Popen([python,'-I','-B',str(package/'scripts/run-official-runtime.py'),'--database',str(state/'official.sqlite'),'--ledger',str(state/'access.sqlite'),'--issuer-policy',str(policy_path),'--port',str(port)],stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
 try:
  ready=json.loads(process.stdout.readline());assert ready['status']=='ready'
  def get(path):
   with urllib.request.urlopen('http://127.0.0.1:'+str(port)+path,timeout=5) as r:return json.load(r)
  item=get('/official-channel?channel=system')['items'][0];assert item['channel']==info['channel'] and item['label']=='SYSTEM'
  head=get('/official-head?channel='+info['channel']);assert head['height']==2 and head['head']==second['head']
  assert run('system-post','Third packaged system notice')['height']==3
  assert get('/official-head?channel='+info['channel'])['height']==3
  process.terminate();stdout,stderr=process.communicate(timeout=15)
  if process.returncode:raise RuntimeError(stderr)
  process=subprocess.Popen([python,'-I','-B',str(package/'scripts/run-official-runtime.py'),'--database',str(state/'official.sqlite'),'--ledger',str(state/'access.sqlite'),'--issuer-policy',str(policy_path),'--port',str(port)],stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
  assert json.loads(process.stdout.readline())['status']=='ready';assert get('/official-head?channel='+info['channel'])['height']==3;assert run('system-post','After restart')['height']==4
  print(json.dumps({'status':'PASS','checks':6,'package':'system-channel-r2'}))
 finally:
  process.terminate();stdout,stderr=process.communicate(timeout=15)
  if process.returncode:raise RuntimeError(stderr)
