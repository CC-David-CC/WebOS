#!/usr/bin/env python3
"""Real loopback WS protocol checks; fixture SDP is not WebRTC connectivity proof."""
import asyncio,json,secrets,socket,sys,time,urllib.request,threading,hashlib
from http.server import ThreadingHTTPServer
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent.parent))
from cryptography.hazmat.primitives.asymmetric import ec
from websockets.asyncio.client import connect
from websockets.exceptions import ConnectionClosed,InvalidStatus
from steward.protocol import jose,AUTH,CHALLENGE,REQUEST,RESPONSE,EVENT,LEASE,ERROR
from steward.server import StewardServer
from steward.publisher import PublisherState
from serve import PublicHandler

def key():return ec.generate_private_key(ec.SECP256R1())

def fixture():
 root,service=key(),key();realm=secrets.token_urlsafe(32);scope=secrets.token_urlsafe(32);now=int(time.time())
 with socket.socket() as s:s.bind(('127.0.0.1',0));port=s.getsockname()[1]
 endpoint=f'ws://127.0.0.1:{port}/rendezvous'
 grant={'key_id':jose.thumbprint(jose.public_jwk(service)),'public_key':jose.public_jwk(service),'endpoints':[endpoint],'scopes':[scope],'limits':{'lease_seconds':10,'sample_size':4,'signal_bytes':32768},'exp':now+600,'failure_domain':'one-loopback-host'}
 seed={'version':'codi-seed/1','realm':realm,'revision':1,'iat':now,'exp':now+600,'stewards':[grant]}
 state_dir=Path(__file__).resolve().parent.parent/'.build/checks/publisher-network'/secrets.token_hex(12);state_dir.parent.mkdir(parents=True,exist_ok=True);publisher=PublisherState.initialize(state_dir)
 args=dict(publisher_state=publisher,seed=jose.sign(seed,root,'codi-seed/1'),root_key=jose.public_jwk(root),realm=realm,endpoint=endpoint,service_key=service,identity_policy={'mode':'local-development'},origins=['http://127.0.0.1:8097'],admission_seconds=12)
 return args,scope,port,root,seed

class Client:
 def __init__(self,args,scope):
  self.args=args;self.scope=scope;self.key=key();sid=secrets.token_urlsafe(24);self.identity={'sid':sid,'sub':sid,'name':'fixture','kind':'anonymous','key':jose.public_jwk(self.key),'certificate':None};self.sequence=0
 async def open(self,patch=None):
  self.ws=await connect(self.args['endpoint'],origin='http://127.0.0.1:8097',compression=None,max_size=65536,proxy=None)
  challenge=jose.verify(await self.ws.recv(),jose.public_jwk(self.args['service_key']),CHALLENGE);self.nonce=challenge['nonce'];now=int(time.time())
  p={'version':AUTH,'realm':self.args['realm'],'endpoint':self.args['endpoint'],'nonce':self.nonce,'iat':now,'exp':now+30,'identity':self.identity,'scopes':[self.scope]};p.update(patch or {})
  await self.ws.send(jose.sign(p,self.key,AUTH));return await self.receive(RESPONSE)
 async def receive(self,typ):return jose.verify(await self.ws.recv(),jose.public_jwk(self.args['service_key']),typ)
 async def send(self,op,body,patch=None):
  self.sequence+=1;now=int(time.time());p={'version':REQUEST,'nonce':self.nonce,'sequence':self.sequence,'iat':now,'exp':now+30,'operation':op,'body':body};p.update(patch or {})
  await self.ws.send(jose.sign(p,self.key,REQUEST))
 async def call(self,op,body):
  await self.send(op,body);token=await self.ws.recv()
  try:jose.inspect(token,ERROR);typ=ERROR
  except ValueError:typ=RESPONSE
  return jose.verify(token,jose.public_jwk(self.args['service_key']),typ)['body']
 async def register(self,invitations=True):
  body=await self.call('REGISTER_LEASE',{'scope':self.scope,'invitations':invitations});return jose.verify(body['lease'],jose.public_jwk(self.args['service_key']),LEASE)
 def signal(self,kind,room,reply_to=None,patch=None):
  now=int(time.time());p={'v':1,'kind':kind,'room':room,'iat':now,'exp':now+120,'reply_to':reply_to,'sender':self.identity,'sdp':'v=0\r\nfixture-only\r\n','applications':[]};p.update(patch or {});return jose.sign(p,self.key,'codi-signal+jws')
 async def close(self):await self.ws.close()

async def main():
 args,scope,port,_,_=fixture();server=StewardServer(**args);await server.start(port);checks=[]
 async def connect_pair():
  a,b=Client(args,scope),Client(args,scope);await a.open();await b.open();la,lb=await a.register(),await b.register();return a,b,la,lb
 try:
  a,b,la,lb=await connect_pair()
  for label,patch in [('legacy',{}),('features',{'features':['codi-device/1:scout/1','codi-device/1:retry-hint/1']})]:
   offer=a.signal('offer','room-'+label,patch=patch);await a.send('FORWARD_SIGNAL',{'kind':'offer','signal':offer,'source_id':la['lease_id'],'destination_id':lb['lease_id'],'reply_route':lb['reply_route'],'route_id':None});event=await b.receive(EVENT);ack=await a.receive(RESPONSE);assert event['body']['signal']==offer and ack['body']['route_id'];checks.append(label+' offer forwarded intact')
  await a.close();await b.close()
  for label,features in [('null',None),('wrong-type','x'),('duplicates',['x','x']),('excess',['a','b','c','d','e']),('oversized',['x'*65]),('unicode-oversized',['🌍'*33]),('non-string',[{}])]:
   a,b,la,lb=await connect_pair();offer=a.signal('offer','bad-'+label,patch={'features':features});await a.send('FORWARD_SIGNAL',{'kind':'offer','signal':offer,'source_id':la['lease_id'],'destination_id':lb['lease_id'],'reply_route':lb['reply_route'],'route_id':None})
   try:await asyncio.wait_for(a.ws.recv(),5);raise AssertionError('invalid features accepted: '+label)
   except ConnectionClosed as e:assert e.rcvd and e.rcvd.code==1008
   await a.close();await b.close();checks.append(label+' rejected before forwarding')
 finally:await server.close()
 print(json.dumps({'status':'PASS','checks':checks,'scope':'Local authenticated signed WebSocket forwarding, fixture SDP, no real RTC or account identity.'},indent=2))
asyncio.run(main())
