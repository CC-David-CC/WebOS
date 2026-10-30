#!/usr/bin/env python3
"""Ten public browsers recover after three disconnect, including i36."""
import importlib.util,json,os,re,secrets,shlex,shutil,subprocess,tempfile,time,urllib.error,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];spec=importlib.util.spec_from_file_location('driver',ROOT/'scripts/touch-preview-check.py');d=importlib.util.module_from_spec(spec);spec.loader.exec_module(d);origin='https://ksu.codes';remote='maint@10.0.7.105';port=19537;runid=secrets.token_hex(8);pidfile='/tmp/codi-server-ten-'+runid+'.pid';sessions=[];names=[];profiles=[];proc=tunnel=None;remote_profile=None;messages=[]
def call(index,path,data=None,method=None):
 if index!=9:return d.call(path,data,method)
 req=urllib.request.Request('http://127.0.0.1:'+str(port)+path,data=None if data is None else json.dumps(data).encode(),headers={'Content-Type':'application/json'},method=method)
 try:
  with urllib.request.urlopen(req,timeout=120) as response:return json.load(response)['value']
 except urllib.error.HTTPError as error:raise RuntimeError(error.read().decode()) from error
def js(index,code,args=[]):return call(index,'/session/'+sessions[index]+'/execute/sync',{'script':code,'args':args})
try:
 public_ip=subprocess.check_output(['ssh','-o','BatchMode=yes',remote,'curl','-4','-fsS','--max-time','10','https://api.ipify.org'],text=True,timeout=20).strip();assert public_ip=='104.180.210.36',public_ip
 remote_profile=subprocess.check_output(['ssh','-o','BatchMode=yes',remote,'mktemp','-d','/tmp/codi-server-ten-XXXXXXXX'],text=True,timeout=15).strip();assert re.fullmatch(r'/tmp/codi-server-ten-[A-Za-z0-9]{8}',remote_profile)
 command='umask 077; echo $$ > '+pidfile+'; exec /usr/bin/chromedriver --port='+str(port)+' --allowed-ips=127.0.0.1';proc=subprocess.Popen(['ssh','-o','BatchMode=yes',remote,command],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL);tunnel=subprocess.Popen(['ssh','-o','BatchMode=yes','-o','ExitOnForwardFailure=yes','-N','-L','127.0.0.1:'+str(port)+':127.0.0.1:'+str(port),remote],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
 def remote_ready():
  if proc.poll() is not None or tunnel.poll() is not None:raise RuntimeError('i36 test driver stopped')
  try:
   with urllib.request.urlopen('http://127.0.0.1:'+str(port)+'/status',timeout=1) as response:return json.load(response)['value']['ready']
  except OSError:return False
 d.wait(remote_ready,25)
 for i in range(10):
  name='scaletest'+secrets.token_hex(5);names.append(name);profile=Path(remote_profile) if i==9 else Path(tempfile.mkdtemp(prefix='codi-server-ten-',dir=Path.home()/'snap/chromium/common'));profiles.append(profile)
  binary='/usr/bin/chromium' if i==9 else '/snap/chromium/current/usr/lib/chromium-browser/chrome';args=['--headless=new','--no-sandbox','--disable-dev-shm-usage','--user-data-dir='+str(profile)];sid=call(i,'/session',{'capabilities':{'alwaysMatch':{'browserName':'chrome','goog:chromeOptions':{'binary':binary,'args':args}}}})['sessionId'];sessions.append(sid)
  if os.environ.get('CODI_TEST_CHAT_ONLY')=='1':
   call(i,'/session/'+sid+'/goog/cdp/execute',{'cmd':'Network.enable','params':{}});call(i,'/session/'+sid+'/goog/cdp/execute',{'cmd':'Network.setBlockedURLs','params':{'urls':['*/.build/v86/*','*/assets/speech/*']}})
  call(i,'/session/'+sid+'/url',{'url':origin+'/'});call(i,'/session/'+sid+'/goog/cdp/execute',{'cmd':'Browser.setPermission','params':{'permission':{'name':'persistent-storage'},'setting':'granted','origin':origin}});d.wait(lambda:js(i,'return !!document.querySelector(".login-gate");'),45);js(i,'document.querySelector(".login-toggle").click();');js(i,'''const set=(a,v)=>{const n=document.querySelector('.login-gate input[aria-label="'+a+'"]');n.value=v;n.dispatchEvent(new Event('input',{bubbles:true}));};set('Username',arguments[0]);set('Password','1!$?');set('Confirm password','1!$?');document.querySelector('.login-form').requestSubmit();''',[name]);d.wait(lambda:js(i,'return !!currentSession&&!document.documentElement.classList.contains("login-required")&&surfaces.size>0;'),90);js(i,'localStorage.setItem("codi-device-history-consent-v1","accepted-v1");window.testDesktop=[...surfaces.values()][0];window.chatId=testDesktop.launch("chat").id;')
  def chat_ready():
   value=js(i,'''const n=document.querySelector('[data-window="'+chatId+'"]'),b=n?.querySelector('button[type=submit]');return {ready:!!b&&!b.disabled,text:n?.textContent||''};''')
   if 'Could not load this app' in value['text'] or 'Chat networking is unavailable' in value['text']:raise RuntimeError(value['text'])
   return value['ready']
  d.wait(chat_ready,90);print('Ready',i+1,'of 10'+(' (i36)' if i==9 else ''),flush=True)
 for i in range(10):call(i,'/session/'+sessions[i]+'/goog/cdp/execute',{'cmd':'Network.enable','params':{}})
 for i in range(10):js(i,'''window.testFailures=[];window.testStatuses=[];const n=document.querySelector('[data-window="'+chatId+'"]'),status=n.querySelector('.channel-conversation .app-status');new MutationObserver(()=>{const text=status.textContent;if(testStatuses.at(-1)!==text)testStatuses.push(text);}).observe(status,{childList:true,characterData:true,subtree:true});const original=window.fetch.bind(window);window.fetch=async(...args)=>{const url=new URL(args[0] instanceof Request?args[0].url:String(args[0]),location.href);try{const response=await original(...args);if(!response.ok&&url.pathname.includes('/official-'))testFailures.push({path:url.pathname,status:response.status});return response;}catch(error){if(url.pathname.includes('/official-'))testFailures.push({path:url.pathname,status:0});throw error;}};''')
 messages=['Group recovery '+runid[:6]+' participant '+str(i+1) for i in range(10)];offline=[0,4,9];online=[i for i in range(10) if i not in offline]
 for i in offline:
  call(i,'/session/'+sessions[i]+'/goog/cdp/execute',{'cmd':'Network.emulateNetworkConditions','params':{'offline':True,'latency':0,'downloadThroughput':-1,'uploadThroughput':-1}});d.wait(lambda:js(i,'return navigator.onLine===false;'),10)
 def send(i):js(i,"""const n=document.querySelector('[data-window="'+chatId+'"]'),t=n.querySelector('textarea');t.value=arguments[0];n.querySelector('form').requestSubmit();""",[messages[i]])
 def has(i,wanted):return js(i,"""const n=document.querySelector('[data-window="'+chatId+'"]'),t=n?.querySelector('.channel-history')?.textContent||'';return {has:t.includes(arguments[0]),pending:n?.querySelectorAll('.is-pending').length||0,draft:n?.querySelector('.channel-composer textarea')?.value||''};""",[wanted])
 for i in offline:send(i)
 for i in offline:d.wait(lambda:has(i,messages[i])['has'] and has(i,messages[i])['pending']>0,120)
 print('PASS three disconnected participants retained locally pending messages',flush=True)
 for i in online:send(i)
 for i in online:d.wait(lambda:has(i,messages[i])['has'] and has(i,messages[i])['pending']==0,180)
 assert all(not has(online[0],messages[i])['has'] for i in offline);assert all(not has(offline[0],messages[i])['has'] for i in online)
 print('PASS seven connected participants sent while the others were offline',flush=True)
 started=time.monotonic()
 for i in offline:call(i,'/session/'+sessions[i]+'/goog/cdp/execute',{'cmd':'Network.emulateNetworkConditions','params':{'offline':False,'latency':0,'downloadThroughput':-1,'uploadThroughput':-1}});d.wait(lambda:js(i,'return navigator.onLine===true;'),10)
 for i in range(10):
  d.wait(lambda:js(i,"""const n=document.querySelector('[data-window="'+chatId+'"]'),lines=[...(n?.querySelectorAll('.channel-history .channel-message')||[])];return arguments[0].every(x=>lines.filter(line=>line.textContent.endsWith(': '+x)).length===1)&&!n?.querySelector('.is-pending');""",[messages]),180);print('Recovered',i+1,'of 10 in',round(time.monotonic()-started,1),'seconds',flush=True)
 print('PASS ten participants recovered all messages exactly once in',round(time.monotonic()-started,1),'seconds without reload; i36 IP',public_ip,flush=True)
finally:
 if messages:
  for i in range(len(sessions)):
   try:print('Final diagnostic',i+1,json.dumps(js(i,'''const n=document.querySelector('[data-window="'+chatId+'"]'),lines=[...(n?.querySelectorAll('.channel-history .channel-message')||[])],has=x=>lines.some(line=>line.textContent.endsWith(': '+x));return {seen:arguments[0].filter(has).length,missing:arguments[0].map((x,i)=>has(x)?null:i+1).filter(Boolean),pending:n?.querySelectorAll('.is-pending').length||0,draft:n?.querySelector('.channel-composer textarea')?.value||'',statuses:(window.testStatuses||[]).slice(-20),technical:n?.querySelector('.channel-conversation > details > p')?.textContent||'',failures:(window.testFailures||[]).slice(-20)};''',[messages])),flush=True)
   except Exception as error:print('Diagnostic unavailable',i+1,type(error).__name__,flush=True)
 for i,sid in enumerate(sessions):
  try:call(i,'/session/'+sid,method='DELETE')
  except Exception:pass
 for child in (tunnel,proc):
  if child:
   child.terminate()
   try:child.wait(5)
   except subprocess.TimeoutExpired:child.kill();child.wait()
 if remote_profile:
  cleanup='''import os,pathlib,re,shutil,signal,sys\np=pathlib.Path(sys.argv[1]);f=pathlib.Path(sys.argv[2]);assert re.fullmatch(r"/tmp/codi-server-ten-[A-Za-z0-9]{8}",str(p)) and re.fullmatch(r"/tmp/codi-server-ten-[0-9a-f]{16}[.]pid",str(f))\nif f.exists():\n pid=int(f.read_text());cmd=pathlib.Path("/proc")/str(pid)/"cmdline"\n if cmd.exists() and b"chromedriver" in cmd.read_bytes():os.kill(pid,signal.SIGTERM)\n f.unlink()\nif p.exists():shutil.rmtree(p)\nprint("clean")'''
  try:subprocess.run(['ssh','-o','BatchMode=yes',remote,'python3','-c',shlex.quote(cleanup),remote_profile,pidfile],check=True,capture_output=True,text=True,timeout=30)
  except Exception as error:print('i36 test cleanup failed:',error,flush=True)
 for p in profiles[:9]:
  if p.exists() and p.name.startswith('codi-server-ten-'):shutil.rmtree(p)
 if names:
  cleanup='''import json,re,sqlite3,sys\nnames=json.load(sys.stdin);assert len(names)<=10 and all(re.fullmatch(r"scaletest[0-9a-f]{10}",n) for n in names)\nd=sqlite3.connect("/var/lib/codi-connected/ksu/issuer/state/accounts.sqlite3",timeout=30);b=sqlite3.connect("/var/lib/codi-official/state/official.sqlite",timeout=30)\nfor name in names:\n row=d.execute("SELECT subject FROM accounts WHERE username=?",(name,)).fetchone()\n if row:\n  subject=row[0];b.execute("BEGIN IMMEDIATE");b.execute("DELETE FROM official_chat_names WHERE EXISTS (SELECT 1 FROM official_chat_actors a WHERE a.channel=official_chat_names.channel AND a.actor=official_chat_names.actor AND a.subject=?)",(subject,))\n  for table in ("official_upload_bans","official_chat_ban_epochs","official_chat_actor_reviews","official_chat_actors"):b.execute("DELETE FROM "+table+" WHERE subject=?",(subject,))\n  b.commit();d.execute("BEGIN IMMEDIATE");d.execute("DELETE FROM account_policy WHERE subject=?",(subject,));d.execute("DELETE FROM accounts WHERE username=? AND subject=?",(name,subject));d.commit()\nprint("removed",len(names),"disposable accounts and associated author metadata")'''
  try:print(subprocess.run(['ssh','-o','BatchMode=yes','box-webhost','sudo','-n','/usr/bin/python3','-B','-c',shlex.quote(cleanup)],input=json.dumps(names),capture_output=True,text=True,check=True,timeout=30).stdout.strip(),flush=True)
  except Exception as error:print('Test account cleanup failed:',error,'names:',names,flush=True)
