#!/usr/bin/env python3
"""One real Chrome, two real compiled controllers, deterministic clock/unit peers.
Proves the former allocation-boundary grant defect, not a signed RTC/WAN test.
"""
import argparse,functools,hashlib,http.server,importlib.util,json,shutil,tempfile,threading,traceback
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
s=importlib.util.spec_from_file_location('credit_boundary_driver',ROOT/'scripts/touch-preview-check.py');d=importlib.util.module_from_spec(s);s.loader.exec_module(d)
class Quiet(http.server.SimpleHTTPRequestHandler):
 def log_message(self,*args):pass

def run(old,new):
 result={'status':'FAIL','scope':__doc__,'productionChanged':False,'wholeGoalComplete':False,'driverSHA256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()};sid=None;server=None;thread=None;profile=None
 with tempfile.TemporaryDirectory(prefix='codi-credit-boundary-') as folder:
  folder=Path(folder)
  try:
   for name,source in [('old',old),('new',new)]:
    catalog=json.loads((source/'apps.json').read_bytes());app=catalog['apps'][0];assert len(catalog['apps'])==1;code=(source/Path(app['path']).relative_to('assets/desktop')).read_bytes();assert hashlib.sha256(code).hexdigest()==app['sha256'];(folder/(name+'.mjs')).write_bytes(code);result[name+'CompiledSHA256']=app['sha256']
   (folder/'index.html').write_text('<!doctype html><title>Owned credit boundary regression</title>')
   server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Quiet,directory=str(folder)));thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start();origin='http://127.0.0.1:'+str(server.server_port)
   profile=Path(tempfile.mkdtemp(prefix='codi-credit-boundary-',dir=Path.home()/'snap/chromium/common'));sid=d.call('/session',{'capabilities':{'alwaysMatch':{'browserName':'chrome','goog:chromeOptions':{'binary':'/snap/chromium/current/usr/lib/chromium-browser/chrome','args':['--headless=new','--no-sandbox','--disable-dev-shm-usage','--user-data-dir='+str(profile)]}}}})['sessionId'];d.call('/session/'+sid+'/url',{'url':origin+'/'});d.call('/session/'+sid+'/timeouts',{'script':30000})
   script='''const done=arguments[0];(async()=>{const outputs={};for(const name of ['old','new']){const {DeviceChannelBandwidth,sessionBudget}=await import('./'+name+'.mjs'),budget=sessionBudget({}),pool={resourceBudget:budget,attachDeviceTraffic(){},detachDeviceTraffic(){}},sent=[],channel='A'.repeat(43),genesisHash='B'.repeat(43);let clock=0;const owner=new DeviceChannelBandwidth(pool,{clock:()=>clock,creditLifetimeMs:6000}),peer={id:'boundary-peer',link:{closed:false,deviceCreditReady:true,deviceCreditCost:()=>512,sendDeviceCredit:async b=>sent.push(b)}};owner.register(channel,genesisHash,()=>({windowMs:10000,uploadBytes:1048576,downloadBytes:1048576,serveBytes:1048576,controlBytes:65536}));owner.snapshot(channel);clock=9999;await owner.control(peer,{op:'request',channel,genesisHash,request_id:'1'.repeat(32),minBytes:1024,wantBytes:16384},512);const grant=sent[0],allocated=owner.snapshot(channel).allocated.download;owner.close();await owner.idle();outputs[name]={bytes:grant.bytes,validForMs:grant.validForMs,allocated,leasesZero:Object.entries(budget.snapshot()).every(([k,v])=>k==='closed'||v===0)};}return outputs;})().then(value=>done({ok:true,value}),error=>done({ok:false,error:error.stack}));'''
   script=script.replace("genesisHash='B'.repeat(43)","genesisHash='B'.repeat(42)+'A'")
   value=d.call('/session/'+sid+'/execute/async',{'script':script,'args':[]});assert value['ok'],value;result['observed']=value['value'];assert result['observed']['old']['validForMs']==1 and result['observed']['new']['validForMs']==6000;assert all(v['allocated']==16384 and v['bytes']==16384 and v['leasesZero'] for v in result['observed'].values());result['status']='PASS'
  except Exception as error:result.update(error=str(error),traceback=traceback.format_exc())
  finally:
   if sid:d.call('/session/'+sid,method='DELETE')
   if server:server.shutdown();server.server_close()
   if thread:thread.join(timeout=3)
   if profile:shutil.rmtree(profile)
   result['ownedProfileRemoved']=profile is None or not profile.exists()
 result['fixtureRemoved']=not folder.exists();return result
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--old-core',type=Path,required=True);p.add_argument('--new-core',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();assert not a.output.exists();r=run(a.old_core,a.new_core);a.output.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2));raise SystemExit(r['status']!='PASS')
