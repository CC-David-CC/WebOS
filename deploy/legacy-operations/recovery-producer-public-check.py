#!/usr/bin/env python3
"""Real root Linux/app/download/reload/file-import recovery with real expiry.

One owned QA account and Chrome, ordinary TLS. No clock/expiry/permission override,
server-data restore, outside WAN, independent replicas, chess or8k claim.
"""
import argparse
import base64
import hashlib
import importlib.util
import json
from pathlib import Path
import secrets
import shlex
import tempfile
import time
import traceback

ROOT=Path(__file__).resolve().parents[1]
def module(name,path):
    s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
public=module('producer_public_support',ROOT/'scripts/hosted-peer-public-check.py')
driver=module('producer_public_driver',ROOT/'scripts/touch-preview-check.py')
vm=module('producer_public_runtime',ROOT/'scripts/upgrade-signin-native-vm.py');vm.remote=public.public_remote

def run(release):
    checks=[];sid=None;subject=None;username='vmhosted_'+secrets.token_hex(6);password=secrets.token_urlsafe(32)
    temporary=tempfile.TemporaryDirectory(prefix='codi-live-proposal-',dir=Path.home()/'snap/chromium/common');downloads=Path(temporary.name)
    result={'status':'FAIL','scope':__doc__,'checks':checks,'wholeGoalComplete':False,'createdTestAccount':username,'ordinaryTLS':True,'actualBrowsers':1,'actualV86Desktops':1,'clockOverridden':False,'publicWANTested':False}
    def js(code,args=[]):return driver.call('/session/'+sid+'/execute/sync',{'script':code,'args':args})
    def task(code,args=[]):
        d=driver.call('/session/'+sid+'/execute/async',{'script':'const params=Array.from(arguments),done=params.pop();(async()=>{'+code+'})().then(value=>done({ok:true,value}),e=>done({ok:false,error:e.stack}));','args':args});assert d['ok'],d;return d.get('value')
    def wait(fn,seconds=90):return driver.wait(fn,seconds)
    def ready():wait(lambda:js('return window.desktopLab?.guestState==="ready"&&guestFiles.ready&&desktopNetwork.appContext().hostedRooms?.snapshot().ready;'),180)
    def state(node=None):return js('return desktopNetwork.appContext().hostedRooms.snapshot(arguments[0]);',[node])
    def idle():wait(lambda:state()['busy']==0)
    def check(name,ok):assert ok,name;checks.append(name);print(json.dumps({'check':name}),flush=True)
    def open_rooms():
        ids=js('return [...surfaces.values()][0].windows.map(w=>w.id);');js('document.querySelector(".app-menu-button").click();[...document.querySelectorAll(".menu-row")].find(b=>b.querySelector(".row-text")?.textContent==="Rooms").click();')
        w=wait(lambda:js('return [...surfaces.values()][0].windows.find(w=>w.app==="rooms"&&!arguments[0].includes(w.id))?.id;',[ids]));wait(lambda:js('return !!document.querySelector(`[data-window="${arguments[0]}"] [data-hosted-create]`);',[w]));return w
    def click(w,key):js('const b=document.querySelector(`[data-window="${arguments[0]}"] [data-hosted-${arguments[1]}]`);if(!b||b.disabled||b.hidden)throw Error("Disabled app action "+arguments[1]);b.click();',[w,key])
    def text(w,key,value):js('const e=document.querySelector(`[data-window="${arguments[0]}"] [data-hosted-${arguments[1]}]`);e.value=arguments[2];e.dispatchEvent(new Event("input",{bubbles:true}));',[w,key,value])
    try:
        before=vm.runtime();pin=hashlib.sha256((release/'connected-release.json').read_bytes()).hexdigest();assert before['manifestSHA256']==pin;result['nativeManifestSHA256']=pin
        sid=driver.call('/session',{'capabilities':{'alwaysMatch':{'browserName':'chrome','acceptInsecureCerts':False,'goog:chromeOptions':{'binary':'/snap/chromium/current/usr/lib/chromium-browser/chrome','args':['--headless=new','--no-sandbox','--disable-dev-shm-usage','--no-proxy-server','--window-size=1366,900']}}}})['sessionId'];driver.call('/session/'+sid+'/timeouts',{'script':120000})
        driver.call('/session/'+sid+'/goog/cdp/execute',{'cmd':'Browser.setDownloadBehavior','params':{'behavior':'allow','downloadPath':str(downloads)}});driver.call('/session/'+sid+'/url',{'url':'https://ksu.codes/'});ready()
        check('actual root Linux starts with recovery enabled and no certificate bypass',state()['delivery']['proposalRecovery'] and js('return currentSession.public.kind==="anonymous";'))
        task('await changeAccount("register",params[0],params[1]);return true;',[username,password]);ready();subject=js('return currentSession.public.sub;');old_sid=js('return currentSession.public.sid;');result['subject']=subject
        w=open_rooms();click(w,'create');idle();node=js('return [...surfaces.values()][0].windows.find(w=>w.id===arguments[0]).hostedRoomId;',[w]);assert node;result['ownedRoom']=node
        js("window.proposalNativeFetch=fetch;window.fetch=(u,o)=>{let op;try{op=JSON.parse(JSON.parse(o?.body||'{}').request||'{}').operation;}catch{}return op==='accept'?Promise.reject(new TypeError('Owned unsent proposal fixture')):proposalNativeFetch(u,o);};")
        text(w,'draft','Original proposal after real reload');click(w,'send');idle();js('window.fetch=proposalNativeFetch;')
        check('failed dispatch keeps an unsent original rather than claiming a server save',state(node)['selected']['pending'] and state(node)['selected']['count']==0)
        click(w,'save-proposal');download=downloads/'pending-public-chat.json';wait(lambda:download.exists() and not list(downloads.glob('*.crdownload')),20)
        proposal=json.loads(download.read_bytes());assert set(proposal)=={'version','node_id','grant','event'}
        payload=json.loads(base64.urlsafe_b64decode(proposal['event'].split('.')[1]+'=='));a,b,_=proposal['event'].split('.');event_id=hashlib.sha256(json.dumps(['codi-hosted-room-origin+jws',a,b],separators=(',',':')).encode()).digest();event_id=base64.urlsafe_b64encode(event_id).decode().rstrip('=');expiry=payload['exp']
        check('actual app download exports only the original public signed envelope',proposal['node_id']==node and payload['author_session_id']==old_sid and len(download.read_bytes())<=32768)
        driver.call('/session/'+sid+'/refresh',{});ready();task('await changeAccount("signin",params[0],params[1]);return true;',[username,password]);ready();fresh_sid=js('return currentSession.public.sid;');check('real reload signs the same account into a distinct new session',js('return currentSession.public.sub===arguments[0];',[subject]) and fresh_sid!=old_sid)
        w=open_rooms();text(w,'id',node);click(w,'open');idle();click(w,'join');idle();text(w,'draft','Accepted current branch before the old proposal returns');click(w,'send');idle()
        check('the current branch accepts a different message before original recovery',state(node)['selected']['count']==1 and not state(node)['selected']['pending'])
        print(json.dumps({'phase':'waiting-for-real-origin-expiry','secondsRemaining':max(0,expiry+1-int(time.time()))}),flush=True)
        wait(lambda:time.time()>expiry+1,70)
        selector=f'[data-window="{w}"] [data-hosted-proposal-file]';element=driver.call('/session/'+sid+'/element',{'using':'css selector','value':selector})['element-6066-11e4-a52e-4f735466cecf'];driver.call('/session/'+sid+'/element/'+element+'/value',{'text':str(download)})
        wait(lambda:state(node)['selected']['pending']);check('native file import retains an expired original without automatically sending it',state(node)['selected']['count']==1 and state(node)['selected']['pendingExpired'])
        click(w,'reauthorize');idle();wait(lambda:state(node)['selected']['count']==2)
        records=state(node)['selected']['records'];matches=[r for r in records if r['eventId']==event_id]
        check('explicit app recovery verifies one original ID with fresh consent after real expiry',len(matches)==1 and matches[0]['recovered'] and matches[0]['historical'] and matches[0]['author']['sid']==old_sid and not state(node)['selected']['pending'])
        # Read only this public QA receipt, not controller keys or private files.
        code='''import json,sqlite3
from pathlib import Path
c=json.loads(Path('/etc/codi-rooms/ksu/managed.json').read_bytes())
with sqlite3.connect('file:'+str(Path(c['stateRoot'])/'rooms.sqlite3')+'?mode=ro',uri=True) as db:
 row=db.execute('SELECT receipt FROM events WHERE node=? AND event_id=?',(NODE,EVENT)).fetchone();floors=db.execute('SELECT sid,highest FROM streams WHERE node=?',(NODE,)).fetchall();count=db.execute('SELECT count(*) FROM events WHERE node=?',(NODE,)).fetchone()[0]
print(json.dumps({'receipt':row[0],'floors':floors,'count':count}))
'''.replace('NODE',repr(node)).replace('EVENT',repr(event_id))
        saved=json.loads(vm.remote('/usr/bin/python3 -I -B -c '+shlex.quote(code)));accepted=json.loads(base64.urlsafe_b64decode(saved['receipt'].split('.')[1]+'=='));floors=dict(saved['floors'])
        check('actual server disk preserves exact original bytes and both independent stream floors',accepted['event']==proposal['event'] and accepted['event_id']==event_id and accepted['recovery']['requester']['sid']==fresh_sid and saved['count']==2 and floors[old_sid]==floors[fresh_sid]==1)
        task('await changeAccount("anonymous");return true;');ready();a=open_rooms();text(a,'id',node);click(a,'open');idle();read=state(node)['selected']
        check('a fresh anonymous reader verifies recovered public history without writer membership',read['count']==2 and not read['joined'] and any(r.get('recovered') and r['eventId']==event_id for r in read['records']))
        assert vm.runtime()==before
        result.update(status='PASS',originalEventID=event_id,acceptedMessages=2,actualPageReload=True,actualNativeFileSelection=True,actualOSDownload=True,realExpiryPassed=True,serverReceipt=saved['receipt'])
    except Exception as e:
        result.update(error=str(e),traceback=traceback.format_exc())
        if sid:
            try:result['appError']=js('return [...document.querySelectorAll("[data-hosted-status]")].map(e=>e.textContent);')
            except Exception as error:result['diagnosticError']=str(error)
    finally:
        try:
            if sid:driver.call('/session/'+sid,method='DELETE');result['ownedBrowserContextsClosed']=1
        except Exception as e:result['status']='FAIL';result['browserCleanupError']=str(e)
        try:
            if subject:
                code='''import json,sys,os
from pathlib import Path
c=json.loads(Path('/etc/codi-connected/ksu/managed.json').read_bytes());sys.path[:0]=[c['release'],str(Path(c['release'])/'codiserver-server-v0.3.0')]
from origin_service.lifecycle import connection,private_database,set_disabled
state=Path(c['stateRoot'])/'issuer/state';owner=state.stat();os.setgroups([]);os.setgid(owner.st_gid);os.setuid(owner.st_uid)
with connection(private_database(state)) as db:assert db.execute('SELECT subject FROM accounts WHERE username=?',(NAME,)).fetchone()==(SUBJECT,)
print(json.dumps(set_disabled(state,NAME,True)))
'''.replace('NAME',repr(username)).replace('SUBJECT',repr(subject))
                result['ownedAccountPolicy']=json.loads(vm.remote('/srv/codi-network-fixture/venv/bin/python -I -B -c '+shlex.quote(code)));assert result['ownedAccountPolicy']['disabled']
        except Exception as e:result['status']='FAIL';result['accountCleanupError']=str(e)
        if result.get('ownedBrowserContextsClosed')==1:temporary.cleanup()
    return result

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--release',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();assert not a.output.exists();v=run(a.release.resolve());a.output.write_text(json.dumps(v,indent=2)+'\n');print(json.dumps({'status':v['status'],'checks':len(v['checks']),'error':v.get('error')}));raise SystemExit(0 if v['status']=='PASS' else 1)
