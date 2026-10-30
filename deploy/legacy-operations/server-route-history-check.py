#!/usr/bin/env python3
"""Two real registered Chrome sessions exchange signed frames over server WebSockets."""
import asyncio,copy,json,os,secrets,shutil,socket,subprocess,sys,tempfile,threading,time,types,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];m=types.ModuleType('steward_fixture');m.__file__=str(ROOT/'scripts/steward-network-check.py');exec((ROOT/'scripts/steward-network-check.py').read_text().split('async def main():',1)[0],m.__dict__)
import importlib.util
spec=importlib.util.spec_from_file_location('driver',ROOT/'scripts/touch-preview-check.py');d=importlib.util.module_from_spec(spec);spec.loader.exec_module(d)
name='serverroute'+secrets.token_hex(5);folder=ROOT/'.build/connected-instances'/name;issuer=None;server=None;loop=None;thread=None;sessions=[];profiles=[];publisher=None
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
 async def official(c,g):return True
 args['official_channel_allowed']=official;args['offered_channels_only']=True
 loop=asyncio.new_event_loop();thread=threading.Thread(target=loop.run_forever,daemon=True);thread.start();server=m.StewardServer(**args);asyncio.run_coroutine_threadsafe(server.start(steward_port),loop).result(15)
 public=folder/'public';
 for module in (ROOT/'network').glob('*.mjs'):shutil.copyfile(module,public/'network'/module.name)
 shutil.copytree(ROOT.parent/'served_apps_public/chess/engine',public/'engine');shutil.copyfile(ROOT/'assets/vendor/chess/chess.mjs',public/'engine/chess.mjs')
 (public/'server-route-fixture.mjs').write_text((ROOT/'scripts/server-route-history-fixture.mjs').read_text());(public/'server-route-fixture.html').write_text('<!doctype html><meta charset="utf-8"><script type="module" src="server-route-fixture.mjs"></script>')
 payload={'channel':channel,'genesis':genesis,'tag':tag,'discovery':{'pin':{'realm':args['realm'],'rootKey':args['root_key'],'endpoints':[args['endpoint']],'allowLoopback':True},'seed':args['seed'],'descriptor':server.descriptor(),'scope':scope}}
 (public/'server-route-config.json').write_text(json.dumps(payload))
 def js(s,code,args=[]):return d.call('/session/'+s+'/execute/sync',{'script':code,'args':args})
 def task(s,code,args=[]):
  value=d.call('/session/'+s+'/execute/async',{'script':'const a=Array.from(arguments),done=a.pop();(async()=>{'+code+'})().then(value=>done({value}),error=>done({error:error.stack}));','args':args});assert 'error' not in value,value;return value['value']
 def start_browser(i):
  sid=d.call('/session',{'capabilities':{'alwaysMatch':{'browserName':'chrome','goog:chromeOptions':{'binary':'/snap/chromium/current/usr/lib/chromium-browser/chrome','args':['--headless=new','--no-sandbox','--disable-dev-shm-usage','--user-data-dir='+str(profiles[i])]}}}})['sessionId']
  d.call('/session/'+sid+'/goog/cdp/execute',{'cmd':'Page.setBypassCSP','params':{'enabled':True}})
  d.call('/session/'+sid+'/goog/cdp/execute',{'cmd':'Browser.setPermission','params':{'permission':{'name':'persistent-storage'},'setting':'granted','origin':origin}})
  d.call('/session/'+sid+'/url',{'url':origin+'/server-route-fixture.html?name='+name+str(i)})
  def ready():
   status=js(sid,'return {ready:window.fixtureReady,error:window.fixtureError};')
   if status.get('error'):
    logs=d.call('/session/'+sid+'/log',{'type':'browser'});raise RuntimeError(status['error']+' browser logs '+str(logs)[-2000:])
   return status.get('ready')
  d.wait(ready,30);return sid
 for i in range(2):
  profiles.append(Path(tempfile.mkdtemp(prefix='codi-server-history-',dir=Path.home()/'snap/chromium/common')))
  sessions.append(start_browser(i))
 invitation=task(sessions[0],'return await historyFixture.create();')
 task(sessions[1],'await historyFixture.join(a[0]);',[invitation])
 for sid in sessions:d.wait(lambda:js(sid,'return historyFixture.peers().some(x=>x.state==="ready");'),90)
 for sid in sessions:assert task(sid,'return await historyFixture.transport();')=='Server WebSocket'
 task(sessions[1],'await historyFixture.queue("Server history hello");')
 for sid in sessions:
  d.call('/session/'+sid+'/timeouts',{'script':180000})
  d.wait(lambda:task(sid,'const s=await historyFixture.snapshot();return s.state.messages.some(x=>x.text==="Server history hello")&&!s.pending.some(x=>x.data?.text==="Server history hello");'),120)
 print('PASS registered browsers accept and synchronize a queued signed channel message via the server, with pending cleared',flush=True)
 async def drop_all():await asyncio.gather(*(ws.close(1013,'fixture interruption') for ws,_ in list(server.clients.values())))
 asyncio.run_coroutine_threadsafe(drop_all(),loop).result(15)
 for sid in sessions:d.wait(lambda:js(sid,'return historyFixture.recovery().recoveries>0;'),90)
 for sid in sessions:d.wait(lambda:js(sid,'return historyFixture.peers().some(x=>x.state==="ready");'),90)
 task(sessions[0],'await historyFixture.queue("After server reconnect");')
 for sid in sessions:d.wait(lambda:task(sid,'const s=await historyFixture.snapshot();return s.state.messages.some(x=>x.text==="After server reconnect")&&!s.pending.some(x=>x.data?.text==="After server reconnect");'),120)
 print('PASS reconnects after the coordinator drops both sockets and resumes signed channel delivery',flush=True)
 channel_id=invitation['config']['channel']
 task(sessions[1],'await historyFixture.close();');d.call('/session/'+sessions[1],method='DELETE');sessions[1]=None
 task(sessions[0],'await historyFixture.queue("While browser was away");')
 d.wait(lambda:task(sessions[0],'const s=await historyFixture.snapshot();return s.state.messages.some(x=>x.text==="While browser was away")&&!s.pending.some(x=>x.data?.text==="While browser was away");'),120)
 sessions[1]=start_browser(1);task(sessions[1],'await historyFixture.restore(a[0]);',[channel_id])
 d.wait(lambda:task(sessions[1],'const s=await historyFixture.snapshot();return s.state.messages.some(x=>x.text==="While browser was away");'),120)
 print('PASS a restarted browser restores its channel and catches up on the missed accepted message',flush=True)

 profiles.append(Path(tempfile.mkdtemp(prefix='codi-server-history-',dir=Path.home()/'snap/chromium/common')));sessions.append(start_browser(2))
 white=task(sessions[0],'return await historyFixture.player();');black=task(sessions[1],'return await historyFixture.player();')
 match=task(sessions[0],'return await historyFixture.createMatch(a[0],a[1]);',[white,black])
 assert task(sessions[1],'return await historyFixture.joinMatch(a[0],a[1]);',[match,black])=='black'
 assert task(sessions[2],'return await historyFixture.joinMatch(a[0]);',[match])=='spectator'
 first=task(sessions[0],'return await historyFixture.engineMove();')
 for sid in sessions:d.wait(lambda:task(sid,'return (await historyFixture.game()).state.moves.join(" ")===a[0];',[first]),120)
 second=task(sessions[1],'return await historyFixture.engineMove();')
 for sid in sessions:d.wait(lambda:task(sid,'return (await historyFixture.game()).state.moves.join(" ")===a[0]+" "+a[1];',[first,second]),120)
 task(sessions[2],'await historyFixture.sendGameChat("A spectator watches");')
 for sid in sessions:d.wait(lambda:task(sid,'return (await historyFixture.gameChat()).state.messages.some(x=>x.text==="A spectator watches");'),120)
 for sid in sessions:assert task(sid,'return (await historyFixture.game()).state.messages.length===0;')
 print('PASS two Stockfish players and a registered spectator exchange legal moves and separate chat over server WebSockets',flush=True)
 sys.path.insert(0,str(ROOT));from steward.official_content import reconstruct_scratch_history
 from steward.official_registry import OfficialChannelRegistry
 from steward.official_chess_replay import OfficialChessReplay
 game=match['game']['config'];data=d.call('/session/'+sessions[0]+'/execute/async',{'script':"const done=arguments[arguments.length-1],q=indexedDB.open('codi-device-channel-archive-v1');q.onerror=()=>done({error:String(q.error)});q.onsuccess=()=>{const db=q.result,tx=db.transaction(['heads','nodes'],'readonly'),h=tx.objectStore('heads').getAll(),n=tx.objectStore('nodes').getAll();tx.oncomplete=()=>{db.close();done({heads:h.result,nodes:n.result});};tx.onerror=()=>done({error:String(tx.error)});};",'args':[]});assert not data.get('error')
 entry=next(x for x in data['heads'] if x['key'][1]==game['channel']);pins=entry['key'];nodes={r['cid']:r['wire'] for r in data['nodes'] if r['key'][:2]==pins[:2]};head=json.loads(nodes[entry['history']])['head'];segment=reconstruct_scratch_history(nodes.get,channel=game['channel'],genesis=game['genesisHash'],history=entry['history'],height=2,head=head)
 replay=OfficialChessReplay(game['policyWire'],channel=game['channel'],genesis=game['genesisHash']);bad=copy.deepcopy(segment['blocks'][0]['block']);bad['header']['count']+=1
 try:replay.append([bad]);raise AssertionError('Tampered chess block was accepted')
 except ValueError:pass
 assert replay.snapshot()['height']==0;assert replay.append([row['block'] for row in segment['blocks']])['state']['moves']==[first,second]
 with tempfile.TemporaryDirectory(prefix='codi-chess-archive-') as directory:
  database=Path(directory)/'official.sqlite';registry=OfficialChannelRegistry(database)
  registry._db.execute('INSERT INTO official_channels(channel,genesis_hash,policy_wire,label,description,enabled,enrolled_at) VALUES(?,?,?,?,?,1,0)',(game['channel'],game['genesisHash'],game['policyWire'],'Stockfish match',''))
  for cid,wire in nodes.items():
   if json.loads(wire).get('kind') in ('head','chunk','parts','blob'):registry.stage_node(game['channel'],cid,wire)
  initial=OfficialChessReplay(game['policyWire'],channel=game['channel'],genesis=game['genesisHash']).snapshot()['head'];registry.append_staged_history(game['channel'],expected_head=initial,history=entry['history'],height=2,head=head);registry.close()
  registry=OfficialChannelRegistry(database);assert registry.replayed_head(game['channel'])['state']['moves']==[first,second];page=registry.read_replayed_segment(game['channel'],after_height=0,after_head=initial);assert page['complete'] and len(page['blocks'])==2;registry.close()
 print('PASS server verifies real signed Stockfish moves, rejects a tampered block, and restores chess history after reopening disk storage',flush=True)

finally:
 for sid in sessions:
  if not sid:continue
  try:task(sid,'await historyFixture.close();')
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
 for profile in profiles:
  if profile.exists():shutil.rmtree(profile)
 if folder.exists():shutil.rmtree(folder)
 if publisher and publisher.exists():shutil.rmtree(publisher)
