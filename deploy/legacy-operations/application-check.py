#!/usr/bin/env python3
"""Prove negotiated public application framing over one real RTC link."""
import json,time,urllib.request
from pathlib import Path
BASE='http://127.0.0.1:19515';sessions=[]
def request(path,data=None,method=None):
    req=urllib.request.Request(BASE+path,data=None if data is None else json.dumps(data).encode(),headers={'Content-Type':'application/json'},method=method)
    with urllib.request.urlopen(req,timeout=90) as r:return json.load(r)['value']
def js(s,code):return request('/session/'+s+'/execute/sync',{'script':code,'args':[]})
def run(s,code):
    r=request('/session/'+s+'/execute/async',{'script':'const done=arguments[0];(async()=>{'+code+'})().then(value=>done({value})).catch(e=>done({error:e.message}));','args':[]});assert 'error' not in r,r;return r['value']
def until(s,code):
    end=time.monotonic()+60
    while time.monotonic()<end:
        if js(s,code):return
        time.sleep(.1)
    raise AssertionError('Timeout: '+code)
try:
    for _ in range(2):
        s=request('/session',{'capabilities':{'alwaysMatch':{'browserName':'chrome','goog:chromeOptions':{'binary':'/snap/chromium/current/usr/lib/chromium-browser/chrome','args':['--headless=new','--no-sandbox','--disable-dev-shm-usage']}}}})['sessionId'];sessions.append(s)
        request('/session/'+s+'/url',{'url':'http://127.0.0.1:8097/'})
        until(s,'return !!window.desktopLab?.session?.localKeyFingerprint')
        run(s,"const {PeerLink}=await import('./network/peer.mjs');window.messages=[];window.appFrames=[];window.probe=new PeerLink(currentSession,identityConfig,{onMessage:m=>messages.push(m),onApplication:a=>appFrames.push(a)});")
    left,right=sessions
    offer=run(left,'return await probe.offer();')
    answer=run(right,'return await probe.answer('+json.dumps(offer)+');')
    run(left,'await probe.acceptAnswer('+json.dumps(answer)+');')
    for s in sessions:until(s,'return probe.applicationReady')
    run(left,"await probe.sendApplication('control',{operation:'test',text:'<b>data</b>'});await probe.send('ordinary chat');")
    until(right,'return appFrames.length===1&&messages.length===1')
    assert js(right,'return appFrames[0].body.text==="<b>data</b>"&&messages[0].text==="ordinary chat"')
    run(right,"await probe.sendApplication('event',{event:'opaque signed-origin fixture'});")
    until(left,'return appFrames.length===1')
    # Real invitation and separate chat/move origin streams on that same link.
    run(left,"const rooms=await import('./network/room-invitation.mjs');window.testBundle=await rooms.createRoomInvitation(currentSession,probe.remote.payload.sender,identityConfig.identity,'Two-peer test',probe.connectionId);await probe.sendApplication('control',{operation:'invite',invitation:testBundle});window.ownedFixture=await rooms.prepareOwnedRoom(testBundle,probe.remote.payload.sender,currentSession,identityConfig.identity,probe.connectionId);")
    until(right,'return appFrames.length===2')
    run(right,"const rooms=await import('./network/room-invitation.mjs');window.acceptedFixture=await rooms.acceptRoomInvitation(appFrames[1].body.invitation,probe.remote.payload.sender,currentSession,identityConfig.identity,probe.connectionId);const {OriginReplayGate}=await import('./network/replay.mjs');window.originGate=new OriginReplayGate(currentSession,identityConfig.identity);for(const admission of acceptedFixture.lanes)originGate.admit(admission);window.verifiedOrigins=[];")
    for kind in ['chat','chess.move']:
        run(left,"const {signOrigin}=await import('./network/origin-event.mjs');const a=ownedFixture.lanes.find(a=>a.identity.sid===currentSession.public.sid&&a.scope.kinds[0]==="+json.dumps(kind)+");const now=Math.floor(Date.now()/1000);const payload="+ ('{text:"room chat only"}' if kind=='chat' else '{match_id:ownedFixture.nodeId,ply:1,notation:"e4"}') +";const token=await signOrigin({version:'codi-mesh/1',room_id:a.scope.room_id,descriptor_hash:a.scope.descriptor_hash,membership_epoch:1,author_session_id:currentSession.public.sid,stream_incarnation:a.incarnation,sequence:1,issued_at:now,expires_at:Math.min(now+60,a.expiresAt),kind:"+json.dumps(kind)+",payload},currentSession,identityConfig.identity,a.scope);await probe.sendApplication('event',{origin:token});")
        until(right,'return appFrames.length==='+str(3 if kind=='chat' else 4))
        run(right,"const result=await originGate.receive(appFrames.at(-1).body.origin);verifiedOrigins.push(result.event);")
    assert js(right,'return verifiedOrigins.length===2&&verifiedOrigins[0].kind==="chat"&&verifiedOrigins[1].kind==="chess.move"&&verifiedOrigins[0].room_id!==verifiedOrigins[1].room_id&&messages.length===1')
    run(right,'originGate.close();acceptedFixture.directory.close();')
    run(left,'ownedFixture.directory.close();')
    stats=[run(s,'return await probe.stats();') for s in sessions]
    assert all(x['publicApplication'] and x['connectionState']=='connected' for x in stats)
    # Verify that an endpoint with no application callback cannot negotiate or send it.
    run(left,"probe.close();const {PeerLink}=await import('./network/peer.mjs');window.legacy=new PeerLink(currentSession,identityConfig);let rejected=false;try{await legacy.sendApplication('control',{});}catch{rejected=true;}legacy.close();if(!rejected)throw Error('Unnegotiated send allowed');")
    result={'status':'PASS','scope':'Authenticated application framing and ordinary chat on one RTC link; explicit two-peer room admission and separate chat/move origins; not GUI or routed delivery','stats':stats,'verifiedPeerInvitation':True,'separateChatAndMoveOrigins':True,'unnegotiatedSendRejected':True,'wanTested':False}
    Path('.build/checks/application-result.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
finally:
    for s in sessions:request('/session/'+s,method='DELETE')
