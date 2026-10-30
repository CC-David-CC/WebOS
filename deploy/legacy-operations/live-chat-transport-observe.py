#!/usr/bin/env python3
"""Observe connections used by two registered public chat browsers."""
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
  cdp(i,'Page.addScriptToEvaluateOnNewDocument',{'source':"""(()=>{window.transportTrace={rendezvous:0,rtc:0};const W=window.WebSocket;window.WebSocket=new Proxy(W,{construct(t,a,n){try{if(new URL(String(a[0]),location.href).pathname==='/rendezvous')transportTrace.rendezvous++;}catch{}return Reflect.construct(t,a,n);}});const R=window.RTCPeerConnection;if(R)window.RTCPeerConnection=new Proxy(R,{construct(t,a,n){transportTrace.rtc++;return Reflect.construct(t,a,n);}});})();"""});
  cdp(i,'Network.enable',{});cdp(i,'Network.setBlockedURLs',{'urls':['*/.build/v86/*','*/assets/speech/*']});call(i,'/session/'+sid+'/url',{'url':origin+'/'});cdp(i,'Browser.setPermission',{'permission':{'name':'persistent-storage'},'setting':'granted','origin':origin});d.wait(lambda:js(i,'return !!document.querySelector(".login-gate");'),45);js(i,'document.querySelector(".login-toggle").click();');js(i,'''const set=(a,v)=>{const n=document.querySelector('.login-gate input[aria-label="'+a+'"]');n.value=v;n.dispatchEvent(new Event('input',{bubbles:true}));};set('Username',arguments[0]);set('Password','1!$?');set('Confirm password','1!$?');document.querySelector('.login-form').requestSubmit();''',[name]);d.wait(lambda:js(i,'return !!currentSession&&!document.documentElement.classList.contains("login-required")&&surfaces.size>0;'),90);js(i,'localStorage.setItem("codi-device-history-consent-v1","accepted-v1");window.testDesktop=[...surfaces.values()][0];window.chatId=testDesktop.launch("chat").id;')
  def ready():
   value=js(i,'''const n=document.querySelector('[data-window="'+chatId+'"]'),b=n?.querySelector('button[type=submit]');return {ready:!!b&&!b.disabled,text:n?.textContent||''};''')
   if 'Could not load this app' in value['text']:raise RuntimeError(value['text'])
   return value['ready']
  d.wait(ready,90);print('Ready participant',i+1,flush=True)
 tag=secrets.token_hex(4);baseline='Reconnect baseline '+tag;send(0,baseline)
 for i in range(2):d.wait(lambda:baseline in snapshot(i)['history'] and snapshot(i)['pending']==0,120)
 print('PASS both participants received baseline',flush=True)
 time.sleep(15)
 traces=[js(i,'return window.transportTrace;') for i in range(2)];print('Chat transport traces:',json.dumps(traces),flush=True)
 if os.environ.get('CODI_EXPECT_NO_PEERS')=='1':assert all(t['rendezvous']==0 and t['rtc']==0 for t in traces),traces
 print('PASS official chat baseline exchanged; peer connection counts observed',flush=True)
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
