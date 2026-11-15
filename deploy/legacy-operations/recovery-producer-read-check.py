#!/usr/bin/env python3
"""Fresh anonymous full desktop verifies the original saved recovery after code changes."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import traceback

ROOT=Path(__file__).resolve().parents[1]
def module(name,path):
    s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
support=module('saved_recovery_public',ROOT/'scripts/recovery-producer-public-check.py');driver,vm=support.driver,support.vm

def run(release,original,enabled):
    assert original['status']=='PASS';node,event=original['ownedRoom'],original['originalEventID'];sid=None
    result={'status':'FAIL','scope':__doc__,'wholeGoalComplete':False,'checks':[],'actualBrowsers':1,'actualV86Desktops':1,'ordinaryTLS':True,'publicWANTested':False}
    def js(code,args=[]):return driver.call('/session/'+sid+'/execute/sync',{'script':code,'args':args})
    def wait(fn,seconds=90):return driver.wait(fn,seconds)
    def check(name,ok):assert ok,name;result['checks'].append(name);print(json.dumps({'check':name}),flush=True)
    try:
        before=vm.runtime();pin=hashlib.sha256((release/'connected-release.json').read_bytes()).hexdigest();assert before['manifestSHA256']==pin
        sid=driver.call('/session',{'capabilities':{'alwaysMatch':{'browserName':'chrome','acceptInsecureCerts':False,'goog:chromeOptions':{'binary':'/snap/chromium/current/usr/lib/chromium-browser/chrome','args':['--headless=new','--no-sandbox','--disable-dev-shm-usage','--no-proxy-server','--window-size=1366,900']}}}})['sessionId'];driver.call('/session/'+sid+'/url',{'url':'https://ksu.codes/'})
        wait(lambda:js('return window.desktopLab?.guestState==="ready"&&guestFiles.ready&&desktopNetwork.appContext().hostedRooms?.snapshot().ready;'),180)
        check('fresh Linux desktop is anonymous with the expected recovery-control policy',js('return currentSession.public.kind==="anonymous"&&desktopNetwork.appContext().hostedRooms.snapshot().delivery.proposalRecovery===arguments[0];',[enabled]))
        js('document.querySelector(".app-menu-button").click();[...document.querySelectorAll(".menu-row")].find(b=>b.querySelector(".row-text")?.textContent==="Rooms").click();')
        wait(lambda:js('return !!document.querySelector("[data-hosted-id]");'));js('const e=document.querySelector("[data-hosted-id]");e.value=arguments[0];e.dispatchEvent(new Event("input",{bubbles:true}));document.querySelector("[data-hosted-open]").click();',[node])
        wait(lambda:js('return desktopNetwork.appContext().hostedRooms.snapshot(arguments[0]).selected?.count===arguments[1];',[node,original['acceptedMessages']]))
        state=js('return desktopNetwork.appContext().hostedRooms.snapshot(arguments[0]).selected;',[node]);matches=[r for r in state['records'] if r['eventId']==event]
        check('a new public reader verifies the exact recovered event once from retained server history',len(matches)==1 and matches[0]['recovered'] and matches[0]['historical'] and not state['joined'])
        check('the actual Rooms app displays the original without granting writer membership',js('return document.querySelector("[data-hosted-history]").textContent.includes("Original proposal after real reload")&&document.querySelector("[data-hosted-send]").disabled&&document.querySelector("[data-hosted-reauthorize]").hidden===!arguments[0];',[enabled]))
        check('read-only verification leaves native processes and configuration unchanged',vm.runtime()==before)
        result.update(status='PASS',nativeManifestSHA256=pin,originalEventID=event,acceptedCount=state['count'],recoveryControlsEnabled=enabled)
    except Exception as e:result.update(error=str(e),traceback=traceback.format_exc())
    finally:
        if sid:driver.call('/session/'+sid,method='DELETE');result['ownedBrowserContextsClosed']=1
    return result

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--release',type=Path,required=True);p.add_argument('--original-result',type=Path,required=True);p.add_argument('--recovery-enabled',action='store_true');p.add_argument('--output',type=Path,required=True);a=p.parse_args();assert not a.output.exists();v=run(a.release.resolve(),json.loads(a.original_result.read_bytes()),a.recovery_enabled);a.output.write_text(json.dumps(v,indent=2)+'\n');print(json.dumps({'status':v['status'],'checks':len(v['checks']),'error':v.get('error')}));raise SystemExit(0 if v['status']=='PASS' else 1)
