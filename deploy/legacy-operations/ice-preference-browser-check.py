#!/usr/bin/env python3
"""Real cached R16, modern and mixed app/module clients against one issuer.

Owned loopback guest/issuer fixture only, not installed systemd or public TLS.
Old bytes come from the verified immutable live R16/native13 artifact. Actual
CacheStorage/service worker, v86, key proofs and SQLite accounts are exercised.
"""
import asyncio,hashlib,importlib.util,json,mimetypes,time
from pathlib import Path
from aiohttp import web
ROOT=Path(__file__).resolve().parent.parent
spec=importlib.util.spec_from_file_location('ice_browser_fixture',ROOT/'scripts/guest-client-browser-check.py');fixture=importlib.util.module_from_spec(spec);spec.loader.exec_module(fixture)
from origin_service.ice_preference import PreferenceService
from origin_service.turn import TurnPolicy
fixture.Service=PreferenceService;fixture.PAGE=(ROOT/'index.html').read_bytes();call,wait=fixture.call,fixture.wait
OLD=ROOT/'.build/releases/connected-maintenance-r3'

class Fixture(fixture.Fixture):
 async def start(self):
  assert hashlib.sha256((OLD/'connected-release.json').read_bytes()).hexdigest()=='abb67a1f7a2e718c006cf0784dd216cceebb49982d4a8c03f14b7e21bfff2abf'
  self.old_public=json.loads((OLD/'release.json').read_text())['files']
  await super().start();self.issuer.turn_policy=TurnPolicy(b'x'*32,['turns:fixture.invalid:443?transport=tcp'],'relay')
 async def proxy(self,request):
  path=request.path[len(self.base):] if self.base else request.path
  build=request.cookies.get('codi_fixture_build')
  if path=='/':
   response=await super().proxy(request);build=request.query.get('build',build or 'modern')
   if build in ('legacy','mixed'):response.body=(OLD/'index.html').read_bytes()
   response.set_cookie('codi_fixture_build',build,path=self.base+'/',samesite='Strict');return response
  name=path.lstrip('/')
  if name!='config.json' and name in self.old_public and (build=='legacy' or build=='mixed' and name=='app.js'):
   typ='text/javascript' if name.endswith('.mjs') else mimetypes.guess_type(name)[0] or 'application/octet-stream'
   response=web.Response(body=(OLD/name).read_bytes(),content_type=typ,headers={'Cross-Origin-Opener-Policy':'same-origin','Cross-Origin-Embedder-Policy':'require-corp','Cache-Control':'no-store'})
   if name=='assets/desktop/offline-worker.js':response.headers['Service-Worker-Allowed']=self.base+'/'
   return response
  return await super().proxy(request)
 def replace(self,transport):
  old=self.issuer;self.issuer=type(old)(old.c,base_path=self.base,turn_policy=TurnPolicy(b'x'*32,['turns:fixture.invalid:443?transport=tcp'],transport))
  self.http.set_app(fixture.staging.HeadSupport(fixture.GuestAuthority(self.issuer,self.policy.sha256)))

def browser(f):
 sessions=[];checks=[]
 def js(s,source,args=[]):return call('/session/'+s+'/execute/sync',{'script':source,'args':args})
 def task(s,source):
  r=call('/session/'+s+'/execute/async',{'script':'const done=arguments[0];(async()=>{'+source+'})().then(value=>done({ok:true,value}),error=>done({ok:false,error:error.message}));','args':[]});assert r['ok'],r;return r.get('value')
 def check(name,value):assert value,name;checks.append(name)
 def open_client(build):
  s=call('/session',{'capabilities':{'alwaysMatch':{'browserName':'chrome','goog:chromeOptions':{'binary':'/snap/chromium/current/usr/lib/chromium-browser/chrome','args':['--headless=new','--no-sandbox','--disable-dev-shm-usage']}}}})['sessionId'];sessions.append(s)
  call('/session/'+s+'/timeouts',{'script':120000});call('/session/'+s+'/url',{'url':f.origin+f.base+'/?build='+build})
  wait(lambda:js(s,'return window.desktopLab?.guestState==="ready"&&desktopLab.lifecycle?.epoch&&!desktopLab.lifecycle.blocked'),150)
  if build!='mixed':wait(lambda:js(s,'return !!navigator.serviceWorker.controller'),30)
  return s
 def keep(s):
  js(s,'window.savedVM=v86Instance;window.savedFS=v86Instance.fs9p;window.oldSession=currentSession.id;window.d=[...surfaces.values()][0];d.launch("text")')
  wait(lambda:js(s,'return !!document.querySelector(".guest-editor")'),15)
  js(s,'window.savedEditor=document.querySelector(".guest-editor");savedEditor.value="unsaved cached-client draft";savedEditor.dispatchEvent(new Event("input",{bubbles:true}));savedEditor.focus();savedEditor.setSelectionRange(3,8)')
  js(s,'sendTerminal(2,arguments[0])',["export ICE_KEEP=shell_kept; printf file_kept > /home/guest/ice-keep.txt; printf '\\nICE_KEEP_READY\\n'\r"])
  wait(lambda:js(s,'return serialScreen.text().includes("\\nICE_KEEP_READY\\n")'),30)
 def retained(s):
  check('same VM, filesystem, draft and cursor after restart',js(s,'return v86Instance===savedVM&&v86Instance.fs9p===savedFS&&savedEditor.isConnected&&savedEditor.value==="unsaved cached-client draft"&&savedEditor.selectionStart===3&&savedEditor.selectionEnd===8'))
  token='ICE_'+str(time.time_ns());js(s,'sendTerminal(2,arguments[0])',['printf "\\n'+token+'=%s:" "$ICE_KEEP"; cat /home/guest/ice-keep.txt\r'])
  wait(lambda:js(s,'return serialScreen.text().includes(arguments[0])',['\n'+token+'=shell_kept:file_kept']),30)
 def native_policy(s,expected):
  result=task(s,'const {PeerLink}=await import("./network/peer.mjs");const link=new PeerLink(currentSession,identityConfig);try{link.create();return link.pc.getConfiguration().iceTransportPolicy}finally{link.close()}')
  check('native RTC policy is '+expected,result==expected)
 try:
  legacy=open_client('legacy');modern=open_client('modern')
  check('actual old identity module stays loaded',task(legacy,'return !("icePreference" in await import("./network/identity.mjs"));'))
  check('old app served from original immutable bytes',task(legacy,'const bytes=await (await fetch("app.js")).arrayBuffer();return [...new Uint8Array(await crypto.subtle.digest("SHA-256",bytes))].map(n=>n.toString(16).padStart(2,"0")).join("");')=='514d2e56d88dd9e5482c82a8751bd46fa904562e30735ba6bbf0f4f8bbcc844f')
  check('old worker has populated the actual public cache',task(legacy,'return (await caches.keys()).some(n=>n.includes("1224e578c8f30cce633a593cbad0990513ac35f349d8dd7c868166d7f202ee66"));'))
  for s in [legacy,modern]:keep(s);native_policy(s,'relay')
  f.replace('all')
  for s in [legacy,modern]:wait(lambda:js(s,'return !desktopLab.lifecycle.blocked&&currentSession.id!==oldSession'),25);retained(s)
  native_policy(legacy,'relay');native_policy(modern,'all')
  name='ice_'+__import__('uuid').uuid4().hex[:12];password=__import__('secrets').token_urlsafe(32)
  js(modern,'window.qaName=arguments[0];window.qaPassword=arguments[1]',[name,password]);registered=task(modern,'await changeAccount("register",qaName,qaPassword);return currentSession.public.kind;')
  check('modern register succeeds with signed preference',registered=='registered');native_policy(modern,'all')
  mixed=open_client('mixed');check('mixed app uses old recovery code',js(mixed,'return typeof recoverDesktopSession==="undefined"'))
  js(mixed,'window.qaName=arguments[0];window.qaPassword=arguments[1]',[name,password]);task(mixed,'await changeAccount("signin",qaName,qaPassword);return true;');native_policy(mixed,'all')
  check('old app plus new identity module signs in to the same account',js(mixed,'return currentSession.public.kind==="registered"') and js(mixed,'return currentSession.public.sub')==js(modern,'return currentSession.public.sub'))
  for s in [legacy,modern]:js(s,'window.oldSession=currentSession.id')
  f.replace('relay')
  for s in [legacy,modern]:wait(lambda:js(s,'return !desktopLab.lifecycle.blocked&&currentSession.id!==oldSession'),25);retained(s);native_policy(s,'relay')
  return {'status':'PASS','scope':__doc__,'checks':checks,'legacyWorkerActuallyCached':True,'oldR16NoReloadAcrossBothPolicyChanges':True,'modernNoReloadAcrossBothPolicyChanges':True,'mixedOldAppNewModuleSignin':True,'mixedWorkerInstallationClaimed':False,'actualRTCPeerConfigurationChecked':True,'RTCTransportOrTURNConnectivityProven':False,'publicOrInstalledRuntimeChanged':False,'physicalAndroidVerified':False}
 finally:
  for s in sessions:
   try:js(s,'desktopLifecycle?.stop();desktopNetwork.close();guestNetworkAdapter?.destroy();v86Instance?.destroy()')
   finally:call('/session/'+s,method='DELETE')

async def main():
 f=Fixture('/hidden')
 try:await f.start();return await asyncio.to_thread(browser,f)
 finally:await f.close()

if __name__=='__main__':
 value={'status':'FAIL','scope':__doc__}
 try:value.update(asyncio.run(main()))
 finally:
  names=['scripts/ice-preference-browser-check.py','origin_service/ice_preference.py','network/identity.mjs','assets/desktop/recovery-policy.mjs','app.js']
  value['sha256']={n:hashlib.sha256((ROOT/n).read_bytes()).hexdigest() for n in names};output=ROOT/'.build/checks/ice-preference-browser-result.json'
  if output.exists():output.rename(output.with_name(output.stem+'-before-'+str(time.time_ns())+'.json'))
  output.write_text(json.dumps(value,indent=2)+'\n');print(json.dumps(value,indent=2))
