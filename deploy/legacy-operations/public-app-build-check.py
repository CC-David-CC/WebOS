#!/usr/bin/env python3
"""Real Chrome: bundled npm/local imports, CSS/assets, worker and view cleanup.

Uses temporary source/output trees and owned browser sessions. No public service,
user tab, boot image, account or managed deployment is changed.
"""
import argparse
import hashlib
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import threading
import time
import urllib.request

ROOT = Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location('public_builder', ROOT/'scripts/build-public-apps.py')
builder = importlib.util.module_from_spec(spec); spec.loader.exec_module(builder)
BASE = 'http://127.0.0.1:19515'

def call(path, data=None, method=None):
    request = urllib.request.Request(BASE+path, None if data is None else json.dumps(data).encode(),
                                    headers={'Content-Type': 'application/json'}, method=method)
    with urllib.request.urlopen(request, timeout=90) as response:
        return json.load(response)['value']

def run(node):
    checks = []; sessions = []; requests = []
    def check(label, condition):
        if not condition: raise AssertionError(label)
        checks.append(label)
    with tempfile.TemporaryDirectory(prefix='codi-app-pipeline-') as directory:
        root=Path(directory); source=root/'source'; app=source/'calculator'; app.mkdir(parents=True)
        (app/'workers').mkdir(); (app/'data').mkdir()
        (app/'index.mjs').write_text('''
import {Terminal} from '@xterm/xterm';
import {FitAddon} from '@xterm/addon-fit';
import '@xterm/xterm/css/xterm.css';
import './style.css';
import {greeting} from './sibling.mjs';
import icon from './icon.svg';
import wasmURL from './tiny.wasm';
export function mount(host){
 const element=document.createElement('div');element.className='window-content pipeline-fixture';
 element.style.cssText='width:640px;height:160px';
 const term=new Terminal({cols:40,rows:4});term.loadAddon(new FitAddon());term.open(element);term.write(greeting+'\\r\\n');
 window.fixtureTerm=term;window.mounts=(window.mounts||0)+1;
 const worker=new Worker(new URL('./workers/analysis.mjs',import.meta.url),{type:'module'});
 window.fixtureWorker=worker;worker.onmessage=event=>{window.workerReply=event.data.answer;window.workerAssetLoaded=event.data.asset;};worker.postMessage(40);
 const timer=setInterval(()=>window.ticks=(window.ticks||0)+1,10);
 host.onDispose(()=>clearInterval(timer));host.onDispose(()=>worker.terminate());
 window.addEventListener('fixture-event',()=>window.events=(window.events||0)+1,{signal:host.signal});
 window.resources=Promise.all([fetch(icon).then(r=>r.text()),fetch(wasmURL).then(r=>r.arrayBuffer()).then(b=>WebAssembly.compile(b)),fetch(new URL('./data/readme.txt',import.meta.url)).then(r=>r.text()),import('./later.mjs').then(m=>m.later)]);
 return {element,dispose(){window.disposals=(window.disposals||0)+1;window.signalAborted=host.signal.aborted;term.dispose();}};
}
''')
        (app/'sibling.mjs').write_text('export const greeting="Packaged local dependency";\n')
        (app/'later.mjs').write_text('export const later="Lazy chunk works";\n')
        (app/'workers/analysis.mjs').write_text('import {add} from "./math.mjs";import icon from "../icon.svg";onmessage=async e=>postMessage({answer:add(e.data,2),asset:(await (await fetch(icon)).text()).startsWith("<svg")});\n')
        (app/'workers/math.mjs').write_text('export const add=(a,b)=>a+b;\n')
        (app/'style.css').write_text('@import "./theme.css"; .pipeline-fixture{background-image:url("./icon.svg")}\n')
        (app/'theme.css').write_text('.pipeline-fixture{--fixture-theme:loaded;color:rgb(12,34,56)}\n')
        (app/'icon.svg').write_text('<svg xmlns="http://www.w3.org/2000/svg" width="1" height="1"/>\n')
        (app/'tiny.wasm').write_bytes(b'\0asm\x01\0\0\0')
        (app/'data/readme.txt').write_text('Explicit asset delivered\n')
        (app/'private.env').write_text('FIXTURE_PRIVATE_DO_NOT_PUBLISH=yes\n')
        (app/'app.json').write_text(json.dumps({'assets':['data/readme.txt'],'workers':{'analysis':'workers/analysis.mjs'}}))
        webroot=root/'web'; output=webroot/'assets/desktop'
        builder.build(source,output,['calculator'],node)
        first=(output/'apps.json').read_bytes(); item=json.loads(first)['apps'][0]
        bundle=webroot/Path(item['path']).parent
        check('complete graph emits CSS, imported image/WASM, worker, lazy chunk and npm notices',
              'index.css' in item['files'] and 'workers/analysis.mjs' in item['files'] and
              any(name.startswith('chunks/') for name in item['files']) and
              any(name.endswith('.wasm') for name in item['files']) and
              any('@xterm-xterm-6.0.0' in name for name in item['files']))
        check('unreferenced private source is not copied',not any('private.env' in name for name in item['files']))
        for name,record in item['files'].items():
            data=(bundle/name).read_bytes();assert hashlib.sha256(data).hexdigest()==record['sha256'] and len(data)==record['bytes']
        builder.build(source,output,['calculator'],node)
        check('repeated build keeps identical catalog and immutable bytes',(output/'apps.json').read_bytes()==first)
        (app/'sibling.mjs').write_text('export const greeting="Changed dependency";\n')
        builder.build(source,output,['calculator'],node)
        check('dependency-only edit changes bundle address and retains old bundle',json.loads((output/'apps.json').read_text())['apps'][0]['bundleSHA256']!=item['bundleSHA256'] and bundle.is_dir())
        # Restore the first graph for browser assertions.
        (app/'sibling.mjs').write_text('export const greeting="Packaged local dependency";\n')
        builder.build(source,output,['calculator'],node)
        stable=(output/'apps.json').read_bytes()
        def rejects(label):
            try: builder.build(source,output,['calculator'],node)
            except subprocess.CalledProcessError: pass
            else: raise AssertionError(label+' was accepted')
            check(label+' fails without publishing a partial catalog',(output/'apps.json').read_bytes()==stable)
        (app/'sibling.mjs').unlink(); rejects('missing dependency')
        outside=root/'secret.mjs';outside.write_text('export const greeting="outside";')
        (app/'sibling.mjs').symlink_to(outside);rejects('symlinked dependency');(app/'sibling.mjs').unlink()
        (app/'sibling.mjs').write_text('export const greeting="Packaged local dependency";\n')
        old=(app/'index.mjs').read_text()
        (app/'index.mjs').write_text(old+'\nimport "https://example.invalid/runtime.mjs";\n');rejects('remote runtime dependency')
        (app/'index.mjs').write_text(old+'\nconst name=window.fixtureModule;import(name);\n');rejects('unresolved computed module import')
        (app/'index.mjs').write_text(old)
        (app/'app.json').write_text(json.dumps({'assets':['private.env']}));rejects('private asset extension')
        (app/'app.json').write_text(json.dumps({'assets':['data/readme.txt'],'workers':{'analysis':'workers/analysis.mjs'}}))
        builder.build(source,output,['calculator'],node)
        original=output/'apps/calculator';original.rename(output/'apps/held-calculator')
        redirect=root/'redirect';redirect.mkdir();original.symlink_to(redirect,target_is_directory=True)
        rejects('symlinked output parent')
        original.unlink();(output/'apps/held-calculator').rename(original)
        check('output redirection writes no files outside public target',not list(redirect.iterdir()))
        (webroot/'network').mkdir()
        shutil.copyfile(ROOT/'network/strict-json.mjs',webroot/'network/strict-json.mjs')
        for name in ['apps.mjs','app-instance.mjs']:shutil.copyfile(ROOT/'assets/desktop'/name,output/name)
        shutil.copyfile(ROOT/'desktop-apps.js',webroot/'desktop-apps.js')
        (webroot/'index.html').write_text('''<!doctype html><meta charset="utf-8"><title>Owned app pipeline fixture</title>
<script>
const make=(tag,cls='',text='')=>{const n=document.createElement(tag);n.className=cls;n.textContent=text;return n;};
const textButton=(text,fn)=>{const n=make('button','',text);n.onclick=fn;return n;};
let currentSession={},guestState='ready',guestMessage='',identityConfig={};
const signedInSubject=()=>null,terminalSession=()=>{},sendTerminal=()=>{},sendTerminalBytes=()=>{},attachTerminalRenderer=()=>{},resizeTerminal=()=>{},setScreenKeyboardEnabled=()=>{},feedback=()=>{},applyScreenKeyboardPolicy=()=>{};
const desktopNetwork={appContext:()=>({})};
</script><script src="desktop-apps.js"></script>''')
        class Handler(SimpleHTTPRequestHandler):
            def __init__(self,*args,**kwargs):super().__init__(*args,directory=str(webroot),**kwargs)
            def do_GET(self):
                requests.append(self.path)
                if self.path.startswith('/hidden/'):
                    self.path=self.path[len('/hidden'):]
                return super().do_GET()
            def log_message(self,*args):pass
        server=ThreadingHTTPServer(('127.0.0.1',0),Handler);thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
        try:
            for prefix in ['', '/hidden']:
                sid=call('/session',{'capabilities':{'alwaysMatch':{'browserName':'chrome','goog:chromeOptions':{'binary':'/snap/chromium/current/usr/lib/chromium-browser/chrome','args':['--headless=new','--no-sandbox','--disable-dev-shm-usage']}}}})['sessionId'];sessions.append(sid)
                def js(script):return call('/session/'+sid+'/execute/sync',{'script':script,'args':[]})
                def task(script):
                    value=call('/session/'+sid+'/execute/async',{'script':'const done=arguments[0];(async()=>{'+script+'})().then(value=>done({value}),e=>done({error:e.message}));','args':[]})
                    assert 'error' not in value,value;return value.get('value')
                def wait(script):
                    end=time.monotonic()+20
                    while not js(script):
                        if time.monotonic()>end:raise AssertionError('Timed out: '+script)
                        time.sleep(.05)
                before=len(requests)
                call('/session/'+sid+'/url',{'url':'http://127.0.0.1:'+str(server.server_port)+prefix+'/'})
                check(prefix+' app graph stays unloaded before launch',not any('/apps/calculator/' in r for r in requests[before:]))
                js('window.w={id:1,title:"Fixture",app:"calculator"};window.desktop={windows:[w]};window.win=make("section","window");win.append(publicAppContent("calculator",desktop,w));document.body.append(win);')
                wait('return !!win.appView&&window.workerReply===42')
                values=task('return (await resources).map((v,i)=>i===1?v instanceof WebAssembly.Module:v);')
                check(prefix+' actual bundled npm xterm/local/lazy/worker/WASM/assets work in Chrome',values[0].startswith('<svg') and values[1] and values[2]=='Explicit asset delivered\n' and values[3]=='Lazy chunk works' and js('return !!document.querySelector(".xterm")&&workerAssetLoaded'))
                check(prefix+' generic CSS loads before mount',js('return getComputedStyle(win.firstElementChild).getPropertyValue("--fixture-theme").trim()==="loaded"'))
                task('const m=await import("./assets/desktop/apps.mjs");await m.loadApp("calculator");return true;')
                check(prefix+' app styles deduplicated',js('return document.querySelectorAll("link[data-public-app-style]").length===1'))
                js('win.hidden=true;window.savedElement=win.firstElementChild;')
                time.sleep(.08)
                check(prefix+' hiding/minimizing retains running view',js('return !win.appView.signal.aborted&&win.firstElementChild===savedElement&&!window.disposals'))
                js('window.finishedView=win.appView;disposePublicAppView(win);disposePublicAppView(win);win.remove();window.finalTicks=ticks;window.dispatchEvent(new Event("fixture-event"));')
                time.sleep(.08)
                check(prefix+' closing disposes once, aborts listener and stops timer',js('return disposals===1&&signalAborted&&finishedView.signal.aborted&&ticks===finalTicks&&!window.events'))
                # All callbacks run even if one disposer fails; mount failures abort too.
                check(prefix+' failed mount cleans allocated resources',task('const {mountApp}=await import("./assets/desktop/app-instance.mjs");let cleaned=0,s;try{mountApp({mount(h){s=h.signal;h.onDispose(()=>cleaned++);throw Error("expected");}},{});}catch{}return cleaned===1&&s.aborted;'))
                check(prefix+' disposer failure does not skip remaining cleanups',task('const {mountApp}=await import("./assets/desktop/app-instance.mjs");let n=0;const h=mountApp({mount(h){h.onDispose(()=>n++);h.onDispose(()=>{throw Error("expected cleanup error");});return {element:make("div","window-content"),dispose(){throw Error("expected dispose error");}};}},{});const errors=h.dispose();return errors.length===2&&n===1&&h.dispose().length===0;'))
                # An app removed before its module promise settles never mounts.
                js('window.late=make("section","window");late.append(publicAppContent("calculator",desktop,w));document.body.append(late);late.remove();')
                time.sleep(.1)
                check(prefix+' close during lazy load never mounts orphan resources',js('return mounts===1'))
                call('/session/'+sid,method='DELETE');sessions.remove(sid)
        finally:
            for sid in sessions:call('/session/'+sid,method='DELETE')
            server.shutdown();thread.join(3);server.server_close()
    return {'status':'PASS','checks':checks,'count':len(checks),'liveChanged':False,'physicalPhoneTested':False}

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--node',required=True);args=parser.parse_args()
    result={'status':'FAIL'}
    try:result=run(args.node)
    finally:
        names=['scripts/build-public-apps.py','scripts/public-app-build-check.py','tools/app-builder/build.mjs','tools/app-builder/package.json','tools/app-builder/package-lock.json','assets/desktop/apps.mjs','assets/desktop/app-instance.mjs','desktop-apps.js','app.js','terminal.js']
        result['sha256']={name:hashlib.sha256((ROOT/name).read_bytes()).hexdigest() for name in names}
        output=ROOT/'.build/checks/public-app-build-result.json';output.parent.mkdir(exist_ok=True,parents=True)
        if output.exists():output.rename(output.with_name('public-app-build-before-'+str(time.time_ns())+'.json'))
        output.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
