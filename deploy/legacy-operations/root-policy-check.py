#!/usr/bin/env python3
"""Actual native WS and Chrome policy reload tests in disposable loopback state."""
import asyncio,hashlib,json,secrets,socket,sys,threading,time,urllib.request
from http.server import ThreadingHTTPServer
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent.parent))
from cryptography.hazmat.primitives.asymmetric import ec
from websockets.asyncio.client import connect
from websockets.exceptions import ConnectionClosed
from steward.server import StewardServer
from steward.publisher import PublisherState,PublisherFrozen
from steward.protocol import jose,AUTH,REQUEST,RESPONSE,CHALLENGE
from serve import PublicHandler
ROOT=Path(__file__).resolve().parent.parent

class Peer:
 def __init__(self,fixture,scope):
  self.f=fixture;self.scope=scope;self.key=ec.generate_private_key(ec.SECP256R1());sid=secrets.token_urlsafe(24);self.public={'sid':sid,'sub':sid,'kind':'anonymous','name':'policy-fixture','key':jose.public_jwk(self.key),'certificate':None};self.seq=0
 async def open(self):
  self.ws=await connect(self.f.endpoint,origin='http://127.0.0.1:8100',proxy=None);p=jose.verify(await self.ws.recv(),jose.public_jwk(self.f.key),CHALLENGE);self.nonce=p['nonce'];now=int(time.time())
  await self.ws.send(jose.sign({'version':AUTH,'realm':self.f.realm,'endpoint':self.f.endpoint,'nonce':self.nonce,'iat':now,'exp':now+30,'identity':self.public,'scopes':[self.scope]},self.key,AUTH));return await self.ws.recv()
 async def request(self,operation,body):
  self.seq+=1;now=int(time.time());await self.ws.send(jose.sign({'version':REQUEST,'nonce':self.nonce,'sequence':self.seq,'iat':now,'exp':now+30,'operation':operation,'body':body},self.key,REQUEST));return jose.verify(await self.ws.recv(),jose.public_jwk(self.f.key),RESPONSE)['body']
 async def closed(self,code):
  try:await self.ws.recv()
  except ConnectionClosed as e:assert e.rcvd and e.rcvd.code==code;return
  raise AssertionError('Control remained open')
 async def close(self):
  if hasattr(self,'ws'):await self.ws.close()

class Fixture:
 async def start(self,origins=()):
  self.root=ec.generate_private_key(ec.SECP256R1());self.key=ec.generate_private_key(ec.SECP256R1());self.realm=secrets.token_urlsafe(32);self.a=secrets.token_urlsafe(32);self.b=secrets.token_urlsafe(32);now=int(time.time())
  with socket.socket() as selected:selected.bind(('127.0.0.1',0));self.port=selected.getsockname()[1]
  self.endpoint=f'ws://127.0.0.1:{self.port}/rendezvous'
  self.grant={'key_id':jose.thumbprint(jose.public_jwk(self.key)),'public_key':jose.public_jwk(self.key),'endpoints':[self.endpoint],'scopes':[self.a,self.b],'limits':{'lease_seconds':10,'sample_size':4,'signal_bytes':32768},'exp':now+240,'failure_domain':'one-loopback-host'}
  self.seed={'version':'codi-seed/1','realm':self.realm,'revision':1,'iat':now,'exp':now+240,'stewards':[self.grant]}
  directory=ROOT/'.build/checks/root-policy'/secrets.token_hex(12);directory.parent.mkdir(parents=True,exist_ok=True);self.state=PublisherState.initialize(directory)
  self.args={'seed':self.sign(self.seed),'root_key':jose.public_jwk(self.root),'realm':self.realm,'endpoint':self.endpoint,'service_key':self.key,'identity_policy':{'mode':'local-development'},'origins':['http://127.0.0.1:8100',*origins],'publisher_state':self.state,'admission_seconds':12}
  self.server=StewardServer(**self.args);self.server.descriptor();await self.server.start(self.port);return self
 def sign(self,seed):return jose.sign(seed,self.root,'codi-seed/1')
 def narrow(self):return {**self.seed,'revision':2,'stewards':[{**self.grant,'scopes':[self.b],'limits':{'lease_seconds':10,'sample_size':2,'signal_bytes':16384},'exp':self.seed['iat']+120}]}
 async def close(self):await self.server.close()

async def main():
 results=[];browser={}
 async def check(name,fn):
  try:await fn();results.append({'name':name,'status':'PASS'})
  except Exception as error:results.append({'name':name,'status':'FAIL','error':str(error)});raise
 async def invalid():
  f=await Fixture().start();p=Peer(f,f.a);await p.open();lease=await p.request('REGISTER_LEASE',{'scope':f.a,'invitations':True});generation=f.server.policy_generation
  try:
   variants=[jose.sign(f.narrow(),ec.generate_private_key(ec.SECP256R1()),'codi-seed/1'),f.sign({**f.seed,'revision':2,'realm':secrets.token_urlsafe(32)}),f.sign({**f.seed,'revision':2,'stewards':[{**f.grant,'limits':{'lease_seconds':999,'sample_size':2,'signal_bytes':16384}}]})]
   for token in variants:
    try:await f.server.reload_seed(token)
    except ValueError:pass
    else:raise AssertionError('Invalid root update accepted')
   assert f.server.policy_generation==generation and f.server.authorized
   assert (await p.request('RENEW',{'lease_id':jose.verify(lease['lease'],jose.public_jwk(f.key),'codi-steward-lease/1')['lease_id'],'counter':1}))['lease']
  finally:await p.close();await f.close()
 await check('invalid signatures, realms and limits do not replace current policy',invalid)
 async def narrow():
  f=await Fixture().start();a,b=Peer(f,f.a),Peer(f,f.b);await a.open();await b.open();await a.request('REGISTER_LEASE',{'scope':f.a,'invitations':True});await b.request('REGISTER_LEASE',{'scope':f.b,'invitations':True})
  old=f.server.registry;starts=len(f.server.starts)
  try:
   assert await f.server.reload_seed(f.sign(f.narrow()));await a.closed(1012);await b.closed(1012)
   assert old.snapshot()=={'owners':0,'leases':0,'routes':0,'closed':True};assert f.server.registry.scopes==frozenset([f.b]) and f.server.registry.MAX_SAMPLE==2 and f.server.signal_bytes==16384 and len(f.server.starts)==starts
   c=Peer(f,f.a)
   try:
    try:await c.open()
    except ConnectionClosed:pass
    else:raise AssertionError('Revoked scope authenticated')
   finally:await c.close()
   c=Peer(f,f.b);await c.open();await c.request('REGISTER_LEASE',{'scope':f.b,'invitations':True});await c.close()
   assert not await f.server.reload_seed(f.sign(f.narrow()))
   try:await f.server.reload_seed(f.sign(f.seed))
   except ValueError:pass
   else:raise AssertionError('Rollback accepted')
  finally:await a.close();await b.close();await f.close()
 await check('valid scope and capacity narrowing replaces RAM permissions without resetting global limits',narrow)
 async def queued():
  f=await Fixture().start();p=Peer(f,f.b);await p.open();ws,c=next(iter(f.server.clients.values()));lock=f.server.send_locks[ws];await lock.acquire()
  task=asyncio.create_task(f.server.send(ws,c.response(99,'TEST',{})));await asyncio.sleep(.01)
  try:
   await f.server.reload_seed(f.sign(f.narrow()));lock.release()
   try:await task
   except ValueError as error:assert 'Policy changed' in str(error)
   else:raise AssertionError('Old policy frame sent')
  finally:
   if lock.locked():lock.release()
   await p.close();await f.close()
 await check('queued control sends cannot cross a policy generation',queued)
 async def revoke():
  f=await Fixture().start();p=Peer(f,f.a);await p.open();old=f.server.descriptor();other=ec.generate_private_key(ec.SECP256R1());grant={**f.grant,'key_id':jose.thumbprint(jose.public_jwk(other)),'public_key':jose.public_jwk(other)};revoked={**f.seed,'revision':2,'stewards':[grant]}
  try:
   await f.server.reload_seed(f.sign(revoked));await p.closed(1008);assert not f.server.authorized and f.server.bundle()['descriptor']==old
   assert jose.verify(f.server.bundle()['seed'],jose.public_jwk(f.root),'codi-seed/1')['revision']==2
   try:f.server.descriptor()
   except ValueError:pass
   else:raise AssertionError('Revoked service signed metadata')
   try:StewardServer(**f.args)
   except ValueError:pass
   else:raise AssertionError('Restart rolled back revocation')
   await f.server.reload_seed(f.sign({**f.seed,'revision':3}));fresh=Peer(f,f.a);await fresh.open();await fresh.close()
  finally:await p.close();await f.close()
 await check('service-key revocation is durable and reauthorization needs a newer signed seed',revoke)
 async def fork():
  f=await Fixture().start();p=Peer(f,f.b);await p.open();new=f.narrow();await f.server.reload_seed(f.sign(new))
  try:
   try:await f.server.reload_seed(f.sign({**new,'exp':new['exp']+1}))
   except PublisherFrozen:pass
   else:raise AssertionError('Authenticated fork accepted')
   assert f.server.policy_frozen and not f.server.authorized
   try:StewardServer(**{**f.args,'seed':f.sign({**f.seed,'revision':3})})
   except PublisherFrozen:pass
   else:raise AssertionError('Fork freeze lost on restart')
  finally:await p.close();await f.close()
 await check('authenticated equal-revision root forks freeze runtime and durable publication',fork)
 async def publish_failure():
  f=await Fixture().start();p=Peer(f,f.a);await p.open()
  try:
   def broken(bundle):raise OSError('test public publication failure')
   try:await f.server.reload_seed(f.sign(f.narrow()),publish=broken)
   except OSError:pass
   else:raise AssertionError('Publication failure hidden')
   assert not f.server.authorized and f.server.registry.closed;await p.closed(1008)
  finally:await p.close();await f.close()
 await check('publication failure does not leave old permissions live',publish_failure)
 # Browser source refresh and active RTC are exercised below.
 await browser_case(check,browser)
 receipt={'status':'PASS','results':results,'browser':browser,'scope':'Loopback WS/native policy and one actual Chrome with two independent session actors; no WAN/TLS proof','sourceHashes':{n:hashlib.sha256((ROOT/n).read_bytes()).hexdigest() for n in ['steward/server.py','steward/provision.py','steward/publisher.py','network/support-client.mjs','scripts/root-policy-check.py']}}
 (ROOT/'.build/checks/root-policy-result.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt,indent=2))

async def browser_case(check,evidence):
 f=Fixture()
 class Quiet(PublicHandler):
  def log_message(self,*args):pass
  def do_GET(self):
   if self.path=='/policy.json':
    raw=json.dumps(f.server.bundle()).encode();self.send_response(200);self.send_header('Content-Type','application/json');self.send_header('Content-Length',str(len(raw)));self.end_headers();self.wfile.write(raw);return
   super().do_GET()
 http=ThreadingHTTPServer(('127.0.0.1',0),Quiet);origin=f'http://127.0.0.1:{http.server_port}';threading.Thread(target=http.serve_forever,daemon=True).start();await f.start([origin])
 base='http://127.0.0.1:19515';sid=None
 def req(path,data=None,method=None):
  request=urllib.request.Request(base+path,data=None if data is None else json.dumps(data).encode(),headers={'Content-Type':'application/json'},method=method)
  with urllib.request.urlopen(request,timeout=60) as response:return json.load(response)['value']
 async def js(code,async_=False,args=None):return await asyncio.to_thread(req,'/session/'+sid+('/execute/async' if async_ else '/execute/sync'),{'script':code,'args':args or []})
 async def scenario():
  code='''const cfg=arguments[0],done=arguments[arguments.length-1];(async()=>{const {beginSession}=await import('./network/identity.mjs'),{PeerPool}=await import('./network/peer-pool.mjs'),{Discovery}=await import('./network/discovery.mjs'),{sessionBudget}=await import('./network/resource-budget.mjs');const actors=[];for(const scope of [cfg.a,cfg.b]){const session=await beginSession({identity:{mode:'local-development'}},'anonymous'),received=[],pool=new PeerPool(session,{identity:{mode:'local-development'},rtc:{iceServers:[]}},{onMessage:(_,m)=>received.push(m.text)}),manager=new Discovery(session,{pin:{realm:cfg.realm,rootKey:cfg.root,endpoints:[cfg.endpoint],allowLoopback:true},seed:cfg.seed,descriptor:cfg.descriptor,scope,sourcePath:'/policy.json',identity:{mode:'local-development'}},pool);await manager.start();actors.push({session,pool,manager,received,budget:sessionBudget(session)});}window.policyActors=actors;const offer=await actors[0].pool.offer(),answer=await actors[1].pool.answer(offer.token);await actors[0].pool.accept(offer.entry.id,answer.token);return actors.map(a=>({sid:a.session.public.sid,key:a.session.fingerprint}));})().then(done).catch(e=>done({error:e.message}));'''
  identities=await js(code,True,[{'a':f.a,'b':f.b,'realm':f.realm,'root':jose.public_jwk(f.root),'endpoint':f.endpoint,'seed':f.server.seed,'descriptor':f.server.descriptor()}]);assert isinstance(identities,list),identities
  for _ in range(200):
   if await js('return policyActors.every(a=>a.pool.firstReady())'):break
   await asyncio.sleep(.05)
  assert await js('return policyActors.every(a=>a.pool.firstReady())')
  before=await js('return policyActors.map(a=>a.pool.firstReady().link.connectionId)')
  await f.server.reload_seed(f.sign(f.narrow()))
  for _ in range(250):
   states=await js('return policyActors.map(a=>a.manager.snapshot())')
   if states[0]['status']=='closed' and states[1]['status']=='ready' and states[1]['recoveries']>=1:break
   await asyncio.sleep(.05)
  assert states[0]['status']=='closed' and states[1]['status']=='ready' and states[1]['authorityRevision']==2,states
  assert len(f.server.registry.owners)==1 and next(iter(f.server.registry.owners.values())).admission.scopes==frozenset([f.b])
  assert await js('return policyActors.map(a=>a.pool.firstReady().link.connectionId)')==before
  assert await js('return policyActors.map(a=>({sid:a.session.public.sid,key:a.session.fingerprint}))')==identities
  result=await js('const done=arguments[0];policyActors[0].pool.firstReady().link.send("RTC survives root scope reload").then(()=>done(true)).catch(e=>done(e.message));',True);assert result is True
  for _ in range(100):
   if await js('return policyActors[1].received.includes("RTC survives root scope reload")'):break
   await asyncio.sleep(.05)
  assert await js('return policyActors[1].received.includes("RTC survives root scope reload")')
  result=await js('const done=arguments[0];(async()=>{for(const a of policyActors){a.manager.close();a.pool.close();}for(let i=0;i<100;i++){const b=policyActors.map(a=>a.budget.snapshot());if(b.every(x=>!x.metadataBytes&&!x.connections&&!x.crypto&&!x.queuedBytes))return done(b);await new Promise(r=>setTimeout(r,50));}done(null);})();',True);assert result and all(x['hints']==0 for x in result)
  evidence.update({'revokedScopeClosed':True,'remainingScopeReauthenticated':True,'sourceVerifiedRevision':2,'sameSessionKeys':True,'sameRtcConnections':True,'rtcDelivered':True,'zeroBudgetDisposal':True})
 try:
  created=await asyncio.to_thread(req,'/session',{'capabilities':{'alwaysMatch':{'browserName':'chrome','goog:chromeOptions':{'binary':'/snap/chromium/current/usr/lib/chromium-browser/chrome','args':['--headless=new','--no-sandbox','--disable-dev-shm-usage']}}}});sid=created['sessionId'];await asyncio.to_thread(req,'/session/'+sid+'/url',{'url':origin+'/'})
  await check('actual Chrome learns narrowed root before reauth; revoked scope stops while RTC and remaining scope survive',scenario)
 finally:
  if sid:await asyncio.to_thread(req,'/session/'+sid,None,'DELETE')
  await f.close();await asyncio.to_thread(http.shutdown);http.server_close()

try:asyncio.run(main())
except Exception as error:
 (ROOT/'.build/checks/root-policy-result.json').write_text(json.dumps({'status':'FAIL','error':str(error)},indent=2)+'\n')
 raise
