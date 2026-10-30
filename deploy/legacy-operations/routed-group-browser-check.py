#!/usr/bin/env python3
"""Real three-browser routed public chat on the existing desktop/issuer/v86 pool.

Owned loopback fixture only. Two leaf browsers never connect to one another;
the controller verifies and forwards original signed events. No public rollout,
private encryption, independent WAN, automatic history repair or scale claim.
"""
import asyncio
import hashlib
import importlib.util
import json
from pathlib import Path
import time
from aiohttp import web

ROOT=Path(__file__).resolve().parent.parent
spec=importlib.util.spec_from_file_location('routed_fixture',ROOT/'scripts/guest-client-browser-check.py')
fixture=importlib.util.module_from_spec(spec);spec.loader.exec_module(fixture)
fixture.PAGE=(ROOT/'index.html').read_bytes()
call,wait=fixture.call,fixture.wait

class Fixture(fixture.Fixture):
    async def start(self):
        self.http_chat=False
        await super().start()
        for name in ['routed-rooms.mjs','routed-room-grant.mjs','routed-history.mjs']:
            (self.root/'public/network'/name).write_bytes((ROOT/'network'/name).read_bytes())
    async def proxy(self,request):
        response=await super().proxy(request)
        # Observe the cached body AFTER the forwarding handler consumes it.
        # Pre-reading changes can_read_body and would forward an empty request.
        if request.method=='POST':
            body=await request.read()
            if b'ROUTED_MARKER_' in body:self.http_chat=True
        if request.path.endswith('/config.json'):
            data=json.loads(response.body);data['routedGroups']={'version':'codi-routed-room/2'}
            return web.json_response(data,headers={k:v for k,v in response.headers.items() if k.lower() not in ('content-type','content-length')})
        return response

def browser(f):
    sessions=[];checks=[]
    def js(s,code,args=[]):return call('/session/'+s+'/execute/sync',{'script':code,'args':args})
    def task(s,code,args=[]):
        r=call('/session/'+s+'/execute/async',{'script':'const params=arguments,done=arguments[arguments.length-1];(async()=>{'+code+'})().then(value=>done({ok:true,value}),error=>done({ok:false,error:error.message,stack:error.stack}));','args':args})
        assert r['ok'],r
        return r.get('value')
    def check(name,value):assert value,name;checks.append(name)
    def click(s,selector):js(s,'document.querySelector(arguments[0]).click()',[selector])
    def ready(s):
        return js(s,'return window.desktopLab?.guestState==="ready"&&desktopNetwork.appContext().routedRooms&&guestNetworkAdapter?.mode==="anonymous"')
    def snapshot(s):return js(s,'return desktopNetwork.appContext().routedRooms.snapshot(window.groupView)')
    def history(s):return js(s,'return document.querySelector("[data-routed-history]").textContent')
    def send(s,text):
        js(s,'const f=document.querySelector("[data-routed-draft]");f.value=arguments[0];f.dispatchEvent(new Event("input"));document.querySelector("[data-routed-send]").click()',[text])
        wait(lambda:not js(s,'return groupView.routedWorking'),20)
        assert not js(s,'return groupView.routedError'),snapshot(s)
    try:
        for _ in range(3):
            s=call('/session',{'capabilities':{'alwaysMatch':{'browserName':'chrome','goog:chromeOptions':{'binary':'/snap/chromium/current/usr/lib/chromium-browser/chrome','args':['--headless=new','--no-sandbox','--disable-dev-shm-usage']},'goog:loggingPrefs':{'browser':'ALL'}}}})['sessionId'];sessions.append(s)
            call('/session/'+s+'/timeouts',{'script':120000})
            call('/session/'+s+'/goog/cdp/execute',{'cmd':'Page.addScriptToEvaluateOnNewDocument','params':{'source':'window.BroadcastChannel=class{constructor(){throw Error("Hidden tab bus forbidden by test")}};'}})
            call('/session/'+s+'/url',{'url':f.origin+f.base+'/'})
            wait(lambda:ready(s),150)
            check('development issuer identity and real Linux '+str(len(sessions)),js(s,'return currentSession.trust.level==="test-server"&&guestFiles.ready&&!!v86Instance.fs9p'))
            js(s,'window.savedVM=v86Instance;window.savedFS=v86Instance.fs9p;window.savedSession=currentSession;window.groupOutcomes=[];window.groupPackets=[];const r=desktopNetwork.appContext().routedRooms,original=r.receive.bind(r);r.receive=async(...args)=>{const result=await original(...args);if(groupOutcomes.length<100)groupOutcomes.push(result);return result};')
        centre,left,right=sessions
        for leaf in [left,right]:
            offer=task(centre,'const result=await desktopNetwork.appContext().pool.offer();return {id:result.entry.id,token:result.token}')
            answer=task(leaf,'const result=await desktopNetwork.appContext().pool.answer(params[0]);return result.token',[offer['token']])
            task(centre,'await desktopNetwork.appContext().pool.accept(params[0],params[1]);return true',[offer['id'],answer])
            wait(lambda:js(leaf,'return desktopNetwork.appContext().pool.firstReady()?.link.routedApplicationReady'),30)
        wait(lambda:js(centre,'return desktopNetwork.appContext().pool.list().filter(e=>e.state==="ready").length===2'),30)
        for s in sessions:
            js(s,'window.groupView=[...surfaces.values()][0].launch("rooms");for(const e of desktopNetwork.appContext().pool.list()){const link=desktopNetwork.appContext().pool.get(e.id).link,original=link.sendRoutedApplication.bind(link);link.sendRoutedApplication=(type,body,expiry)=>{if(groupPackets.length<100)groupPackets.push({type,body:structuredClone(body)});return original(type,body,expiry);};}')
            wait(lambda:js(s,'return !!document.querySelector("[data-routed-rooms]")'),20)
        js(centre,'for(const o of document.querySelector("[data-routed-peers]").options)o.selected=true;document.querySelector("[data-routed-create]").click()')
        wait(lambda:snapshot(centre)['selected'] is not None,20)
        group=snapshot(centre)['selected']['id']
        for s in [left,right]:
            wait(lambda:len(snapshot(s)['groups'])==1,20)
            wait(lambda:js(s,'return [...document.querySelector("[data-routed-select]").options].some(o=>o.value===arguments[0])',[group]),20)
            js(s,'const c=document.querySelector("[data-routed-select]");c.value=arguments[0];c.dispatchEvent(new Event("change"))',[group])
            wait(lambda:snapshot(s)['selected'] is not None,20)
            check('invitation requires explicit consent '+s,snapshot(s)['selected']['state']=='pending' and js(s,'return document.querySelector("[data-routed-send]").disabled'))
        click(left,'[data-routed-accept]')
        wait(lambda:snapshot(left)['selected']['state']=='waiting',20)
        check('one acceptance cannot activate the group',snapshot(centre)['selected']['state']=='waiting' and snapshot(right)['selected']['state']=='pending')
        click(right,'[data-routed-accept]')
        for s in sessions:wait(lambda:snapshot(s)['selected']['state']=='active',20)
        markers=['ROUTED_MARKER_'+str(i)+'_'+str(time.time_ns()) for i in range(3)]
        markers[1]+=' <b>literal</b> ☃'
        for s,text in zip(sessions,markers):
            send(s,text)
            for destination in sessions:wait(lambda:text in history(destination),20)
        for s in sessions:
            check('all admitted origins delivered exactly once '+s,all(history(s).count(m)==1 for m in markers))
            check('routed text is literal DOM '+s,js(s,'return !document.querySelector("[data-routed-history] b")'))
        check('leaf browsers have one physical link each and no direct leaf link',all(js(s,'return desktopNetwork.appContext().pool.list().filter(e=>e.state==="ready").length===1') for s in [left,right]))
        check('controller forwards original leaf authors',snapshot(centre)['selected']['forwarded']==4 and all(snapshot(s)['selected']['received']==3 for s in sessions))
        # Real authenticated link replay, route mismatch and invalid origin signature.
        frame=js(left,'return groupPackets.find(p=>p.type==="event").body')
        def invalid_leaf_packet(value,expected):
            before=js(centre,'return groupOutcomes.length')
            task(left,'await desktopNetwork.appContext().pool.firstReady().link.sendRoutedApplication("event",params[0]);return true',[value])
            wait(lambda:js(centre,'return groupOutcomes.length>arguments[0]',[before]),20)
            outcome=js(centre,'return groupOutcomes.at(-1)');check(expected,not outcome['accepted'])
        invalid_leaf_packet(frame,'replayed signed origin rejected over real RTC')
        alternate=task(left,'const c=await import("./network/crypto.mjs"),o=await import("./network/origin-event.mjs"),frame=params[0],p=c.inspectJws(frame.event,o.ORIGIN_TYPE,16384).payload;frame.event=await c.signJws(p,currentSession.privateKey,o.ORIGIN_TYPE);return frame',[frame])
        check('alternate ES256 signature preserves the signed event ID',alternate['event']!=frame['event'] and alternate['request_id']==frame['request_id'])
        invalid_leaf_packet(alternate,'alternate valid signature cannot bypass replay floor')
        invalid_leaf_packet({**frame,'hops_remaining':1},'wrong ingress hop rejected before replay')
        invalid_leaf_packet({**frame,'destination_cell':js(centre,'return crypto.randomUUID()')},'malformed destination rejected')
        forged=task(centre,'const c=await import("./network/crypto.mjs"),o=await import("./network/origin-event.mjs");const frame=params[0],p=c.inspectJws(frame.event,o.ORIGIN_TYPE,16384).payload;p.sequence=2;p.payload.text="FORGED";frame.event=await c.signJws(p,currentSession.privateKey,o.ORIGIN_TYPE);frame.request_id=await o.originEventId(frame.event);return frame',[frame])
        invalid_leaf_packet(forged,'controller cannot forge a leaf origin signature')
        good='ROUTED_MARKER_AFTER_FORGERY_'+str(time.time_ns());send(left,good)
        for s in sessions:wait(lambda:good in history(s),20)
        check('rejected forgery did not poison sequence floor',all('FORGED' not in history(s) and history(s).count(good)==1 for s in sessions))
        # Exhaust global metadata, fail a new join, then prove existing group still works.
        failure=task(centre,'const {sessionBudget,NETWORK_LIMITS}=await import("./network/resource-budget.mjs"),b=sessionBudget(currentSession),release=b.metadata(b.limits().metadataBytes-b.snapshot().metadataBytes);try{await desktopNetwork.appContext().routedRooms.create(desktopNetwork.appContext().pool.list().filter(e=>e.state==="ready").map(e=>e.id),"Must fail",{});return false}catch(e){return /metadataBytes/.test(e.message)}finally{release()}')
        check('new group refuses exhausted shared session budget',failure)
        send(right,'ROUTED_MARKER_AFTER_CAPACITY_'+str(time.time_ns()))
        # Explicit consent does not validate a forged/oversized controller grant.
        bundle=js(centre,'return groupPackets.find(p=>p.type==="control"&&p.body.operation==="invite").body.invitation')
        for name,mutation in [('unknown version','p.version="unknown"'),('extra grant privilege','p.owner=true'),('excessive hops','p.max_hops=16'),('duplicate member','p.members[2]=p.members[1]'),('bad incarnation','p.members[1].incarnation="bad"'),('overlong authority','p.expires_at=p.issued_at+301')]:
            bad=task(centre,'const c=await import("./network/crypto.mjs"),g=await import("./network/routed-room-grant.mjs"),b=params[0],p=c.inspectJws(b.grant,g.GROUP_TYPE,18000).payload;'+mutation+';b.grant=await c.signJws(p,currentSession.privateKey,g.GROUP_TYPE);return b',[bundle])
            rejected=task(left,'const {verifyRoutedGrant}=await import("./network/routed-room-grant.mjs");try{const v=await verifyRoutedGrant(params[0],desktopNetwork.appContext().pool.firstReady().link.remoteIdentity,currentSession,identityConfig.identity);v.directory.close();return false}catch{return true}',[bad])
            check('signed grant refuses '+name,rejected)
        witnesses=[]
        for s in sessions:
            stats=task(s,'return await desktopNetwork.stats()');check('same session and real v86 filesystem '+s,js(s,'renderPreviews();return v86Instance===savedVM&&v86Instance.fs9p===savedFS&&currentSession===savedSession'))
            witnesses.append({'group':snapshot(s),'physicalLinks':len([e for e in stats['peers'] if e['state']=='ready']),'stats':stats})
        entry=js(centre,'return desktopNetwork.appContext().pool.list().find(e=>e.peerId===arguments[0]).id',[js(left,'return currentSession.public.sid')])
        js(centre,'desktopNetwork.appContext().pool.closeEntry(arguments[0])',[entry])
        for s in sessions:wait(lambda:snapshot(s)['selected']['state']=='closed',20)
        check('required link loss closes the fixed group instead of inventing membership',True)
        disposed=[]
        for s in sessions:
            task(s,'desktopNetwork.close();await new Promise(r=>setTimeout(r,300));return true')
            stats=task(s,'return await desktopNetwork.stats()');check('all shared network budgets released '+s,stats['budget']['closed'] and all(v==0 for k,v in stats['budget'].items() if k!='closed'));disposed.append(True)
        check('no HTTP chat relay',not f.http_chat)
        return {'status':'PASS','scope':__doc__,'checks':checks,'contexts':3,'physicalLinks':2,'expectedRemoteChatDeliveries':6,'observedRemoteChatDeliveries':6,'originalLeafSignaturesVerified':True,'explicitAllMemberConsent':True,'sameSessionPoolAndV86':True,'hiddenLocalBusUsed':False,'privateEncryptionClaimed':False,'publicRollout':False,'independentWANVerified':False,'witnesses':witnesses,'allBudgetsReleased':disposed}
    except Exception:
        for i,s in enumerate(sessions):
            try:(ROOT/'.build/checks'/('routed-group-failure-'+str(i)+'.json')).write_text(json.dumps({'text':js(s,'return document.body.textContent'),'snapshot':snapshot(s),'console':call('/session/'+s+'/log',{'type':'browser'})},indent=2)+'\n')
            except Exception:pass
        raise
    finally:
        for s in sessions:
            try:js(s,'desktopNetwork.close();guestNetworkAdapter?.destroy();v86Instance?.destroy();')
            finally:call('/session/'+s,method='DELETE')

async def main():
    f=Fixture('/hidden')
    try:await f.start();return await asyncio.to_thread(browser,f)
    finally:await f.close()

if __name__=='__main__':
    result={'status':'FAIL','scope':__doc__}
    try:result.update(asyncio.run(main()))
    finally:
        result['sha256']={name:hashlib.sha256((ROOT/name).read_bytes()).hexdigest() for name in ['network/routed-room-grant.mjs','network/routed-rooms.mjs','network/peer.mjs','network/peer-pool.mjs','networking.js','desktop-apps.js','scripts/routed-group-browser-check.py']}
        file=ROOT/'.build/checks/routed-group-browser-result.json'
        if file.exists():file.rename(file.with_name(file.stem+'-before-'+str(time.time_ns())+'.json'))
        file.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
