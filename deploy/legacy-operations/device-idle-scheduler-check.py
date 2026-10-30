#!/usr/bin/env python3
"""One real device host must not wake itself when reporting its idle phase.

Packaged Chat, native consent/key/directory/ledger/solo policy, shared scheduler
and topology; local-development identity, no fake driver or RTC/WAN claim.
"""
import argparse,functools,hashlib,http.server,importlib.util,json,shutil,tempfile,threading,time,traceback
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def mod(n,p):
 s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
d=mod('idle_driver',ROOT/'scripts/touch-preview-check.py');builder=mod('idle_builder',ROOT/'scripts/build-public-apps.py')
class Quiet(http.server.SimpleHTTPRequestHandler):
 def log_message(self,*args):pass
 def end_headers(self):self.send_header('Cache-Control','no-store');super().end_headers()
def run(compiled):
 checks=[];r={'status':'FAIL','scope':__doc__,'checks':checks,'actualBrowsers':1,'actualRTCLinks':0,'actualV86Desktops':0,'productionChanged':False,'wholeGoalComplete':False};sid=None;tmp=tempfile.TemporaryDirectory(prefix='codi-idle-host-');folder=Path(tmp.name);profile=Path(tempfile.mkdtemp(prefix='codi-idle-host-',dir=Path.home()/'snap/chromium/common'));server=None;thread=None
 def js(code,args=[]):return d.call('/session/'+sid+'/execute/sync',{'script':code,'args':args})
 def task(code,args=[]):
  v=d.call('/session/'+sid+'/execute/async',{'script':'const params=Array.from(arguments),done=params.pop();(async()=>{'+code+'})().then(value=>done({ok:true,value}),error=>done({ok:false,error:error?.stack||String(error)}));','args':args});assert v['ok'],v;return v.get('value')
 def check(name,ok):assert ok,name;checks.append(name);print(json.dumps({'check':name}),flush=True)
 try:
  assets=folder/'assets/desktop';assets.mkdir(parents=True);builder.build(ROOT.parent/'served_apps_public',assets,['chat','rooms','calculator'],str(ROOT/'.build/tools/node-v24.22.1-linux-x64/bin/node'));files={str(p.relative_to(ROOT)) for p in (ROOT/'assets/desktop').glob('*.mjs')}|{str(p.relative_to(ROOT)) for p in (ROOT/'network').glob('*.mjs')}|{'networking.js','desktop-apps.js','assets/vendor/chess/chess.mjs','scripts/fixtures/device-session-page.mjs','scripts/fixtures/device-session-bootstrap.js'};r['sourceSHA256']={}
  for n in files:
   b=(ROOT/n).read_bytes();r['sourceSHA256'][n]=hashlib.sha256(b).hexdigest();p=folder/n;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b)
  raw=(ROOT/'networking.js').read_text();assert raw.count('const disabled=true;')==1;(folder/'networking-fixture.js').write_text(raw.replace('const disabled=true;','const disabled=false;'));(folder/'bootstrap.js').write_bytes((ROOT/'scripts/fixtures/device-session-bootstrap.js').read_bytes());fixture=(ROOT/'scripts/fixtures/device-session-page.mjs').read_text();c=json.loads((compiled/'apps.json').read_bytes());app=c['apps'][0];src=compiled/Path(app['path']).parent.relative_to('assets/desktop');b=(src/'index.mjs').read_bytes();assert hashlib.sha256(b).hexdigest()==app['sha256'];(assets/'device-history-host.mjs').write_bytes(b);r['actualCompiledCoreSHA256']=app['sha256'];r['driverSHA256']=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
  for name in ['device-channel-session.mjs','channel-archive.mjs','channel-directory.mjs','storage-consent.mjs','channel-keys.mjs']:fixture=fixture.replace("'./assets/desktop/"+name+"'","'./assets/desktop/device-history-host.mjs'")
  for name in ['device-channel-state.mjs','device-replica.mjs','device-replica-round.mjs','device-member-channel.mjs','device-member-introductions.mjs','device-replica-exchange.mjs']:fixture=fixture.replace("'./network/"+name+"'","'./assets/desktop/device-history-host.mjs'")
  (folder/'fixture.mjs').write_text(fixture);(folder/'index.html').write_text('<!doctype html><main id="windows"></main><script src="bootstrap.js"></script><script src="networking-fixture.js"></script><script src="desktop-apps.js"></script><script type="module" src="fixture.mjs"></script>');server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Quiet,directory=str(folder)));thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start();origin='http://127.0.0.1:'+str(server.server_port)
  v=d.call('/session',{'capabilities':{'alwaysMatch':{'browserName':'chrome','goog:chromeOptions':{'binary':'/snap/chromium/current/usr/lib/chromium-browser/chrome','args':['--headless=new','--no-sandbox','--disable-dev-shm-usage','--user-data-dir='+str(profile)]}}}});sid=v['sessionId'];d.call('/session/'+sid+'/timeouts',{'script':45000});d.call('/session/'+sid+'/url',{'url':origin+'/?side=idle&automatic=1&peers=1&inline=1&credits=1'});d.wait(lambda:js('return window.fixtureReady===true;'),20);d.call('/session/'+sid+'/goog/cdp/execute',{'cmd':'Browser.setPermission','params':{'permission':{'name':'persistent-storage'},'setting':'granted','origin':origin}});w=js('return hostSessionCase.open("chat");');d.wait(lambda:js('return !!hostSessionCase.node(arguments[0])?.querySelector(".storage-consent button:not(:disabled)");',[w]),20);e=d.call('/session/'+sid+'/element',{'using':'css selector','value':'.storage-consent button'})['element-6066-11e4-a52e-4f735466cecf'];d.call('/session/'+sid+'/element/'+e+'/click',{});d.wait(lambda:js('return !!hostSessionCase.node(arguments[0])?.querySelector("[data-device-channels]");',[w]),20);js('hostSessionCase.view=hostSessionCase.facades.get(arguments[0]);',[w]);task('const actor=(await hostSessionCase.view.createIdentity("Idle actor")).channel;hostSessionCase.group=await hostSessionCase.view.createChannel({label:"Quiet native group",controller:actor,validators:[actor],publicRead:true,publicWrite:true});return true;');d.wait(lambda:task('const o=hostSessionCase.owner().stats();return o.peerOrganization[0].coreRuns>=1&&o.scheduler.jobs===0;'),20);time.sleep(3);r['observed']=task('return {owner:hostSessionCase.owner().stats(),snapshot:await hostSessionCase.group.snapshot()};');check('a native idle phase update does not trigger a second self-woken reconciliation',r['observed']['owner']['peerOrganization'][0]['coreRuns']==1);check('the idle native host retains one bounded worker and no pending original or accepted block',r['observed']['owner']['scheduler']['channels']==1 and r['observed']['snapshot']['height']==0 and not r['observed']['snapshot']['pending']);r['status']='PASS'
 except Exception as e:r.update(error=str(e),traceback=traceback.format_exc())
 finally:
  if sid:
   try:r['cleanup']=task('await hostSessionCase.closeAll();return {owner:hostSessionCase.owner().stats(),network:(await hostSessionCase.stats()).network.budget};');assert all(v==0 for k,v in r['cleanup']['network'].items() if k!='closed')
   except Exception as e:r.update(status='FAIL',cleanupError=str(e))
   try:d.call('/session/'+sid,method='DELETE')
   except Exception as e:r['browserCleanupError']=str(e)
  if server:server.shutdown();server.server_close()
  if thread:thread.join(timeout=3)
  shutil.rmtree(profile);tmp.cleanup();r.update(ownedProfileRemoved=not profile.exists(),fixtureRemoved=not folder.exists())
 return r
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--compiled-core',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();assert not a.output.exists();r=run(a.compiled_core);a.output.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({'status':r['status'],'checks':len(r['checks']),'error':r.get('error'),'cleanupError':r.get('cleanupError')}));raise SystemExit(r['status']!='PASS')
