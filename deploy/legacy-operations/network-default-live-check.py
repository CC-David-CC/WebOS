#!/usr/bin/env python3
"""Verify live browser default and adjustable accounted networking limit."""
import argparse,importlib.util,json,shutil,tempfile,time,traceback
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];spec=importlib.util.spec_from_file_location('driver',ROOT/'scripts/touch-preview-check.py');d=importlib.util.module_from_spec(spec);spec.loader.exec_module(d)
p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args();assert not a.output.exists();profile=Path(tempfile.mkdtemp(prefix='codi-network-default-',dir=Path.home()/'snap/chromium/common'));sid=None;checks=[];r={'status':'FAIL','checks':checks}
def js(code,args=[]):return d.call('/session/'+sid+'/execute/sync',{'script':code,'args':args})
def check(label,value):assert value,label;checks.append(label);print(json.dumps({'check':label}),flush=True)
try:
 sid=d.call('/session',{'capabilities':{'alwaysMatch':{'browserName':'chrome','goog:chromeOptions':{'binary':'/snap/chromium/current/usr/lib/chromium-browser/chrome','args':['--headless=new','--no-sandbox','--disable-dev-shm-usage','--user-data-dir='+str(profile)]}}}})['sessionId'];d.call('/session/'+sid+'/url',{'url':'https://ksu.codes/'});d.wait(lambda:js('return !!window.desktopLab?.session;'),120);check('fresh browser default is 512 MiB',js('return desktopNetwork.memoryPolicy().metadataMiB===512;'))
 d.call('/session/'+sid+'/goog/cdp/execute',{'cmd':'Browser.setPermission','params':{'permission':{'name':'persistent-storage'},'setting':'granted','origin':'https://ksu.codes'}});js("localStorage.setItem('codi-device-history-consent-v1','accepted-v1');");d.call('/session/'+sid+'/url',{'url':'https://ksu.codes/'});d.wait(lambda:js('return !!window.desktopLab?.session&&desktopNetwork.appContext().deviceChannelsReady;'),120)
 value=d.call('/session/'+sid+'/execute/async',{'script':'const done=arguments[arguments.length-1];desktopNetwork.stats().then(done,e=>done({error:e.message}));','args':[]});r['accountedBytes']=value['budget']['metadataBytes'];check('running shared budget uses the 512 MiB ceiling',value['limits']['metadataBytes']==512*1048576 and r['accountedBytes']<512*1048576)
 check('allowance remains adjustable',js('return desktopNetwork.configureMemoryBudgetMiB(256).metadataMiB===256&&desktopNetwork.configureMemoryBudgetMiB(512).metadataMiB===512;'));r['status']='PASS'
except Exception as e:r.update(error=str(e),traceback=traceback.format_exc())
finally:
 if sid:d.call('/session/'+sid,method='DELETE')
 shutil.rmtree(profile,ignore_errors=True);r['profileRemoved']=not profile.exists()
a.output.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({'status':r['status'],'error':r.get('error'),'checks':len(checks),'accountedBytes':r.get('accountedBytes')}));raise SystemExit(r['status']!='PASS')
