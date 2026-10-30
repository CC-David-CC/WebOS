#!/usr/bin/env python3
import json,os,subprocess,sys,time
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
from cryptography.hazmat.primitives.asymmetric import ec
from steward.protocol import jose, TYPE, KEY_VERSION, CHANNEL_PROFILE, PROFILE
root=Path(__file__).resolve().parents[2];python=sys.executable;cli=root/'scripts/manage-official-channels.py'
key=ec.generate_private_key(ec.SECP256R1());public=jose.public_jwk(key);channel=jose.digest(jose.dumps([KEY_VERSION,jose.thumbprint(public)]))
def sign(body):return jose.sign({'version':KEY_VERSION,'channel':channel,'key':public,'purpose':'checkpoint','body':body},key,TYPE)
policy=sign({'profile':CHANNEL_PROFILE,'type':'policy','channel':channel,'stream':'chat','validators':[channel],'publicWrite':True,'players':None,'publicRead':True});parts=policy.split('.');genesis=jose.digest(jose.dumps([CHANNEL_PROFILE,'signed-content',parts[0],parts[1]]));now=int(time.time());listing=sign({'profile':PROFILE,'category':'user','channel':channel,'genesisHash':genesis,'policyWire':policy,'label':'Operator fixture','description':'','issued':now,'expires':now+180})
directory=subprocess.check_output(['sudo','-n','mktemp','-d','/run/codi-official-fixture-XXXXXXXX'],text=True).strip()
def run(*args,wire=None,root=True,state=directory):return subprocess.run((['sudo','-n'] if root else [])+[python,str(cli),'--state-dir',state,*args],input=wire,text=True,capture_output=True,timeout=15)
try:
 assert run('enroll',wire=listing,root=False).returncode!=0
 assert run('enroll',wire='invalid').returncode!=0
 p=run('enroll',wire=listing);assert p.returncode==0,p.stderr;assert json.loads(p.stdout)['enabled'] is True
 p=run('disable',channel);assert p.returncode==0 and json.loads(p.stdout)['enabled'] is False
 p=run('inspect',channel);assert p.returncode==0 and json.loads(p.stdout)['enabled'] is False
 p=run('enable',channel);assert p.returncode==0 and json.loads(p.stdout)['enabled'] is True
 assert run('enable','missing').returncode!=0
 mode=subprocess.check_output(['sudo','-n','stat','-c','%a',directory+'/official.sqlite'],text=True).strip();assert mode=='600'
 subprocess.run(['sudo','-n','chmod','755',directory],check=True);assert run('inspect',channel).returncode!=0
 print(json.dumps({'status':'PASS','checks':['nonroot refused','invalid listing refused','valid listing enrolled','disable and enable persist','unknown channel refused','database mode protected','insecure directory refused'],'scope':'local root CLI only; no network listener or deployment'}))
finally:
 assert directory.startswith('/run/codi-official-fixture-') and '/' not in directory.removeprefix('/run/')
 subprocess.run(['sudo','-n','rm','-rf','--',directory],check=True)
