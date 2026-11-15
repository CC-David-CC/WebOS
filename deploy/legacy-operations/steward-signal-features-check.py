#!/usr/bin/env python3
"""Verify signed optional signal-feature validation without a network listener."""
import json,sys,time
from pathlib import Path
from types import SimpleNamespace
from cryptography.hazmat.primitives.asymmetric import ec
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from steward.protocol import Connection,jose
key=ec.generate_private_key(ec.SECP256R1());public=jose.public_jwk(key);now=int(time.time());identity={'sid':'test','sub':'test','name':'test','kind':'anonymous','key':public,'certificate':None};conn=Connection(SimpleNamespace(registry=SimpleNamespace(now=lambda:now),policy={'mode':'local-development'}));conn.key=public;conn.public=identity
base={'v':1,'kind':'offer','room':'room','iat':now,'exp':now+120,'reply_to':None,'sender':identity,'sdp':'v=0\r\ntest','applications':[]}
def verify(feature='absent'):
 body=dict(base)
 if feature!='absent':body['features']=feature
 return conn.signal(jose.sign(body,key,'codi-signal+jws'),'offer')
assert 'features' not in verify();assert verify(['codi-device/1:scout/1'])['features']==['codi-device/1:scout/1']
invalid=[None,'invalid',['a','a'],['x']*5,['x'*65],['🌍'*33],[{}],[1]]
for item in invalid:
 try:verify(item)
 except (ValueError,TypeError):continue
 raise AssertionError('invalid feature list accepted: '+repr(item))
print(json.dumps({'status':'PASS','validCases':2,'invalidCases':len(invalid),'scope':'Signed signal parser; no WebSocket or durable account state.'}))
