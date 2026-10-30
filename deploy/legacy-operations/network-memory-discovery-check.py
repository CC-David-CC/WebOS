#!/usr/bin/env python3
"""Installed Chrome: adjustable shared allowance and lazy real steward discovery."""
import hashlib,importlib.util,json,time
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
RELEASE=ROOT/'.build/releases/connected-routed-r8'
def load(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def run():
 vm=load('memory_vm',ROOT/'scripts/upgrade-signin-native-vm.py');h=load('memory_helpers',ROOT/'scripts/touch-preview-check.py');runtime=vm.runtime();assert runtime['manifestSHA256']==hashlib.sha256((RELEASE/'connected-release.json').read_bytes()).hexdigest()
 installed=json.loads(vm.remote('cat /srv/codi-network-fixture/installed-result.json'));graph=json.loads((RELEASE/'assets/desktop/network-release.json').read_text());sessions=[];checks=[];budgets=[]
 def js(s,code,args=[]):return h.call('/session/'+s+'/execute/sync',{'script':code,'args':args})
 def task(s,code,args=[]):
  value=h.call('/session/'+s+'/execute/async',{'script':'const params=arguments,done=arguments[arguments.length-1];(async()=>{'+code+'})().then(value=>done({ok:true,value}),error=>done({ok:false,error:error.stack}));','args':args});assert value['ok'],value;return value.get('value')
 def stats(s):return task(s,'return await desktopNetwork.stats();')
 def check(name,value):assert value,name;checks.append(name)
 def action(s,kind):return task(s,'await desktopNetwork.appContext().discoveryAction(params[0],document.querySelector("[data-discovery]"));return true;',[kind])
 try:
  for _ in range(2):
   s=h.call('/session',{'capabilities':{'alwaysMatch':{'browserName':'chrome','goog:chromeOptions':{'binary':'/snap/chromium/current/usr/lib/chromium-browser/chrome','args':['--headless=new','--no-sandbox','--disable-dev-shm-usage','--ignore-certificate-errors-spki-list='+installed['fixtureSPKI']]},'goog:loggingPrefs':{'browser':'ALL'}}}})['sessionId'];sessions.append(s)
   h.call('/session/'+s+'/timeouts',{'script':120000});h.call('/session/'+s+'/url',{'url':installed['publicOrigin']+'/hidden/'})
   h.wait(lambda:js(s,'return window.desktopLab?.guestState==="ready"&&!desktopLab.lifecycle.blocked'),150)
   js(s,'window.memoryVM=v86Instance;window.memorySession=currentSession;window.memoryDesktop=[...surfaces.values()][0];memoryDesktop.showStatus("account");')
   check('desktop default is one shared 128 MiB allowance',stats(s)['limits']['metadataBytes']==128*1048576)
   check('advanced session menu exposes the actual shared allowance',js(s,'return document.querySelector("[data-network-memory]")?.value==="128"'))
   js(s,'const f=document.querySelector("[data-network-memory]");f.value="256";f.dispatchEvent(new Event("change"));')
   check('menu raises allowance without changing identity or Linux',stats(s)['limits']['metadataBytes']==256*1048576 and js(s,'return currentSession===memorySession&&v86Instance===memoryVM'))
   task(s,'window.memoryBudget=(await import(params[0])).sessionBudget(currentSession);window.memoryHold=memoryBudget.metadata(40*1048576);return true;',['./'+graph['directory']+'/resource-budget.mjs'])
   js(s,'const f=document.querySelector("[data-network-memory]");f.value="32";f.dispatchEvent(new Event("change"));')
   check('shrinking below already-held state is refused without eviction',stats(s)['limits']['metadataBytes']==256*1048576 and js(s,'return document.querySelector("[data-network-memory]").value==="256"'))
   js(s,'memoryHold();memoryHold=null;const f=document.querySelector("[data-network-memory]");f.value="32";f.dispatchEvent(new Event("change"));memoryDesktop.closePopups();memoryDesktop.launch("chat");')
   h.wait(lambda:js(s,'return !!document.querySelector("[data-discovery]")'),20)
   h.call('/session/'+s+'/goog/cdp/execute',{'cmd':'Emulation.setDeviceMetricsOverride','params':{'width':390,'height':844,'deviceScaleFactor':1,'mobile':True}})
   js(s,'memoryDesktop.closePopups();memoryDesktop.showStatus("account");const f=document.querySelector("[data-network-memory]");f.closest("details").querySelector("summary").click();f.scrollIntoView({block:"nearest"});')
   h.wait(lambda:js(s,'const f=document.querySelector("[data-network-memory]"),p=f.closest(".status-popup"),r=p.getBoundingClientRect();return f.getBoundingClientRect().height>=44&&f.closest("details").querySelector("summary").getBoundingClientRect().height>=44&&r.left>=0&&r.right<=innerWidth&&r.bottom<=innerHeight'),10)
   check('phone advanced allowance controls are contained with 44px targets',True)
   js(s,'const f=document.querySelector("[data-network-memory]");f.value="64";f.dispatchEvent(new Event("change"));')
   check('phone allowance change reaches the same shared budget',stats(s)['limits']['metadataBytes']==64*1048576)
   js(s,'desktopNetwork.configureMemoryBudgetMiB(32);memoryDesktop.closePopups();')
   h.call('/session/'+s+'/goog/cdp/execute',{'cmd':'Emulation.clearDeviceMetricsOverride','params':{}})
   before=stats(s);check('32 MiB profile remains usable with discovery still offline',before['limits']['metadataBytes']==32*1048576 and before['discovery']['status']=='offline' and before['budget']['support']==0)
   action(s,'start');h.wait(lambda:stats(s)['discovery']['status']=='ready',30)
   started=stats(s);check('explicit discovery start opens one authenticated support connection',started['budget']['support']==1 and started['budget']['connections']==1)
   check('unused support buffers are charged only on discovery start',started['budget']['metadataBytes']-before['budget']['metadataBytes']>=4*1048576)
   budgets.append({'beforeDiscovery':before['budget'],'startedDiscovery':started['budget']})
  left,right=sessions;right_sid=js(right,'return currentSession.public.sid')
  action(left,'sample');h.wait(lambda:any(right_sid[:8] in s['label'] for s in stats(left)['discovery']['samples']),20)
  sample=next(s['id'] for s in stats(left)['discovery']['samples'] if right_sid[:8] in s['label'])
  js(left,'document.querySelector("[data-discovery-sample]").value=arguments[0];',[sample]);action(left,'invite')
  h.wait(lambda:len(stats(right)['discovery']['invitations'])==1,25);action(right,'accept')
  for s in sessions:h.wait(lambda:js(s,'return desktopNetwork.appContext().pool.firstReady()?.state==="ready"'),40)
  check('real steward discovery establishes RTC in the same desktop peer pool',all(stats(s)['budget']['connections']==2 for s in sessions))
  for s in sessions:js(s,'window.memoryLink=desktopNetwork.appContext().pool.firstReady().link;')
  task(left,'await memoryLink.send("MEMORY_DISCOVERY_before_stop");return true;');h.wait(lambda:js(right,'return document.querySelector("[data-chat-history]").textContent.includes("MEMORY_DISCOVERY_before_stop")'),15)
  for s in sessions:
   action(s,'stop');h.wait(lambda:stats(s)['budget']['support']==0,15)
   check('stopping discovery preserves the established peer connection',js(s,'return desktopNetwork.appContext().pool.firstReady()?.link===memoryLink&&memoryLink.channel.readyState==="open"'))
   js(s,'desktopNetwork.configureMemoryBudgetMiB(128);')
   check('live allowance change preserves original VM identity and peer',js(s,'return v86Instance===memoryVM&&currentSession===memorySession&&desktopNetwork.appContext().pool.firstReady().link===memoryLink'))
  task(right,'await memoryLink.send("MEMORY_DISCOVERY_after_stop");return true;');h.wait(lambda:js(left,'return document.querySelector("[data-chat-history]").textContent.includes("MEMORY_DISCOVERY_after_stop")'),15)
  check('ordinary chat continues after discovery resources are released',True)
  for s in sessions:
   task(s,'desktopNetwork.close();await new Promise(r=>setTimeout(r,200));return true;');h.wait(lambda:all(v==0 for k,v in stats(s)['budget'].items() if k!='closed'),15)
  check('all shared resource charges release on session close',True)
  assert runtime==vm.runtime()
  return {'status':'PASS','checks':checks,'nativeManifestSHA256':runtime['manifestSHA256'],'budgetWitnesses':budgets,'realChromeContexts':2,'realStewardAndRTC':True,'phoneEmulated':True,'physicalPhoneTested':False,'physicalRAMReservationClaimed':False,'publicSiteChanged':False}
 except Exception:
  for i,s in enumerate(sessions):
   try:(ROOT/'.build/checks'/('network-memory-failure-'+str(time.time_ns())+'-'+str(i)+'.json')).write_text(json.dumps({'stats':stats(s),'text':js(s,'return document.body.innerText.slice(-4500)'),'console':h.call('/session/'+s+'/log',{'type':'browser'})},indent=2)+'\n')
   except Exception:pass
  raise
 finally:
  for s in sessions:
   try:js(s,'if(typeof memoryHold==="function")memoryHold();desktopNetwork.close();guestNetworkAdapter?.destroy();v86Instance?.destroy();')
   finally:h.call('/session/'+s,method='DELETE')
if __name__=='__main__':
 result={'status':'FAIL'}
 try:result.update(run())
 finally:
  result['sourceSHA256']=hashlib.sha256(Path(__file__).read_bytes()).hexdigest();path=ROOT/'.build/checks/network-memory-discovery-result.json'
  if path.exists():path.rename(path.with_name(path.stem+'-before-'+str(time.time_ns())+'.json'))
  path.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
