#!/usr/bin/env python3
"""Inspect one fresh i35 Chromium session against the public root with default TLS."""
import json,subprocess,tempfile,socket,time,urllib.request
s=socket.socket();s.bind(('127.0.0.1',0));port=s.getsockname()[1];s.close();url='http://127.0.0.1:'+str(port)
def req(path,data=None,method=None):
 b=None if data is None else json.dumps(data).encode();q=urllib.request.Request(url+path,data=b,headers={'Content-Type':'application/json'},method=method)
 with urllib.request.urlopen(q,timeout=40) as r:return json.load(r)
result={'status':'FAIL','browser':'i35 Chromium','url':'https://ksu.codes/','acceptInsecureCerts':False,'peerConnectionsTested':False};start=time.monotonic()
with tempfile.TemporaryDirectory(prefix='codi-i35-webdriver-') as profile:
 p=subprocess.Popen(['chromedriver','--port='+str(port),'--allowed-ips=127.0.0.1'],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL);sid=None
 try:
  for _ in range(100):
   try:req('/status');break
   except Exception:time.sleep(.1)
  caps={'capabilities':{'alwaysMatch':{'browserName':'chrome','pageLoadStrategy':'none','goog:chromeOptions':{'binary':'/usr/bin/chromium','args':['--headless=new','--no-sandbox','--disable-dev-shm-usage','--disable-gpu','--user-data-dir='+profile]}}}}
  r=req('/session',caps);sid=r['value']['sessionId'];result['browserVersion']=r['value']['capabilities']['browserVersion'];req('/session/'+sid+'/url',{'url':result['url']});deadline=time.monotonic()+180
  while time.monotonic()<deadline:
   time.sleep(3);state=req('/session/'+sid+'/execute/sync',{'script':'return {url:location.href,title:document.title,ready:document.readyState,guest:window.desktopLab?.guestState||null,xterm:!!document.querySelector(".xterm"),files:typeof guestFiles!=="undefined"&&!!guestFiles.ready,kind:typeof currentSession!=="undefined"?currentSession?.public?.kind:null};','args':[]})['value'];result['state']=state
   if state['guest']=='ready' and state['xterm'] and state['files']:break
  assert state['url']=='https://ksu.codes/' and state['guest']=='ready' and state['xterm'] and state['files'] and state['kind']=='anonymous',state
  result['status']='PASS'
 except Exception as e:result['error']=str(e)
 finally:
  if sid:
   try:req('/session/'+sid,method='DELETE');result['sessionClosed']=True
   except Exception as e:result['cleanupError']=str(e);result['status']='FAIL'
  p.terminate()
  try:p.wait(timeout=8)
  except subprocess.TimeoutExpired:p.kill();p.wait()
result['elapsedSeconds']=round(time.monotonic()-start,2);print(json.dumps(result),flush=True)
raise SystemExit(result['status']!='PASS')
