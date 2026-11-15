#!/usr/bin/env python3
"""Fresh trusted public Chrome: paused chat, no network pool, unaffected desktop."""
import importlib.util,json,time,urllib.request,urllib.error,argparse
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
s=importlib.util.spec_from_file_location('pause_driver',ROOT/'scripts/touch-preview-check.py');d=importlib.util.module_from_spec(s);s.loader.exec_module(d)
def run():
 checks=[];sid=None;r={'status':'FAIL','checks':checks,'actualBrowsers':1,'actualV86Desktops':1,'outsideWAN':False,'storageConsentGateImplemented':False}
 def check(name,ok):
  assert ok,name
  checks.append(name);print(json.dumps({'check':name}),flush=True)
 try:
  for path in ['/rooms','/rooms/use','/rooms/challenge','/rooms/readers/health','/rooms/readers/use','/api/v1/room-control/controller','/api/v1/room-control/authorize','/rendezvous']:
   request=urllib.request.Request('https://ksu.codes'+path,data=b'{}',headers={'Content-Type':'application/json'})
   try:urllib.request.urlopen(request,timeout=15);raise AssertionError('Chat endpoint remained available: '+path)
   except urllib.error.HTTPError as e:check('public chat route blocked: '+path,e.code==503 and b'Chat is temporarily unavailable' in e.read())
  sid=d.call('/session',{'capabilities':{'alwaysMatch':{'browserName':'chrome','goog:chromeOptions':{'binary':'/snap/chromium/current/usr/lib/chromium-browser/chrome','args':['--headless=new','--no-sandbox','--disable-dev-shm-usage']}}}})['sessionId']
  def js(code,args=[]):return d.call('/session/'+sid+'/execute/sync',{'script':code,'args':args})
  d.call('/session/'+sid+'/url',{'url':'https://ksu.codes/'})
  d.wait(lambda:js('return window.desktopLab?.guestState==="ready"&&typeof surfaces!=="undefined"'),150)
  check('trusted root desktop boots real Linux with terminal',js('return !!document.querySelector(".xterm")'))
  js('window.pauseDesktop=[...surfaces.values()][0];')
  for i in range(12):
   for app in ['chat','rooms']:
    js('window.pauseWindow=pauseDesktop.launch(arguments[0]);',[app])
    d.wait(lambda:js('return !!document.querySelector("[data-window=\\\""+pauseWindow.id+"\\\"] [data-chat-disabled]")'),20)
    assert js('return !document.querySelector("[data-window=\\\""+pauseWindow.id+"\\\"] textarea")')
    js('pauseDesktop.windows=pauseDesktop.windows.filter(w=>w!==pauseWindow);pauseDesktop.render();')
  check('24 Chat and Rooms opens/closes show notice without send controls or stale views',js('return !document.querySelector("[data-chat-disabled]")'))
  state=d.call('/session/'+sid+'/execute/async',{'script':'const done=arguments[0];desktopNetwork.stats().then(done);','args':[]})
  check('chat has no peer pool, subscriptions, history stores or network allowance allocation',state.get('peers')==[] and state.get('hosted') is None and state.get('mesh') is None and not state.get('budget') and state.get('hostedViews')==state.get('meshViews')==0)
  check('browser never contacts hosted rooms or rendezvous during startup or app opens',js('return !performance.getEntriesByType("resource").some(r=>{const p=new URL(r.name).pathname;return p.startsWith("/rooms/")||p==="/rendezvous";})'))
  js('pauseDesktop.launch("calculator")');d.wait(lambda:js('return !!document.querySelector("[aria-label=\\"Arithmetic expression\\"]")'),20)
  js('const n=document.querySelector("[aria-label=\\"Arithmetic expression\\"]");n.value="6 * 7";n.form.requestSubmit()')
  check('independent calculator remains usable',js('return document.querySelector(".calculator-result").textContent==="42"'))
  js('pauseDesktop.launch("text")');d.wait(lambda:js('return !!document.querySelector(".guest-editor")'),20)
  js('const n=document.querySelector(".guest-editor");n.value="unrelated editor still works";n.dispatchEvent(new Event("input",{bubbles:true}));')
  check('independent text editor remains editable',js('return document.querySelector(".guest-editor").value==="unrelated editor still works"'))
  r['status']='PASS'
 except Exception as e:
  import traceback
  r.update(error=str(e),traceback=traceback.format_exc())
 finally:
  if sid:d.call('/session/'+sid,None,'DELETE');r['ownedBrowserClosed']=True
 return r
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args();v=run();a.output.write_text(json.dumps(v,indent=2)+'\n');print(json.dumps({'status':v['status'],'checks':len(v['checks']),'error':v.get('error')}));raise SystemExit(0 if v['status']=='PASS' else 1)
