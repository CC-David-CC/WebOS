#!/usr/bin/env python3
"""Actual RTC scope-transplant and legacy-capability negatives; loopback only."""
import asyncio,hashlib,importlib.util,json,time
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
spec=importlib.util.spec_from_file_location('routed_scope_fixture',ROOT/'scripts/routed-group-browser-check.py');fixture=importlib.util.module_from_spec(spec);spec.loader.exec_module(fixture)
call,wait=fixture.call,fixture.wait
def browser(f):
    sessions=[]
    def js(s,code,args=[]):return call('/session/'+s+'/execute/sync',{'script':code,'args':args})
    def task(s,code,args=[]):
        r=call('/session/'+s+'/execute/async',{'script':'const params=arguments,done=arguments[arguments.length-1];(async()=>{'+code+'})().then(value=>done({ok:true,value}),e=>done({ok:false,error:e.message}));','args':args});assert r['ok'],r;return r.get('value')
    def state(s,g):return js(s,'return desktopNetwork.appContext().routedRooms.snapshot(scopeViews[arguments[0]]).selected',[g])
    try:
        for _ in range(3):
            s=call('/session',{'capabilities':{'alwaysMatch':{'browserName':'chrome','goog:chromeOptions':{'binary':'/snap/chromium/current/usr/lib/chromium-browser/chrome','args':['--headless=new','--no-sandbox','--disable-dev-shm-usage']}}}})['sessionId'];sessions.append(s)
            call('/session/'+s+'/timeouts',{'script':120000});call('/session/'+s+'/url',{'url':f.origin+f.base+'/'})
            wait(lambda:js(s,'return window.desktopLab?.guestState==="ready"&&desktopNetwork.appContext().routedRooms&&!desktopLab.lifecycle.blocked'),150)
            js(s,'window.scopeViews=[{},{}];window.scopeOutcomes=[];const rooms=desktopNetwork.appContext().routedRooms,original=rooms.receive.bind(rooms);rooms.receive=async(...args)=>{const result=await original(...args);scopeOutcomes.push(result);return result};')
        centre,author,recipient=sessions
        for leaf in [author,recipient]:
            o=task(centre,'const o=await desktopNetwork.appContext().pool.offer();return {id:o.entry.id,token:o.token}')
            a=task(leaf,'return (await desktopNetwork.appContext().pool.answer(params[0])).token',[o['token']])
            task(centre,'await desktopNetwork.appContext().pool.accept(params[0],params[1]);return true',[o['id'],a]);wait(lambda:js(leaf,'return !!desktopNetwork.appContext().pool.firstReady()?.link.routedApplicationReady'),30)
        js(author,'window.scopePackets=[];const link=desktopNetwork.appContext().pool.firstReady().link,original=link.sendRoutedApplication.bind(link);link.sendRoutedApplication=(type,body,exp)=>{if(type==="event")scopePackets.push(structuredClone(body));return original(type,body,exp)};')
        for g in range(2):
            group=task(centre,'return await desktopNetwork.appContext().routedRooms.create(desktopNetwork.appContext().pool.list().filter(e=>e.state==="ready").map(e=>e.id),"Scope "+params[0],scopeViews[params[0]])',[g])
            for leaf in [author,recipient]:
                wait(lambda:js(leaf,'return desktopNetwork.appContext().routedRooms.snapshot(null).groups.some(g=>g.id===arguments[0])',[group]),20)
                task(leaf,'await desktopNetwork.appContext().routedRooms.accept(params[0],scopeViews[params[1]]);return true',[group,g])
            for s in sessions:wait(lambda:state(s,g)['state']=='active',20)
        task(author,'return await desktopNetwork.appContext().routedRooms.send(scopeViews[0],"scope base")')
        wait(lambda:len(state(recipient,0)['history'])==1,20)
        original=task(author,'const c=await import("./network/crypto.mjs"),o=await import("./network/origin-event.mjs"),frame=structuredClone(scopePackets[0]),p=c.inspectJws(frame.event,o.ORIGIN_TYPE,16384).payload;p.sequence=2;p.payload.text="VALID_AFTER_TRANSPLANT_REJECTION";frame.event=await c.signJws(p,currentSession.privateKey,o.ORIGIN_TYPE);frame.request_id=await o.originEventId(frame.event);return frame')
        room_two=task(author,'const {roomId}=await import("./network/mesh-contract.mjs");return await roomId(desktopNetwork.appContext().routedRooms.snapshot(scopeViews[1]).selected.id,"chat")')
        before=js(centre,'return scopeOutcomes.length')
        task(author,'await desktopNetwork.appContext().pool.firstReady().link.sendRoutedApplication("event",params[0]);return true',[{**original,'destination_cell':room_two}])
        wait(lambda:js(centre,'return scopeOutcomes.length>arguments[0]',[before]),20)
        denied=js(centre,'return scopeOutcomes.at(-1)');assert not denied['accepted'] and 'destination group' in denied['error'],denied
        assert all(not state(s,1)['history'] for s in sessions)
        task(author,'await desktopNetwork.appContext().pool.firstReady().link.sendRoutedApplication("event",params[0]);return true',[original])
        for s in [centre,recipient]:wait(lambda:any(m['text']=='VALID_AFTER_TRANSPLANT_REJECTION' for m in state(s,0)['history']),20)
        assert all(not state(s,1)['history'] for s in sessions)
        # Existing two-person rooms and separate SAN moves share these same links.
        author_sid=js(author,'return currentSession.public.sid')
        old_room=task(centre,'window.legacyView={};const e=desktopNetwork.appContext().pool.list().find(e=>e.peerId===params[0]);return await desktopNetwork.appContext().roomService.create("Legacy chess regression",legacyView,desktopNetwork.appContext().pool.get(e.id).link)',[author_sid])
        wait(lambda:js(author,'return desktopNetwork.appContext().roomService.snapshot(null).rooms.some(r=>r.id===arguments[0])',[old_room]),20)
        task(author,'window.legacyView={};await desktopNetwork.appContext().roomService.accept(params[0],legacyView);return true',[old_room])
        for s in [centre,author]:wait(lambda:js(s,'return desktopNetwork.appContext().roomService.snapshot(legacyView).selected?.state==="active"'),20)
        task(centre,'await desktopNetwork.appContext().roomService.send(legacyView,"chat","LEGACY_CHAT_SEPARATE");await desktopNetwork.appContext().roomService.send(legacyView,"chess.move","e4");return true')
        wait(lambda:js(author,'return desktopNetwork.appContext().roomService.snapshot(legacyView).selected.moves.length===1'),20)
        task(author,'await desktopNetwork.appContext().roomService.send(legacyView,"chess.move","e5");return true')
        wait(lambda:js(centre,'return desktopNetwork.appContext().roomService.snapshot(legacyView).selected.moves.length===2'),20)
        pgn=[js(s,'return desktopNetwork.appContext().roomService.exportPgn(legacyView)') for s in [centre,author]]
        assert pgn[0]==pgn[1] and '1. e4 e5' in pgn[0] and 'LEGACY_CHAT_SEPARATE' not in pgn[0]
        assert js(author,'return desktopNetwork.appContext().roomService.snapshot(legacyView).selected.chat.some(m=>m.text==="LEGACY_CHAT_SEPARATE")')
        # Separate throwaway identities test the existing signed capability boundary.
        legacy=task(centre,'''const {beginSession}=await import('./network/identity.mjs'),{PeerPool}=await import('./network/peer-pool.mjs'),{sessionBudget}=await import('./network/resource-budget.mjs');
          const config={identity:{mode:'local-development'},rtc:{iceServers:[]}},a=await beginSession(config,'anonymous'),b=await beginSession(config,'anonymous');let delivered=0;
          const left=new PeerPool(a,config,{onApplication:()=>{},onRoutedApplication:()=>{}}),right=new PeerPool(b,config,{onApplication:()=>{delivered++}});
          try{const offer=await left.offer(),answer=await right.answer(offer.token);await left.accept(offer.entry.id,answer.token);const until=Date.now()+15000;while((!left.firstReady()||!right.firstReady())&&Date.now()<until)await new Promise(r=>setTimeout(r,25));
          const link=left.firstReady()?.link;if(!link||link.routedApplicationReady)throw Error('Legacy negotiation incorrectly enabled routing');let denied=false;try{await link.sendRoutedApplication('event',{})}catch{denied=true}if(!denied)throw Error('Unnegotiated send allowed');
          await link.sendPacket('application',JSON.stringify({version:'codi-mesh/1',mode:'routed-public-jws/2',type:'event',body:{}}));const end=Date.now()+5000;while(!answer.entry.link.closed&&Date.now()<end)await new Promise(r=>setTimeout(r,25));
          if(!answer.entry.link.closed||delivered)throw Error('Legacy receiver accepted routed data');return true;
          }finally{left.close();right.close();await new Promise(r=>setTimeout(r,100));for(const s of [a,b]){const used=sessionBudget(s).snapshot();if(Object.entries(used).some(([k,v])=>k!=='closed'&&v!==0))throw Error('Protocol fixture leaked shared budget')}}''')
        assert legacy and js(centre,'return desktopNetwork.appContext().pool.list().filter(e=>e.state==="ready").length===2')
        return {'status':'PASS','scope':__doc__,'validOriginCannotBeTransplantedBetweenTwoAdmittedGroups':True,'rejectedScopeDidNotAdvanceOriginalReplayFloor':True,'correctDestinationDeliversExactlyOnce':all(sum(m['text']=='VALID_AFTER_TRANSPLANT_REJECTION' for m in state(s,0)['history'])==1 for s in [centre,recipient]),'legacyUnnegotiatedRoutingRejectedBeforeDelivery':True,'existingTwoPeerChatAndSeparateLegalChessOnSamePool':True,'matchingLegacyPgnExcludesChat':True,'existingDesktopPoolPreserved':True,'publicRollout':False}
    finally:
        for s in sessions:
            try:js(s,'desktopNetwork.close();guestNetworkAdapter?.destroy();v86Instance?.destroy();')
            finally:call('/session/'+s,method='DELETE')
async def main():
    f=fixture.Fixture('/hidden')
    try:await f.start();return await asyncio.to_thread(browser,f)
    finally:await f.close()
if __name__=='__main__':
    result={'status':'FAIL','scope':__doc__}
    try:result.update(asyncio.run(main()))
    finally:
        names=['network/routed-room-grant.mjs','network/routed-rooms.mjs','network/peer.mjs','network/peer-pool.mjs','networking.js','desktop-apps.js','scripts/routed-scope-browser-check.py']
        result['sha256']={n:hashlib.sha256((ROOT/n).read_bytes()).hexdigest() for n in names};p=ROOT/'.build/checks/routed-scope-browser-result.json'
        if p.exists():p.rename(p.with_name(p.stem+'-before-'+str(time.time_ns())+'.json'))
        p.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
