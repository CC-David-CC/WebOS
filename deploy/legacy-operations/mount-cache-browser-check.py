#!/usr/bin/env python3
"""Real Chrome old/new workers and CacheStorage across root/hidden transitions.

Owned localhost secure-context fixture with authentic sealed public workers and
assets. Identity metadata is a context stub; no account/VM or public TLS claim.
"""
import asyncio,hashlib,importlib.util,json,time
from pathlib import Path
from aiohttp import web

ROOT=Path(__file__).resolve().parent.parent
OLD=ROOT/'.build/releases/connected-terminal-scroll-r2'
NEW=ROOT/'.build/releases/connected-root-cache-r2'
spec=importlib.util.spec_from_file_location('mount_cache_helpers',ROOT/'scripts/touch-preview-check.py');helpers=importlib.util.module_from_spec(spec);spec.loader.exec_module(helpers);call,wait=helpers.call,helpers.wait


def browser(origin,client_path):
    sid=call('/session',{'capabilities':{'alwaysMatch':{'browserName':'chrome','goog:chromeOptions':{'binary':'/snap/chromium/current/usr/lib/chromium-browser/chrome','args':['--headless=new','--no-sandbox','--disable-dev-shm-usage']},'goog:loggingPrefs':{'browser':'ALL'}}}})['sessionId'];checks=[]
    def js(code,args=[]):return call('/session/'+sid+'/execute/sync',{'script':code,'args':args})
    def task(code,args=[]):
        r=call('/session/'+sid+'/execute/async',{'script':'const params=arguments,done=arguments[arguments.length-1];(async()=>{'+code+'})().then(value=>done({ok:true,value}),error=>done({ok:false,error:error.stack}));','args':args});assert r['ok'],r;return r.get('value')
    def check(name,value):assert value,name;checks.append(name)
    def navigate(path):call('/session/'+sid+'/url',{'url':origin+path})
    def import_client():task('window.mountCache=await import(params[0]);return true;',[origin+'/'+client_path])
    def config(mode):task('const r=await fetch("/fixture/phase",{method:"POST",body:params[0]});if(!r.ok)throw Error("Fixture phase refused");return true;',[mode])
    def persistent_sentinels():
        return task('''const db=await new Promise((resolve,reject)=>{const r=indexedDB.open('private-mount-test',1);r.onsuccess=()=>resolve(r.result);r.onerror=()=>reject(r.error);});
          const value=await new Promise((resolve,reject)=>{const t=db.transaction('documents'),r=t.objectStore('documents').get('draft');r.onsuccess=()=>resolve(r.result);r.onerror=()=>reject(r.error);});db.close();
          const names=['test-private-cache','foreign-cache','codi-public-v1|/desktop/|sentinel'],cachesPresent=await caches.keys(),registrations=await navigator.serviceWorker.getRegistrations();
          for(const name of names){if(!cachesPresent.includes(name)||await (await (await caches.open(name)).match('/fixture/sentinel'))?.text()!=='KEEP_SENTINEL')return false;}
          return value==='DO_NOT_DELETE_PRIVATE_DRAFT'&&localStorage.getItem('private-mount-test')==='KEEP_LOCAL_PRIVATE'&&registrations.some(r=>new URL(r.scope).pathname==='/desktop/'&&r.active?.scriptURL===location.origin+'/fixture/prototype-worker.js');''')
    try:
        call('/session/'+sid+'/timeouts',{'script':120000});navigate('/hidden/cache-check.html')
        task('''localStorage.setItem('private-mount-test','KEEP_LOCAL_PRIVATE');
          await new Promise((resolve,reject)=>{const r=indexedDB.open('private-mount-test',1);r.onupgradeneeded=()=>r.result.createObjectStore('documents');r.onsuccess=()=>{const db=r.result,t=db.transaction('documents','readwrite');t.objectStore('documents').put('DO_NOT_DELETE_PRIVATE_DRAFT','draft');t.oncomplete=()=>{db.close();resolve();};t.onerror=()=>reject(t.error);};r.onerror=()=>reject(r.error);});
          for(const name of ['test-private-cache','foreign-cache','codi-public-v1|/desktop/|sentinel','codi-public-v1|/hidden/|stale-extra'])await (await caches.open(name)).put('/fixture/sentinel',new Response('KEEP_SENTINEL'));
          await navigator.serviceWorker.register('/fixture/prototype-worker.js',{scope:'/desktop/'});
          await navigator.serviceWorker.register('/hidden/assets/desktop/offline-worker.js',{scope:'/hidden/'});
          await navigator.serviceWorker.ready;return true;''')
        wait(lambda:js('return navigator.serviceWorker.controller?.scriptURL.endsWith("/hidden/assets/desktop/offline-worker.js")'),30)
        check('authentic previous hidden worker controls a warm browser profile',True)
        old_names=task('return (await caches.keys()).filter(n=>n.startsWith("codi-public-v1|/hidden/|"));')
        check('old worker installs verified public core assets alongside stale owned cache',len(old_names)>=2)
        config('root');navigate('/cache-check.html');import_client()
        task('await mountCache.registerDeviceCache();await navigator.serviceWorker.ready;return true;')
        wait(lambda:js('return navigator.serviceWorker.controller?.scriptURL===location.origin+"/assets/desktop/offline-worker.js"'),30)
        info=task('return await mountCache.deviceStorageInfo();')
        check('root registration retires the known hidden worker after server-context confirmation',info['mountRetirement']['status']=='retired' and info['mountRetirement']['workers']==1)
        check('root registration removes only owned hidden public caches',task('return !(await caches.keys()).some(n=>n.startsWith("codi-public-v1|/hidden/|"));'))
        check('root transition preserves prototype foreign caches localStorage and IndexedDB',persistent_sentinels())
        check('root worker installs its new verified core',task('return (await caches.keys()).some(n=>n.startsWith("codi-public-v1|/|"));'))
        again=task('return await mountCache.retirePreviousMount();')
        check('repeated root retirement is idempotent',again['workers']==0 and again['cachesRemoved']==0)
        stale=task('return await mountCache.retirePreviousMount(new URL("/hidden/",location.origin));')
        check('cached hidden-page context cannot retire the currently authoritative root worker',stale['status']=='not-current-mount' and task('return !!(await navigator.serviceWorker.getRegistration("/"));'))
        ignored=task('return await mountCache.retirePreviousMount(new URL("/desktop/",location.origin));')
        check('prototype mount never participates in desktop cache retirement',ignored['status']=='not-applicable')
        call('/session/'+sid+'/goog/cdp/execute',{'cmd':'Network.enable','params':{}})
        call('/session/'+sid+'/goog/cdp/execute',{'cmd':'Network.emulateNetworkConditions','params':{'offline':True,'latency':0,'downloadThroughput':0,'uploadThroughput':0}})
        deferred=task('return await mountCache.retirePreviousMount();')
        call('/session/'+sid+'/goog/cdp/execute',{'cmd':'Network.emulateNetworkConditions','params':{'offline':False,'latency':0,'downloadThroughput':-1,'uploadThroughput':-1}})
        check('offline metadata does not authorize destructive cache or worker retirement',deferred['status']=='deferred' and task('return !!(await navigator.serviceWorker.getRegistration("/"));'))
        config('rollback');navigate('/')
        check('warm root navigation loads the authoritative blog after rollback',js('return document.querySelector("h1")?.textContent==="AUTHORITATIVE BLOG"'))
        check('rollback blog HTML never replaces the verified desktop cache',task('for(const n of await caches.keys())if(n.startsWith("codi-public-v1|/|")){const r=await (await caches.open(n)).match(new URL("/index.html",location.origin));if(r&&(await r.text()).includes("AUTHORITATIVE BLOG"))return false;}return true;'))
        navigate('/hidden/cache-check.html');import_client()
        task('await mountCache.registerDeviceCache();await navigator.serviceWorker.ready;return true;')
        wait(lambda:js('return navigator.serviceWorker.controller?.scriptURL===location.origin+"/hidden/assets/desktop/offline-worker.js"'),30)
        result=task('return await mountCache.deviceStorageInfo();')
        check('authoritative rollback retires only the owned root worker',result['mountRetirement']['workers']==1 and not task('return !!(await navigator.serviceWorker.getRegistration("/"));'))
        check('rollback removes root public caches while retaining current hidden assets',task('const n=await caches.keys();return !n.some(n=>n.startsWith("codi-public-v1|/|"))&&n.some(n=>n.startsWith("codi-public-v1|/hidden/|"));'))
        check('rollback preserves all unrelated storage and prototype registration',persistent_sentinels())
        task('await navigator.serviceWorker.register("/fixture/foreign-worker.js",{scope:"/"});return true;')
        wait(lambda:task('return !!(await navigator.serviceWorker.getRegistration("/"))?.active;'),20)
        foreign=task('return await mountCache.retirePreviousMount();')
        check('worker at previous scope with a foreign script is never unregistered',foreign['workers']==0 and task('return (await navigator.serviceWorker.getRegistration("/"))?.active?.scriptURL.endsWith("/fixture/foreign-worker.js");'))
        config('oversize');oversize=task('return await mountCache.retirePreviousMount();');config('rollback')
        check('oversized configuration metadata defers retirement without clearing private stores',oversize['status']=='deferred' and persistent_sentinels())
        return {'status':'PASS','scope':__doc__,'checks':checks,'authenticOldAndNewPublicWorkers':True,'privateBrowserStoresPreserved':True,'realVMOrAccountUsed':False,'publicDeploymentChanged':False}
    finally:call('/session/'+sid,method='DELETE')


async def run():
    phase={'value':'hidden'};origins={};old_files=json.loads((OLD/'release.json').read_text())['files'];new_files=json.loads((NEW/'release.json').read_text())['files'];client_path=json.loads((ROOT/'.build/checks/root-cache-build-result.json').read_text())['clientPath']
    async def route(request):
        path=request.path
        if path=='/fixture/phase' and request.method=='POST':
            value=await request.text()
            if value not in ['hidden','root','rollback','oversize']:raise web.HTTPBadRequest()
            phase['value']=value;return web.Response(text='ok')
        if path in ['/fixture/prototype-worker.js','/fixture/foreign-worker.js']:
            return web.Response(text='self.addEventListener("install",e=>self.skipWaiting());self.addEventListener("activate",e=>e.waitUntil(self.clients.claim()));',content_type='text/javascript',headers={'Service-Worker-Allowed':'/'})
        if path in ['/cache-check.html','/hidden/cache-check.html']:return web.Response(text='<!doctype html><meta charset="utf-8"><title>Owned mount cache fixture</title>',content_type='text/html')
        if path=='/' and phase['value']=='rollback':return web.Response(text='<!doctype html><h1>AUTHORITATIVE BLOG</h1>',content_type='text/html')
        if path in ['/config.json','/hidden/config.json']:
            if phase['value']=='oversize':return web.Response(body=b' '*70000,content_type='application/json')
            base='' if phase['value']=='root' else '/hidden'
            return web.json_response({'identity':{'mode':'server','issuer':origins['value'],'apiBase':base+'/api/v1'}},headers={'Cache-Control':'no-store'})
        hidden=path.startswith('/hidden/');folder=OLD if hidden and phase['value']=='hidden' else NEW;records=old_files if folder==OLD else new_files
        name=path[len('/hidden/'):] if hidden else path.lstrip('/')
        if name not in records:raise web.HTTPNotFound()
        raw=(folder/name).read_bytes();record=records[name];assert record=={'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()}
        headers={'Cache-Control':'no-store'}
        if name=='assets/desktop/offline-worker.js':headers['Service-Worker-Allowed']='/hidden/' if hidden else '/'
        typ='text/javascript' if name.endswith(('.js','.mjs')) else 'text/css' if name.endswith('.css') else 'application/json' if name.endswith('.json') else 'text/html' if name.endswith('.html') else 'application/octet-stream'
        return web.Response(body=raw,content_type=typ,headers=headers)
    app=web.Application();app.router.add_route('*','/{path:.*}',route);runner=web.AppRunner(app,access_log=None);await runner.setup();site=web.TCPSite(runner,'127.0.0.1',0);await site.start();origins['value']='http://127.0.0.1:'+str(site._server.sockets[0].getsockname()[1])
    try:return await asyncio.to_thread(browser,origins['value'],client_path)
    finally:await runner.cleanup()


if __name__=='__main__':
    result={'status':'FAIL'}
    try:result.update(asyncio.run(run()))
    finally:
        result['scriptSHA256']=hashlib.sha256(Path(__file__).read_bytes()).hexdigest();out=ROOT/'.build/checks/mount-cache-browser-result.json'
        if out.exists():out.rename(out.with_name(out.stem+'-before-'+str(time.time_ns())+'.json'))
        out.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
