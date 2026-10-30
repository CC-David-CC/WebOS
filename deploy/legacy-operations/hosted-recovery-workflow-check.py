#!/usr/bin/env python3
"""Bundled Rooms app downloads a signed proposal, reloads and imports it natively.

Actual Chrome/HTTP/SQLite/IndexedDB/OS file download and file selection. New
account session, simulated fifteen days, original signed event preserved. Local
source integration, not deployed native, full Files app, WAN, v86 or8k proof.
"""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import tempfile
import time
import traceback

ROOT=Path(__file__).resolve().parents[1]
def module(name,path):
    spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
support=module('recovery_workflow_support',ROOT/'scripts/hosted-client-check.py');fixture,driver,builder=support.fixture,support.driver,support.builder


def run():
    sid=None;f=None;checks=[];sources=[Path(__file__),ROOT/'scripts/hosted-recovery-workflow-page.mjs',ROOT/'scripts/hosted-client-page.mjs',ROOT.parent/'served_apps_public/rooms/hosted-view.mjs',ROOT.parent/'served_apps_public/rooms/mesh-view.css',*sorted((ROOT/'network').glob('*.mjs')),*sorted((ROOT/'room_service').glob('*.py'))]
    pins={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in sources};result={'status':'FAIL','scope':__doc__,'checks':checks,'actualBrowserInstances':1,'actualV86Desktops':0,'wholeGoalComplete':False}
    def js(code,args=[]):return driver.call('/session/'+sid+'/execute/sync',{'script':code,'args':args})
    def task(code,args=[]):
        r=driver.call('/session/'+sid+'/execute/async',{'script':'const params=Array.from(arguments),done=params.pop();(async()=>{'+code+'})().then(value=>done({ok:true,value}),error=>done({ok:false,error:error.stack}));','args':args});assert r['ok'],r;return r.get('value')
    def check(name,ok):assert ok,name;checks.append(name);print(json.dumps({'check':name}),flush=True)
    def file_input(selector):
        element=driver.call('/session/'+sid+'/element',{'using':'css selector','value':selector})['element-6066-11e4-a52e-4f735466cecf']
        driver.call('/session/'+sid+'/element/'+element+'/value',{'text':str(download)})
    try:
        common=Path.home()/'snap/chromium/common';assert common.is_dir()
        with tempfile.TemporaryDirectory(prefix='codi-recovery-workflow-',dir=common) as directory:
            folder=Path(directory);f=fixture.Fixture(folder);f.clock.realtime=True;public=folder/'public';downloads=folder/'downloads';downloads.mkdir();download=downloads/'pending-public-chat.json'
            config=f.issuer.config();config['hostedRooms']={'version':'codi-hosted-room/1','basePath':'/rooms','controllerKey':f.store.public,'certificatePath':'/api/v1/room-control/controller','challengePath':'/api/v1/room-control/challenge','authorizePath':'/api/v1/room-control/authorize'};(public/'fixture-config.json').write_text(json.dumps(config))
            source=folder/'app-source/rooms';source.mkdir(parents=True)
            for name in ['hosted-view.mjs','mesh-view.css']:shutil.copyfile(ROOT.parent/'served_apps_public/rooms'/name,source/name)
            (source/'index.mjs').write_text("export {mountHostedView as mount} from './hosted-view.mjs';\n")
            build=builder.build(source.parent,public/'assets/desktop',['rooms'],str(ROOT/'.build/tools/node-v24.22.1-linux-x64/bin/node'))
            page=(ROOT/'scripts/hosted-client-page.mjs').read_text();old='new HostedRooms(s,config,{sessionValid:()=>currentSession===s})';assert page.count(old)==1;page=page.replace(old,'new HostedRooms(s,config,{atomicSync:true,proposalRecovery:true,sessionValid:()=>currentSession===s})')
            old='storage:{downloadGuestFile(){}}';assert page.count(old)==1
            new="storage:{downloadGuestFile(name,text){const url=URL.createObjectURL(new Blob([text],{type:'application/json'})),a=document.createElement('a');a.download=name;a.href=url;document.body.append(a);a.click();a.remove();setTimeout(()=>URL.revokeObjectURL(url),1000);}}"
            page=page.replace(old,new)+'\n'+(ROOT/'scripts/hosted-recovery-workflow-page.mjs').read_text();(public/'workflow.mjs').write_text(page)
            (public/'loader.mjs').write_text("const days=new URL(location.href).searchParams.get('days');if(days==='15'){const now=Date.now;Date.now=()=>now()+15*86400000;}import('./workflow.mjs').catch(error=>window.workflowFatal=error.stack);")
            (public/'index.html').write_text('<!doctype html><title>Owned original proposal workflow</title><script type="module" src="/loader.mjs"></script>');shutil.copytree(ROOT/'network',public/'network',ignore=shutil.ignore_patterns('*.md'))
            sid=driver.call('/session',{'capabilities':{'alwaysMatch':{'browserName':'chrome','goog:chromeOptions':{'binary':'/snap/chromium/current/usr/lib/chromium-browser/chrome','args':['--headless=new','--no-sandbox','--disable-dev-shm-usage']}}}})['sessionId'];driver.call('/session/'+sid+'/timeouts',{'script':120000});driver.call('/session/'+sid+'/goog/cdp/execute',{'cmd':'Browser.setDownloadBehavior','params':{'behavior':'allow','downloadPath':str(downloads)}});driver.call('/session/'+sid+'/url',{'url':f.origin+'/'})
            def ready():return driver.wait(lambda:js('if(window.workflowFatal)throw Error(workflowFatal);return window.hostedClientReady===true;'),30)
            ready();password=fixture.secrets.token_urlsafe(32);prior=task('return await recoveryPrepare(params[0]);',[password]);driver.wait(lambda:download.exists() and not list(downloads.glob('*.crdownload')),20)
            exported=json.loads(download.read_bytes());node=prior['node'];original=exported['event'];original_id=fixture.token_id(original,fixture.ORIGIN_TYPE)
            check('real app download saves only the original signed event/grant envelope, not credentials or a false server save',set(exported)=={'version','node_id','event','grant'} and exported['node_id']==node and not exported.get('privateKey') and len(download.read_bytes())<=32768)
            member=fixture.Actor(f,'workflow_member');work=member.operation('join_challenge',{'node_id':node});grant=member.operation('join',{'node_id':node,'proof':fixture.solve(work['challenge'])})['grant'];member.operation('accept',{'node_id':node,'grant':grant,'event':member.origin(grant,1,'An accepted branch while the original was absent')})
            before=task('return await recoveryCloseForReload();');f.clock.offset=15*86400
            js("history.replaceState(null,'','/?days=15');");driver.call('/session/'+sid+'/refresh',{});ready();fresh=task('return await recoveryFresh(params[0],params[1]);',[password,prior])
            file_input('[data-hosted-proposal-file]');task('return await recoveryImported();');task('return await recoverySubmit();')
            with f.store.lock(),f.store.db() as db:
                row=db.execute('SELECT receipt FROM events WHERE node=? AND event_id=?',(node,original_id)).fetchone();count=db.execute('SELECT count(*) FROM events WHERE node=?',(node,)).fetchone()[0]
                receipt=fixture.jose.inspect(row[0],fixture.RECEIPT_TYPE)[1];sequences=dict(db.execute('SELECT sid,highest FROM streams WHERE node=?',(node,)))
            check('actual server history contains one exact original signature and distinct old/new session sequence floors',count==3 and receipt['event']==original and receipt['recovery']['requester']['sid']==fresh['freshSID'] and sequences[prior['sid']]==sequences[fresh['freshSID']]==1)
            task('return recoveryHoldFile();');file_input('[data-hosted-rooms]:last-of-type [data-hosted-proposal-file]');task('return await recoveryCancelFile();')
            task('return await recoveryAnonymous();');file_input('[data-hosted-proposal-file]');final=task('return await recoveryForeignRefused();');checks.extend(final['checks'])
            check('independent app workflow and all tracked final resources close cleanly',not any(v for k,v in final['budget'].items() if k!='closed'))
            result.update(status='PASS',genericAppBundle=build,actualPageReload=True,actualNativeFileSelection=True,actualOSDownload=True,simulatedAbsenceDays=15,acceptedMessages=count,originalEventID=original_id,resourceCleanup=final['budget'],preReloadCleanup=before['budget'])
    except Exception as error:
        result.update(error=str(error),traceback=traceback.format_exc())
        if sid:
            try:result['browserState']=js('return {fatal:window.workflowFatal,checks:window.recoveryChecks,body:document.body.innerText.slice(-3000)};')
            except Exception as failure:result['diagnosticError']=str(failure)
    finally:
        if sid:driver.call('/session/'+sid,method='DELETE');result['ownedBrowserContextsClosed']=1
        if f:f.close()
    result.update(sourceSHA256=pins,sourceChangedDuringTest=any(hashlib.sha256(Path(p).read_bytes()).hexdigest()!=h for p,h in pins.items()))
    if result['sourceChangedDuringTest']:result['status']='FAIL'
    return result


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args();assert not a.output.exists();v=run();a.output.write_text(json.dumps(v,indent=2)+'\n');print(json.dumps({'status':v['status'],'checks':len(v['checks']),'error':v.get('error')}));raise SystemExit(0 if v['status']=='PASS' else 1)
