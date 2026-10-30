#!/usr/bin/env python3
"""Ten anonymous public desktop profiles try a shared chat with manual peer introductions."""
import argparse,importlib.util,json,shutil,tempfile,traceback,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];spec=importlib.util.spec_from_file_location('driver',ROOT/'scripts/touch-preview-check.py');d=importlib.util.module_from_spec(spec);spec.loader.exec_module(d)
def run():
 sessions={};profiles={};selectors={};checks=[];r={'status':'FAIL','scope':__doc__,'checks':checks,'actualBrowsers':10,'serverAccountsCreated':0,'liveSite':'https://ksu.codes/','transport':'WebRTC; peer invitation manually transferred by test driver'};started=time.monotonic()
 def js(side,code,args=[]):return d.call('/session/'+sessions[side]+'/execute/sync',{'script':code,'args':args})
 def wait(side,code,args=[],seconds=60):return d.wait(lambda:js(side,code,args),seconds)
 def check(name,v):assert v,name;checks.append(name);print(json.dumps({'check':name}),flush=True)
 def node(side,attr):return selectors[side]+' ['+attr+']'
 def click(side,attr):
  selector=node(side,attr);wait(side,'const n=document.querySelector(arguments[0]);return !!n&&!n.disabled;',[selector]);js(side,'document.querySelector(arguments[0]).click();',[selector])
 def value(side,attr):return js(side,'return document.querySelector(arguments[0]).value;',[node(side,attr)])
 def input_value(side,attr,v):js(side,'const n=document.querySelector(arguments[0]);n.value=arguments[1];n.dispatchEvent(new Event("input",{bubbles:true}));',[node(side,attr),v])
 def generous(side):
  wait(side,'return !document.querySelector(arguments[0]).disabled;',[node(side,'data-device-apply-global-allowance')],60)
  for key in ['uploadBytes','downloadBytes','serveBytes']:
   sel=selectors[side]+' [data-device-global-quota="'+key+'"]';js(side,'const n=document.querySelector(arguments[0]);n.value="65536";n.dispatchEvent(new Event("input",{bubbles:true}));',[sel])
  click(side,'data-device-apply-global-allowance');wait(side,'return !document.querySelector(arguments[0]).disabled;',[node(side,'data-device-apply-global-allowance')],60)
 def trace_history(side,seconds):
  start=time.monotonic();samples=[]
  while time.monotonic()-start<seconds:
   for who in ('a',side):
    try:
     v=d.call('/session/'+sessions[who]+'/execute/async',{'script':'const done=arguments[arguments.length-1];desktopNetwork.stats().then(x=>done({device:x.deviceChannels,budget:x.budget}),e=>done({error:e.message}));','args':[]})
     v['side']=who;v['t']=round(time.monotonic()-start,1);samples.append(v)
    except Exception as e:samples.append({'side':who,'error':str(e)})
   if js(side,'return document.querySelector(arguments[0]).textContent.includes("Small group initial message");',[node(side,'data-device-history')]):r.setdefault('trace',{})[side]=samples;return True
   time.sleep(5)
  r.setdefault('trace',{})[side]=samples
  raise AssertionError('History recovery timed out for '+side)
 try:
  for side in 'abcdefghij':
   profiles[side]=Path(tempfile.mkdtemp(prefix='codi-live-p2p-'+side+'-',dir=Path.home()/'snap/chromium/common'))
   v=d.call('/session',{'capabilities':{'alwaysMatch':{'browserName':'chrome','goog:chromeOptions':{'binary':'/snap/chromium/current/usr/lib/chromium-browser/chrome','args':['--headless=new','--no-sandbox','--disable-dev-shm-usage','--user-data-dir='+str(profiles[side])]},'goog:loggingPrefs':{'browser':'ALL'}}}});sessions[side]=v['sessionId'];d.call('/session/'+sessions[side]+'/timeouts',{'script':180000});d.call('/session/'+sessions[side]+'/url',{'url':'https://ksu.codes/'});wait(side,'return !!window.desktopLab?.session&&window.desktopLab.surfaces.size>0;',seconds=90);d.call('/session/'+sessions[side]+'/goog/cdp/execute',{'cmd':'Browser.setPermission','params':{'permission':{'name':'persistent-storage'},'setting':'granted','origin':'https://ksu.codes'}})
   wid=js(side,'window.testDesktop=[...surfaces.values()][0];return testDesktop.launch("chat").id;');selectors[side]='[data-window="'+str(wid)+'"]';wait(side,'return !!document.querySelector(arguments[0])?.querySelector(".storage-consent button:not(:disabled),[data-device-channels]");',[selectors[side]],90)
   if not js(side,'return !!document.querySelector(arguments[0]).querySelector("[data-device-channels]");',[selectors[side]]):
    e=d.call('/session/'+sessions[side]+'/element',{'using':'css selector','value':selectors[side]+' .storage-consent button:not(:disabled)'})['element-6066-11e4-a52e-4f735466cecf'];d.call('/session/'+sessions[side]+'/element/'+e+'/click',{})
   wait(side,'return !!document.querySelector(arguments[0])?.querySelector("[data-device-channels]");',[selectors[side]],90)
   js(side,'for(const e of document.querySelector(arguments[0]).querySelectorAll("details"))e.open=true;',[selectors[side]])
  check('ten anonymous browsers opened device-owned chat',True)
  js('a','document.querySelector(arguments[0]).checked=true;',[node('a','data-device-public-read')]);click('a','data-device-create');wait('a','return !!document.querySelector(arguments[0]).value;',[node('a','data-device-select')],60)
  js('a','const n=document.querySelector(arguments[0]);n.value="fast";n.dispatchEvent(new Event("change",{bubbles:true}));',[node('a','data-device-traffic')]);wait('a','return !document.querySelector(arguments[0]).disabled;',[node('a','data-device-queue')],60)
  generous('a')
  input_value('a','data-device-draft','Small group initial message');click('a','data-device-queue');wait('a','return document.querySelector(arguments[0]).textContent.includes("Small group initial message");',[node('a','data-device-history')],90)
  click('a','data-device-export');share=wait('a','return document.querySelector(arguments[0]).value||false;',[node('a','data-device-share')],60)
  r['joined']=[]
  for number,side in enumerate('bcdefghij'):
   parent='abcdefghi'[number//3];r['currentPeer']=side;r['currentParent']=parent
   input_value(parent,'data-device-connection-out','');click(parent,'data-device-offer');offer=wait(parent,'return document.querySelector(arguments[0]).value||false;',[node(parent,'data-device-connection-out')],60)
   input_value(side,'data-device-connection-in',offer);click(side,'data-device-answer');answer=wait(side,'return document.querySelector(arguments[0]).value||false;',[node(side,'data-device-connection-out')],60)
   input_value(parent,'data-device-connection-in',answer);click(parent,'data-device-accept');wait(side,'return document.querySelector(arguments[0]).options.length>0;',[node(side,'data-device-peer')],45)
   input_value(side,'data-device-share',share);click(side,'data-device-import');generous(side);trace_history(side,60)
   js(side,'const n=document.querySelector(arguments[0]);n.value="fast";n.dispatchEvent(new Event("change",{bubbles:true}));',[node(side,'data-device-traffic')]);wait(side,'return !document.querySelector(arguments[0]).disabled;',[node(side,'data-device-traffic')],60)
   actor=value(side,'data-device-member-key');input_value('a','data-device-member-subject',actor);click('a','data-device-allow-write');wait(side,'return !document.querySelector(arguments[0]).disabled;',[node(side,'data-device-queue')],60)
   r['joined'].append(side);print(json.dumps({'joined':side}),flush=True)
  check('nine peers joined and received initial message',True)
  for side in 'bcdefghij':
   message='small group message '+side;input_value(side,'data-device-draft',message);click(side,'data-device-queue');wait('a','return document.querySelector(arguments[0]).textContent.includes(arguments[1]);',[node('a','data-device-history'),message],90)
  check('all nine peers sent accepted messages',True)
  for side in 'bcdefghij':
   for sender in 'bcdefghij':wait(side,'return document.querySelector(arguments[0]).textContent.includes(arguments[1]);',[node(side,'data-device-history'),'small group message '+sender],90)
  check('every peer received every message',True)
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
