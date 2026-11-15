#!/usr/bin/env python3
"""Repeated real Chrome/v86 launches, UI Close, resource counts and stale reads."""
import asyncio
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import time
ROOT=Path(__file__).resolve().parent.parent
spec=importlib.util.spec_from_file_location('app_stress_fixture',ROOT/'scripts/guest-client-browser-check.py');f=importlib.util.module_from_spec(spec);spec.loader.exec_module(f);f.PAGE=(ROOT/'index.html').read_bytes();call,wait=f.call,f.wait

def browser(fixture):
    sid=call('/session',{'capabilities':{'alwaysMatch':{'browserName':'chrome','goog:chromeOptions':{'binary':'/snap/chromium/current/usr/lib/chromium-browser/chrome','args':['--headless=new','--no-sandbox','--disable-dev-shm-usage']},'goog:loggingPrefs':{'browser':'ALL'}}}})['sessionId'];checks=[];samples=[]
    def js(code,args=[]):return call('/session/'+sid+'/execute/sync',{'script':code,'args':args})
    def task(code):
        value=call('/session/'+sid+'/execute/async',{'script':'const done=arguments[0];(async()=>{'+code+'})().then(value=>done({ok:true,value}),error=>done({ok:false,error:error.stack}));','args':[]});assert value['ok'],value;return value.get('value')
    def check(label,value):assert value,label;checks.append(label)
    try:
        call('/session/'+sid+'/timeouts',{'script':180000});call('/session/'+sid+'/url',{'url':fixture.origin+fixture.base+'/'})
        wait(lambda:js('return window.desktopLab?.guestState==="ready"&&document.querySelector("[data-window=\\\"2\\\"]")?.appView'),150)
        js('window.d=[...surfaces.values()][0];window.keepVM=v86Instance;window.keepFS=v86Instance.fs9p;')
        js((ROOT/'scripts/fixtures/app-lifecycle-probe.js').read_text())
        task('''window.stressShellPids=[];window.stressApps=['calculator','help','chat','rooms','text','files','terminal'];window.cycleApps=async()=>{
          for(const app of stressApps){const w=d.launch(app);let node;
            for(let i=0;i<150;i++){node=document.querySelector('[data-window="'+w.id+'"]');if(node?.appView)break;await new Promise(r=>setTimeout(r,20));}
            if(!node?.appView)throw Error('App failed to mount: '+app);const view=node.appView;
            if(app==='calculator'){const input=node.querySelector('input');input.value='6*7';input.form.requestSubmit();if(!node.textContent.includes('42'))throw Error('Calculator failed');}
            if(app==='terminal'){node.querySelector('.xterm-terminal')?.terminal?.focus();const marker='STRESS_READY_'+w.id+'_PID=';sendTerminal(w.id,'printf "\\n'+marker+'%s\\n" "$$"\\r');let pid;
              for(let i=0;i<150;i++){const match=terminalSessions.get(w.id)?.screen.text().match(new RegExp('\\n'+marker+'([0-9]+)\\n'));if(match){pid=Number(match[1]);break;}await new Promise(r=>setTimeout(r,20));}
              if(!pid)throw Error('Shell did not respond');stressShellPids.push(pid);}
            node.querySelector('[aria-label="Close"]').click();if(!view.signal.aborted||node.isConnected||d.windows.includes(w))throw Error('Close failed: '+app);
          }
        };await cycleApps();await new Promise(r=>setTimeout(r,4500));return true;''')
        baseline=js('return appLifecycleProbe.snapshot()');budget=task('return (await desktopNetwork.stats()).budget;');samples.append({'cycle':0,'resources':baseline,'budget':budget})
        for batch in range(5):
            task('for(let i=0;i<5;i++)await cycleApps();await new Promise(r=>setTimeout(r,4500));return true;')
            snapshot=js('return appLifecycleProbe.snapshot()');used=task('return (await desktopNetwork.stats()).budget;');samples.append({'cycle':(batch+1)*5,'resources':snapshot,'budget':used})
            check('all app resources return to warm baseline after '+str((batch+1)*5)+' cycles',snapshot==baseline and used==budget)
        check('same Linux and shared filesystem survive 182 application opens/closes',js('return v86Instance===keepVM&&v86Instance.fs9p===keepFS'))
        pids=js('return stressShellPids');assert len(pids)==26
        marker='STRESS_CLOSED_PIDS_'+str(time.time_ns())
        command='stress_left=0; for stress_pid in '+ ' '.join(map(str,pids))+'; do [ ! -e /proc/$stress_pid ] || stress_left=$((stress_left+1)); done; printf "\\n'+marker+'=%s\\n" "$stress_left"\r'
        js('sendTerminal(2,arguments[0])',[command]);wait(lambda:js('return terminalSessions.get(2).screen.text().includes(arguments[0])',['\n'+marker+'=0\n']),20)
        check('all 26 closed Linux shell PIDs are gone from guest procfs',True)
        # Start an actual file read then close before its Promise resolves.
        result=task('''await guestFiles.write('/Documents/stress-read.txt','after close');const original=guestFiles.read;let finish;
          guestFiles.read=path=>path==='/Documents/stress-read.txt'?new Promise(resolve=>finish=resolve):original.call(guestFiles,path);
          const w=d.launch('text');w.editor={path:'/Documents/stress-read.txt',text:'before close',loaded:false,dirty:false};d.render();
          let node;for(let i=0;i<150;i++){node=document.querySelector('[data-window="'+w.id+'"]');if(node?.appView&&finish)break;await new Promise(r=>setTimeout(r,20));}
          if(!finish)throw Error('Read did not start');node.querySelector('[aria-label="Close"]').click();finish(new TextEncoder().encode('after close'));await new Promise(r=>setTimeout(r,50));guestFiles.read=original;
          return w.editor.text==='before close'&&!w.editor.loaded&&!node.isConnected;''')
        check('closed editor ignores a late guest file read',result)
        result=task('''const original=guestFiles.write;let finish;
          guestFiles.write=(path,bytes)=>path==='/Documents/late-create.txt'?new Promise(resolve=>finish=()=>original.call(guestFiles,path,bytes).then(resolve)):original.call(guestFiles,path,bytes);
          const w=d.launch('files');w.path='/Documents';d.render();let node;
          for(let i=0;i<150;i++){node=document.querySelector('[data-window="'+w.id+'"]');if(node?.appView)break;await new Promise(r=>setTimeout(r,20));}
          const input=node.querySelector('[aria-label="New item name"]');input.value='late-create.txt';[...node.querySelectorAll('button')].find(b=>b.textContent==='New text file').click();
          if(!finish)throw Error('Write did not start');node.querySelector('[aria-label="Close"]').click();await finish();await new Promise(r=>setTimeout(r,50));guestFiles.write=original;
          return !d.windows.some(w=>w.editor?.path==='/Documents/late-create.txt')&&!node.isConnected;''')
        check('accepted file write may finish but closed Files cannot open a stale editor',result)
        # File.arrayBuffer() yields before the shared parser starts: close in that gap.
        result=task('''const w=d.launch('rooms');let node;for(let i=0;i<150;i++){node=document.querySelector('[data-window="'+w.id+'"]');if(node?.appView)break;await new Promise(r=>setTimeout(r,20));}
          const input=node.querySelector('[aria-label="Import historical PGN"]');const transfer=new DataTransfer();transfer.items.add(new File(['[Event "Lifecycle"]\\n\\n1. e4 e5 *'],'lifecycle.pgn',{type:'text/plain'}));input.files=transfer.files;input.dispatchEvent(new Event('change'));node.querySelector('[aria-label="Close"]').click();
          await new Promise(r=>setTimeout(r,1000));return desktopNetwork.appContext().pgnImports.get(w)===null;''')
        check('PGN selected immediately before Close leaves no stale import record',result)
        result=task('''const w=d.launch('rooms');let node;for(let i=0;i<150;i++){node=document.querySelector('[data-window="'+w.id+'"]');if(node?.appView)break;await new Promise(r=>setTimeout(r,20));}
          const imports=desktopNetwork.appContext().pgnImports;const done=imports.load(w,new TextEncoder().encode('[Event "Lifecycle"]\\n\\n1. e4 e5 *')).then(()=>false,()=>true);
          node.querySelector('[aria-label="Close"]').click();return await done&&imports.get(w)===null;''')
        check('closing Rooms terminates an already-running PGN worker',result)
        task('await new Promise(r=>setTimeout(r,4500));return true;')
        snapshot=js('return appLifecycleProbe.snapshot()');used=task('return (await desktopNetwork.stats()).budget;');samples.append({'cycle':'late-operations','resources':snapshot,'budget':used});check('late operations return all resources to baseline',snapshot==baseline and used==budget)
        errors=[e for e in call('/session/'+sid+'/log',{'type':'browser'}) if e['level']=='SEVERE'];check('no unexpected browser errors or unhandled rejections',not errors)
        return {'status':'PASS','checks':checks,'cyclesPerApp':26,'ordinaryOpensAndCloses':182,'apps':js('return stressApps'),'samples':samples,'realChromeAndV86':True,'liveChanged':False,'unboundedLifetimeLeakProof':False}
    except Exception:
        try:(ROOT/'.build/checks/public-app-lifecycle-stress-diagnostics.json').write_text(json.dumps({'checks':checks,'samples':samples,'current':js('return appLifecycleProbe.snapshot()'),'budget':task('return (await desktopNetwork.stats()).budget;')},indent=2)+'\n')
        except Exception:pass
        raise
    finally:
        try:task('desktopNetwork.close();guestNetworkAdapter?.destroy();await v86Instance?.destroy();return true;')
        except Exception:pass
        call('/session/'+sid,method='DELETE')
async def main():
    fixture=f.Fixture('/hidden')
    try:await fixture.start();return await asyncio.to_thread(browser,fixture)
    finally:await fixture.close()
if __name__=='__main__':
    report={'status':'FAIL'}
    try:report.update(asyncio.run(main()))
    finally:
        names=['scripts/public-app-lifecycle-stress-check.py','scripts/fixtures/app-lifecycle-probe.js','app.js','desktop-apps.js','terminal.js','networking.js','assets/desktop/app-instance.mjs','assets/desktop/apps.json']
        report['sha256']={name:hashlib.sha256((ROOT/name).read_bytes()).hexdigest() for name in names};report['appSourcesSHA256']={p.parent.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (ROOT.parent/'served_apps_public').glob('*/index.mjs')}
        out=ROOT/'.build/checks/public-app-lifecycle-stress-result.json'
        if out.exists():out.rename(out.with_name('public-app-lifecycle-stress-before-'+str(time.time_ns())+'.json'))
        out.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
