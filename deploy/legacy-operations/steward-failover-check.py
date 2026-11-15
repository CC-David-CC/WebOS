#!/usr/bin/env python3
"""Independent native steward processes; three isolated Chrome actors; actual failover."""
import hashlib,json,os,secrets,socket,subprocess,sys,threading,time,urllib.request
from pathlib import Path
from http.server import ThreadingHTTPServer
sys.path.insert(0,str(Path(__file__).resolve().parent.parent))
from serve import PublicHandler
from steward.publisher import PublisherState
from steward.protocol import jose
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ec
ROOT=Path(__file__).resolve().parent.parent;BASE='http://127.0.0.1:19515';sessions=[];processes=[];results=[];receipt={};mode='valid';outputs=[]
workspace=ROOT/'.build/checks/steward-failover'/secrets.token_hex(12);workspace.mkdir(parents=True,mode=0o700);public=workspace/'public';public.mkdir()
def bundle():
 descriptors=[json.loads(path.read_text())['descriptor'] for path in outputs]
 b={'version':'codi-bootstrap-bundle/2','seed':seed,'descriptors':descriptors}
 if mode=='duplicate':b['descriptors']=[descriptors[0],descriptors[0]]
 elif mode=='same-key':
  payload=jose.inspect(descriptors[0],'codi-steward/1')[1];payload['revision']+=1;b['descriptors']=[descriptors[0],jose.sign(payload,keys[0],'codi-steward/1')]
 elif mode=='extra':b['admin']=True
 elif mode=='unknown':b['version']='codi-bootstrap-bundle/3'
 elif mode=='too-many':b['descriptors']=descriptors*5
 elif mode=='unpin':b['seed']=unpin_seed
 elif mode=='retire-primary':b['seed']=retired_seed;b['descriptors']=[descriptors[1]]
 elif mode=='root-only-revoke':b['seed']=revoked_seed;b['descriptors']=[]
 return b
class Handler(PublicHandler):
 def do_GET(self):
  if self.path in ('/fixture','/stewards.json'):
   body=b'<!doctype html><title>Disposable steward failover fixture</title>' if self.path=='/fixture' else json.dumps(bundle()).encode();self.send_response(200);self.send_header('Content-Type','text/html' if self.path=='/fixture' else 'application/json');self.send_header('Content-Length',str(len(body)));self.end_headers();self.wfile.write(body)
  else:super().do_GET()
 def log_message(self,*args):pass
server=ThreadingHTTPServer(('127.0.0.1',0),Handler);thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start();origin=f'http://127.0.0.1:{server.server_port}'
def req(path,data=None,method=None):
 r=urllib.request.Request(BASE+path,data=None if data is None else json.dumps(data).encode(),headers={'Content-Type':'application/json'},method=method)
 with urllib.request.urlopen(r,timeout=90) as response:return json.load(response)['value']
def js(s,code):return req('/session/'+s+'/execute/sync',{'script':code,'args':[]})
def run(s,code):
 r=req('/session/'+s+'/execute/async',{'script':'const done=arguments[0];(async()=>{'+code+'})().then(value=>done({value})).catch(e=>done({error:e.message}));','args':[]})
 if 'error' in r:raise AssertionError(r['error'])
 return r.get('value')
def wait(s,code,timeout=25):
 end=time.monotonic()+timeout
 while time.monotonic()<end:
  if js(s,code):return
  time.sleep(.1)
 raise AssertionError('Timeout: '+code+'; '+str(js(s,'return manager.snapshot()')))
def passed(name):results.append({'name':name,'status':'PASS'})
root=ec.generate_private_key(ec.SECP256R1());keys=[ec.generate_private_key(ec.SECP256R1()) for _ in range(2)];realm=secrets.token_urlsafe(32);scope=secrets.token_urlsafe(32);now=int(time.time());ports=[]
for _ in keys:
 with socket.socket() as selected:selected.bind(('127.0.0.1',0));ports.append(selected.getsockname()[1])
endpoints=[f'ws://127.0.0.1:{port}/rendezvous' for port in ports]
grants=[{'key_id':jose.thumbprint(jose.public_jwk(key)),'public_key':jose.public_jwk(key),'endpoints':[endpoint],'scopes':[scope],'limits':{'lease_seconds':30,'sample_size':4,'signal_bytes':32768},'exp':now+300,'failure_domain':'one-loopback-host'} for key,endpoint in zip(keys,endpoints)]
seed=jose.sign({'version':'codi-seed/1','realm':realm,'revision':1,'iat':now,'exp':now+300,'stewards':grants},root,'codi-seed/1')
retired_seed=jose.sign({'version':'codi-seed/1','realm':realm,'revision':2,'iat':now,'exp':now+300,'stewards':[grants[1]]},root,'codi-seed/1')
unpin_seed=jose.sign({'version':'codi-seed/1','realm':realm,'revision':2,'iat':now,'exp':now+300,'stewards':[grants[0],{**grants[1],'endpoints':['ws://127.0.0.1:9/rendezvous']}]},root,'codi-seed/1')
revoked_seed=jose.sign({'version':'codi-seed/1','realm':realm,'revision':3,'iat':now,'exp':now+300,'stewards':[{**grants[1],'scopes':[secrets.token_urlsafe(32)]}]},root,'codi-seed/1')
def actor(prefer_second=False,stale_release=False):
 s=req('/session',{'capabilities':{'alwaysMatch':{'browserName':'chrome','goog:chromeOptions':{'binary':'/snap/chromium/current/usr/lib/chromium-browser/chrome','args':['--headless=new','--no-sandbox','--disable-dev-shm-usage']}}}})['sessionId'];sessions.append(s);req('/session/'+s+'/url',{'url':origin+'/fixture'})
 current=bundle() if not stale_release else {'seed':seed,'descriptors':[json.loads(p.read_text())['descriptor'] for p in outputs]}
 config={'identity':{'mode':'local-development'},'rtc':{'iceServers':[]},'discovery':{'pin':{'realm':realm,'rootKey':jose.public_jwk(root),'endpoints':endpoints,'allowLoopback':True},'seed':current['seed'],'descriptors':current['descriptors'][::-1] if prefer_second else current['descriptors'],'scope':scope,'sourcePath':'/stewards.json'}}
 run(s,"window.config="+json.dumps(config)+";window.id=await import('./network/identity.mjs');window.c=await import('./network/crypto.mjs');window.session=await id.beginSession(config,'anonymous');window.messages=[];const {PeerPool}=await import('./network/peer-pool.mjs');const {Discovery}=await import('./network/discovery.mjs');window.pool=new PeerPool(session,config,{onMessage:(e,m)=>messages.push(m)});window.manager=new Discovery(session,{...config.discovery,identity:config.identity},pool);try{await manager.start();}catch(e){if(manager.status!=='recovering')throw e;}")
 return s
try:
 for i,(key,port) in enumerate(zip(keys,ports)):
  private=workspace/f'private-{i}';private.mkdir(mode=0o700);state=private/'publisher';PublisherState.initialize(state)
  key_path=private/'service.pem';provision_path=private/'provision.json';output=public/f'{i}.json';outputs.append(output)
  provision={'seed':seed,'root_key':jose.public_jwk(root),'realm':realm,'endpoint':endpoints[i],'identity_policy':{'mode':'local-development'},'origins':[origin]}
  for path,raw in [(key_path,key.private_bytes(serialization.Encoding.PEM,serialization.PrivateFormat.PKCS8,serialization.NoEncryption())),(provision_path,json.dumps(provision).encode())]:
   fd=os.open(path,os.O_CREAT|os.O_EXCL|os.O_WRONLY,0o600)
   with os.fdopen(fd,'wb') as f:f.write(raw)
  process=subprocess.Popen([sys.executable,str(ROOT/'scripts/serve-steward.py'),'serve','--state',str(state),'--key',str(key_path),'--provision',str(provision_path),'--bundle-out',str(output),'--port',str(port)],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,cwd=ROOT);processes.append(process)
  deadline=time.monotonic()+10
  while not output.exists():
   if process.poll() is not None:raise AssertionError('Provisioned steward exited')
   if time.monotonic()>deadline:raise AssertionError('Provisioned steward did not publish')
   time.sleep(.05)
 left,right=actor(),actor()
 for s in (left,right):assert js(s,'return manager.snapshot().stewardKeyId')==grants[0]['key_id']
 passed('two browsers verify two delegated services but maintain one active control connection each')
 run(left,'await manager.discover();');sample=js(left,'return [...manager.samples.keys()][0]');run(left,'await manager.invite('+json.dumps(sample)+');')
 wait(right,'return manager.incoming.size===1');run(right,'await manager.accept([...manager.incoming.keys()][0]);')
 for s in (left,right):wait(s,'return pool.firstReady()!==null')
 link_ids=[js(s,'return pool.firstReady().link.connectionId') for s in (left,right)];assert link_ids[0]==link_ids[1]
 old_leases=[js(s,'return manager.lease.lease_id') for s in (left,right)];old_nonces=[js(s,'return manager.client.nonce') for s in (left,right)]
 passed('native service A forwards actual signed RTC establishment with explicit peer consent')
 # Selection respects verified domain metadata without making an HA claim.
 selection=run(left,"""
 const client=manager.client,actual=client.directory.snapshot.bind(client.directory),contact=client.contact,failures=client.failures,counter=client.handoffs;
 const fake=[{key_id:'same',failure_domain:'old',limits:{lease_seconds:30}},{key_id:'diverse',failure_domain:'other',limits:{lease_seconds:30}},{key_id:'too-short',failure_domain:'other',limits:{lease_seconds:1}}];
 try{client.directory.snapshot=()=>({contacts:fake});client.contact={key_id:'old-key',failure_domain:'old'};client.failures=new Map();if(client.selectContact().key_id!=='diverse')throw Error('Failure-domain preference lost');client.failures=new Map([['diverse',1]]);if(client.selectContact().key_id!=='same')throw Error('Failed endpoint outranked untried endpoint');return true;}
 finally{client.directory.snapshot=actual;client.contact=contact;client.failures=failures;client.handoffs=counter;}
 """);assert selection
 passed('selection prefers a different declared domain among unfailed compatible candidates')
 for invalid in ['duplicate','same-key','extra','unknown','too-many','unpin']:
  mode=invalid
  rejected=run(left,"let rejected=false;try{await manager.client.refreshBootstrap();}catch{rejected=true;}return rejected&&manager.status==='ready'&&manager.client.status==='ready';")
  assert rejected;passed('bounded source rejects '+invalid+' without replacing valid live authority')
 mode='valid'
 security=actor();run(security,"manager.client.ws.send('malformed-control');")
 wait(security,'return manager.status==="closed"')
 assert js(security,'return manager.retryCount===0&&manager.client.handoffs===0')
 run(security,'manager.close();pool.close();');req('/session/'+security,method='DELETE');sessions.remove(security)
 passed('native protocol rejection is fatal despite a healthy alternate; no security-error retry')
 mode='retire-primary'
 processes[0].kill();processes[0].wait(timeout=5)
 for s in (left,right):wait(s,'return manager.status==="ready"&&manager.client.contact.key_id==='+json.dumps(grants[1]['key_id'])+'&&manager.recoveries===1')
 for i,s in enumerate((left,right)):
  assert js(s,'return pool.firstReady().link.connectionId')==link_ids[i]
  assert js(s,'return manager.lease.lease_id')!=old_leases[i]
  assert js(s,'return manager.client.nonce')!=old_nonces[i]
  assert js(s,'return manager.snapshot().stewardHandoffs===1&&manager.client.directory.snapshot().contacts.length===1&&manager.client.directory.snapshot().revision===2&&manager.samples.size===0&&manager.incoming.size===0')
  budget=js(s,'return manager.budget.snapshot()');assert budget['support']==1 and budget['connections']==2
 run(left,"await pool.firstReady().link.send('RTC after native process A SIGKILL');")
 wait(right,'return messages.some(m=>m.text==="RTC after native process A SIGKILL")')
 passed('SIGKILL of independent native A hands both browsers to B with fresh nonce/lease and preserved RTC')
 for s in (left,right):
  assert run(s,'let rejected=false;try{await manager.client.directory.acceptSeed('+json.dumps(seed)+');}catch{rejected=true;}return rejected&&manager.client.directory.snapshot().revision===2&&manager.status==="ready";')
 passed('recovery learns signed retirement of A and retains root revision floors while selecting B')
 startup=actor(stale_release=True)
 wait(startup,'return manager.status==="ready"&&manager.client.contact.key_id==='+json.dumps(grants[1]['key_id'])+'&&manager.recoveries===1')
 assert js(startup,'return manager.client.directory.snapshot().revision===2&&manager.budget.snapshot().support===1&&pool.list().length===0')
 run(startup,'manager.close();pool.close();');req('/session/'+startup,method='DELETE');sessions.remove(startup)
 passed('cached release startup with unavailable primary recovers through fresh pinned metadata')
 # A third browser starts on B and is discovered through the replacement service.
 third=actor(True);third_sid=js(third,'return session.public.sid')
 run(left,'await manager.discover();');new_sample=js(left,'return [...manager.samples].find(([,s])=>s.lease.session_id==='+json.dumps(third_sid)+')?.[0]');assert new_sample
 run(left,'await manager.invite('+json.dumps(new_sample)+');');wait(third,'return manager.incoming.size===1');run(third,'await manager.accept([...manager.incoming.keys()][0]);')
 wait(third,'return pool.firstReady()!==null');wait(left,'return pool.list().filter(e=>e.state==="ready").length===2')
 left_sid=js(left,'return session.public.sid')
 run(third,"await pool.firstReady().link.send('New RTC established through B');");wait(left,'return messages.some(m=>m.text==="New RTC established through B")')
 assert js(left,'return pool.list().filter(e=>e.state==="ready").some(e=>e.connectionId==='+json.dumps(link_ids[0])+')')
 passed('replacement native B establishes a new consented RTC link without replacing the original link')
 # A root-only bundle must still carry revocation before leaf processing.
 mode='root-only-revoke'
 assert run(right,"let rejected=false;try{await manager.client.refreshBootstrap();}catch{rejected=true;}return rejected&&manager.status==='closed';")
 run(left,"await pool.get(pool.list().find(e=>e.connectionId==="+json.dumps(link_ids[0])+").id).link.send('RTC after root-only discovery revocation');")
 wait(right,'return messages.some(m=>m.text==="RTC after root-only discovery revocation")')
 passed('root-only source applies learned scope revocation without disrupting existing RTC')
 # Explicit stop prevents any handoff/re-registration.
 run(third,"manager.close('explicit stop');");processes[1].terminate();processes[1].wait(timeout=5);time.sleep(1)
 assert js(third,'return manager.status==="closed"&&manager.retryCount===0')
 passed('explicit Stop remains final when the replacement service disappears')
 for s in sessions:
  run(s,"manager.close();pool.close();const {sessionBudget}=await import('./network/resource-budget.mjs');for(let i=0;i<150;i++){const b=sessionBudget(session).snapshot();if(!b.connections&&!b.support&&!b.metadataBytes&&!b.crypto&&!b.queuedBytes&&!b.hints)return;await new Promise(r=>setTimeout(r,25));}throw Error('Failover disposal leaked');")
 passed('all three actors release connection, hint, metadata, crypto and wire budgets')
 files=['network/bootstrap-source.mjs','network/bootstrap.mjs','network/support-client.mjs','network/discovery.mjs','scripts/steward-failover-check.py']
 receipt={'status':'PASS','results':results,'scope':'Two independently provisioned native processes and three isolated Chrome processes on one host; synthetic selection metadata only, no host-domain/WAN/replication proof','sourceHashes':{f:hashlib.sha256((ROOT/f).read_bytes()).hexdigest() for f in files}}
except Exception as error:receipt={'status':'FAIL','results':results,'error':str(error)};raise
finally:
 for s in sessions:
  try:req('/session/'+s,method='DELETE')
  except Exception:pass
 for process in processes:
  if process.poll() is None:process.terminate();process.wait(timeout=5)
 server.shutdown();server.server_close();thread.join(timeout=3)
 (ROOT/'.build/checks/steward-failover-result.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt,indent=2))
