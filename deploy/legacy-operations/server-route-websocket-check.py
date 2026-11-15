#!/usr/bin/env python3
"""Two real registered Chrome sessions exchange signed frames over server WebSockets."""
import asyncio,json,os,secrets,shutil,socket,subprocess,threading,time,types,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];m=types.ModuleType('steward_fixture');m.__file__=str(ROOT/'scripts/steward-network-check.py');exec((ROOT/'scripts/steward-network-check.py').read_text().split('async def main():',1)[0],m.__dict__)
import importlib.util
spec=importlib.util.spec_from_file_location('driver',ROOT/'scripts/touch-preview-check.py');d=importlib.util.module_from_spec(spec);spec.loader.exec_module(d)
name='serverroute'+secrets.token_hex(5);folder=ROOT/'.build/connected-instances'/name;issuer=None;server=None;loop=None;thread=None;sessions=[];publisher=None
with socket.socket() as probe:probe.bind(('127.0.0.1',0));port=probe.getsockname()[1]
origin=f'http://127.0.0.1:{port}'
try:
 issuer=subprocess.Popen([str(ROOT.parent/'.build/auth-venv/bin/python'),str(ROOT/'scripts/serve-connected.py'),'--port',str(port),'--instance',name],stdout=subprocess.DEVNULL,stderr=subprocess.PIPE,text=True)
 def config_ready():
  if issuer.poll() is not None:raise RuntimeError('Issuer exited: '+issuer.stderr.read()[-1000:])
  try:
   with urllib.request.urlopen(origin+'/config.json',timeout=1) as f:return json.load(f)
  except OSError:return False
 config=d.wait(config_ready,30)
 args,scope,steward_port,root,seed=m.fixture();publisher=args['publisher_state'].directory;seed['stewards'][0]['limits']['lease_seconds']=120;args['seed']=m.jose.sign(seed,root,'codi-seed/1');args['admission_seconds']=300;args['identity_policy']=config['identity'];args['origins'].append(origin)
 channel=secrets.token_urlsafe(32);genesis=secrets.token_urlsafe(32);tag=m.jose.digest(m.jose.dumps(['codi-channel-rendezvous/1',channel,genesis]))
 async def official(c,g):return (c,g)==(channel,genesis)
 args['official_channel_allowed']=official;args['offered_channels_only']=True
 loop=asyncio.new_event_loop();thread=threading.Thread(target=loop.run_forever,daemon=True);thread.start();server=m.StewardServer(**args);asyncio.run_coroutine_threadsafe(server.start(steward_port),loop).result(15)
 public=folder/'public';(public/'server-route-fixture.mjs').write_text((ROOT/'scripts/server-route-live-fixture.mjs').read_text());(public/'server-route-fixture.html').write_text('<!doctype html><meta charset="utf-8"><script type="module" src="server-route-fixture.mjs"></script>')
 payload={'channel':channel,'genesis':genesis,'tag':tag,'discovery':{'pin':{'realm':args['realm'],'rootKey':args['root_key'],'endpoints':[args['endpoint']],'allowLoopback':True},'seed':args['seed'],'descriptor':server.descriptor(),'scope':scope}}
 (public/'server-route-config.json').write_text(json.dumps(payload))
 def js(s,code,args=[]):return d.call('/session/'+s+'/execute/sync',{'script':code,'args':args})
 def task(s,code,args=[]):
  value=d.call('/session/'+s+'/execute/async',{'script':'const a=Array.from(arguments),done=a.pop();(async()=>{'+code+'})().then(value=>done({value}),error=>done({error:error.stack}));','args':args});assert 'error' not in value,value;return value['value']
 for i in range(2):
  sid=d.call('/session',{'capabilities':{'alwaysMatch':{'browserName':'chrome','goog:chromeOptions':{'binary':'/snap/chromium/current/usr/lib/chromium-browser/chrome','args':['--headless=new','--no-sandbox','--disable-dev-shm-usage']}}}})['sessionId'];sessions.append(sid)
  d.call('/session/'+sid+'/goog/cdp/execute',{'cmd':'Page.setBypassCSP','params':{'enabled':True}})
  d.call('/session/'+sid+'/url',{'url':origin+'/server-route-fixture.html?name='+name+str(i)})
  def ready():
   status=js(sid,'return {ready:window.fixtureReady,error:window.fixtureError};')
   if status.get('error'):
    logs=d.call('/session/'+sid+'/log',{'type':'browser'});raise RuntimeError(status['error']+' browser logs '+str(logs)[-2000:])
   return status.get('ready')
  d.wait(ready,30)
 for sid in sessions:d.wait(lambda:js(sid,'return routeFixture.pool.list().some(x=>x.state==="ready");'),60)
 for sid in sessions:assert task(sid,'return await routeFixture.stats();')['transport']=='Server WebSocket'
 task(sessions[0],'await routeFixture.send("server route hello");')
 d.wait(lambda:'server route hello' in js(sessions[1],'return routeFixture.messages;'),20)
 task(sessions[1],'await routeFixture.send("server route reply");')
 d.wait(lambda:'server route reply' in js(sessions[0],'return routeFixture.messages;'),20)
 print('PASS two registered browser sessions exchanged signed messages over coordinator WebSocket without WebRTC',flush=True)
finally:
 for sid in sessions:
  try:task(sid,'await routeFixture.close();')
  except Exception:pass
  try:d.call('/session/'+sid,method='DELETE')
  except Exception:pass
 if server and loop:asyncio.run_coroutine_threadsafe(server.close(),loop).result(15)
 if loop:loop.call_soon_threadsafe(loop.stop)
 if thread:thread.join(5)
 if issuer:
  issuer.terminate()
  try:issuer.wait(10)
  except subprocess.TimeoutExpired:issuer.kill();issuer.wait()
 if folder.exists():shutil.rmtree(folder)
 if publisher and publisher.exists():shutil.rmtree(publisher)
