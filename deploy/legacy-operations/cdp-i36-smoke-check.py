#!/usr/bin/env python3
"""Check disposable i36 Chrome can intercept its own test module, with cleanup."""
import importlib.util,json,shlex,socket,subprocess,time,urllib.request
from pathlib import Path
spec=importlib.util.spec_from_file_location('probe',Path(__file__).with_name('cdp-test-module-instrument.py'));probe=importlib.util.module_from_spec(spec);spec.loader.exec_module(probe)
def port():
 s=socket.socket();s.bind(('127.0.0.1',0));n=s.getsockname()[1];s.close();return n
host='maint@10.0.7.105';driverport=19537;localdriver=port();profile=subprocess.check_output(['ssh','-o','BatchMode=yes',host,'mktemp','-d','/tmp/codi-cdp-smoke-XXXXXXXX'],text=True).strip();pidfile=profile+'/driver.pid';driver=tunnel=cdptunnel=ins=sid=None
try:
 command='umask 077; echo $$ > '+pidfile+'; exec /usr/bin/chromedriver --port='+str(driverport)+' --allowed-ips=127.0.0.1';driver=subprocess.Popen(['ssh','-o','BatchMode=yes',host,command],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL);tunnel=subprocess.Popen(['ssh','-o','BatchMode=yes','-o','ExitOnForwardFailure=yes','-N','-L',f'127.0.0.1:{localdriver}:127.0.0.1:{driverport}',host],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
 def call(path,data=None,method=None):
  request=urllib.request.Request(f'http://127.0.0.1:{localdriver}'+path,data=None if data is None else json.dumps(data).encode(),headers={'Content-Type':'application/json'},method=method)
  with urllib.request.urlopen(request,timeout=90) as f:return json.load(f)['value']
 for i in range(50):
  try:call('/status');break
  except OSError:time.sleep(.2)
 v=call('/session',{'capabilities':{'alwaysMatch':{'browserName':'chrome','goog:chromeOptions':{'binary':'/usr/bin/chromium','args':['--headless=new','--no-sandbox','--disable-dev-shm-usage','--remote-allow-origins=*','--user-data-dir='+profile]}}}});sid=v['sessionId'];debugport=int(v['capabilities']['goog:chromeOptions']['debuggerAddress'].rsplit(':',1)[1]);localdebug=port();cdptunnel=subprocess.Popen(['ssh','-o','BatchMode=yes','-o','ExitOnForwardFailure=yes','-N','-L',f'127.0.0.1:{localdebug}:127.0.0.1:{debugport}',host],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
 for i in range(50):
  try:
   with urllib.request.urlopen(f'http://127.0.0.1:{localdebug}/json/list',timeout=1) as f:tabs=json.load(f)
   break
  except OSError:time.sleep(.2)
 handle=call('/session/'+sid+'/window').removeprefix('CDwindow-');print('targets',[(t['id'],t['type'],t['url']) for t in tabs],'selected',handle,flush=True);ins=probe.ModuleInstrument(f'127.0.0.1:{localdebug}',handle);call('/session/'+sid+'/timeouts',{'script':90000});call('/session/'+sid+'/url',{'url':'https://ksu.codes/'});result=call('/session/'+sid+'/execute/async',{'script':'''const done=arguments[arguments.length-1];(async()=>{const r=await(await fetch('/assets/desktop/shared-services.json')).json();const m=await import('/'+r.services.find(x=>x.name==='device-history').path);return {member:typeof m.__TraceMember,topology:typeof m.__TraceTopology,transfer:typeof m.__TraceTransfer};})().then(done,e=>done({error:e.message}));''','args':[]});print('module',result,'modified',ins.changed,'error',ins.error,flush=True)
finally:
 if ins:ins.close()
 if sid:call('/session/'+sid,method='DELETE')
 for process in (cdptunnel,tunnel,driver):
  if process:process.terminate();process.wait(timeout=10)
 code='import os,signal,sys,shutil;from pathlib import Path;p=Path(sys.argv[1]);assert p.parent==Path("/tmp") and p.name.startswith("codi-cdp-smoke-");f=p/"driver.pid";pid=int(f.read_text()) if f.exists() else 0;c=Path("/proc")/str(pid)/"cmdline";b=c.read_bytes() if c.exists() else b"";assert not b or b"chromedriver" in b;os.kill(pid,signal.SIGTERM) if b else None;shutil.rmtree(p);print("clean")';print(subprocess.check_output(['ssh','-o','BatchMode=yes',host,'python3','-c',shlex.quote(code),profile],text=True,timeout=30).strip(),flush=True)
