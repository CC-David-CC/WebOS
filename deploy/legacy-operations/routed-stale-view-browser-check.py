#!/usr/bin/env python3
"""Close real Rooms windows during grant creation/verification on installed code."""
import argparse,hashlib,importlib.util,json,time
from pathlib import Path

ROOT=Path(__file__).resolve().parent.parent
def module(name,path):
 spec=importlib.util.spec_from_file_location(name,path);value=importlib.util.module_from_spec(spec);spec.loader.exec_module(value);return value

def run(release):
 vm=module('stale_view_vm',ROOT/'scripts/upgrade-signin-native-vm.py');h=module('stale_helpers',ROOT/'scripts/touch-preview-check.py')
 pin=hashlib.sha256((release/'connected-release.json').read_bytes()).hexdigest();assert vm.runtime()['manifestSHA256']==pin
 installed=json.loads(vm.remote('cat /srv/codi-network-fixture/installed-result.json'));graph=json.loads((release/'assets/desktop/network-release.json').read_text())
 sessions=[];checks=[]
 def js(s,code,args=[]):return h.call('/session/'+s+'/execute/sync',{'script':code,'args':args})
 def task(s,code,args=[]):
  value=h.call('/session/'+s+'/execute/async',{'script':'const params=arguments,done=arguments[arguments.length-1];(async()=>{'+code+'})().then(value=>done({ok:true,value}),error=>done({ok:false,error:error.stack}));','args':args});assert value['ok'],value;return value.get('value')
 try:
  for _ in range(3):
   s=h.call('/session',{'capabilities':{'alwaysMatch':{'browserName':'chrome','goog:chromeOptions':{'binary':'/snap/chromium/current/usr/lib/chromium-browser/chrome','args':['--headless=new','--no-sandbox','--disable-dev-shm-usage','--ignore-certificate-errors-spki-list='+installed['fixtureSPKI']]},'goog:loggingPrefs':{'browser':'ALL'}}}})['sessionId'];sessions.append(s)
   h.call('/session/'+s+'/timeouts',{'script':120000});h.call('/session/'+s+'/url',{'url':installed['publicOrigin']+'/hidden/'})
   h.wait(lambda:js(s,'return window.desktopLab?.guestState==="ready"&&!!desktopNetwork.appContext().routedRooms'),150)
   js(s,'window.stalePool=desktopNetwork.appContext().pool;window.staleRouter=desktopNetwork.appContext().routedRooms;')
  centre=sessions[0]
  for leaf in sessions[1:]:
   offer=task(centre,'const r=await stalePool.offer();return {id:r.entry.id,token:r.token};');answer=task(leaf,'return (await stalePool.answer(params[0])).token;',[offer['token']]);task(centre,'await stalePool.accept(params[0],params[1]);return true;',[offer['id'],answer]);h.wait(lambda:js(leaf,'return stalePool.firstReady()?.link.routedApplicationReady'),40)
  task(centre,'window.staleBudget=(await import(params[0])).sessionBudget(currentSession);window.staleNativeCrypto=staleBudget.runCrypto.bind(staleBudget);return true;',['./'+graph['directory']+'/resource-budget.mjs'])
  baseline=task(centre,'return (await desktopNetwork.stats()).budget;')
  for held_call in [1,2]:
   js(centre,'window.staleDesktop=[...surfaces.values()][0];window.staleView=staleDesktop.launch("rooms");')
   h.wait(lambda:js(centre,'return !!document.querySelector(`[data-window="${staleView.id}"]`)?.appView'),20)
   js(centre,'''window.staleCalls=0;window.staleRelease=null;window.staleOutcome=null;
staleBudget.runCrypto=async fn=>{if(++staleCalls===arguments[0])await new Promise(r=>staleRelease=r);return staleNativeCrypto(fn);};
staleRouter.create(stalePool.list().map(e=>e.id),'Cancelled view',staleView).then(()=>staleOutcome={accepted:true},e=>staleOutcome={accepted:false,error:e.message});''',[held_call])
   h.wait(lambda:js(centre,'return typeof staleRelease==="function"'),15)
   js(centre,'document.querySelector(`[data-window="${staleView.id}"] [aria-label="Close"]`).click();staleRelease();')
   h.wait(lambda:js(centre,'return !!staleOutcome'),20)
   outcome=js(centre,'return staleOutcome');assert outcome['accepted'] is False,outcome
   assert js(centre,'return staleRouter.snapshot(staleView).selected===null&&staleRouter.snapshot(staleView).groups.length===0')
   js(centre,'staleBudget.runCrypto=staleNativeCrypto;')
   h.wait(lambda:task(centre,'return (await desktopNetwork.stats()).budget;')==baseline,15)
   for leaf in sessions[1:]:assert js(leaf,'return staleRouter.snapshot({}).groups.length===0')
   checks.append('closing window during crypto stage '+str(held_call)+' cancels creation with no invitation, subscription or retained charge')
  return {'status':'PASS','checks':checks,'nativeManifestSHA256':pin,'actualChromeContexts':3,'actualRTCLinks':2,'liveSiteChanged':False}
 finally:
  for s in sessions:
   try:js(s,'if(typeof staleRelease==="function")staleRelease();desktopNetwork.close();guestNetworkAdapter?.destroy();v86Instance?.destroy();')
   finally:h.call('/session/'+s,method='DELETE')

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--release-dir',type=Path,required=True);p.add_argument('--output',required=True);a=p.parse_args();result={'status':'FAIL'}
 try:result.update(run(a.release_dir.resolve()))
 finally:
  result['sourceSHA256']=hashlib.sha256(Path(__file__).read_bytes()).hexdigest();path=ROOT/'.build/checks'/a.output
  assert not path.exists(),'Preserve previous evidence';path.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
