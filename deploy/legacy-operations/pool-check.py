#!/usr/bin/env python3
"""Three actual browsers: two peers, isolated rooms, failed joins and disconnect."""
import argparse,hashlib,json,time,urllib.request
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--url',default='http://127.0.0.1:8097/');args=p.parse_args()
BASE='http://127.0.0.1:19515';sessions=[];checks=[];action_trace=[]
def req(path,data=None,method=None):
    r=urllib.request.Request(BASE+path,data=None if data is None else json.dumps(data).encode(),headers={'Content-Type':'application/json'},method=method)
    with urllib.request.urlopen(r,timeout=90) as response:return json.load(response)['value']
def js(s,script):return req('/session/'+s+'/execute/sync',{'script':script,'args':[]})
def wait(s,script):
    end=time.monotonic()+60
    while time.monotonic()<end:
        try:value=js(s,script)
        except urllib.error.HTTPError:value=None
        if value:return value
        time.sleep(.1)
    raise AssertionError('Timed out: '+script+'; '+str(js(s,'return [...document.querySelectorAll("[data-chat-status],[data-room-status]")].map(n=>n.textContent)')))
def stats(s,id=None):return req('/session/'+s+'/execute/async',{'script':'const done=arguments[0];desktopNetwork.stats('+json.dumps(id)+').then(done)','args':[]})
def click(s,selector):js(s,'document.querySelector('+json.dumps(selector)+').click()')
def select(s,selector,value):js(s,'const n=document.querySelector('+json.dumps(selector)+');n.value='+json.dumps(value)+';n.dispatchEvent(new Event("change"));')
def input_value(s,selector,text):js(s,'const n=document.querySelector('+json.dumps(selector)+');n.value='+json.dumps(text)+';n.dispatchEvent(new Event("input"));')
def launch(s,app):return js(s,'return surfaces.values().next().value.launch('+json.dumps(app)+').id')
def prefix(window_id):return '[data-window="'+str(window_id)+'"] '
def peer_id(s,remote_sid):return next(e['id'] for e in stats(s)['peers'] if e['peerId']==remote_sid and e['state']=='ready')
def connect(a,b):
    wait(a,'return !desktopLab.lifecycle?.blocked&&!document.querySelector("[data-chat-action=offer]").disabled')
    wait(b,'return !desktopLab.lifecycle?.blocked&&!document.querySelector("[data-chat-action=answer]").disabled')
    previous_offer=js(a,'return document.querySelector("[data-chat-out]").value')
    previous_answer=js(b,'return document.querySelector("[data-chat-out]").value')
    action_trace.append({'phase':'offer','source':a,'destination':b,'previousOfferBytes':len(previous_offer),'previousAnswerBytes':len(previous_answer)})
    click(a,'[data-chat-action="offer"]');offer=wait(a,'const value=document.querySelector("[data-chat-out]").value;return value&&value!=='+json.dumps(previous_offer)+'?value:null;')
    action_trace.append({'phase':'answer','offerSHA256':hashlib.sha256(offer.encode()).hexdigest()})
    input_value(b,'[data-chat-in]',offer)
    wait(b,'return !desktopLab.lifecycle?.blocked&&!document.querySelector("[data-chat-action=answer]").disabled')
    click(b,'[data-chat-action="answer"]');answer=wait(b,'const value=document.querySelector("[data-chat-out]").value;return value&&value!=='+json.dumps(previous_answer)+'?value:null;')
    action_trace.append({'phase':'accept','answerSHA256':hashlib.sha256(answer.encode()).hexdigest()})
    input_value(a,'[data-chat-in]',answer)
    wait(a,'return !desktopLab.lifecycle?.blocked&&!document.querySelector("[data-chat-action=accept]").disabled')
    click(a,'[data-chat-action="accept"]')
    for s,other in [(a,b),(b,a)]:
        sid=js(other,'return desktopLab.session.id');end=time.monotonic()+30
        while not any(e['peerId']==sid and e['state']=='ready' for e in stats(s)['peers']):
            assert time.monotonic()<end;time.sleep(.1)
    action_trace.append({'phase':'connected','source':a,'destination':b})
def room_select(s,w,id):select(s,prefix(w)+'[data-room-select]',id)
def create_room(a,wa,b,wb,name):
    input_value(a,prefix(wa)+'[aria-label="New room name"]',name);click(a,prefix(wa)+'[data-room-create]')
    id=wait(a,'return document.querySelector('+json.dumps(prefix(wa)+'[data-room-select]')+').value')
    wait(b,'return [...document.querySelector('+json.dumps(prefix(wb)+'[data-room-select]')+').options].some(o=>o.value==='+json.dumps(id)+')')
    room_select(b,wb,id);click(b,prefix(wb)+'[data-room-accept]')
    for s,w in [(a,wa),(b,wb)]:wait(s,'return document.querySelector('+json.dumps(prefix(w)+'[data-room-status]')+').textContent.includes("active")')
    return id
def room_send(s,w,kind,text):
    button=prefix(w)+('[data-room-send-move]' if kind=='move' else '[data-room-send-chat]')
    wait(s,'return !document.querySelector('+json.dumps(button)+').disabled')
    input_value(s,prefix(w)+('[aria-label="Chess move notation"]' if kind=='move' else '[aria-label="Room chat message"]'),text);click(s,button)
def room_has(s,w,text,kind='move'):
    return wait(s,'return document.querySelector('+json.dumps(prefix(w)+('[data-room-moves]' if kind=='move' else '[data-room-chat]'))+').textContent.includes('+json.dumps(text)+')')
def close_window(s,w):click(s,prefix(w)+'.window-controls button[aria-label="Close"]')
try:
    chat_windows=[]
    for _ in range(3):
        s=req('/session',{'capabilities':{'alwaysMatch':{'browserName':'chrome','goog:chromeOptions':{'binary':'/snap/chromium/current/usr/lib/chromium-browser/chrome','args':['--headless=new','--no-sandbox','--disable-dev-shm-usage','--window-size=1400,1000']}}}})['sessionId'];sessions.append(s)
        req('/session/'+s+'/url',{'url':args.url});wait(s,'return !!window.desktopLab?.session?.localKeyFingerprint&&desktopLab.guestState==="ready"&&!!v86Instance&&!desktopLab.lifecycle?.blocked')
        js(s,'window.poolVM=v86Instance;window.poolSession=desktopLab.session.id;');chat_windows.append(launch(s,'chat'))
        wait(s,'return !document.querySelector("[data-chat-action=offer]").disabled')
    a,b,c=sessions;sidb=js(b,'return desktopLab.session.id');sidc=js(c,'return desktopLab.session.id')
    connect(a,b);ab=peer_id(a,sidb);wa,wb=launch(a,'rooms'),launch(b,'rooms');rab=create_room(a,wa,b,wb,'AB table')
    room_send(a,wa,'chat','AB before C');room_has(b,wb,'AB before C','chat')
    connect(a,c);ac=peer_id(a,sidc)
    assert stats(a)['budget']['connections']==2
    room_send(a,wa,'move','e4');room_has(b,wb,'e4');room_send(b,wb,'move','e5');room_has(a,wa,'e5')
    checks.append('second peer preserves first accepted room and guest')
    # Separate Chat windows select different pooled peers, without creating links.
    extra=launch(a,'chat');select(a,prefix(extra)+'[data-chat-peer]',ac)
    input_value(a,prefix(extra)+'[data-chat-draft]','AC only');click(a,prefix(extra)+'[data-chat-send]')
    wait(c,'return document.querySelector("[data-chat-history]").textContent.includes("AC only")')
    assert not js(b,'return document.querySelector("[data-chat-history]").textContent.includes("AC only")')
    assert stats(a)['budget']['connections']==2
    checks.append('separate peer conversations share the pool without history bleed')
    # A different room uses C while the AB transcript/identity remains intact.
    select(a,prefix(wa)+'[data-room-peer]',ac);wc=launch(c,'rooms');rac=create_room(a,wa,c,wc,'AC table')
    room_select(a,wa,rab);assert room_has(a,wa,'e5')
    close_window(a,chat_windows[0]);close_window(a,extra)
    wa2=launch(a,'rooms');room_select(a,wa2,rac)
    room_send(a,wa,'move','Nf3');room_has(b,wb,'Nf3');room_send(b,wb,'move','Nc6');room_has(a,wa,'Nc6')
    room_send(a,wa2,'move','d4');room_has(c,wc,'d4');room_send(c,wc,'move','d5');room_has(a,wa2,'d5')
    assert not js(a,'return document.querySelector('+json.dumps(prefix(wa2)+'[data-room-moves]')+').textContent.includes("1. e4")')
    assert stats(a)['budget']['connections']==2 and stats(a)['rooms']['active']==4
    witnesses=[stats(a,ab),stats(a,ac)]
    assert all(w['localCandidateType']=='host' and w['remoteCandidateType']=='host' for w in witnesses)
    checks.append('two simultaneous accepted games use two pooled links and four hot lanes')
    # Invitations from independent links share one pending-room ceiling.
    from concurrent.futures import ThreadPoolExecutor
    with ThreadPoolExecutor(max_workers=2) as executor:
        futures=[executor.submit(click,b,prefix(wb)+'[data-room-create]'),executor.submit(click,c,prefix(wc)+'[data-room-create]')]
        for future in futures:future.result()
    wait(a,'return [...document.querySelector('+json.dumps(prefix(wa)+'[data-room-select]')+').options].filter(o=>o.textContent.endsWith("pending")).length===2')
    first_pending_b=wait(b,'return document.querySelector('+json.dumps(prefix(wb)+'[data-room-select]')+').value!=='+json.dumps(rab)+'&&document.querySelector('+json.dumps(prefix(wb)+'[data-room-select]')+').value')
    click(b,prefix(wb)+'[data-room-create]')
    wait(b,'return document.querySelector('+json.dumps(prefix(wb)+'[data-room-select]')+').value!=='+json.dumps(first_pending_b))
    wait(a,'return document.querySelector('+json.dumps(prefix(wa)+'[data-room-status]')+').textContent.includes("Pending invitation limit")')
    assert js(a,'return [...document.querySelector('+json.dumps(prefix(wa)+'[data-room-select]')+').options].filter(o=>o.textContent.endsWith("pending")).length===2')
    room_select(b,wb,rab);room_select(c,wc,rac)
    assert stats(a)['budget']['connections']==2
    checks.append('independent peers share a bounded pending-invitation ceiling')
    # Duplicate-session attempts are explicitly rejected; old links keep working.
    failure_window=launch(a,'chat')
    click(a,'[data-chat-action="offer"]');offer=wait(a,'return document.querySelector("[data-chat-out]").value')
    input_value(b,'[data-chat-in]',offer);click(b,'[data-chat-action="answer"]')
    wait(b,'return document.querySelector("[data-chat-status]").textContent.includes("already exists")')
    click(a,'[data-chat-action="cancel"]')
    end=time.monotonic()+5
    while stats(a)['budget']['connections']!=2:assert time.monotonic()<end;time.sleep(.1)
    room_send(a,wa,'move','Bb5');room_has(b,wb,'Bb5')
    checks.append('duplicate join rejected and pending cancellation preserves existing rooms')
    # Closing only C leaves AB active and its guest/key unchanged.
    close_window(a,wa2);select(a,prefix(failure_window)+'[data-chat-peer]',ac);click(a,prefix(failure_window)+'[data-chat-action="reset"]')
    assert stats(a)['budget']['connections']==1
    room_send(b,wb,'move','a6');room_has(a,wa,'a6')
    for s in sessions:assert js(s,'return v86Instance===poolVM&&desktopLab.session.id===poolSession')
    checks.append('disconnecting C preserves AB transport, game and guest identity')
    old_session=js(a,'return desktopLab.session');click(a,'.panel .account');js(a,'[...document.querySelectorAll(".status-popup button")].find(button=>button.textContent==="End session").click()')
    wait(a,'return window.desktopLab?.guestState==="ready"&&desktopLab.session.id!=='+json.dumps(old_session['id']))
    assert js(a,'return desktopLab.session.localKeyFingerprint')!=old_session['localKeyFingerprint']
    end=time.monotonic()+5
    while stats(b)['budget']['connections']!=0:assert time.monotonic()<end;time.sleep(.1)
    assert not stats(a)['peers'] and stats(a)['budget']['replayStreams']==0
    wait(b,'return document.querySelector('+json.dumps(prefix(wb)+'[data-room-status]')+').textContent.includes("closed")')
    checks.append('explicit End session closes pooled links and starts a fresh identity/guest')
    for s in sessions:
        js(s,'desktopNetwork.close()');end=time.monotonic()+5
        while True:
            snapshot=stats(s)['budget']
            if snapshot['closed'] and all(v==0 for k,v in snapshot.items() if k!='closed'):break
            assert time.monotonic()<end,snapshot;time.sleep(.1)
    checks.append('all three managers release every resource on disposal')
    result={'status':'PASS','url':args.url,'browsers':3,'checks':checks,'witnesses':witnesses,'wanTested':False,'defaultCertificateTrust':args.url.startswith('https://'),'actionTrace':action_trace,'sourceSHA256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    Path('.build/checks/'+('pool-connected-result.json' if ':8098/' in args.url else 'pool-result.json')).write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
except Exception as error:
    diagnostic={'status':'FAIL','url':args.url,'checks':checks,'actionTrace':action_trace,'error':str(error),'browsers':[],'sourceSHA256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    for s in sessions:
        try:diagnostic['browsers'].append({'session':s,'state':js(s,'return {guestState:desktopLab.guestState,lifecycle:desktopLab.lifecycle,chatStatus:[...document.querySelectorAll("[data-chat-status]")].map(n=>n.textContent),buttons:[...document.querySelectorAll("[data-chat-action]")].map(n=>({kind:n.dataset.chatAction,disabled:n.disabled})),incomingLengths:[...document.querySelectorAll("[data-chat-in]")].map(n=>n.value.length),outgoingLengths:[...document.querySelectorAll("[data-chat-out]")].map(n=>n.value.length)}'),'network':stats(s)})
        except Exception as failure:diagnostic['browsers'].append({'session':s,'inspectionError':str(failure)})
    Path('.build/checks/pool-failure-'+str(time.time_ns())+'.json').write_text(json.dumps(diagnostic,indent=2)+'\n');raise
finally:
    for s in sessions:req('/session/'+s,method='DELETE')
