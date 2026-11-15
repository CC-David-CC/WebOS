#!/usr/bin/env python3
"""Public-site offline draft, missed chat and automatic reconnect on two devices."""
import importlib.util,json,os,re,secrets,shlex,shutil,subprocess,tempfile,time,urllib.error,urllib.request
from pathlib import Path
R=Path(__file__).resolve().parents[1];spec=importlib.util.spec_from_file_location('driver',R/'scripts/touch-preview-check.py');d=importlib.util.module_from_spec(spec);spec.loader.exec_module(d)
origin='https://ksu.codes';remote='maint@10.0.7.105';port=19539;pidfile='/tmp/codi-reconnect-'+secrets.token_hex(8)+'.pid';sessions=[];names=[];profiles=[];remote_profile=None;proc=tunnel=None;server_stopped=False

def call(i,path,data=None,method=None):
 if i==0:return d.call(path,data,method)
 req=urllib.request.Request('http://127.0.0.1:'+str(port)+path,data=None if data is None else json.dumps(data).encode(),headers={'Content-Type':'application/json'},method=method)
 try:
  with urllib.request.urlopen(req,timeout=120) as response:return json.load(response)['value']
 except urllib.error.HTTPError as error:raise RuntimeError(error.read().decode()) from error

def js(i,script,args=[]):return call(i,'/session/'+sessions[i]+'/execute/sync',{'script':script,'args':args})
def cdp(i,cmd,params):return call(i,'/session/'+sessions[i]+'/goog/cdp/execute',{'cmd':cmd,'params':params})
def snapshot(i):return js(i,'''const n=document.querySelector('[data-window="'+chatId+'"]');return {history:n?.querySelector('.channel-history')?.textContent||'',pending:n?.querySelectorAll('.is-pending').length||0,status:n?.querySelector('.channel-conversation .app-status')?.textContent||'',technical:n?.querySelector('.channel-conversation > details > p')?.textContent||'',draft:n?.querySelector('.channel-composer textarea')?.value||''};''')
def send(i,message):js(i,'''const n=document.querySelector('[data-window="'+chatId+'"]'),t=n.querySelector('.channel-composer textarea');t.value=arguments[0];n.querySelector('form').requestSubmit();''',[message])
try:
 ip=subprocess.check_output(['ssh','-o','BatchMode=yes',remote,'curl','-4','-fsS','--max-time','10','https://api.ipify.org'],text=True,timeout=20).strip();assert ip=='104.180.210.36',ip
 remote_profile=subprocess.check_output(['ssh','-o','BatchMode=yes',remote,'mktemp','-d','/tmp/codi-reconnect-XXXXXXXX'],text=True,timeout=15).strip();assert re.fullmatch(r'/tmp/codi-reconnect-[A-Za-z0-9]{8}',remote_profile)
 command='umask 077; echo $$ > '+pidfile+'; exec /usr/bin/chromedriver --port='+str(port)+' --allowed-ips=127.0.0.1';proc=subprocess.Popen(['ssh','-o','BatchMode=yes',remote,command],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL);tunnel=subprocess.Popen(['ssh','-o','BatchMode=yes','-o','ExitOnForwardFailure=yes','-N','-L','127.0.0.1:'+str(port)+':127.0.0.1:'+str(port),remote],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
 def remote_ready():
  if proc.poll() is not None or tunnel.poll() is not None:raise RuntimeError('i36 driver stopped')
  try:
   with urllib.request.urlopen('http://127.0.0.1:'+str(port)+'/status',timeout=1) as response:return json.load(response)['value']['ready']
  except OSError:return False
 d.wait(remote_ready,25)
 for i in range(2):
  name='recoverytest'+secrets.token_hex(5);names.append(name);profile=Path(remote_profile) if i else Path(tempfile.mkdtemp(prefix='codi-reconnect-',dir=Path.home()/'snap/chromium/common'));profiles.append(profile);binary='/usr/bin/chromium' if i else '/snap/chromium/current/usr/lib/chromium-browser/chrome';args=['--headless=new','--no-sandbox','--disable-dev-shm-usage','--user-data-dir='+str(profile)];sid=call(i,'/session',{'capabilities':{'alwaysMatch':{'browserName':'chrome','goog:chromeOptions':{'binary':binary,'args':args}}}})['sessionId'];sessions.append(sid)
  cdp(i,'Network.enable',{});cdp(i,'Network.setBlockedURLs',{'urls':['*/.build/v86/*','*/assets/speech/*']});call(i,'/session/'+sid+'/url',{'url':origin+'/'});cdp(i,'Browser.setPermission',{'permission':{'name':'persistent-storage'},'setting':'granted','origin':origin});d.wait(lambda:js(i,'return !!document.querySelector(".login-gate");'),45);js(i,'document.querySelector(".login-toggle").click();');js(i,'''const set=(a,v)=>{const n=document.querySelector('.login-gate input[aria-label="'+a+'"]');n.value=v;n.dispatchEvent(new Event('input',{bubbles:true}));};set('Username',arguments[0]);set('Password','1!$?');set('Confirm password','1!$?');document.querySelector('.login-form').requestSubmit();''',[name]);d.wait(lambda:js(i,'return !!currentSession&&!document.documentElement.classList.contains("login-required")&&surfaces.size>0;'),90);js(i,'localStorage.setItem("codi-device-history-consent-v1","accepted-v1");window.testDesktop=[...surfaces.values()][0];window.chatId=testDesktop.launch("chat").id;')
  def ready():
   value=js(i,'''const n=document.querySelector('[data-window="'+chatId+'"]'),b=n?.querySelector('button[type=submit]');return {ready:!!b&&!b.disabled,text:n?.textContent||''};''')
   if 'Could not load this app' in value['text']:raise RuntimeError(value['text'])
   return value['ready']
  d.wait(ready,90);print('Ready participant',i+1,flush=True)
 tag=secrets.token_hex(4);baseline='Reconnect baseline '+tag;send(0,baseline)
 for i in range(2):d.wait(lambda:baseline in snapshot(i)['history'] and snapshot(i)['pending']==0,120)
 print('PASS both participants received baseline',flush=True)
 if os.environ.get('CODI_RECOVERY_MODE')=='early':
  cdp(0,'Network.emulateNetworkConditions',{'offline':True,'latency':0,'downloadThroughput':-1,'uploadThroughput':-1});d.wait(lambda:js(0,'return navigator.onLine===false;'),10)
  draft='Early reconnect draft '+tag;missed=['Early missed '+tag+' '+str(i) for i in range(3)];send(0,draft);d.wait(lambda:draft in snapshot(0)['history'] and snapshot(0)['pending']>0,90)
  for message in missed:send(1,message);d.wait(lambda:message in snapshot(1)['history'] and snapshot(1)['pending']==0,90)
  assert draft not in snapshot(1)['history'];js(0,"""window.recoveryRealFetch=window.fetch.bind(window);window.holdRecoveryHistory=true;window.fetch=(input,options)=>{const u=new URL(input instanceof Request?input.url:String(input),location.href);return holdRecoveryHistory&&u.pathname==='/official-history'?Promise.resolve(new Response('{\"error\":\"held\"}',{status:503,headers:{'Content-Type':'application/json'}})):recoveryRealFetch(input,options);};""")
  started=time.monotonic();cdp(0,'Network.emulateNetworkConditions',{'offline':False,'latency':0,'downloadThroughput':-1,'uploadThroughput':-1});d.wait(lambda:draft in snapshot(1)['history'],120);elapsed=time.monotonic()-started;local=snapshot(0);assert local['pending']>0 and all(m not in local['history'] for m in missed),local;print('PASS server accepted offline draft in',round(elapsed,1),'seconds while local history was held and draft remained pending',flush=True)
  js(0,'window.holdRecoveryHistory=false;');
  for i in range(2):d.wait(lambda:all(m in snapshot(i)['history'] for m in [draft,*missed]) and snapshot(i)['pending']==0,180)
  print('PASS both browsers verified all messages after history was restored',flush=True)
 elif os.environ.get('CODI_RECOVERY_MODE')=='reload':
  cdp(0,'Network.emulateNetworkConditions',{'offline':True,'latency':0,'downloadThroughput':-1,'uploadThroughput':-1});d.wait(lambda:js(0,'return navigator.onLine===false;'),10)
  draft='Reload pending draft '+tag;send(0,draft);d.wait(lambda:draft in snapshot(0)['history'] and snapshot(0)['pending']>0,90);assert draft not in snapshot(1)['history']
  cdp(0,'Network.setBlockedURLs',{'urls':['*/.build/v86/*','*/assets/speech/*','*/official-ingest/*']});cdp(0,'Network.emulateNetworkConditions',{'offline':False,'latency':0,'downloadThroughput':-1,'uploadThroughput':-1});call(0,'/session/'+sessions[0]+'/url',{'url':origin+'/'})
  d.wait(lambda:js(0,'return !!document.querySelector(".login-gate");'),45);js(0,"""const set=(a,v)=>{const n=document.querySelector('.login-gate input[aria-label="'+a+'"]');n.value=v;n.dispatchEvent(new Event('input',{bubbles:true}));};set('Username',arguments[0]);set('Password','1!$?');document.querySelector('.login-form').requestSubmit();""",[names[0]]);d.wait(lambda:js(0,'return !!currentSession&&!document.documentElement.classList.contains("login-required")&&surfaces.size>0;'),90);js(0,'window.testDesktop=[...surfaces.values()][0];window.chatId=testDesktop.launch("chat").id;')
  d.wait(lambda:draft in snapshot(0)['history'] and snapshot(0)['pending']>0,120);assert draft not in snapshot(1)['history'];print('PASS pending draft survives page reload and sign-in',flush=True)
  started=time.monotonic();cdp(0,'Network.setBlockedURLs',{'urls':['*/.build/v86/*','*/assets/speech/*']})
  for i in range(2):d.wait(lambda:draft in snapshot(i)['history'] and snapshot(i)['pending']==0,180)
  print('PASS recovered draft settles on both browsers in',round(time.monotonic()-started,1),'seconds',flush=True)
 elif os.environ.get('CODI_RECOVERY_MODE')=='server':
  server_stopped=True;subprocess.run(['ssh','-o','BatchMode=yes','box-webhost','sudo','-n','systemctl','stop','codi-official.service'],check=True,timeout=30);print('Official chat service stopped for recovery test',flush=True)
  drafts=['Server restart draft '+tag+' '+str(i) for i in range(2)]
  for i in range(2):send(i,drafts[i]);d.wait(lambda:drafts[i] in snapshot(i)['history'] and snapshot(i)['pending']>0,90)
  assert drafts[0] not in snapshot(1)['history'] and drafts[1] not in snapshot(0)['history'];print('PASS both drafts stay pending while the server is down',flush=True)
  started=time.monotonic();subprocess.run(['ssh','-o','BatchMode=yes','box-webhost','sudo','-n','systemctl','start','codi-official.service'],check=True,timeout=30);server_stopped=False
  for i in range(2):d.wait(lambda:all(m in snapshot(i)['history'] for m in drafts) and snapshot(i)['pending']==0,180)
  print('PASS both drafts settled after server restart in',round(time.monotonic()-started,1),'seconds without a page reload',flush=True)
 else:
  cdp(0,'Network.emulateNetworkConditions',{'offline':True,'latency':0,'downloadThroughput':-1,'uploadThroughput':-1});d.wait(lambda:js(0,'return navigator.onLine===false;'),10)
  d.wait(lambda:'Connection lost' in snapshot(0)['status'],20);print('PASS chat shows connection loss promptly',flush=True)
  away='Message while disconnected '+tag;missed=['Missed message '+tag+' '+str(i) for i in range(3)];send(0,away);d.wait(lambda:away in snapshot(0)['history'] and snapshot(0)['pending']>0,60)
  for message in missed:
   send(1,message);d.wait(lambda:message in snapshot(1)['history'] and snapshot(1)['pending']==0,90)
  assert away not in snapshot(1)['history'];assert all(m not in snapshot(0)['history'] for m in missed);print('PASS offline message is pending and missed messages remain remote',flush=True)
  started=time.monotonic();cdp(0,'Network.emulateNetworkConditions',{'offline':False,'latency':0,'downloadThroughput':-1,'uploadThroughput':-1});d.wait(lambda:js(0,'return navigator.onLine===true;'),10)
  for i in range(2):d.wait(lambda:all(m in snapshot(i)['history'] for m in [away,*missed]) and snapshot(i)['pending']==0,180)
  d.wait(lambda:'Connection lost' not in snapshot(0)['status'],20);print('PASS connection-loss message clears after reconnect',flush=True)
  print('PASS both participants recovered all messages automatically in',round(time.monotonic()-started,1),'seconds without a page reload',flush=True)
finally:
 if server_stopped:
  try:subprocess.run(['ssh','-o','BatchMode=yes','box-webhost','sudo','-n','systemctl','start','codi-official.service'],check=True,timeout=30);print('Restored official service',flush=True)
  except Exception as e:print('Official service restoration failed:',e,flush=True)
 for i in range(len(sessions)):
  try:
   info=snapshot(i);info.pop('history',None);print('Final diagnostic',i+1,json.dumps(info),flush=True)
  except Exception as e:print('Diagnostic unavailable',i+1,str(e)[:120],flush=True)
 for i,sid in enumerate(sessions):
  try:call(i,'/session/'+sid,method='DELETE')
  except Exception:pass
 for child in (tunnel,proc):
  if child:
   child.terminate()
   try:child.wait(5)
   except subprocess.TimeoutExpired:child.kill();child.wait()
 if remote_profile:
  cleanup='''import os,pathlib,re,shutil,signal,sys\np=pathlib.Path(sys.argv[1]);f=pathlib.Path(sys.argv[2]);assert re.fullmatch(r"/tmp/codi-reconnect-[A-Za-z0-9]{8}",str(p)) and re.fullmatch(r"/tmp/codi-reconnect-[0-9a-f]{16}[.]pid",str(f))\nif f.exists():\n pid=int(f.read_text());cmd=pathlib.Path('/proc')/str(pid)/'cmdline'\n if cmd.exists() and b'chromedriver' in cmd.read_bytes():os.kill(pid,signal.SIGTERM)\n f.unlink()\nif p.exists():shutil.rmtree(p)'''
  try:subprocess.run(['ssh','-o','BatchMode=yes',remote,'python3','-c',shlex.quote(cleanup),remote_profile,pidfile],check=True,capture_output=True,text=True,timeout=30)
  except Exception as e:print('i36 cleanup failed:',e,flush=True)
 for p in profiles[:1]:
  if p.exists() and p.name.startswith('codi-reconnect-'):shutil.rmtree(p)
 if names:
  cleanup='''import json,re,sqlite3,sys\nnames=json.load(sys.stdin);assert len(names)<=2 and all(re.fullmatch(r"recoverytest[0-9a-f]{10}",n) for n in names)\na=sqlite3.connect('/var/lib/codi-connected/ksu/issuer/state/accounts.sqlite3',timeout=30);b=sqlite3.connect('/var/lib/codi-official/state/official.sqlite',timeout=30)\nfor name in names:\n row=a.execute('SELECT subject FROM accounts WHERE username=?',(name,)).fetchone()\n if row:\n  sub=row[0];b.execute('BEGIN IMMEDIATE');b.execute('DELETE FROM official_chat_names WHERE EXISTS (SELECT 1 FROM official_chat_actors x WHERE x.channel=official_chat_names.channel AND x.actor=official_chat_names.actor AND x.subject=?)',(sub,))\n  for table in ('official_upload_bans','official_chat_ban_epochs','official_chat_actor_reviews','official_chat_actors'):b.execute('DELETE FROM '+table+' WHERE subject=?',(sub,))\n  b.commit();a.execute('BEGIN IMMEDIATE');a.execute('DELETE FROM account_policy WHERE subject=?',(sub,));a.execute('DELETE FROM accounts WHERE username=? AND subject=?',(name,sub));a.commit()\nprint('removed',len(names),'disposable accounts and author metadata')'''
  try:print(subprocess.run(['ssh','-o','BatchMode=yes','box-webhost','sudo','-n','python3','-B','-c',shlex.quote(cleanup)],input=json.dumps(names),capture_output=True,text=True,check=True,timeout=30).stdout.strip(),flush=True)
  except Exception as e:print('Account cleanup failed:',e,'names:',names,flush=True)
