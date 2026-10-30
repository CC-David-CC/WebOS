#!/usr/bin/env python3
"""Two registered public desktop profiles connect and exchange signed channel messages."""
import argparse,importlib.util,json,shutil,tempfile,traceback,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];spec=importlib.util.spec_from_file_location('driver',ROOT/'scripts/touch-preview-check.py');d=importlib.util.module_from_spec(spec);spec.loader.exec_module(d)
def run():
 sessions={};profiles={};selectors={};checks=[];r={'status':'FAIL','scope':__doc__,'checks':checks,'actualBrowsers':2,'serverAccountsCreated':0,'liveSite':'https://ksu.codes/','transport':'WebRTC; peer invitation manually transferred by test driver'};started=time.monotonic()
 def js(side,code,args=[]):return d.call('/session/'+sessions[side]+'/execute/sync',{'script':code,'args':args})
 def wait(side,code,args=[],seconds=60):return d.wait(lambda:js(side,code,args),seconds)
 def check(name,v):assert v,name;checks.append(name);print(json.dumps({'check':name}),flush=True)
 def node(side,attr):return selectors[side]+' ['+attr+']'
 def click(side,attr):
  selector=node(side,attr);wait(side,'const n=document.querySelector(arguments[0]);return !!n&&!n.disabled;',[selector]);js(side,'document.querySelector(arguments[0]).click();',[selector])
 def value(side,attr):return js(side,'return document.querySelector(arguments[0]).value;',[node(side,attr)])
 def input_value(side,attr,v):js(side,'const n=document.querySelector(arguments[0]);n.value=arguments[1];n.dispatchEvent(new Event("input",{bubbles:true}));',[node(side,attr),v])
 try:
  for side in 'ab':
   profiles[side]=Path(tempfile.mkdtemp(prefix='codi-live-p2p-'+side+'-',dir=Path.home()/'snap/chromium/common'))
   v=d.call('/session',{'capabilities':{'alwaysMatch':{'browserName':'chrome','goog:chromeOptions':{'binary':'/snap/chromium/current/usr/lib/chromium-browser/chrome','args':['--headless=new','--no-sandbox','--disable-dev-shm-usage','--user-data-dir='+str(profiles[side])]},'goog:loggingPrefs':{'browser':'ALL'}}}});sessions[side]=v['sessionId'];d.call('/session/'+sessions[side]+'/timeouts',{'script':180000});d.call('/session/'+sessions[side]+'/url',{'url':'https://ksu.codes/'});wait(side,'return !!window.desktopLab?.session&&window.desktopLab.surfaces.size>0;',seconds=90);registered=d.call('/session/'+sessions[side]+'/execute/async',{'script':'const done=arguments[arguments.length-1],name="p2ptest"+crypto.randomUUID().replaceAll("-","").slice(0,16),password=crypto.randomUUID()+crypto.randomUUID();changeAccount("register",name,password).then(()=>done({kind:currentSession.public.kind}),e=>done({error:e.message}));','args':[]});assert registered.get('kind')=='registered',registered;r['serverAccountsCreated']+=1;d.call('/session/'+sessions[side]+'/goog/cdp/execute',{'cmd':'Browser.setPermission','params':{'permission':{'name':'persistent-storage'},'setting':'granted','origin':'https://ksu.codes'}})
   wid=js(side,'window.testDesktop=[...surfaces.values()][0];return testDesktop.launch("chat").id;');selectors[side]='[data-window="'+str(wid)+'"]';wait(side,'return !!document.querySelector(arguments[0])?.querySelector(".storage-consent button:not(:disabled),[data-device-channels]");',[selectors[side]],90)
   if not js(side,'return !!document.querySelector(arguments[0]).querySelector("[data-device-channels]");',[selectors[side]]):
    e=d.call('/session/'+sessions[side]+'/element',{'using':'css selector','value':selectors[side]+' .storage-consent button:not(:disabled)'})['element-6066-11e4-a52e-4f735466cecf'];d.call('/session/'+sessions[side]+'/element/'+e+'/click',{})
   wait(side,'return !!document.querySelector(arguments[0])?.querySelector("[data-device-channels]");',[selectors[side]],90)
   js(side,'for(const e of document.querySelector(arguments[0]).querySelectorAll("details"))e.open=true;',[selectors[side]])
  check('two registered browsers opened device-owned chat',True)
  js('a','document.querySelector(arguments[0]).checked=true;',[node('a','data-device-public-read')]);click('a','data-device-create');wait('a','return !!document.querySelector(arguments[0]).value;',[node('a','data-device-select')],60)
  input_value('a','data-device-draft','Peer history live test');click('a','data-device-queue');wait('a','return document.querySelector(arguments[0]).textContent.includes("Peer history live test");',[node('a','data-device-history')],90);check('first browser accepted a signed local channel message',True)
  click('a','data-device-offer');offer=wait('a','return document.querySelector(arguments[0]).value||false;',[node('a','data-device-connection-out')],90)
  input_value('b','data-device-connection-in',offer);click('b','data-device-answer');answer=wait('b','return document.querySelector(arguments[0]).value||false;',[node('b','data-device-connection-out')],90)
  input_value('a','data-device-connection-in',answer);click('a','data-device-accept')
  for side in 'ab':wait(side,'return document.querySelector(arguments[0]).options.length>0;',[node(side,'data-device-peer')],90)
  check('two browsers establish an actual WebRTC peer connection',True)
  click('a','data-device-export');share=wait('a','return document.querySelector(arguments[0]).value||false;',[node('a','data-device-share')],60);input_value('b','data-device-share',share);click('b','data-device-import');wait('b','return document.querySelector(arguments[0]).textContent.includes("Peer history live test");',[node('b','data-device-history')],120);check('reader verifies and receives signed channel history',True)
  actor=value('b','data-device-member-key');assert actor;input_value('a','data-device-member-subject',actor);click('a','data-device-allow-write');wait('b','return !document.querySelector(arguments[0]).disabled;',[node('b','data-device-queue')],120)
  input_value('b','data-device-draft','Reply from second browser');click('b','data-device-queue');wait('a','return document.querySelector(arguments[0]).textContent.includes("Reply from second browser");',[node('a','data-device-history')],120);check('authorized second browser sends a signed reply',True)
  r['status']='PASS'
 except Exception as e:
  r.update(error=str(e),traceback=traceback.format_exc())
  for side in sessions:
   try:r[side+'Diagnostic']=js(side,'return {body:document.body.innerText,status:document.querySelector(arguments[0])?.querySelector("[data-device-status]")?.textContent,peer:document.querySelector(arguments[0])?.querySelector("[data-device-peer]")?.options.length};',[selectors.get(side,'body')])
   except Exception as x:r[side+'DiagnosticError']=str(x)
 finally:
  for side,sid in sessions.items():
   try:d.call('/session/'+sid,method='DELETE')
   except Exception as e:r['status']='FAIL';r[side+'CleanupError']=str(e)
  for p in profiles.values():shutil.rmtree(p)
  r.update(ownedProfilesRemoved=all(not p.exists() for p in profiles.values()),elapsedSeconds=round(time.monotonic()-started,3))
 return r
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args();assert not a.output.exists();r=run();a.output.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({'status':r['status'],'error':r.get('error'),'checks':len(r['checks'])}));raise SystemExit(r['status']!='PASS')
