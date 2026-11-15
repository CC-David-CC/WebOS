#!/usr/bin/env python3
"""Characterize authorization-refused receive credit in a real compiled controller.
One Chrome, fake peer/pool, no signatures/native binding race or WAN claim.
This diagnostic observes missing refusal replies; it does not fix or accept them.
"""
import argparse,functools,hashlib,http.server,importlib.util,json,shutil,tempfile,threading,traceback
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
s=importlib.util.spec_from_file_location('refusal_driver',ROOT/'scripts/touch-preview-check.py');d=importlib.util.module_from_spec(s);s.loader.exec_module(d)
class Quiet(http.server.SimpleHTTPRequestHandler):
 def log_message(self,*args):pass

def run(core):
 r={'status':'FAIL','scope':__doc__,'driverSHA256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'productionChanged':False,'wholeGoalComplete':False};sid=None;server=None;thread=None;profile=None
 with tempfile.TemporaryDirectory(prefix='codi-credit-refusal-') as folder:
  folder=Path(folder)
  try:
   catalog=json.loads((core/'apps.json').read_text());app=catalog['apps'][0];assert len(catalog['apps'])==1;code=(core/Path(app['path']).relative_to('assets/desktop')).read_bytes();assert hashlib.sha256(code).hexdigest()==app['sha256'];r['actualCompiledCoreSHA256']=app['sha256'];(folder/'core.mjs').write_bytes(code);(folder/'index.html').write_text('<!doctype html><title>Owned credit-refusal diagnostic</title>')
   server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Quiet,directory=str(folder)));thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start();profile=Path(tempfile.mkdtemp(prefix='codi-credit-refusal-',dir=Path.home()/'snap/chromium/common'))
   sid=d.call('/session',{'capabilities':{'alwaysMatch':{'browserName':'chrome','goog:chromeOptions':{'binary':'/snap/chromium/current/usr/lib/chromium-browser/chrome','args':['--headless=new','--no-sandbox','--disable-dev-shm-usage','--user-data-dir='+str(profile)]}}}})['sessionId'];d.call('/session/'+sid+'/url',{'url':'http://127.0.0.1:'+str(server.server_port)+'/'});d.call('/session/'+sid+'/timeouts',{'script':30000})
   script='''const done=arguments[0];(async()=>{const {DeviceChannelBandwidth,sessionBudget}=await import('./core.mjs'),budget=sessionBudget({}),pool={resourceBudget:budget,attachDeviceTraffic(){},detachDeviceTraffic(){}},sent=[],channel='A'.repeat(43),genesisHash='B'.repeat(42)+'A';let authorized=false,checks=0;const owner=new DeviceChannelBandwidth(pool),peer={id:'owned-peer',link:{closed:false,deviceCreditReady:true,deviceCreditCost:()=>512,sendDeviceCredit:async b=>sent.push(b)}};owner.register(channel,genesisHash,()=>({windowMs:60000,uploadBytes:1048576,downloadBytes:1048576,serveBytes:1048576,controlBytes:65536}),async()=>{checks++;if(!authorized)throw Error('Owned fresh native binding not available yet');});const request=n=>({op:'request',channel,genesisHash,request_id:n.repeat(32),minBytes:1024,wantBytes:16384}),refused=await owner.control(peer,request('1'),512),before={returned:refused,replies:sent.length,allocated:owner.snapshot(channel).allocated.download,rejected:owner.stats().rejected};authorized=true;const accepted=await owner.control(peer,request('2'),512),after={returned:accepted,replies:sent.length,bytes:sent[0]?.bytes,validForMs:sent[0]?.validForMs};owner.close();await owner.idle();return {before,after,authorizationChecks:checks,leasesZero:Object.entries(budget.snapshot()).every(([k,v])=>k==='closed'||v===0)};})().then(value=>done({ok:true,value}),error=>done({ok:false,error:error.stack}));'''
   value=d.call('/session/'+sid+'/execute/async',{'script':script,'args':[]});assert value['ok'],value;r['observed']=v=value['value'];assert v['before']=={'returned':False,'replies':0,'allocated':0,'rejected':1};assert v['after']=={'returned':True,'replies':1,'bytes':16384,'validForMs':60000};assert v['authorizationChecks']==2 and v['leasesZero'];r['status']='OBSERVED'
  except Exception as e:r.update(error=str(e),traceback=traceback.format_exc())
  finally:
   if sid:d.call('/session/'+sid,method='DELETE')
   if server:server.shutdown();server.server_close()
   if thread:thread.join(timeout=3)
   if profile:shutil.rmtree(profile)
   r['ownedProfileRemoved']=profile is None or not profile.exists()
 r['fixtureRemoved']=not folder.exists();return r
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--compiled-core',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();assert not a.output.exists();v=run(a.compiled_core);a.output.write_text(json.dumps(v,indent=2)+'\n');print(json.dumps(v,indent=2));raise SystemExit(v['status']!='OBSERVED')
