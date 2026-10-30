#!/usr/bin/env python3
"""Test a signed moderation marker in an owned, disposable live channel."""
import importlib.util,json,secrets,shlex,subprocess,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];spec=importlib.util.spec_from_file_location('driver',ROOT/'scripts/touch-preview-check.py');d=importlib.util.module_from_spec(spec);spec.loader.exec_module(d)
tag=secrets.token_hex(6);name='spamtest'+secrets.token_hex(5);sid=None;created=False
db='/var/lib/codi-official/state/official.sqlite';keys='/var/lib/codi-official/state/validator-keys';package='/srv/codi-connected/official-services/chess-rotation-r2';python='/srv/codi-connected/venvs/official-chess-r1/bin/python';helper='/tmp/temporary-spam-test-channel-r1.py'
def remote(*args):return subprocess.run(['ssh','-o','BatchMode=yes','box-webhost',*args],capture_output=True,text=True,check=True,timeout=60).stdout.strip()
def channel_control(action):return remote('sudo','-n','-u','codi-official',python,'-B',helper,action,tag,db,keys,package,'spam-test')
def moderate(channel,*args):return json.loads(remote('sudo','-n','-u','codi-official',python,'-I','-B','/srv/codi-connected/official-services/chat-ban-review-r3/scripts/official-mark-spam.py','--database',db,'--validator-key-dir',keys,'--channel',channel,*args))
def js(code,args=[]):return d.call('/session/'+sid+'/execute/sync',{'script':code,'args':args})
try:
 result=json.loads(channel_control('create'));created=True;channel=result['channel'];label=result['label'];text='Spam check '+tag;print('Created isolated channel',flush=True)
 sid=d.call('/session',{'capabilities':{'alwaysMatch':{'browserName':'chrome','goog:chromeOptions':{'binary':'/snap/chromium/current/usr/lib/chromium-browser/chrome','args':['--headless=new','--no-sandbox','--disable-dev-shm-usage']}}}})['sessionId']
 d.call('/session/'+sid+'/url',{'url':'https://ksu.codes/'});d.call('/session/'+sid+'/goog/cdp/execute',{'cmd':'Browser.setPermission','params':{'permission':{'name':'persistent-storage'},'setting':'granted','origin':'https://ksu.codes'}})
 d.wait(lambda:js('return !!document.querySelector(".login-gate");'),30);js('document.querySelector(".login-toggle").click();');js('''const set=(a,v)=>{const n=document.querySelector('.login-gate input[aria-label="'+a+'"]');n.value=v;n.dispatchEvent(new Event('input',{bubbles:true}));};set('Username',arguments[0]);set('Password','1!$?');set('Confirm password','1!$?');document.querySelector('.login-form').requestSubmit();''',[name]);d.wait(lambda:js('return !!currentSession&&!document.documentElement.classList.contains("login-required")&&surfaces.size>0;'),60)
 js('localStorage.setItem("codi-device-history-consent-v1","accepted-v1");window.testDesktop=[...surfaces.values()][0];window.chatId=testDesktop.launch("chat").id;')
 d.wait(lambda:js('''const n=document.querySelector('[data-window="'+chatId+'"]');return !!n?.querySelector('.channel-composer button:not(:disabled)');'''),90)
 d.wait(lambda:js('''const n=document.querySelector('[data-window="'+chatId+'"]');return [...(n?.querySelectorAll('.channel-list-item')||[])].some(x=>x.textContent===arguments[0]);''',[label]),90)
 js('''const n=document.querySelector('[data-window="'+chatId+'"]');[...n.querySelectorAll('.channel-list-item')].find(x=>x.textContent===arguments[0]).click();''',[label])
 d.wait(lambda:js('''const n=document.querySelector('[data-window="'+chatId+'"]');return n?.querySelector('.channel-title')?.textContent===arguments[0]&&!!n?.querySelector('.channel-composer button:not(:disabled)');''',[label]),90)
 js('''const n=document.querySelector('[data-window="'+chatId+'"]');n.querySelector('textarea').value=arguments[0];n.querySelector('form').requestSubmit();''',[text])
 d.wait(lambda:js('''const n=document.querySelector('[data-window="'+chatId+'"]');return n?.querySelector('.channel-history')?.textContent.includes(arguments[0])&&!n.querySelector('.is-pending');''',[text]),120)
 listing=moderate(channel,'--list');matches=[m for m in listing['messages'] if m['text']==text];assert len(matches)==1 and len(listing['messages'])==1
 assert moderate(channel,'--message',matches[0]['id'])['status']=='marked'
 d.wait(lambda:js('''const n=document.querySelector('[data-window="'+chatId+'"]');return [...(n?.querySelectorAll('.channel-history details')||[])].some(x=>x.querySelector('summary')?.textContent.includes('marked as spam')&&x.querySelector('p')?.textContent===arguments[0]);''',[text]),120)
 js('''const n=document.querySelector('[data-window="'+chatId+'"]');[...n.querySelectorAll('.channel-history details')].find(x=>x.querySelector('p')?.textContent===arguments[0]).open=true;''',[text]);time.sleep(6)
 assert js('''const n=document.querySelector('[data-window="'+chatId+'"]');return [...n.querySelectorAll('.channel-history details')].some(x=>x.open&&x.querySelector('p')?.textContent===arguments[0]);''',[text]);print('PASS signed spam marker arrived and original remained readable through refresh',flush=True)
finally:
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
