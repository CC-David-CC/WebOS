#!/usr/bin/env python3
"""Verify an offline queued message survives browser closure and later sign-in."""
import importlib.util,json,os,re,secrets,shlex,shutil,subprocess,tempfile,time,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];spec=importlib.util.spec_from_file_location('driver',ROOT/'scripts/touch-preview-check.py');d=importlib.util.module_from_spec(spec);spec.loader.exec_module(d)
tag=secrets.token_hex(6);name='scaletest'+secrets.token_hex(5);db='/var/lib/codi-official/state/official.sqlite';keys='/var/lib/codi-official/state/validator-keys';package='/srv/codi-connected/official-services/chess-rotation-r2';helper='/tmp/temporary-restart-test-channel-r1.py';created=False;sid=None;profile=Path(tempfile.mkdtemp(prefix='codi-pending-reopen-',dir=Path.home()/'snap/chromium/common'));message='Restart '+tag+' participant 1'
def remote(*args):return subprocess.run(['ssh','-o','BatchMode=yes','box-webhost',*args],capture_output=True,text=True,check=True,timeout=60).stdout.strip()
def control(action):return remote('sudo','-n','-u','codi-official','/srv/codi-connected/venvs/official-chess-r1/bin/python','-B',helper,action,tag,db,keys,package,'history-test')
def call(path,data=None,method=None):return d.call('/session/'+sid+path,data,method)
def js(code,args=[]):return call('/execute/sync',{'script':code,'args':args})
def start():
 global sid
 sid=d.call('/session',{'capabilities':{'alwaysMatch':{'browserName':'chrome','goog:chromeOptions':{'binary':'/snap/chromium/current/usr/lib/chromium-browser/chrome','args':['--headless=new','--no-sandbox','--disable-dev-shm-usage','--user-data-dir='+str(profile)]}}}})['sessionId'];call('/url',{'url':'https://ksu.codes/'});call('/goog/cdp/execute',{'cmd':'Browser.setPermission','params':{'permission':{'name':'persistent-storage'},'setting':'granted','origin':'https://ksu.codes'}})
def login(register):
 d.wait(lambda:js('return !!document.querySelector(".login-gate");'),45)
 if register:js('document.querySelector(".login-toggle").click();')
 js('''const set=(a,v)=>{const n=document.querySelector('.login-gate input[aria-label="'+a+'"]');n.value=v;n.dispatchEvent(new Event('input',{bubbles:true}));};set('Username',arguments[0]);set('Password','1!$?');if(arguments[1])set('Confirm password','1!$?');document.querySelector('.login-form').requestSubmit();''',[name,register]);d.wait(lambda:js('return !!currentSession&&!document.documentElement.classList.contains("login-required")&&surfaces.size>0;'),90)
def open_chat(label):
 js('localStorage.setItem("codi-device-history-consent-v1","accepted-v1");window.testDesktop=[...surfaces.values()][0];window.chatId=testDesktop.launch("chat").id;')
 d.wait(lambda:js('''const n=document.querySelector('[data-window="'+chatId+'"]');return [...(n?.querySelectorAll('.channel-list-item')||[])].some(x=>x.textContent===arguments[0]);''',[label]),90)
 js('''const n=document.querySelector('[data-window="'+chatId+'"]');[...n.querySelectorAll('.channel-list-item')].find(x=>x.textContent===arguments[0]).click();''',[label])
 d.wait(lambda:js('''const n=document.querySelector('[data-window="'+chatId+'"]');return n?.querySelector('.channel-title')?.textContent===arguments[0]&&!!n?.querySelector('.channel-composer button:not(:disabled)');''',[label]),90)
try:
 value=json.loads(control('create'));created=True;label=value['label'];print('Created isolated test channel',flush=True)
 start();login(True);open_chat(label)
 js("""window.testLostReply={attempts:0,drops:0,blocked:0,block:true,channel:arguments[0]};window.testOriginalFetch=window.fetch.bind(window);window.fetch=async(...args)=>{const u=new URL(args[0] instanceof Request?args[0].url:String(args[0]),location.href);if(u.pathname==='/official-history'&&u.searchParams.get('channel')===testLostReply.channel&&testLostReply.drops&&testLostReply.block){testLostReply.blocked++;return new Response('{}',{status:503,headers:{'content-type':'application/json'}});}let message=false;if(u.pathname==='/official-ingest/use')try{message=!!JSON.parse(args[1]?.body||'{}').record;}catch{}if(message)testLostReply.attempts++;const response=await testOriginalFetch(...args);if(message&&response.ok&&!testLostReply.drops){testLostReply.drops++;throw new TypeError('Simulated lost server response');}return response;};""",[value['channel']])
 js("""const n=document.querySelector('[data-window="'+chatId+'"]'),t=n.querySelector('textarea');t.value=arguments[0];t.dispatchEvent(new Event('input',{bubbles:true}));n.querySelector('form').requestSubmit();""",[message])
 d.wait(lambda:js('return testLostReply.drops===1;'),90);print('PASS server answered an accepted message request but browser response was dropped',flush=True)
 def accepted():return js("""const n=document.querySelector('[data-window="'+chatId+'"]'),lines=[...(n?.querySelectorAll('.channel-history .channel-message')||[])].filter(x=>x.textContent.endsWith(': '+arguments[0]));return lines.length===1&&!lines[0].classList.contains('is-pending')&&['sent','delivered'].includes(lines[0].dataset.delivery);""",[message])
 d.wait(lambda:js('return testLostReply.blocked>0;'),30);d.wait(lambda:js('return testLostReply.attempts>=2;'),60);print('PASS browser retried while saved history was unavailable',flush=True);js('testLostReply.block=false;window.dispatchEvent(new Event("online"));');started=time.monotonic();d.wait(accepted,120);elapsed=round(time.monotonic()-started,2);time.sleep(3)
 with urllib.request.urlopen('https://ksu.codes/official-head?channel='+value['channel'],timeout=15) as response:head=json.load(response)
 assert head['height']==1,head
 stats=js('return testLostReply;');assert stats['drops']==1
 print('PASS browser recovered one accepted message in',elapsed,'seconds; server history height 1; message requests:',stats['attempts'],flush=True)
finally:
 if sid:
  try:call('',method='DELETE')
  except Exception as error:print('Browser cleanup failed:',error,flush=True)
 safe=True
 if created:
  try:print(control('remove'),flush=True)
  except Exception as error:safe=False;print('Temporary channel preserved:',error,flush=True)
 if safe:
  cleanup='''import re,sqlite3,sys\nname=sys.argv[1];assert re.fullmatch(r"scaletest[0-9a-f]{10}",name)\na=sqlite3.connect("/var/lib/codi-connected/ksu/issuer/state/accounts.sqlite3",timeout=30);row=a.execute("SELECT subject FROM accounts WHERE username=?",(name,)).fetchone()\nif row:\n s=row[0];b=sqlite3.connect("/var/lib/codi-official/state/official.sqlite",timeout=30);b.execute("BEGIN IMMEDIATE");b.execute("DELETE FROM official_chat_names WHERE EXISTS (SELECT 1 FROM official_chat_actors a WHERE a.channel=official_chat_names.channel AND a.actor=official_chat_names.actor AND a.subject=?)",(s,))\n for t in ("official_upload_bans","official_chat_ban_epochs","official_chat_actor_reviews","official_chat_actors","official_chat_receipts"):b.execute("DELETE FROM "+t+" WHERE subject=?",(s,))\n b.commit();a.execute("BEGIN IMMEDIATE");a.execute("DELETE FROM registered_sessions WHERE json_extract(record, '$.sub')=?",(s,));a.execute("DELETE FROM account_policy WHERE subject=?",(s,));a.execute("DELETE FROM accounts WHERE username=? AND subject=?",(name,s));a.commit()\nprint("removed disposable account and metadata")'''
  try:print(remote('sudo','-n','/usr/bin/python3','-B','-c',shlex.quote(cleanup),name),flush=True)
  except Exception as error:print('Account cleanup failed:',name,error,flush=True)
 if profile.exists() and profile.name.startswith('codi-pending-reopen-'):shutil.rmtree(profile)
