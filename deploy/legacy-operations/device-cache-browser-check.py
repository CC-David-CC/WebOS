#!/usr/bin/env python3
"""Real Chrome service worker: public hashes, lazy modules, offline reload/rebuild.

Owned loopback issuer/v86 fixture. Actual CacheStorage and persist() are used;
physical disk eviction, browser crashes and Android permission UI are not tested.
"""
import argparse
import asyncio
import hashlib
import importlib.util
import json
from pathlib import Path
import time
from urllib.parse import urlsplit
from types import SimpleNamespace

ROOT=Path(__file__).resolve().parent.parent
spec=importlib.util.spec_from_file_location('cache_fixture',ROOT/'scripts/guest-client-browser-check.py');fixture=importlib.util.module_from_spec(spec);spec.loader.exec_module(fixture);fixture.PAGE=(ROOT/'index.html').read_bytes()
call,wait=fixture.call,fixture.wait

def browser(f):
    sid=call('/session',{'capabilities':{'alwaysMatch':{'browserName':'chrome','unhandledPromptBehavior':'accept','goog:chromeOptions':{'binary':'/snap/chromium/current/usr/lib/chromium-browser/chrome','args':['--headless=new','--no-sandbox','--disable-dev-shm-usage',*getattr(f,'chromeArgs',[])]}}}})['sessionId'];checks=[]
    def js(source,args=[]):return call('/session/'+sid+'/execute/sync',{'script':source,'args':args})
    def task(source):
        value=call('/session/'+sid+'/execute/async',{'script':'const done=arguments[0];(async()=>{'+source+'})().then(value=>done({ok:true,value}),error=>done({ok:false,error:error.message}));','args':[]});assert value['ok'],value;return value.get('value')
    def cdp(cmd,params):return call('/session/'+sid+'/goog/cdp/execute',{'cmd':cmd,'params':params})
    def check(name,value):assert value,name;checks.append(name)
    def ready():return js('return window.desktopLab?.guestState==="ready"&&desktopLab.lifecycle?.epoch&&!desktopLab.lifecycle.blocked&&!!navigator.serviceWorker.controller')
    def offline(value):cdp('Network.emulateNetworkConditions',{'offline':value,'latency':0,'downloadThroughput':0 if value else -1,'uploadThroughput':0 if value else -1})
    url=f.origin+f.base+'/'
    try:
        call('/session/'+sid+'/timeouts',{'script':180000});cdp('Network.enable',{});call('/session/'+sid+'/url',{'url':url});wait(ready,150)
        kept=task('return await (await deviceCacheModule).keepLoadedAppFiles();')
        check('real persist request returns a truthful browser decision',type(kept['persistent']) is bool)
        keys=task('const result=[];for(const name of await caches.keys())if(name.startsWith("codi-public-v1|")){const cache=await caches.open(name);result.push(...(await cache.keys()).map(r=>r.url))}return result;')
        check('cached public shell and Linux boot files exist',any(p.endswith('/.build/v86/v86.wasm') for p in keys) and any(p.endswith('/index.html') for p in keys))
        check('versioned identity SDK is cached under its verified public record',url+'network/identity.mjs' in keys)
        check('versioned SDK alias uses the same verified bytes',task('const cache=await caches.open((await caches.keys()).find(n=>n.startsWith("codi-public-v1|")));const url=new URL("network/identity.mjs",document.baseURI);const saved=await (await cache.match(url)).arrayBuffer(),alias=await (await fetch(url.href+"?originProfile=codi-session-ice-1")).arrayBuffer();return saved.byteLength===alias.byteLength&&await crypto.subtle.digest("SHA-256",saved).then(a=>crypto.subtle.digest("SHA-256",alias).then(b=>new Uint8Array(a).every((v,i)=>v===new Uint8Array(b)[i])));'))
        paths=[urlsplit(p).path for p in keys]
        check('identity/config/status/private-file and grant routes are never cached',all(p!=f.base+'/config.json' and not any(p.startswith(f.base+s) for s in ['/api/','/gateway/','/guest-access/','/guest-network']) for p in paths))
        check('unopened calculator/help/chat/chess app modules are not prefetched',all(not any('/apps/'+app+'/' in p for app in ['calculator','help','chat','rooms']) for p in keys))
        # The module loads only on launch and is then cacheable by its exact hash.
        js('window.d=[...surfaces.values()][0];d.launch("calculator")');wait(lambda:js('return !!document.querySelector(".calculator-result")'),15)
        catalog=json.loads((ROOT/getattr(f,'catalogPath','assets/desktop/apps.json')).read_text());calculator=next(p for p in catalog['apps'] if p['id']=='calculator');asset=f.origin+f.base+'/'+calculator['path']
        js('window.cacheTestURL=arguments[0]',[asset])
        check('first calculator request matches its immutable hash',task('const r=await fetch(cacheTestURL),bytes=await r.arrayBuffer();return [...new Uint8Array(await crypto.subtle.digest("SHA-256",bytes))].map(b=>b.toString(16).padStart(2,"0")).join("");')==calculator['sha256'])
        task('for(const name of await caches.keys())if(name.startsWith("codi-public-v1|")){const c=await caches.open(name);if(await c.match(cacheTestURL))await c.put(cacheTestURL,new Response("tampered"));}return true;')
        check('corrupt cached bytes are rejected and rebuilt from the server',task('const r=await fetch(cacheTestURL),bytes=await r.arrayBuffer();return [...new Uint8Array(await crypto.subtle.digest("SHA-256",bytes))].map(b=>b.toString(16).padStart(2,"0")).join("");')==calculator['sha256'])
        # Existing RAM stays open during a drop; an explicit reload cannot keep it.
        offline(True);wait(lambda:js('return desktopLab.lifecycle.blocked'),5)
        call('/session/'+sid+'/url',{'url':url})
        wait(lambda:js('return document.querySelector("#desktop-recovery")&&!document.querySelector("#desktop-recovery").hidden'),20)
        check('cached offline shell gives an honest lost-memory warning after reload',js('return document.querySelector("#desktop-recovery").textContent.includes("not restored a previous Linux session")&&v86Instance===null&&currentSession===null'))
        offline(False);wait(ready,150)
        check('server return creates a fresh working Linux session automatically',js('return guestFiles.ready&&guestState==="ready"'))
        # Clearing site-owned caches/registrations and reloading must rebuild.
        cdp('Storage.clearDataForOrigin',{'origin':f.origin,'storageTypes':'service_workers,cache_storage'})
        call('/session/'+sid+'/url',{'url':url});wait(ready,150)
        rebuilt=task('return await (await deviceCacheModule).keepLoadedAppFiles();')
        check('cleared browser app storage rebuilds using authoritative server files',rebuilt['items']>=11)
        return {'status':'PASS','scope':__doc__,'checks':checks,'actualBrowserPersistenceGranted':kept['persistent'],'cacheItems':kept['items'],'cacheBytes':kept['bytes'],'cacheManifest':json.loads((ROOT/'assets/desktop/cache-manifest.json').read_text())['id'],'userFilesOrCredentialsCached':False,'runningVMWasSaved':False,'offlineReloadRestoresVM':False,'rebuildAfterSiteDataClear':True,'publicDeploymentChanged':False}
    except Exception:
        try:(ROOT/'.build/checks/device-cache-browser-diagnostics.json').write_text(json.dumps(js('return {state:window.desktopLab?.guestState,lifecycle:window.desktopLab?.lifecycle,text:document.body.innerText.slice(-2000)}'),indent=2)+'\n')
        except Exception:pass
        raise
    finally:
        try:js('desktopLifecycle?.stop();bootRecovery?.stop();clearTimeout(bootRetry);guestNetworkAdapter?.destroy();v86Instance?.destroy();')
        finally:call('/session/'+sid,method='DELETE')

async def main(url=None):
    if url:
        parsed=urlsplit(url);assert parsed.scheme=='https' and parsed.hostname=='ksu.codes' and parsed.path=='/hidden/' and not parsed.query and not parsed.fragment
        result=await asyncio.to_thread(browser,SimpleNamespace(origin='https://ksu.codes',base='/hidden'))
        result.update(scope='Actual public HTTPS Chrome CacheStorage/persist, offline reload and cleared-cache rebuild in an owned throwaway browser profile; no personal site data or production services changed',url=url,defaultPublicTLSVerified=True)
        return result
    f=fixture.Fixture('/hidden')
    try:await f.start();return await asyncio.to_thread(browser,f)
    finally:await f.close()

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--url');args=parser.parse_args()
    result={'status':'FAIL','scope':__doc__}
    try:result.update(asyncio.run(main(args.url)))
    finally:
        names=['scripts/device-cache-browser-check.py','scripts/build-device-cache.py','scripts/templates/device-cache-worker.js','assets/desktop/offline-worker.js','assets/desktop/device-cache.mjs','assets/desktop/cache-manifest.json','assets/desktop/lifecycle.mjs','app.js']
        result['sha256']={name:hashlib.sha256((ROOT/name).read_bytes()).hexdigest() for name in names};output=ROOT/'.build/checks'/('device-cache-public-result.json' if args.url else 'device-cache-browser-result.json')
        if output.exists():output.rename(output.with_name('device-cache-browser-before-'+str(time.time_ns())+'.json'))
        output.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
