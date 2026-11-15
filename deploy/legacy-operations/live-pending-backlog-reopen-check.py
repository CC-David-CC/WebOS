#!/usr/bin/env python3
"""Verify an offline queued message survives browser closure and later sign-in."""
import importlib.util,json,os,re,secrets,shlex,shutil,subprocess,tempfile,time,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];spec=importlib.util.spec_from_file_location('driver',ROOT/'scripts/touch-preview-check.py');d=importlib.util.module_from_spec(spec);spec.loader.exec_module(d)
tag=secrets.token_hex(6);name='scaletest'+secrets.token_hex(5);db='/var/lib/codi-official/state/official.sqlite';keys='/var/lib/codi-official/state/validator-keys';package='/srv/codi-connected/official-services/chess-rotation-r2';helper='/tmp/temporary-restart-test-channel-r1.py';created=False;sid=None;profile=Path(tempfile.mkdtemp(prefix='codi-pending-reopen-',dir=Path.home()/'snap/chromium/common'));messages=['Restart '+tag+' participant '+str(i) for i in range(1,11)]
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
 call('/goog/cdp/execute',{'cmd':'Network.enable','params':{}});call('/goog/cdp/execute',{'cmd':'Network.emulateNetworkConditions','params':{'offline':True,'latency':0,'downloadThroughput':0,'uploadThroughput':0}})
 for message in messages:
  js("""const n=document.querySelector('[data-window="'+chatId+'"]'),t=n.querySelector('textarea');t.value=arguments[0];t.dispatchEvent(new Event('input',{bubbles:true}));n.querySelector('form').requestSubmit();""",[message])
  d.wait(lambda:js("""const n=document.querySelector('[data-window="'+chatId+'"]');return [...(n?.querySelectorAll('.is-pending')||[])].some(x=>x.textContent.includes(arguments[0]))&&n.querySelector('textarea').value==='';""",[message]),45)
 print('PASS ten offline messages queued and shown pending before browser close',flush=True)
 call('',method='DELETE');sid=None
 start();login(False);open_chat(label);start_time=time.monotonic()
 def accepted():return js("""const n=document.querySelector('[data-window="'+chatId+'"]'),lines=[...(n?.querySelectorAll('.channel-history .channel-message')||[])],messages=arguments[0],found=lines.filter(x=>messages.some(m=>x.textContent.endsWith(': '+m)));return found.length===messages.length&&messages.every((m,i)=>found[i].textContent.endsWith(': '+m)&&!found[i].classList.contains('is-pending')&&['sent','delivered'].includes(found[i].dataset.delivery));""",[messages])
 d.wait(accepted,120);elapsed=round(time.monotonic()-start_time,2)
 with urllib.request.urlopen('https://ksu.codes/official-head?channel='+value['channel'],timeout=15) as response:head=json.load(response)
 assert head['height']==len(messages),head
 print('PASS reopened profile; server accepted ten queued messages once in order in',elapsed,'seconds after opening chat; server history height',head['height'],flush=True)
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
