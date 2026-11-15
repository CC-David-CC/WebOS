#!/usr/bin/env python3
"""Measure real public chat catch-up in one disposable browser without guest or speech."""
import importlib.util,json,os,re,secrets,shlex,subprocess,time,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];spec=importlib.util.spec_from_file_location('driver',ROOT/'scripts/touch-preview-check.py');d=importlib.util.module_from_spec(spec);spec.loader.exec_module(d)
origin='https://ksu.codes';channel=next(x['channel'] for x in json.load(urllib.request.urlopen('https://ksu.codes/official-directory?after=&limit=32',timeout=15))['items'] if x['label']=='General chess chat');name='profile'+secrets.token_hex(5);sid=None
with urllib.request.urlopen(origin+'/official-head?channel='+channel,timeout=15) as response:target=json.load(response)['height']
print('Disposable account:',name,'starting target height:',target,flush=True)
def js(code,args=[]):return d.call('/session/'+sid+'/execute/sync',{'script':code,'args':args})
try:
 sid=d.call('/session',{'capabilities':{'alwaysMatch':{'browserName':'chrome','goog:chromeOptions':{'binary':'/snap/chromium/current/usr/lib/chromium-browser/chrome','args':['--headless=new','--no-sandbox','--disable-dev-shm-usage']}}}})['sessionId']
 def cdp(cmd,params):return d.call('/session/'+sid+'/goog/cdp/execute',{'cmd':cmd,'params':params})
 cdp('Network.enable',{});
 mode=os.environ.get('CODI_PROFILE_MODE','full' if os.environ.get('CODI_PROFILE_FULL')=='1' else 'chat')
 assert mode in ('full','chat','guest','speech')
 blocked={'full':[],'chat':['*/.build/v86/*','*/assets/speech/*'],'guest':['*/assets/speech/*'],'speech':['*/.build/v86/*']}[mode]
 if blocked:cdp('Network.setBlockedURLs',{'urls':blocked})
 script='''(()=>{const p=window.catchupProfile={start:performance.now(),digest:{count:0,totalMs:0},archiveWrites:{count:0,totalMs:0},archiveReads:{count:0,totalMs:0},history:[],submissions:[],transactions:[]};const digest=SubtleCrypto.prototype.digest;SubtleCrypto.prototype.digest=function(...a){const start=performance.now();return digest.apply(this,a).finally(()=>{p.digest.count++;p.digest.totalMs+=performance.now()-start;});};const transaction=IDBDatabase.prototype.transaction;IDBDatabase.prototype.transaction=function(...a){const start=performance.now(),tx=transaction.apply(this,a),stack=p.userSendAt?(new Error()).stack.split('\\n').slice(1,5):null;if(this.name==='codi-device-channel-archive-v1'){const metric=a[1]==='readwrite'?p.archiveWrites:p.archiveReads;tx.addEventListener('complete',()=>{metric.count++;metric.totalMs+=performance.now()-start;if(p.userSendAt&&start>=p.userSendAt&&p.transactions.length<100)p.transactions.push({at:Math.round(start-p.userSendAt),ms:Math.round(performance.now()-start),mode:a[1]||'readonly',stack});});}return tx;};const fetch0=window.fetch.bind(window);window.fetch=async(...args)=>{const url=new URL(args[0] instanceof Request?args[0].url:String(args[0]),location.href),start=performance.now();let kind='other';if(url.pathname==='/official-ingest/use')try{const body=JSON.parse(args[1]?.body||'{}');kind=body.record?'message':body.receipt?'receipt':'other';}catch{}try{const r=await fetch0(...args);if(url.pathname.includes('official-ingest'))p.submissions.push({path:url.pathname,kind,status:r.status,start:Math.round(start),ms:Math.round(performance.now()-start)});if(url.pathname==='/official-history')p.history.push({status:r.status,ms:Math.round(performance.now()-start),at:Math.round(start-(p.opened||p.start)),height:url.searchParams.get('afterHeight')});return r;}catch(error){if(url.pathname==='/official-history')p.history.push({status:0,ms:Math.round(performance.now()-start),at:Math.round(start-(p.opened||p.start))});throw error;}};})();'''
 cdp('Page.addScriptToEvaluateOnNewDocument',{'source':script});d.call('/session/'+sid+'/url',{'url':origin+'/'});cdp('Browser.setPermission',{'permission':{'name':'persistent-storage'},'setting':'granted','origin':origin});d.wait(lambda:js('return !!document.querySelector(".login-gate");'),30);js('document.querySelector(".login-toggle").click();');js('''const set=(a,v)=>{const n=document.querySelector('.login-gate input[aria-label="'+a+'"]');n.value=v;n.dispatchEvent(new Event('input',{bubbles:true}));};set('Username',arguments[0]);set('Password','1!$?');set('Confirm password','1!$?');document.querySelector('.login-form').requestSubmit();''',[name]);d.wait(lambda:js('return !!currentSession&&!document.documentElement.classList.contains("login-required")&&surfaces.size>0;'),60)
 js('''localStorage.setItem('codi-device-history-consent-v1','accepted-v1');window.profileDesktop=[...surfaces.values()][0];window.profileChat=profileDesktop.launch('chat').id;window.catchupProfile.opened=performance.now();''')
 def snapshot():return js('''const n=document.querySelector('[data-window="'+profileChat+'"]'),t=n?.querySelector('.channel-conversation > details > p')?.textContent||'',m=t.match(/Accepted height (\\d+)/);return {height:m?Number(m[1]):null,text:n?.textContent?.slice(0,400)||''};''')
 def caught():
  value=snapshot()
  if 'Could not load this app' in value['text']:raise RuntimeError(value['text'])
  return value['height'] is not None and value['height']>=target
 d.wait(lambda:js("""const n=document.querySelector('[data-window=\"'+profileChat+'\"]');return !!n?.querySelector('.channel-composer button:not(:disabled)');"""),60)
 tag=secrets.token_hex(3);incoming='Phone check '+tag;reply='Server reply '+tag;ack='Got reply '+tag
 def has(text):return js("""const n=document.querySelector('[data-window=\"'+profileChat+'\"]');return [...(n?.querySelectorAll('.channel-message')||[])].some(x=>x.textContent.endsWith(': '+arguments[0]));""",[text])
 print(json.dumps({'ready':True,'incoming':incoming,'reply':reply,'ack':ack}),flush=True)
 d.wait(lambda:has(incoming),600);print('PASS phone message received',flush=True)
 started=time.monotonic();js("""const n=document.querySelector('[data-window=\"'+profileChat+'\"]'),a=n.querySelector('.channel-composer textarea');a.value=arguments[0];a.dispatchEvent(new Event('input',{bubbles:true}));n.querySelector('form').requestSubmit();""",[reply]);print('Reply submitted',flush=True)
 d.wait(lambda:has(ack) or has('See server reply '+tag),600);print('PASS phone confirmed reply; round trip seconds',round(time.monotonic()-started,1),flush=True)
finally:
 if sid:
  try:d.call('/session/'+sid,method='DELETE')
  except Exception:pass
 cleanup='''import re,sqlite3,sys\nname=sys.argv[1];assert re.fullmatch(r"profile[0-9a-f]{10}",name)\nd=sqlite3.connect("/var/lib/codi-connected/ksu/issuer/state/accounts.sqlite3",timeout=30);row=d.execute("SELECT subject FROM accounts WHERE username=?",(name,)).fetchone()\nif row:\n s=row[0];b=sqlite3.connect("/var/lib/codi-official/state/official.sqlite",timeout=30);b.execute("BEGIN IMMEDIATE");b.execute("DELETE FROM official_chat_names WHERE EXISTS (SELECT 1 FROM official_chat_actors a WHERE a.channel=official_chat_names.channel AND a.actor=official_chat_names.actor AND a.subject=?)",(s,))\n for table in ("official_upload_bans","official_chat_ban_epochs","official_chat_actor_reviews","official_chat_actors","official_chat_receipts"):b.execute("DELETE FROM "+table+" WHERE subject=?",(s,))\n b.commit();d.execute("BEGIN IMMEDIATE");d.execute("DELETE FROM account_policy WHERE subject=?",(s,));d.execute("DELETE FROM accounts WHERE username=? AND subject=?",(name,s));d.commit()\nprint("removed disposable profile account and metadata")'''
 try:print(subprocess.run(['ssh','-o','BatchMode=yes','box-webhost','sudo','-n','/usr/bin/python3','-B','-c',shlex.quote(cleanup),name],check=True,capture_output=True,text=True,timeout=30).stdout.strip(),flush=True)
 except Exception as error:print('Profile account cleanup failed:',error,'name:',name,flush=True)
