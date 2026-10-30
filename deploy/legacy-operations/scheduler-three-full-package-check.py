#!/usr/bin/env python3
"""Candidate public tree with real disposable issuer and candidate steward."""
import asyncio,importlib.util,json,shutil,tempfile,traceback
from pathlib import Path
from aiohttp import web
ROOT=Path(__file__).resolve().parents[1];RELEASE=ROOT/'.build/releases/scheduler-three-profile26-r1'
s=importlib.util.spec_from_file_location('account_fixture',ROOT/'scripts/account-rendezvous-browser-check.py');base=importlib.util.module_from_spec(s);s.loader.exec_module(base);driver=base.driver

def stage(public):
 public.mkdir(parents=True,exist_ok=True)
 for name in json.loads((RELEASE/'release.json').read_text())['files']:
  src=RELEASE/name;dst=public/name;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(src,dst)
 return public

class Fixture(base.Fixture):
 async def start_broker(self):
  self.command[3]=str(RELEASE/'scripts/serve-steward.py');return await super().start_broker()
 async def proxy(self,request):
  if request.path=='/config.json' and hasattr(self,'discovery'):
   async with self.outgoing.get('http://127.0.0.1:'+str(self.issuer_port)+'/config.json',headers={'Host':request.host}) as response:
    value=await response.json();value['discovery']=self.discovery;return web.json_response(value)
  return await super().proxy(request)

async def run():
 base.gateway.staging.stage=stage;fixture=Fixture();profiles=tempfile.TemporaryDirectory(prefix='codi-package-',dir=Path.home()/'snap/chromium/common');sid=None;sessions=[];checks=[];result={'status':'FAIL','checks':checks,'candidate':str(RELEASE)}
 async def call(fn,*args):return await asyncio.to_thread(fn,*args)
 def js(code,args=None):return driver.call('/session/'+sid+'/execute/sync',{'script':code,'args':args or []})
 try:
  await fixture.start();await fixture.provision();v=await call(driver.call,'/session',{'capabilities':{'alwaysMatch':{'browserName':'chrome','goog:chromeOptions':{'binary':'/snap/chromium/current/usr/lib/chromium-browser/chrome','args':['--headless=new','--no-sandbox','--disable-dev-shm-usage','--user-data-dir='+profiles.name]}}}});sid=v['sessionId'];sessions.append(sid);await call(driver.call,'/session/'+sid+'/timeouts',{'script':180000});await call(driver.call,'/session/'+sid+'/url',{'url':fixture.origin+'/'});await call(driver.wait,lambda:js('return !!window.desktopLab?.session&&window.desktopLab.surfaces.size>0;'),45)
  await call(driver.call,'/session/'+sid+'/goog/cdp/execute',{'cmd':'Browser.setPermission','params':{'permission':{'name':'persistent-storage'},'setting':'granted','origin':fixture.origin}})
  wid=await call(js,'window.testDesktop=[...surfaces.values()][0];return testDesktop.launch("chat").id;');sel='[data-window="'+str(wid)+'"]';await call(driver.wait,lambda:js('return !!document.querySelector(arguments[0])?.querySelector(".storage-consent button:not(:disabled),[data-device-channels]");',[sel]),60)
  if not await call(js,'return !!document.querySelector(arguments[0]).querySelector("[data-device-channels]");',[sel]):
   e=await call(driver.call,'/session/'+sid+'/element',{'using':'css selector','value':sel+' .storage-consent button:not(:disabled)'});await call(driver.call,'/session/'+sid+'/element/'+e['element-6066-11e4-a52e-4f735466cecf']+'/click',{})
  await call(driver.wait,lambda:js('return !!document.querySelector(arguments[0])?.querySelector("[data-device-channels]");',[sel]),60);checks.append('sealed desktop loads channel interface using real identity service')
  assert await call(js,'return desktopNetwork.appContext().deviceChannelsReady&&!desktopNetwork.appContext().disabled;');checks.append('sealed desktop starts device-owned networking')
  first=sid;firstsel=sel
  await call(js,'const n=document.querySelector(arguments[0]);[...n.querySelectorAll("input")].find(x=>x.getAttribute("aria-label")==="Device channel label").value="Package club";[...n.querySelectorAll("textarea")].find(x=>x.getAttribute("aria-label")==="Channel description").value="Full package finder";n.querySelector("[data-directory-create]").click();',[firstsel])
  await call(driver.wait,lambda:js('return document.querySelector(arguments[0]).querySelector("[data-device-select]").options.length>0;',[firstsel]),45);checks.append('owner creates public channel in packaged desktop')
  v=await call(driver.call,'/session',{'capabilities':{'alwaysMatch':{'browserName':'chrome','goog:chromeOptions':{'binary':'/snap/chromium/current/usr/lib/chromium-browser/chrome','args':['--headless=new','--no-sandbox','--disable-dev-shm-usage','--user-data-dir='+profiles.name+'-second']}}}});sid=v['sessionId'];sessions.append(sid);await call(driver.call,'/session/'+sid+'/timeouts',{'script':180000});await call(driver.call,'/session/'+sid+'/url',{'url':fixture.origin+'/'});await call(driver.wait,lambda:js('return !!window.desktopLab?.session&&window.desktopLab.surfaces.size>0;'),45);await call(driver.call,'/session/'+sid+'/goog/cdp/execute',{'cmd':'Browser.setPermission','params':{'permission':{'name':'persistent-storage'},'setting':'granted','origin':fixture.origin}})
  wid=await call(js,'window.testDesktop=[...surfaces.values()][0];return testDesktop.launch("chat").id;');secondsel='[data-window="'+str(wid)+'"]';await call(driver.wait,lambda:js('return !!document.querySelector(arguments[0])?.querySelector(".storage-consent button:not(:disabled),[data-device-channels]");',[secondsel]),45)
  if not await call(js,'return !!document.querySelector(arguments[0]).querySelector("[data-device-channels]");',[secondsel]):
   e=await call(driver.call,'/session/'+sid+'/element',{'using':'css selector','value':secondsel+' .storage-consent button:not(:disabled)'});await call(driver.call,'/session/'+sid+'/element/'+e['element-6066-11e4-a52e-4f735466cecf']+'/click',{})
  await call(driver.wait,lambda:js('return !!document.querySelector(arguments[0])?.querySelector("[data-device-channels]");',[secondsel]),45)
  await call(js,'const n=document.querySelector(arguments[0]).querySelector("input[type=search]");n.value="package finder";n.dispatchEvent(new Event("input",{bubbles:true}));',[secondsel])
  await call(driver.wait,lambda:js('return [...document.querySelector(arguments[0]).querySelectorAll("[data-channel-results] button")].some(b=>b.textContent==="Join");',[secondsel]),60)
  await call(js,'[...document.querySelector(arguments[0]).querySelectorAll("[data-channel-results] button")].find(b=>b.textContent==="Join").click();',[secondsel]);await call(driver.wait,lambda:js('return document.querySelector(arguments[0]).querySelector("[data-device-select]").options.length>0;',[secondsel]),45);checks.append('second packaged desktop searches and joins channel')
  await call(driver.wait,lambda:js('return !document.querySelector(arguments[0]).querySelector("[data-device-queue]").disabled;',[secondsel]),60)
  await call(js,'const n=document.querySelector(arguments[0]);n.querySelector("[data-device-draft]").value="Hello from packaged peer";n.querySelector("[data-device-queue]").click();',[secondsel]);second=sid;sid=first
  await call(driver.wait,lambda:js('return document.querySelector(arguments[0]).querySelector("[data-device-history]").textContent.includes("Hello from packaged peer");',[firstsel]),60);checks.append('peer message arrives in owner packaged desktop')
  await call(js,'const n=document.querySelector(arguments[0]);n.querySelector("[data-device-draft]").value="Hello from packaged owner";n.querySelector("[data-device-queue]").click();',[firstsel]);sid=second
  await call(driver.wait,lambda:js('return document.querySelector(arguments[0]).querySelector("[data-device-history]").textContent.includes("Hello from packaged owner");',[secondsel]),60);checks.append('owner reply arrives in peer packaged desktop')
  result['status']='PASS'
 except Exception:
  result['error']=traceback.format_exc()
  if sid:
   try:result['diagnostic']=await call(js,'return {body:document.body.innerText,desktop:!!window.desktopLab,errors:typeof desktopNetwork!=="undefined"?desktopNetwork.appContext().meshError:null,session:window.desktopLab?.session,guestMessage:typeof guestMessage!=="undefined"?guestMessage:null,identity:typeof identityConfig!=="undefined"?identityConfig?.identity?.mode:null};')
   except Exception:result['diagnosticError']=traceback.format_exc()
   try:result['browserLog']=await call(driver.call,'/session/'+sid+'/log',{'type':'browser'})
   except Exception:pass
 finally:
  for owned in sessions:
   try:await call(driver.call,'/session/'+owned,None,'DELETE')
   except Exception:result['status']='FAIL';result['cleanupError']=traceback.format_exc()
  await fixture.close();profiles.cleanup();shutil.rmtree(profiles.name+'-second',ignore_errors=True)
 print(json.dumps(result,indent=2));return result
if __name__=='__main__':
 r=asyncio.run(run());out=ROOT/'.build/checks/scheduler-three-full-package-r1.json';assert not out.exists();out.write_text(json.dumps(r,indent=2)+'\n');raise SystemExit(r['status']!='PASS')
