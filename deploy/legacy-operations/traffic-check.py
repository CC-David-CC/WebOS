#!/usr/bin/env python3
"""Actual RTC contention fixture; no product bulk-transfer feature is claimed."""
import argparse,json,time,urllib.request
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--url',default='http://127.0.0.1:8097/');args=p.parse_args()
BASE='http://127.0.0.1:19515';sessions=[]
def req(path,data=None,method=None):
    r=urllib.request.Request(BASE+path,data=None if data is None else json.dumps(data).encode(),headers={'Content-Type':'application/json'},method=method)
    with urllib.request.urlopen(r,timeout=90) as response:return json.load(response)['value']
def js(s,code):return req('/session/'+s+'/execute/sync',{'script':code,'args':[]})
def run(s,code):
    result=req('/session/'+s+'/execute/async',{'script':'const done=arguments[0];(async()=>{'+code+'})().then(value=>done({value})).catch(e=>done({error:e.message}));','args':[]});assert 'error' not in result,result;return result['value']
def wait(s,code):
    end=time.monotonic()+60
    while time.monotonic()<end:
        value=js(s,code)
        if value:return value
        time.sleep(.1)
    raise AssertionError('Timeout: '+code)
try:
    for _ in range(2):
        s=req('/session',{'capabilities':{'alwaysMatch':{'browserName':'chrome','goog:chromeOptions':{'binary':'/snap/chromium/current/usr/lib/chromium-browser/chrome','args':['--headless=new','--no-sandbox','--disable-dev-shm-usage']}}}})['sessionId'];sessions.append(s)
        req('/session/'+s+'/url',{'url':args.url});wait(s,'return !!window.desktopLab?.session?.localKeyFingerprint')
        run(s,"const {PeerLink}=await import('./network/peer.mjs');window.timeline=[];window.probe=new PeerLink(currentSession,identityConfig,{onMessage:m=>timeline.push({kind:m.text.startsWith('bulk-')?'bulk':'interactive',sequence:m.sequence,at:performance.now()}),onApplication:(a,ctx)=>timeline.push({kind:'control',sequence:ctx.sequence,at:performance.now()})});")
    left,right=sessions
    offer=run(left,'return await probe.offer();');answer=run(right,'return await probe.answer('+json.dumps(offer)+');');run(left,'await probe.acceptAnswer('+json.dumps(answer)+');')
    for s in sessions:wait(s,'return probe.applicationReady')
    run(left,"window.bulkTasks=Array.from({length:24},(_,i)=>probe.sendPacket('chat','bulk-'+i+':'+ 'x'.repeat(8000),'bulk'));const interactive=Array.from({length:4},(_,i)=>probe.send('chat-'+i));const control=probe.sendApplication('control',{operation:'priority-fixture'});window.allSends=Promise.allSettled([...bulkTasks,...interactive,control]);")
    attempt=run(left,"const results=await allSends;const buffered=probe.channel.bufferedAmount;await probe.sendApplication('control',{operation:'while-backpressured'});window.retries=results.slice(0,24).map((r,i)=>r.status==='rejected'?i:null).filter(i=>i!==null);return {results:results.map(r=>({status:r.status,error:r.reason?.message})),buffered};")
    sent=attempt['results'];assert all(r['status']=='fulfilled' or (i<24 and r['error'].startswith('Peer send buffer is full')) for i,r in enumerate(sent)),sent
    wait(left,'return probe.channel?.bufferedAmount===0&&probe.status==="ready"')
    retried=run(left,"for(const i of retries)await probe.sendPacket('chat','bulk-'+i+':'+ 'x'.repeat(8000),'bulk');return retries.length;")
    timeline=wait(right,'return timeline.length===30&&timeline')
    assert [e['sequence'] for e in timeline]==list(range(2,32)),timeline
    control_index=next(i for i,e in enumerate(timeline) if e['kind']=='control');bulk_before=sum(e['kind']=='bulk' for e in timeline[:control_index])
    assert control_index<=5 and bulk_before<=1 and any(e['kind']=='interactive' for e in timeline[:next(i for i in range(len(timeline)-1,-1,-1) if timeline[i]['kind']=='bulk')]),timeline
    witness=run(left,'return await probe.stats();');assert witness['tx']==31 and witness['scheduler']['completed']['bulk']==24 and witness['scheduler']['completed']['interactive']==4,witness
    canceled=run(left,"const tasks=Array.from({length:24},()=>probe.sendPacket('chat','cancel queued','bulk'));probe.close();const results=await Promise.allSettled(tasks);return results.filter(r=>r.status==='rejected').length;");assert canceled==24,canceled
    wait(right,"return probe.closed");assert js(right,'return timeline.length')==30
    for s in sessions:
        run(s,'probe.close();desktopNetwork.close();');end=time.monotonic()+5
        while True:
            budget=run(s,'return (await desktopNetwork.stats()).budget;')
            if budget['closed'] and all(v==0 for k,v in budget.items() if k!='closed'):break
            assert time.monotonic()<end,budget;time.sleep(.1)
    result={'status':'PASS','url':args.url,'fixture':'24 signed ~8 KB bulk-class chat packets, four interactive chats, two control packets on one ordered RTC link, with explicit retry after backpressure','controlIndex':control_index,'bulkBeforeControl':bulk_before,'deliverySpanMs':timeline[-1]['at']-timeline[0]['at'],'backpressureRejected':retried,'bufferedBeforeSecondControl':attempt['buffered'],'all30Delivered':True,'strictSequencePreserved':True,'queuedCancellationRejected':canceled,'disposalZero':True,'witness':witness,'wanTested':False}
    Path('.build/checks/'+('traffic-connected-result.json' if ':8098/' in args.url else 'traffic-result.json')).write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
finally:
    for s in sessions:req('/session/'+s,method='DELETE')
