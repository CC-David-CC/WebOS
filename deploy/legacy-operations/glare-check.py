#!/usr/bin/env python3
"""Real two-browser PeerPool crossed-offer convergence, without UI signaling."""
import argparse,concurrent.futures,hashlib,json,time,urllib.request
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--url',default='http://127.0.0.1:8114/');p.add_argument('--reverse-answers',action='store_true');p.add_argument('--require-trust',choices=['local','test-server']);a=p.parse_args()
BASE='http://127.0.0.1:19515';sessions=[];result={'status':'FAIL','url':a.url}
def req(path,data=None,method=None):
 r=urllib.request.Request(BASE+path,data=None if data is None else json.dumps(data).encode(),headers={'Content-Type':'application/json'},method=method)
 with urllib.request.urlopen(r,timeout=90) as response:return json.load(response)['value']
def js(s,code):return req('/session/'+s+'/execute/sync',{'script':code,'args':[]})
def asyncjs(s,code):
 r=req('/session/'+s+'/execute/async',{'script':'const done=arguments[0];(async()=>{'+code+'})().then(value=>done({value})).catch(e=>done({error:e.message}));','args':[]})
 if 'error' in r:raise AssertionError(r['error'])
 return r['value']
def parallel(fn):
 with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:return list(executor.map(fn,sessions))
try:
 for _ in range(2):
  s=req('/session',{'capabilities':{'alwaysMatch':{'browserName':'chrome','goog:chromeOptions':{'binary':'/snap/chromium/current/usr/lib/chromium-browser/chrome','args':['--headless=new','--no-sandbox','--disable-dev-shm-usage']}}}})['sessionId'];sessions.append(s);req('/session/'+s+'/url',{'url':a.url})
  asyncjs(s,"""const {beginSession}=await import('./network/identity.mjs'),{PeerPool}=await import('./network/peer-pool.mjs');const config=await (await fetch('./config.json',{cache:'no-store'})).json();const owner=await beginSession(config,'anonymous');window.glare={owner,config,messages:[]};glare.pool=new PeerPool(owner,config,{onMessage:(_,m)=>glare.messages.push(m.text)});return owner.public.sid;""")
 trust=[js(s,'return glare.owner.trust.level') for s in sessions]
 if a.require_trust:assert trust==[a.require_trust,a.require_trust],trust
 offers=parallel(lambda s:asyncjs(s,'glare.offer=await glare.pool.offer();return glare.offer.token;'))
 answers={}
 for index in ([1,0] if a.reverse_answers else [0,1]):
  s=sessions[index];answers[s]=asyncjs(s,'return (await glare.pool.answer('+json.dumps(offers[index^1])+')).token;')
 accepted=parallel(lambda s:asyncjs(s,'try{await glare.pool.accept(glare.offer.entry.id,'+json.dumps(answers[sessions[sessions.index(s)^1]])+');return true;}catch(e){return e.message;}'))
 end=time.monotonic()+8
 while time.monotonic()<end:
  counts=[js(s,'return glare.pool.list().filter(e=>e.state==="ready").length') for s in sessions]
  if counts==[1,1]:break
  time.sleep(.1)
 assert counts==[1,1],{'readyCounts':counts,'acceptResults':accepted,'entries':[js(s,'return glare.pool.list()') for s in sessions]}
 ids=[js(s,'return glare.pool.firstReady().link.connectionId') for s in sessions];assert ids[0]==ids[1]
 remote_trust=[js(s,'return glare.pool.firstReady().link.remote.trust.level') for s in sessions]
 assert remote_trust==trust,{'local':trust,'remote':remote_trust}
 assert all(js(s,'const e=glare.pool.firstReady();return e.role===(glare.owner.public.sid<e.link.remoteIdentity.sid?"offer":"answer")') for s in sessions)
 for index,s in enumerate(sessions):asyncjs(s,'await glare.pool.firstReady().link.send('+json.dumps('crossed-offer-message-'+str(index))+');return true;')
 for index,s in enumerate(sessions):
  end=time.monotonic()+5
  while time.monotonic()<end:
   messages=js(s,'return glare.messages')
   if 'crossed-offer-message-'+str(index^1) in messages:break
   time.sleep(.1)
  assert messages==['crossed-offer-message-'+str(index^1)],messages
 # Attempting another connection must preserve the already proved path.
 duplicate=asyncjs(sessions[0],'return (await glare.pool.offer()).token;')
 rejected=asyncjs(sessions[1],'try{await glare.pool.answer('+json.dumps(duplicate)+');return false;}catch{return true;}')
 assert rejected
 assert [js(s,'return glare.pool.firstReady().link.connectionId') for s in sessions]==ids
 witnesses=[asyncjs(s,'return glare.pool.firstReady().link.stats();') for s in sessions]
 assert all(w['connectionState']=='connected' for w in witnesses),witnesses
 result={'status':'PASS','url':a.url,'scope':'Two real Chrome contexts; actual PeerPool API crossed offers and RTC delivery, not manual UI glare or WAN','identityTrust':trust,'remoteIdentityTrust':remote_trust,'answerOrder':'reverse' if a.reverse_answers else 'forward','acceptResults':accepted,'matchingConnectionId':ids[0],'bidirectionalDelivery':True,'establishedDuplicatePreserved':True,'witnesses':witnesses}
except Exception as e:result['error']=str(e);raise
finally:
 clean=[]
 for s in sessions:
  try:
   clean.append(asyncjs(s,"glare?.pool.close();await new Promise(r=>setTimeout(r,0));const {sessionBudget}=await import('./network/resource-budget.mjs');return sessionBudget(glare.owner).snapshot();"))
  finally:req('/session/'+s,method='DELETE')
 result['disposedBudgets']=clean
 result['allReservationsReleased']=all(all(value==0 for key,value in budget.items() if key!='closed') for budget in clean)
 if not result['allReservationsReleased']:result['status']='FAIL'
 result['sha256']={name:hashlib.sha256(Path(name).read_bytes()).hexdigest() for name in ('network/peer-pool.mjs','network/peer.mjs','network/identity.mjs','scripts/glare-check.py')}
 Path('.build/checks/glare-result.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))

assert result['status']=='PASS',result
