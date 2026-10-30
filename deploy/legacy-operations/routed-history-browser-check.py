#!/usr/bin/env python3
"""Actual RTC routed gap recovery; owned three-Chrome/Linux/issuer fixture only."""
import asyncio,hashlib,importlib.util,json,time
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
SOURCES=['network/routed-history.mjs','network/routed-rooms.mjs','network/routed-room-grant.mjs','network/peer.mjs','network/peer-pool.mjs','network/resource-budget.mjs','network/replay.mjs','network/subscriptions.mjs','network/traffic-scheduler.mjs','networking.js','scripts/routed-history-browser-check.py','scripts/routed-group-browser-check.py']
source_pins={n:hashlib.sha256((ROOT/n).read_bytes()).hexdigest() for n in SOURCES}
spec=importlib.util.spec_from_file_location('history_fixture',ROOT/'scripts/routed-group-browser-check.py');fixture=importlib.util.module_from_spec(spec);spec.loader.exec_module(fixture)
call,wait=fixture.call,fixture.wait
class HistoryFixture(fixture.Fixture):
 async def proxy(self,request):
  response=await super().proxy(request)
  if request.method=='POST' and b'ROUTED_HISTORY' in await request.read():self.http_chat=True
  return response

def browser(f):
 sessions=[];checks=[]
 def js(s,code,args=[]):return call('/session/'+s+'/execute/sync',{'script':code,'args':args})
 def task(s,code,args=[]):
  r=call('/session/'+s+'/execute/async',{'script':'const params=arguments,done=arguments[arguments.length-1];(async()=>{'+code+'})().then(value=>done({ok:true,value}),error=>done({ok:false,error:error.stack}));','args':args});assert r['ok'],r;return r.get('value')
 def check(name,value):assert value,name;checks.append(name)
 def selected(s):return js(s,'return desktopNetwork.appContext().routedRooms.snapshot(historyView).selected')
 try:
  for _ in range(3):
   s=call('/session',{'capabilities':{'alwaysMatch':{'browserName':'chrome','goog:chromeOptions':{'binary':'/snap/chromium/current/usr/lib/chromium-browser/chrome','args':['--headless=new','--no-sandbox','--disable-dev-shm-usage']},'goog:loggingPrefs':{'browser':'ALL'}}}})['sessionId'];sessions.append(s)
   call('/session/'+s+'/timeouts',{'script':120000});call('/session/'+s+'/goog/cdp/execute',{'cmd':'Page.addScriptToEvaluateOnNewDocument','params':{'source':'window.BroadcastChannel=class{constructor(){throw Error("Tab bus forbidden")}}'}});call('/session/'+s+'/url',{'url':f.origin+f.base+'/'})
   wait(lambda:js(s,'return window.desktopLab?.guestState==="ready"&&!!desktopNetwork.appContext().routedRooms'),150)
   js(s,'window.historyView={};window.historyRouter=desktopNetwork.appContext().routedRooms;window.historyPool=desktopNetwork.appContext().pool;window.historyVM=v86Instance;window.historyEvents=[];window.historyOutcomes=[];const receive=historyRouter.receive.bind(historyRouter);historyRouter.receive=async(...a)=>{const result=await receive(...a);historyOutcomes.push(result);return result;};')
  centre,left,right=sessions
  for leaf in [left,right]:
   offer=task(centre,'const r=await historyPool.offer();return {id:r.entry.id,token:r.token};');answer=task(leaf,'return (await historyPool.answer(params[0])).token;',[offer['token']]);task(centre,'await historyPool.accept(params[0],params[1]);return true;',[offer['id'],answer]);wait(lambda:js(leaf,'return historyPool.firstReady()?.link.routedApplicationReady'),30)
  group=task(centre,'return await historyRouter.create(historyPool.list().map(e=>e.id),"History repair",historyView);')
  for leaf in [left,right]:
   wait(lambda:js(leaf,'return historyRouter.snapshot(historyView).groups.length===1'),20);task(leaf,'await historyRouter.accept(params[0],historyView);return true;',[group])
  for s in sessions:wait(lambda:selected(s)['state']=='active',20)
  right_sid=js(right,'return currentSession.public.sid');js(centre,'window.historyDropSid=arguments[0];for(const e of historyPool.list()){const link=historyPool.get(e.id).link,send=link.sendRoutedApplication.bind(link);link.historyOriginal=send;link.sendRoutedApplication=(type,body,expiry)=>{historyEvents.push({type,body:structuredClone(body)});if(type==="event"&&e.peerId===historyDropSid&&!window.historyDropped&&JSON.parse(atob(body.event.split(".")[1].replaceAll("-","+").replaceAll("_","/"))).sequence===2){window.historyDropped=true;return Promise.reject(Error("Injected forwarding backpressure"));}return send(type,body,expiry);};}',[right_sid])
  for text in ['ROUTED_HISTORY_one','ROUTED_HISTORY_two','ROUTED_HISTORY_three']:task(centre,'return await historyRouter.send(historyView,params[0]);',[text])
  wait(lambda:any(m['text']=='ROUTED_HISTORY_three' for m in selected(right)['history']),20)
  wait(lambda:any(m['text']=='ROUTED_HISTORY_two' and m.get('historical') is True for m in selected(right)['history']),8)
  check('missing original arrives once as historical data over actual RTC',sum(m['text']=='ROUTED_HISTORY_two' for m in selected(right)['history'])==1)
  check('recovered message fills the gap without a new live delivery',selected(right)['missing']==0 and selected(right)['received']==2 and selected(right)['recovered']==1)
  original_two=js(centre,'return historyEvents.find(p=>p.type==="event"&&JSON.parse(atob(p.body.event.split(".")[1].replaceAll("-","+").replaceAll("_","/"))).sequence===2).body;')
  root_right=js(centre,'return historyPool.list().find(e=>e.peerId===historyDropSid).id')
  before=js(right,'return historyOutcomes.length');task(centre,'await historyPool.get(params[0]).link.historyOriginal("event",params[1]);return true;',[root_right,original_two]);wait(lambda:js(right,'return historyOutcomes.length>arguments[0]',[before]),10)
  check('late live replay of recovered history is rejected',not js(right,'return historyOutcomes.at(-1).accepted') and sum(m['text']=='ROUTED_HISTORY_two' for m in selected(right)['history'])==1)
  other=task(centre,'window.otherHistoryView={};return await historyRouter.create(historyPool.list().map(e=>e.id),"Other history scope",otherHistoryView);')
  for leaf in [left,right]:
   wait(lambda:js(leaf,'return historyRouter.snapshot(historyView).groups.some(g=>g.id===arguments[0])',[other]),10);task(leaf,'window.otherHistoryView={};await historyRouter.accept(params[0],otherHistoryView);return true;',[other])
  for s in sessions:wait(lambda:js(s,'return historyRouter.snapshot(otherHistoryView).selected?.state==="active"'),10)
  js(centre,'window.otherHistoryGroup=arguments[0];window.otherHistoryHash=historyEvents.filter(p=>p.type==="control"&&p.body.operation==="invite").map(p=>JSON.parse(atob(p.body.invitation.grant.split(".")[1].replaceAll("-","+").replaceAll("_","/")))).find(p=>p.node_id===otherHistoryGroup).descriptor_hash;',[other])
  # Hold one original leaf event out of a downstream fanout. A malicious
  # controller first supplies wrongly signed and wrong-request history replies.
  leaf_sid=js(left,'return currentSession.public.sid')
  js(centre,"window.historyLeafSid=arguments[0];const link=historyPool.get(arguments[1]).link,send=link.historyOriginal;window.repairReplies=[];link.sendRoutedApplication=async(type,body,expiry)=>{\n   if(type==='event'){const p=JSON.parse(atob(body.event.split('.')[1].replaceAll('-','+').replaceAll('_','/')));if(p.author_session_id===historyLeafSid&&p.sequence===2)throw Error('Injected downstream leaf-origin loss');}\n   if(type==='history'){repairReplies.push(structuredClone(body));const c=await import('./network/crypto.mjs'),o=await import('./network/origin-event.mjs'),p=c.inspectJws(body.event,o.ORIGIN_TYPE,16384).payload;\n    if(p.author_session_id===historyLeafSid&&p.sequence===2&&!window.forgedHistoryOnce){window.forgedHistoryOnce=true;const forged=await c.signJws({...p,payload:{text:'FORGED_HISTORY'}},currentSession.privateKey,o.ORIGIN_TYPE);\n     await send('history',{...body,event:forged},expiry);await send('history',{...body,node_id:otherHistoryGroup,descriptor_hash:otherHistoryHash},expiry);await send('history',{...body,request_id:(await import('./network/mesh-contract.mjs')).newNodeId()},expiry);await send('history',{...body,event:expiredHistoryToken},Math.floor(Date.now()/1000)+30);\n    }\n   }return send(type,body,expiry);\n  };",[leaf_sid,root_right])
  js(left,'const link=historyPool.firstReady().link,send=link.sendRoutedApplication.bind(link);link.sendRoutedApplication=(type,body,expiry)=>{if(type==="event")window.savedLeafOrigin=JSON.parse(atob(body.event.split(".")[1].replaceAll("-","+").replaceAll("_","/")));return send(type,body,expiry);};')
  for text in ['ROUTED_HISTORY_leaf_one','ROUTED_HISTORY_leaf_two']:task(left,'return await historyRouter.send(historyView,params[0]);',[text])
  wait(lambda:any(m['text']=='ROUTED_HISTORY_leaf_two' for m in selected(centre)['history']),10)
  expired=task(left,'const c=await import("./network/crypto.mjs"),o=await import("./network/origin-event.mjs");const p=window.savedLeafOrigin;return await c.signJws({...p,issued_at:Math.floor(Date.now()/1000)-31,expires_at:Math.floor(Date.now()/1000)-1},currentSession.privateKey,o.ORIGIN_TYPE);')
  js(centre,'window.expiredHistoryToken=arguments[0];',[expired])
  before_rejected=selected(right)['rejected'];task(left,'return await historyRouter.send(historyView,"ROUTED_HISTORY_leaf_three");')
  wait(lambda:any(m['text']=='ROUTED_HISTORY_leaf_two' and m.get('historical') for m in selected(right)['history']),8)
  check('forged wrong-request and expired history cannot poison the valid fill',selected(right)['rejected']>=before_rejected+3 and all(m['text']!='FORGED_HISTORY' for m in selected(right)['history']))
  check('history transplanted to another admitted group cannot consume its floor',js(right,'const r=historyRouter.snapshot(otherHistoryView).selected;return r.rejected===1&&r.history.length===0;'))
  check('historical delivery preserves the original leaf author',next(m for m in selected(right)['history'] if m['text']=='ROUTED_HISTORY_leaf_two')['author']==js(left,'return currentSession.public.name'))
  # Lose an origin before controller dispatch. The controller fetches from
  # its actual author; a downstream leaf can then fetch the same signed origin.
  js(centre,'const receive=historyRouter.receive.bind(historyRouter);historyRouter.receive=async(entry,packet)=>{if(packet.type==="event"){const p=JSON.parse(atob(packet.body.event.split(".")[1].replaceAll("-","+").replaceAll("_","/")));if(p.author_session_id===historyLeafSid&&p.sequence===4&&!window.upstreamLost){window.upstreamLost=true;return {accepted:false,error:"Injected controller dispatch loss"};}}return receive(entry,packet);};historyPool.get(arguments[0]).link.sendRoutedApplication=historyPool.get(arguments[0]).link.historyOriginal;',[root_right])
  for text in ['ROUTED_HISTORY_upstream_four','ROUTED_HISTORY_upstream_five']:task(left,'return await historyRouter.send(historyView,params[0]);',[text])
  for s in [centre,right]:wait(lambda:any(m['text']=='ROUTED_HISTORY_upstream_four' and m.get('historical') for m in selected(s)['history']),8)
  check('controller and downstream member recover the original upstream author',all(sum(m['text']=='ROUTED_HISTORY_upstream_four' for m in selected(s)['history'])==1 for s in [centre,right]))
  # Two independent gaps in one stream arrive while its first reply is held.
  # Finishing that reply must schedule the later gap, with no unbounded queue.
  js(centre,"window.historyHolding=true;window.historyHeld=[];const link=historyPool.get(arguments[0]).link,send=link.historyOriginal;link.sendRoutedApplication=(type,body,expiry)=>{\n    if(type==='event'){const p=JSON.parse(atob(body.event.split('.')[1].replaceAll('-','+').replaceAll('_','/')));if(p.author_session_id===currentSession.public.sid&&[4,6].includes(p.sequence))throw Error('Injected successive gaps');}\n    if(historyHolding&&type==='history'){historyHeld.push({type,body,expiry});window.historyHeldID=body.request_id;return Promise.resolve();}\n    if(historyHolding&&type==='control'&&body.operation==='history-end'&&body.request_id===historyHeldID){historyHeld.push({type,body,expiry});return Promise.resolve();}\n    return send(type,body,expiry);\n  };",[root_right])
  for text in ['ROUTED_HISTORY_deferred_four','ROUTED_HISTORY_deferred_five','ROUTED_HISTORY_deferred_six','ROUTED_HISTORY_deferred_seven']:task(centre,'return await historyRouter.send(historyView,params[0]);',[text])
  wait(lambda:js(right,'return historyRouter.snapshot(historyView).selected.missing===2&&historyRouter.historyStats().pending===1'),5)
  wait(lambda:js(centre,'return historyHeld.length>=2'),5)
  task(centre,'historyHolding=false;const send=historyPool.get(params[0]).link.historyOriginal;for(const p of historyHeld)await send(p.type,p.body,p.expiry);historyHeld=[];return true;',[root_right])
  wait(lambda:all(any(m['text']==text and m.get('historical') for m in selected(right)['history']) for text in ['ROUTED_HISTORY_deferred_four','ROUTED_HISTORY_deferred_six']),8)
  check('successive gaps schedule a bounded deferred fill for the same stream',selected(right)['missing']==0)
  original_seven=js(centre,'return historyEvents.filter(p=>p.type==="event").map(p=>p.body.event).find(t=>{const p=JSON.parse(atob(t.split(".")[1].replaceAll("-","+").replaceAll("_","/")));return p.author_session_id===currentSession.public.sid&&p.sequence===7;});')
  root_identity=js(centre,'return currentSession.public')
  primitive=task(right,"const [{OriginReplayGate},{sessionBudget},{RoomSubscriptions}]=await Promise.all([import('./network/replay.mjs'),import('./network/resource-budget.mjs'),import('./network/subscriptions.mjs')]);const p=JSON.parse(atob(params[0].event.split('.')[1].replaceAll('-','+').replaceAll('_','/'))),owner={},gate=new OriginReplayGate(owner,identityConfig.identity),admission={scope:{room_id:p.room_id,descriptor_hash:p.descriptor_hash,membership_epoch:1,kinds:['chat']},identity:params[2],incarnation:p.stream_incarnation,expiresAt:Math.floor(Date.now()/1000)+60};gate.admit(admission);let denied=false;try{await gate.receiveHistorical(params[0].event);}catch{denied=true;}if(!denied)throw Error('History advanced a new stream');await gate.receive(params[1]);denied=false;try{await gate.receiveHistorical(params[0].event,()=>false);}catch{denied=true;}if(!denied)throw Error('Cancelled request consumed history');const recovered=await gate.receiveHistorical(params[0].event);denied=false;try{await gate.receive(params[0].event);}catch{denied=true;}if(!denied||!recovered.historical)throw Error('Historical replay reached live input');gate.close();const rooms=new RoomSubscriptions(owner);rooms.register({room_id:p.room_id,label:'History guard',kinds:['chat']});denied=false;try{rooms.deliverHistorical(p.room_id,{kind:'chess.move'});}catch{denied=true;}if(!denied)throw Error('Historical game command admitted');rooms.close();return Object.entries(sessionBudget(owner).snapshot()).every(([k,v])=>k==='closed'||v===0);",[original_two,original_seven,root_identity])
  check('historical verification cannot advance a stream or consume a cancelled request',primitive)
  # A hop-exhausted frame and a huge signed-link repair range must cause no
  # forwarding or range-sized allocation. All origins/links here are real.
  root_forwarded=selected(centre)['forwarded'];root_rejected=selected(centre)['rejected']
  task(right,'await historyPool.firstReady().link.sendRoutedApplication("event",{...params[0],hops_remaining:0});return true;',[original_two]);wait(lambda:selected(centre)['rejected']>root_rejected,10)
  check('hop exhaustion does not loop or forward',selected(centre)['forwarded']==root_forwarded)
  root_rejected=selected(centre)['rejected']
  task(right,'const p=JSON.parse(atob(params[0].event.split(".")[1].replaceAll("-","+").replaceAll("_","/")));await historyPool.firstReady().link.sendRoutedApplication("control",{operation:"history-request",node_id:params[1],descriptor_hash:p.descriptor_hash,request_id:(await import("./network/mesh-contract.mjs")).newNodeId(),author_session_id:p.author_session_id,stream_incarnation:p.stream_incarnation,from:1,to:Number.MAX_SAFE_INTEGER});return true;',[original_two,group]);wait(lambda:selected(centre)['rejected']>root_rejected,10)
  check('attacker-sized history range is refused before repair work',js(centre,'const s=historyRouter.historyStats();return s.pending===0&&s.serving===0;'))
  cold_start=selected(right)['repairsSent']
  # A provider with no active view must not retain new incoming history.
  js(centre,'historyRouter.releaseView(historyView);const link=historyPool.get(arguments[0]).link,send=link.historyOriginal;link.sendRoutedApplication=(type,body,expiry)=>{if(type==="event"){const p=JSON.parse(atob(body.event.split(".")[1].replaceAll("-","+").replaceAll("_","/")));if(p.author_session_id===historyLeafSid&&p.sequence===6)throw Error("Injected cold-provider loss");}return send(type,body,expiry);};',[root_right])
  for text in ['ROUTED_HISTORY_cold_six','ROUTED_HISTORY_cold_seven']:task(left,'return await historyRouter.send(historyView,params[0]);',[text])
  wait(lambda:any(m['text']=='ROUTED_HISTORY_cold_seven' for m in selected(right)['history']),10);wait(lambda:js(right,'return historyRouter.historyStats().pending===0'),7)
  check('unavailable history stays visibly incomplete after bounded retry',selected(right)['missing']==1 and selected(right)['incomplete'] and not any(m['text']=='ROUTED_HISTORY_cold_six' for m in selected(right)['history']))
  check('unavailable range consumes at most two requests',selected(right)['repairsSent']-cold_start<=2)
  # Occupy the actual shared repair slots, then cause another independently
  # verified gap. Admission must refuse without disturbing the live route.
  js(right,'window.heldRepairs=[];import("./network/resource-budget.mjs").then(({sessionBudget})=>{for(let i=0;i<4;i++)heldRepairs.push(sessionBudget(currentSession).slot("repairJobs"));});');wait(lambda:js(right,'return heldRepairs.length===4'),5)
  js(centre,'const link=historyPool.get(arguments[0]).link,send=link.historyOriginal;link.sendRoutedApplication=(type,body,expiry)=>{if(type==="event"){const p=JSON.parse(atob(body.event.split(".")[1].replaceAll("-","+").replaceAll("_","/")));if(p.author_session_id===historyLeafSid&&p.sequence===8)throw Error("Injected capacity-case loss");}return send(type,body,expiry);};',[root_right])
  for text in ['ROUTED_HISTORY_capacity_eight','ROUTED_HISTORY_capacity_nine']:task(left,'return await historyRouter.send(historyView,params[0]);',[text])
  wait(lambda:any(m['text']=='ROUTED_HISTORY_capacity_nine' for m in selected(right)['history']),10)
  check('full shared repair budget refuses work while live chat continues',js(right,'return historyRouter.historyStats().pending===0') and selected(right)['missing']==2 and 'capacity' in selected(right)['error'].lower())
  js(right,'heldRepairs.forEach(release=>release());heldRepairs=[];')
  # Leave an actual request pending and lose its required neighbor.
  js(centre,'const link=historyPool.get(arguments[0]).link,send=link.historyOriginal;link.sendRoutedApplication=(type,body,expiry)=>{if(type==="history")return Promise.resolve();if(type==="control"&&body.operation==="history-end"){window.blockedHistoryEnd=body;return Promise.resolve();}if(type==="event"){const p=JSON.parse(atob(body.event.split(".")[1].replaceAll("-","+").replaceAll("_","/")));if(p.author_session_id===historyLeafSid&&[10,12,14].includes(p.sequence)){window.pendingOriginFrame=body;throw Error("Injected pending-repair loss");}}return send(type,body,expiry);};',[root_right])
  for text in ['ROUTED_HISTORY_pending_ten','ROUTED_HISTORY_pending_eleven']:task(left,'return await historyRouter.send(historyView,params[0]);',[text])
  wait(lambda:js(right,'return historyRouter.historyStats().pending===1'),5);wait(lambda:js(centre,'return !!window.blockedHistoryEnd'),5)
  js(right,'window.realHistoryDateNow=Date.now;Date.now=()=>realHistoryDateNow()+6000;')
  try:
   task(centre,'const link=historyPool.get(params[0]).link;await link.historyOriginal("control",blockedHistoryEnd,Math.floor(Date.now()/1000)+30);return true;',[root_right]);wait(lambda:js(right,'return historyRouter.historyStats().pending===0'),5)
  finally:js(right,'Date.now=realHistoryDateNow;')
  check('absolute repair deadline is enforced before a delayed timer runs',not any(m['text']=='ROUTED_HISTORY_pending_ten' for m in selected(right)['history']))
  task(centre,'await historyPool.get(params[0]).link.historyOriginal("event",pendingOriginFrame);return true;',[root_right]);wait(lambda:any(m['text']=='ROUTED_HISTORY_pending_ten' and not m.get('historical') for m in selected(right)['history']),10)
  check('expired request does not poison the original live replay slot',True)
  for text in ['ROUTED_HISTORY_timeout_twelve','ROUTED_HISTORY_timeout_thirteen']:task(left,'return await historyRouter.send(historyView,params[0]);',[text])
  wait(lambda:js(right,'return historyRouter.historyStats().pending===1'),5)
  wait(lambda:js(right,'return historyRouter.historyStats().pending===0'),7)
  check('lost replies expire without fabricated delivery or an infinite retry queue',selected(right)['incomplete'] and 'timed out' in selected(right)['error'] and not any(m['text']=='ROUTED_HISTORY_timeout_twelve' for m in selected(right)['history']))
  for text in ['ROUTED_HISTORY_close_fourteen','ROUTED_HISTORY_close_fifteen']:task(left,'return await historyRouter.send(historyView,params[0]);',[text])
  wait(lambda:js(right,'return historyRouter.historyStats().pending===1'),5);js(centre,'historyPool.closeEntry(arguments[0]);',[root_right])
  for s in sessions:wait(lambda:js(s,'return historyRouter.snapshot(historyView).groups.find(g=>g.id===arguments[0])?.state==="closed"',[group]),10)
  check('required neighbor loss cancels pending repair timers',all(js(s,'return historyRouter.historyStats().pending===0') for s in sessions))
  check('repair preserves the running Linux instance',all(js(s,'return v86Instance===historyVM&&guestFiles.ready') for s in sessions))
  released=[]
  for s in sessions:
   task(s,'desktopNetwork.close();await new Promise(r=>setTimeout(r,200));return true;');stats=task(s,'return await desktopNetwork.stats();');check('session close releases every shared lease '+s,all(v==0 for k,v in stats['budget'].items() if k!='closed'));released.append(True)
  check('no history payload reached HTTP or a hidden tab bus',not f.http_chat)
  return {'status':'PASS','checks':checks,'contexts':3,'physicalLinks':2,'liveSiteChanged':False,'independentWANTested':False,'HTTPChatUsed':f.http_chat,'allBudgetsReleased':released,'sha256':source_pins}
 except Exception:
  for i,s in enumerate(sessions):
   try:(ROOT/'.build/checks'/('routed-history-failure-'+str(i)+'.json')).write_text(json.dumps({'snapshot':selected(s),'console':call('/session/'+s+'/log',{'type':'browser'})},indent=2)+'\n')
   except Exception:pass
  raise
 finally:
  for s in sessions:
   try:js(s,'desktopNetwork.close();guestNetworkAdapter?.destroy();v86Instance?.destroy();')
   finally:call('/session/'+s,method='DELETE')
async def main():
 f=HistoryFixture('/hidden')
 try:await f.start();return await asyncio.to_thread(browser,f)
 finally:await f.close()
if __name__=='__main__':
 result={'status':'FAIL'}
 try:result.update(asyncio.run(main()))
 finally:
  assert source_pins=={n:hashlib.sha256((ROOT/n).read_bytes()).hexdigest() for n in SOURCES},'Source changed during actual browser execution'
  result['sourceSHA256']=hashlib.sha256(Path(__file__).read_bytes()).hexdigest();p=ROOT/'.build/checks/routed-history-browser-result.json'
  if p.exists():p.rename(p.with_name(p.stem+'-before-'+str(time.time_ns())+'.json'))
  p.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
