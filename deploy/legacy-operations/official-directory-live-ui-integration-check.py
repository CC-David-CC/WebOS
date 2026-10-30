#!/usr/bin/env python3
"""Temporary anonymous official channel: real live UI, upload and server recovery."""
import argparse,hashlib,importlib.util,json,re,shlex,shutil,subprocess,tempfile,time,traceback,uuid
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];spec=importlib.util.spec_from_file_location('driver',ROOT/'scripts/touch-preview-check.py');d=importlib.util.module_from_spec(spec);spec.loader.exec_module(d)
p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);args=p.parse_args();assert not args.output.exists();profiles={};sessions={};channel=None;label='Temporary official UI '+uuid.uuid4().hex[:12];checks=[];r={'status':'FAIL','scope':__doc__,'checks':checks,'label':label,'serverAccountsCreated':0}
def js(side,code,args=[]):return d.call('/session/'+sessions[side]+'/execute/sync',{'script':code,'args':args})
def task(side,code,args=[]):
 v=d.call('/session/'+sessions[side]+'/execute/async',{'script':'const params=Array.from(arguments),done=params.pop();(async()=>{'+code+'})().then(value=>done({ok:true,value}),error=>done({ok:false,error:error.stack||String(error)}));','args':args});assert v['ok'],v;return v['value']
def wait(side,code,args=[],seconds=90):return d.wait(lambda:js(side,code,args),seconds)
def check(name,ok):assert ok,name;checks.append(name);print(json.dumps({'check':name}),flush=True)
def start(side):
 if side not in profiles:profiles[side]=Path(tempfile.mkdtemp(prefix='codi-official-ui-live-',dir=Path.home()/'snap/chromium/common'))
 v=d.call('/session',{'capabilities':{'alwaysMatch':{'browserName':'chrome','goog:chromeOptions':{'binary':'/snap/chromium/current/usr/lib/chromium-browser/chrome','args':['--headless=new','--no-sandbox','--disable-dev-shm-usage','--user-data-dir='+str(profiles[side])]}}}});sessions[side]=v['sessionId'];d.call('/session/'+sessions[side]+'/timeouts',{'script':180000});d.call('/session/'+sessions[side]+'/url',{'url':'https://ksu.codes/'});d.call('/session/'+sessions[side]+'/goog/cdp/execute',{'cmd':'Browser.setPermission','params':{'permission':{'name':'persistent-storage'},'setting':'granted','origin':'https://ksu.codes'}})
try:
 start('writer')
 value=task('writer','''const graph=await(await fetch('/assets/desktop/network-release.json')).json(),base='/'+graph.directory+'/',config=await(await fetch('/config.json')).json(),registry=await(await fetch('/assets/desktop/shared-services.json')).json(),sdk='/'+registry.services.find(x=>x.name==='device-history').path;const {beginSession}=await import(base+'identity.mjs'),{PeerPool}=await import(base+'peer-pool.mjs'),{DeviceHistoryHost}=await import(sdk);const priorFetch=window.fetch.bind(window);window.initialOfficialMiss=0;window.fetch=async(...args)=>{const response=await priorFetch(...args);if(new URL(args[0],location.href).pathname==='/official-channel'&&response.status===404)window.initialOfficialMiss++;return response;};const session=await beginSession(config,'anonymous');localStorage.setItem('codi-device-history-consent-v1','accepted-v1');const history=new DeviceHistoryHost(),permit=await history.permit(),pool=new PeerPool(session,config),life=new AbortController(),owner=await history.bindChannelSession({session,issuer:config.identity.issuer,pool,currentSession:()=>session,signal:life.signal,permit,limits:{identityPolicy:config.identity,automaticRounds:true,automaticPeers:false,trafficLimits:false,officialDiscovery:true}}),view=owner.attach({signal:life.signal}),group=await view.createChannel({label:params[0],publicRead:true,publicWrite:true});for(let i=0;i<3;i++)await group.queue('chat',{text:'Official UI test message '+i});const until=performance.now()+60000;while((await group.snapshot()).state.messages.length<3&&performance.now()<until)await new Promise(r=>setTimeout(r,150));const snap=await group.snapshot();if(snap.state.messages.length!==3)throw Error('Messages not accepted');window.fixtureWriter={session,pool,life,history,owner,view,group};return {channel:group.channel,head:snap.head,listing:await view.createPublicListing(group.channel)};''',[label]);channel=value['channel'];assert re.fullmatch('[A-Za-z0-9_-]{43}',channel);r['channel']=channel
 wait('writer','return window.initialOfficialMiss>0;',seconds=20)
 with tempfile.NamedTemporaryFile(mode='w') as f:
  f.write(value['listing']);f.flush();Path(f.name).chmod(0o644);remote='/tmp/codi-official-ui-listing-'+channel;subprocess.run(['scp','-q',f.name,'box-webhost:'+remote],check=True)
  try:subprocess.run(['ssh','-o','BatchMode=yes','box-webhost','sudo','-n','runuser','-u','codi-official','--','/srv/codi-connected/venvs/517179c/bin/python','-I','-B','/srv/codi-connected/official-service-test/scripts/official-admin.py','--state','/var/lib/codi-official/state','enroll',remote],check=True,capture_output=True,text=True)
  finally:subprocess.run(['ssh','-o','BatchMode=yes','box-webhost','rm','-f','--',remote],check=True)
 enrolledAt=time.monotonic();check('temporary anonymous channel enrolled on official server',True)
 task('writer','''const end=performance.now()+120000;while(performance.now()<end){const r=await fetch('/official-head?channel='+encodeURIComponent(params[0]));if(r.ok&&(await r.json()).head===params[1])return true;await new Promise(r=>setTimeout(r,300));}throw Error('Server did not publish expected head');''',[channel,value['head']]);r['publicationDelaySeconds']=round(time.monotonic()-enrolledAt,3);check('server saved the signed channel history',True)
 d.call('/session/'+sessions.pop('writer'),method='DELETE');check('writer browser is closed before reader joins',True)
 start('reader');wait('reader','return !!window.desktopLab?.session&&desktopLab.surfaces.size>0;',seconds=90)
 js('reader','window.officialHistoryCalls=[];const original=window.fetch.bind(window);window.fetch=(u,o)=>{const p=original(u,o),url=new URL(u,location.href);if(url.pathname==="/official-history")p.then(v=>officialHistoryCalls.push(v.status),()=>officialHistoryCalls.push(0));return p;};')
 wid=js('reader','return [...desktopLab.surfaces.values()][0].launch("chat").id;');sel='[data-window="'+str(wid)+'"]';wait('reader','return !!document.querySelector(arguments[0])?.querySelector(".storage-consent button:not(:disabled),[data-device-channels]");',[sel],90)
 if not js('reader','return !!document.querySelector(arguments[0])?.querySelector("[data-device-channels]");',[sel]):
  el=d.call('/session/'+sessions['reader']+'/element',{'using':'css selector','value':sel+' .storage-consent button:not(:disabled)'})['element-6066-11e4-a52e-4f735466cecf'];d.call('/session/'+sessions['reader']+'/element/'+el+'/click',{})
 wait('reader','return !!document.querySelector(arguments[0])?.querySelector("[data-channel-results]");',[sel],90)
 js('reader','const n=document.querySelector(arguments[0]).querySelector("input[type=search]");n.value=arguments[1];n.dispatchEvent(new Event("input",{bubbles:true}));',[sel,label]);wait('reader','return document.querySelector(arguments[0]).querySelector("[data-channel-results]").textContent.includes(arguments[1]);',[sel,label],90)
 check('actual Chat shows the official channel with a server-backed label',js('reader','const n=document.querySelector(arguments[0]).querySelector("[data-channel-results]");return n.textContent.includes(arguments[1])&&n.textContent.includes("Official · server-backed");',[sel,label]))
 js('reader','const root=document.querySelector(arguments[0]).querySelector("[data-channel-results]");[...root.children].find(x=>x.textContent.includes(arguments[1])).querySelector("button").click();',[sel,label]);wait('reader','const n=document.querySelector(arguments[0]).querySelector("[data-device-history]");return n&&[0,1,2].every(i=>n.textContent.includes("Official UI test message "+i));',[sel],120)
 check('actual Chat joins and restores all messages from server fallback',js('reader','return window.officialHistoryCalls.includes(200);'))
 d.call('/session/'+sessions.pop('reader'),method='DELETE');start('reader');wait('reader','return !!window.desktopLab?.session&&desktopLab.surfaces.size>0;',seconds=90)
 wid=js('reader','return [...desktopLab.surfaces.values()][0].launch("chat").id;');sel='[data-window="'+str(wid)+'"]';wait('reader','return !!document.querySelector(arguments[0])?.querySelector(".storage-consent button:not(:disabled),[data-device-channels]");',[sel],90)
 if not js('reader','return !!document.querySelector(arguments[0])?.querySelector("[data-device-channels]");',[sel]):
  el=d.call('/session/'+sessions['reader']+'/element',{'using':'css selector','value':sel+' .storage-consent button:not(:disabled)'})['element-6066-11e4-a52e-4f735466cecf'];d.call('/session/'+sessions['reader']+'/element/'+el+'/click',{})
 wait('reader','const n=document.querySelector(arguments[0]).querySelector("[data-device-history]");return n&&[0,1,2].every(i=>n.textContent.includes("Official UI test message "+i));',[sel],120)
 check('reader reopens the saved channel and retains its messages',True)
 r['status']='PASS'
except Exception as e:
 r.update(error=str(e),traceback=traceback.format_exc())
 for side in sessions:
  try:r[side+'Diagnostic']=js(side,'return document.body.innerText.slice(-8000);')
  except Exception:pass
finally:
 for side,sid in sessions.items():
  try:d.call('/session/'+sid,method='DELETE')
  except Exception as e:r['status']='FAIL';r[side+'CleanupError']=str(e)
 for profile in profiles.values():shutil.rmtree(profile,ignore_errors=True)
 r['profilesRemoved']=all(not p.exists() for p in profiles.values())
 if channel:
  code='''import sqlite3,sys\nc,label=sys.argv[1:];db=sqlite3.connect("/var/lib/codi-official/state/official.sqlite",timeout=30);db.execute("PRAGMA foreign_keys=ON");db.execute("BEGIN IMMEDIATE");row=db.execute("SELECT label FROM official_channels WHERE channel=?",(c,)).fetchone();assert row is None or row[0]==label\nif row:\n for table in ("official_replayed_locators","official_replayed_blocks","official_staged_nodes"):db.execute("DELETE FROM "+table+" WHERE channel=?",(c,))\n db.execute("DELETE FROM official_upload_bans WHERE scope=?",(c,));db.execute("DELETE FROM official_channels WHERE channel=?",(c,))\ndb.commit();print("clean")'''
  try:r['serverCleanup']=subprocess.check_output(['ssh','-o','BatchMode=yes','box-webhost','sudo','-n','runuser','-u','codi-official','--','/srv/codi-connected/venvs/517179c/bin/python','-I','-B','-c',shlex.quote(code),channel,shlex.quote(label)],text=True,timeout=40).strip();assert r['serverCleanup']=='clean'
  except Exception as e:r['status']='FAIL';r['serverCleanupError']=str(e)
args.output.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({'status':r['status'],'checks':len(checks),'error':r.get('error'),'cleanup':r.get('serverCleanup')}));raise SystemExit(r['status']!='PASS')
