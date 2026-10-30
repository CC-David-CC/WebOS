#!/usr/bin/env python3
"""Test a signed moderation marker in an owned, disposable live channel."""
import importlib.util,json,secrets,shlex,subprocess,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];spec=importlib.util.spec_from_file_location('driver',ROOT/'scripts/touch-preview-check.py');d=importlib.util.module_from_spec(spec);spec.loader.exec_module(d)
tag=secrets.token_hex(6);name='spamtest'+secrets.token_hex(5);sid=None;second=None;created=False
db='/var/lib/codi-official/state/official.sqlite';keys='/var/lib/codi-official/state/validator-keys';package='/srv/codi-connected/official-services/chess-rotation-r2';python='/srv/codi-connected/venvs/official-chess-r1/bin/python';helper='/tmp/temporary-history-test-channel-r1.py'
def remote(*args):return subprocess.run(['ssh','-o','BatchMode=yes','box-webhost',*args],capture_output=True,text=True,check=True,timeout=60).stdout.strip()
def channel_control(action):return remote('sudo','-n','-u','codi-official',python,'-B',helper,action,tag,db,keys,package,'history-test')
def moderate(channel,*args):return json.loads(remote('sudo','-n','-u','codi-official',python,'-I','-B','/srv/codi-connected/official-services/chat-ban-review-r3/scripts/official-mark-spam.py','--database',db,'--validator-key-dir',keys,'--channel',channel,*args))
def js(code,args=[]):return d.call('/session/'+sid+'/execute/sync',{'script':code,'args':args})
try:
 result=json.loads(channel_control('create'));created=True;channel=result['channel'];label=result['label'];text='History '+tag+' #';print('Created isolated channel',flush=True)
 sid=d.call('/session',{'capabilities':{'alwaysMatch':{'browserName':'chrome','goog:chromeOptions':{'binary':'/snap/chromium/current/usr/lib/chromium-browser/chrome','args':['--headless=new','--no-sandbox','--disable-dev-shm-usage']}}}})['sessionId']
 d.call('/session/'+sid+'/url',{'url':'https://ksu.codes/'});d.call('/session/'+sid+'/goog/cdp/execute',{'cmd':'Browser.setPermission','params':{'permission':{'name':'persistent-storage'},'setting':'granted','origin':'https://ksu.codes'}})
 d.wait(lambda:js('return !!document.querySelector(".login-gate");'),30);js('document.querySelector(".login-toggle").click();');js('''const set=(a,v)=>{const n=document.querySelector('.login-gate input[aria-label="'+a+'"]');n.value=v;n.dispatchEvent(new Event('input',{bubbles:true}));};set('Username',arguments[0]);set('Password','1!$?');set('Confirm password','1!$?');document.querySelector('.login-form').requestSubmit();''',[name]);d.wait(lambda:js('return !!currentSession&&!document.documentElement.classList.contains("login-required")&&surfaces.size>0;'),60)
 js('localStorage.setItem("codi-device-history-consent-v1","accepted-v1");')
 d.call('/session/'+sid+'/timeouts',{'script':110000})
 writer=d.call('/session/'+sid+'/execute/async',{'script':"""const params=Array.from(arguments),done=params.pop();(async()=>{
 const [channel,prefix]=params,config=identityConfig,session=currentSession,graph=await(await fetch('/assets/desktop/network-release.json')).json(),registry=await(await fetch('/assets/desktop/shared-services.json')).json(),path=registry.services.find(x=>x.name==='device-history').path;
 const {DeviceHistoryHost}=await import('/'+path),{PeerPool}=await import('/'+graph.directory+'/peer-pool.mjs'),history=new DeviceHistoryHost(),permit=await history.permit(),pool=new PeerPool(session,config),life=new AbortController();let owner,view;
 try{owner=await history.bindChannelSession({session,issuer:config.identity.issuer,pool,currentSession:()=>currentSession,signal:life.signal,permit,limits:{identityPolicy:config.identity,automaticRounds:true,automaticPeers:false,trafficLimits:false,officialDiscovery:true}});view=owner.attach({signal:life.signal});await view.officialDirectory({limit:32});const group=(await view.joinOfficialChannel(channel)).channel,start=performance.now();for(let i=0;i<64;i++)await group.queue('chat',{text:prefix+i});const queued=performance.now(),end=performance.now()+85000;while(performance.now()<end){const snap=await group.snapshot();if(snap.state.messages.length===64&&!snap.pending.length)return {queueMs:Math.round(queued-start),totalMs:Math.round(performance.now()-start),height:snap.height};await new Promise(r=>setTimeout(r,200));}throw Error('Writer acceptance timed out');}
 finally{view?.close();owner?.close();if(owner)await owner.idle();pool.close();history.close();life.abort();}
 })().then(value=>done({ok:true,value}),error=>done({ok:false,error:error.stack||String(error)}));""",'args':[channel,text]});assert writer['ok'],writer;print('Writer accepted 64 messages',json.dumps(writer['value']),flush=True)
 second=d.call('/session',{'capabilities':{'alwaysMatch':{'browserName':'chrome','goog:chromeOptions':{'binary':'/snap/chromium/current/usr/lib/chromium-browser/chrome','args':['--headless=new','--no-sandbox','--disable-dev-shm-usage']}}}})['sessionId']
 def js2(code,args=[]):return d.call('/session/'+second+'/execute/sync',{'script':code,'args':args})
 d.call('/session/'+second+'/url',{'url':'https://ksu.codes/'});d.call('/session/'+second+'/goog/cdp/execute',{'cmd':'Browser.setPermission','params':{'permission':{'name':'persistent-storage'},'setting':'granted','origin':'https://ksu.codes'}})
 d.wait(lambda:js2('return !!document.querySelector(".login-gate");'),30);js2('''const set=(a,v)=>{const n=document.querySelector('.login-gate input[aria-label="'+a+'"]');n.value=v;n.dispatchEvent(new Event('input',{bubbles:true}));};set('Username',arguments[0]);set('Password','1!$?');document.querySelector('.login-form').requestSubmit();''',[name]);d.wait(lambda:js2('return !!currentSession&&!document.documentElement.classList.contains("login-required")&&surfaces.size>0;'),60)
 js2('localStorage.setItem("codi-device-history-consent-v1","accepted-v1");window.testDesktop=[...surfaces.values()][0];window.chatId=testDesktop.launch("chat").id;')
 d.wait(lambda:js2('''const n=document.querySelector('[data-window="'+chatId+'"]');return !!n?.querySelector('.channel-composer button:not(:disabled)');'''),90)
 d.wait(lambda:js2('''const n=document.querySelector('[data-window="'+chatId+'"]');return [...(n?.querySelectorAll('.channel-list-item')||[])].some(x=>x.textContent===arguments[0]);''',[label]),90)
 start=time.monotonic();js2('''const n=document.querySelector('[data-window="'+chatId+'"]');[...n.querySelectorAll('.channel-list-item')].find(x=>x.textContent===arguments[0]).click();''',[label])
 d.wait(lambda:js2('''const n=document.querySelector('[data-window="'+chatId+'"]'),lines=[...(n?.querySelectorAll('.channel-history .channel-message')||[])];return n?.querySelector('.channel-title')?.textContent===arguments[0]&&lines.length===64&&[...Array(64).keys()].every(i=>lines.some(x=>x.textContent.endsWith(arguments[1]+i)));''',[label,text]),120)
 print('PASS fresh browser recovered all 64 messages in',round(time.monotonic()-start,2),'seconds',flush=True)

finally:
 if second:
  try:d.call('/session/'+second,method='DELETE')
  except Exception:pass
 if sid:
  try:d.call('/session/'+sid,method='DELETE')
  except Exception:pass
 cleanup_safe=True
 if created:
  try:print(channel_control('remove'),flush=True)
  except Exception as error:cleanup_safe=False;print('Test channel and account preserved for inspection:',error,flush=True)
 cleanup='''import re,sqlite3,sys\nname=sys.argv[1];assert re.fullmatch(r"spamtest[0-9a-f]{10}",name)\na=sqlite3.connect("/var/lib/codi-connected/ksu/issuer/state/accounts.sqlite3",timeout=30);row=a.execute("SELECT subject FROM accounts WHERE username=?",(name,)).fetchone()\nif row:\n subject=row[0];b=sqlite3.connect("/var/lib/codi-official/state/official.sqlite",timeout=30);b.execute("BEGIN IMMEDIATE");b.execute("DELETE FROM official_chat_names WHERE EXISTS (SELECT 1 FROM official_chat_actors a WHERE a.channel=official_chat_names.channel AND a.actor=official_chat_names.actor AND a.subject=?)",(subject,))\n for table in ("official_upload_bans","official_chat_ban_epochs","official_chat_actor_reviews","official_chat_actors","official_chat_receipts"):b.execute("DELETE FROM "+table+" WHERE subject=?",(subject,))\n b.commit();a.execute("BEGIN IMMEDIATE");a.execute("DELETE FROM registered_sessions WHERE json_extract(record, '$.sub')=?",(subject,));a.execute("DELETE FROM account_policy WHERE subject=?",(subject,));a.execute("DELETE FROM accounts WHERE username=? AND subject=?",(name,subject));a.commit()\nprint("removed disposable account and metadata")'''
 if cleanup_safe:
  try:print(remote('sudo','-n','/usr/bin/python3','-B','-c',shlex.quote(cleanup),name),flush=True)
  except Exception as error:print('Account cleanup failed:',name,error,flush=True)
