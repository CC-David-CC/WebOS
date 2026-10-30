#!/usr/bin/env python3
"""HTTPS/WSS/RTC with only owned peers and explicit ICE policy witnesses."""
import argparse,base64,hashlib,http.client,json,os,signal,ssl,stat,subprocess,sys,tempfile,time,urllib.request,urllib.error
from urllib.parse import urlsplit
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--guest-internet',action='store_true');p.add_argument('--expect-relay-protocol',choices=['tls','tcp','udp']);p.add_argument('--url',default='https://127.0.0.1:8445/');p.add_argument('--spki-file',default='.build/checks/tls-preview/spki.txt');p.add_argument('--ca-file',default='.build/checks/tls-preview/cert.pem');p.add_argument('--require-trust',choices=['local','test-server'],default='local');p.add_argument('--wait-delegation-expiry',action='store_true');p.add_argument('--kill-steward-pid-file');p.add_argument('--steward-program',type=Path,default=Path('scripts/serve-steward.py'),help='Exact expected native steward program for the owned failure fixture');p.add_argument('--expect-steward-recovery',action='store_true')
p.add_argument('--renew-root-dir',type=Path);p.add_argument('--renew-runtime-dir',type=Path);p.add_argument('--operator-program',type=Path,default=Path('scripts/provision-connected.py'));p.add_argument('--read-only-operator',action='store_true');p.add_argument('--public-tls',action='store_true',help='Require default certificate trust in Python and Chrome; no certificate bypass');p.add_argument('--expect-relay-address',help='Capture native ICE stats in this disposable test context and require this relay allocation address');p.add_argument('--expect-relay-port-max',type=int,choices=[13531,13627],default=13531);p.add_argument('--restart-guest-config',type=Path,help='Owned disposable fixture only; verify VM/network recovery after guest restart');p.add_argument('--force-relay',action='store_true',help='Restrict only these disposable client PCs to relay while retaining the signed server policy');p.add_argument('--expect-direct',action='store_true')
p.add_argument('--expected-server-policy',choices=['all','relay'],help='Require the actual HTTPS deployment ICE policy')
p.add_argument('--test-native-policy',choices=['all'],help='Preflight only: change owned native PCs, not the server policy; never a rollout proof')
p.add_argument('--output',type=Path,default=Path('.build/checks/owned-tls-discovery-result.json'))
p.add_argument('--chrome-binary',default='/snap/chromium/current/usr/lib/chromium-browser/chrome')
a=p.parse_args()
if a.test_native_policy and a.force_relay:p.error('Native preflight and forced relay are mutually exclusive')
if a.output.resolve().parent!=Path('.build/checks').resolve():p.error('Output must be inside .build/checks')
if a.force_relay and a.expect_direct:p.error('Direct and forced-relay checks are mutually exclusive')
if bool(a.renew_root_dir)!=bool(a.renew_runtime_dir):p.error('Root renewal fixture directories must be paired')
if a.restart_guest_config and (a.public_tls or urlsplit(a.url).hostname!='127.0.0.1' or not __import__('re').fullmatch(r'/srv/codi-persistent-[0-9a-f]{12}/control/managed.json',str(a.restart_guest_config))):p.error('Guest restart requires an owned disposable loopback fixture')
BASE='http://127.0.0.1:19515';sessions=[];result={'status':'FAIL','url':a.url};downloads=tempfile.TemporaryDirectory(prefix='pgn-downloads-',dir=Path('.build/checks').resolve())
def req(path,data=None,method=None):
 r=urllib.request.Request(BASE+path,data=None if data is None else json.dumps(data).encode(),headers={'Content-Type':'application/json'},method=method)
 with urllib.request.urlopen(r,timeout=90) as response:return json.load(response)['value']
def js(s,code):return req('/session/'+s+'/execute/sync',{'script':code,'args':[]})
def send_guest(s,text):return js(s,'(typeof sendTerminal==="function"?text=>sendTerminal(2,text):text=>v86Instance.serial0_send(text))('+json.dumps(text)+')')
def asyncjs(s,code):return req('/session/'+s+'/execute/async',{'script':'const done=arguments[0];'+code,'args':[]})
def wait(s,code):
 end=time.monotonic()+80
 while time.monotonic()<end:
  if js(s,code):return
  time.sleep(.2)
 raise AssertionError(js(s,'return document.body.textContent'))
def click(s,selector):
 wait(s,'return !window.desktopLab?.lifecycle?.blocked&&document.querySelector('+json.dumps(selector)+')&&!document.querySelector('+json.dumps(selector)+').disabled')
 js(s,'document.querySelector('+json.dumps(selector)+').click()')
def send(s,text):js(s,'const n=document.querySelector("[data-chat-draft]");n.value='+json.dumps(text)+';n.dispatchEvent(new Event("input"));document.querySelector("[data-chat-send]").click()')
try:
 if a.public_tls:
  with urllib.request.urlopen(a.url,timeout=10) as response:assert response.status==200
  context=ssl.create_default_context()
 else:
  # Disposable loopback fixtures must fail default trust; use their explicit CA.
  try:urllib.request.urlopen(a.url,timeout=5)
  except urllib.error.URLError as error:assert isinstance(error.reason,ssl.SSLCertVerificationError),error
  else:raise AssertionError('Disposable certificate unexpectedly trusted by default')
  context=ssl.create_default_context(cafile=a.ca_file)
 with urllib.request.urlopen(a.url+'config.json',context=context) as response:config=json.load(response)
 server_policy=config.get('rtc',{}).get('preference',{}).get('preferred',config.get('rtc',{}).get('iceTransportPolicy'))
 if a.expected_server_policy:assert server_policy==a.expected_server_policy,'Server ICE policy differs from the required deployment policy'
 assert config['discovery']['pin']['allowLoopback'] is False
 endpoint=config['discovery']['pin']['endpoints'][0]
 assert endpoint==a.url.replace('https://','wss://').rstrip('/')+'/rendezvous',endpoint
 for path in ('.build/checks/tls-preview/key.pem','scripts/serve-discovery.py'):
  try:urllib.request.urlopen(a.url+path,context=context,timeout=5)
  except urllib.error.HTTPError as error:assert error.code==404,error
  else:raise AssertionError('Private resource served over TLS')
 target=urlsplit(a.url);connection=http.client.HTTPSConnection(target.hostname,target.port or 443,context=context,timeout=5)
 try:
  connection.request('GET',urlsplit(endpoint).path,headers={'Connection':'Upgrade','Upgrade':'websocket','Sec-WebSocket-Version':'13','Sec-WebSocket-Key':'dGhlIHNhbXBsZSBub25jZQ==','Origin':'https://wrong.invalid'})
  response=connection.getresponse();assert response.status==403,response.status;response.read()
 finally:connection.close()
 chrome_args=['--headless=new','--no-sandbox','--disable-dev-shm-usage']
 if not a.public_tls:chrome_args.append('--ignore-certificate-errors-spki-list='+Path(a.spki_file).read_text().strip())
 for _ in range(2):
  s=req('/session',{'capabilities':{'alwaysMatch':{'browserName':'chrome','goog:chromeOptions':{'binary':a.chrome_binary,'args':chrome_args}}}})['sessionId'];sessions.append(s)
  native_policy='relay' if a.force_relay else a.test_native_policy
  override='args[0]={...(args[0]||{}),iceTransportPolicy:'+json.dumps(native_policy)+'};' if native_policy else ''
  req('/session/'+s+'/goog/cdp/execute',{'cmd':'Page.addScriptToEvaluateOnNewDocument','params':{'source':'window.__privateTurnPeers=[];window.__privateTurnErrors=[];window.RTCPeerConnection=new Proxy(window.RTCPeerConnection,{construct(target,args){'+override+'const pc=Reflect.construct(target,args);pc.addEventListener("icecandidateerror",e=>{if(__privateTurnErrors.length<16)__privateTurnErrors.push({code:e.errorCode,text:e.errorText,url:e.url});});window.__privateTurnPeers.push(pc);return pc;}});'}})
  if a.restart_guest_config:req('/session/'+s+'/goog/cdp/execute',{'cmd':'Page.addScriptToEvaluateOnNewDocument','params':{'source':"(()=>{const Native=WebSocket;window.__guestSockets=[];window.WebSocket=class extends Native{constructor(...args){super(...args);if(String(args[0]).includes('/guest-network'))__guestSockets.push(this);}};})();"}})
  req('/session/'+s+'/url',{'url':a.url})
  wait(s,'return !!window.desktopLab?.session?.localKeyFingerprint&&typeof v86Instance!=="undefined"&&!!v86Instance')
  js(s,'window.__networkStatus=[];if(typeof guestNetworkAdapter!=="undefined"&&guestNetworkAdapter){const previous=guestNetworkAdapter.onStatus;guestNetworkAdapter.onStatus=value=>{__networkStatus.push(value);if(__networkStatus.length>32)__networkStatus.shift();previous(value);};}')
  assert js(s,'return isSecureContext&&location.protocol==="https:"&&currentSession.trust.level==='+json.dumps(a.require_trust))
  if a.require_trust=='test-server':assert js(s,'return identityConfig.identity.mode==="server"&&!!currentSession.public.certificate')
  js(s,'window.tlsVM=v86Instance;window.tlsSession=desktopLab.session.id;surfaces.values().next().value.launch("chat")')
  tracked=asyncjs(s,'import(new URL("network/discovery.mjs",document.baseURI)).then(({Discovery})=>{const original=Discovery.prototype.start;Discovery.prototype.start=function(...args){window.__ownedDiscovery=this;return original.apply(this,args);};done(true);}).catch(error=>done({error:error.message}));');assert tracked is True
  click(s,'[data-discovery-action="start"]');wait(s,'return document.querySelector("[data-discovery-status]").textContent.startsWith("ready")')
 left,right=sessions
 right_id=js(right,'return {lease:__ownedDiscovery.lease.lease_id,sid:currentSession.public.sid,key:currentSession.fingerprint};')
 left_id=js(left,'return {sid:currentSession.public.sid,key:currentSession.fingerprint};')
 found=False
 for attempt in range(12):
  click(left,'[data-discovery-action="sample"]');time.sleep(.5)
  found=js(left,'const sample=__ownedDiscovery.samples.get('+json.dumps(right_id['lease'])+');return !!sample&&sample.lease.session_id==='+json.dumps(right_id['sid'])+'&&sample.lease.key_id==='+json.dumps(right_id['key'])+';')
  if found:break
 assert found,'Owned test peer was not sampled; no invitation sent to anyone else'
 js(left,'document.querySelector("[data-discovery-sample]").value='+json.dumps(right_id['lease']))
 click(left,'[data-discovery-action="invite"]')
 wait(right,'return [...__ownedDiscovery.incoming.values()].some(i=>i.peerId==='+json.dumps(left_id['sid'])+'&&i.keyId==='+json.dumps(left_id['key'])+');')
 js(right,'const item=[...__ownedDiscovery.incoming].find(([,i])=>i.peerId==='+json.dumps(left_id['sid'])+'&&i.keyId==='+json.dumps(left_id['key'])+');document.querySelector("[data-discovery-invitation]").value=item[0];')
 click(right,'[data-discovery-action="accept"]')
 result['onlyOwnedPeersInvited']=True
 for s in sessions:wait(s,'return document.querySelector("[data-chat-status]").textContent.startsWith("ready")')
 send(left,'HTTPS WSS peer message left');wait(right,'return document.querySelector("[data-chat-history]").textContent.includes("HTTPS WSS peer message left")')
 send(right,'HTTPS WSS peer message right');wait(left,'return document.querySelector("[data-chat-history]").textContent.includes("HTTPS WSS peer message right")')
 for s in sessions:js(s,'surfaces.values().next().value.launch("rooms")')
 click(left,'[data-room-create]');wait(left,'return !!document.querySelector("[data-room-select]").value')
 room_id=js(left,'return document.querySelector("[data-room-select]").value')
 wait(right,'return document.querySelector("[data-room-select]").options.length>1')
 js(right,'const n=document.querySelector("[data-room-select]");n.value='+json.dumps(room_id)+';n.dispatchEvent(new Event("change"))')
 click(right,'[data-room-accept]')
 for s in sessions:wait(s,'return document.querySelector("[data-room-status]").textContent.includes("active")')
 def room_send(s,label,text,button):
  wait(s,'return !document.querySelector('+json.dumps(button)+').disabled')
  js(s,'const n=document.querySelector('+json.dumps('[aria-label="'+label+'"]')+');n.value='+json.dumps(text)+';n.dispatchEvent(new Event("input"));document.querySelector('+json.dumps(button)+').click()')
 room_send(left,'Room chat message','TLS room conversation only','[data-room-send-chat]')
 wait(right,'return document.querySelector("[data-room-chat]").textContent.includes("TLS room conversation only")')
 room_send(left,'Chess move notation','e4','[data-room-send-move]');wait(right,'return document.querySelector("[data-room-moves]").textContent.includes("e4")')
 room_send(right,'Chess move notation','e5','[data-room-send-move]');wait(left,'return document.querySelector("[data-room-moves]").textContent.includes("e5")')
 for s in sessions:assert js(s,'return !document.querySelector("[data-room-moves]").textContent.includes("TLS room conversation only")&&!document.querySelector("[data-chat-history]").textContent.includes("TLS room conversation only")')
 restart_evidence=None
 if a.restart_guest_config:
  for s in sessions:
   wait(s,'return desktopLab.guestState==="ready"')
   js(s,'window.__cookieVM=v86Instance;')
   send_guest(s,'printf COOKIE_VM_SURVIVOR > /tmp/cookie-vm-survivor; echo COOKIE_FILE_READY\r')
   wait(s,'return /(?:^|\\n)COOKIE_FILE_READY(?:\\n|$)/.test(serialScreen.text())')
  control="""import json,pathlib,stat,subprocess,sys
p=pathlib.Path(sys.argv[1]);v=json.loads(p.read_text());stage=p.parent.parent
assert v['instance']==stage.name and v['release'].startswith(str(stage)+'/') and v['python']==str(stage/'venv/bin/python')
assert p.stat().st_uid==0 and stat.S_IMODE(p.stat().st_mode)==0o600
for action in ['stop','start']:subprocess.run([v['python'],'-B',v['release']+'/scripts/manage-services.py',action,'--config',str(p),'--roles','guest'],check=True,capture_output=True)
"""
  subprocess.run(['sudo','-n','/usr/bin/python3','-B','-c',control,str(a.restart_guest_config)],check=True,capture_output=True,text=True,timeout=90)
  for s in sessions:
   wait(s,'return __guestSockets.length>1&&__guestSockets.at(-1).readyState===WebSocket.OPEN')
   js(s,'window.__cookieOffset=serialScreen.text().length;')
   send_guest(s,'cat /tmp/cookie-vm-survivor; echo; ping -c 2 -W 4 1.1.1.1; echo COOKIE_RESTART_DONE\r')
   wait(s,'return /(?:^|\\n)COOKIE_RESTART_DONE(?:\\n|$)/.test(serialScreen.text().slice(__cookieOffset))&&serialScreen.text().slice(__cookieOffset).includes("2 packets received")')
   assert js(s,'return v86Instance===__cookieVM&&serialScreen.text().slice(__cookieOffset).includes("2 packets received")&&/(?:^|\\n)COOKIE_VM_SURVIVOR\\r?\\n/.test(serialScreen.text().slice(__cookieOffset))')
  restart_evidence={'sameVmObjects':True,'ramFilesPreserved':True,'existingBrowserCookiesReconnect':True,'twoGuestsPingAfterRestart':True}
 internet_evidence=[]
 if a.guest_internet:
  for s in sessions:
   wait(s,'return desktopLab.guestState==="ready"')
   send_guest(s,'ping -c 2 -W 4 1.1.1.1; echo INTEGRATED_PING_DONE\r')
   wait(s,'return serialScreen.text().includes("2 packets transmitted")')
   assert js(s,'return serialScreen.text().includes("2 packets received")')
   command="nslookup example.com; timeout 15 wget -O /tmp/example.html http://example.com; grep -q 'Example Domain' /tmp/example.html && echo HTTP_CONTENT_VERIFIED; echo INTEGRATED_WEB_DONE\r"
   send_guest(s,command)
   wait(s,'return /(?:^|\\n)INTEGRATED_WEB_DONE(?:\\n|$)/.test(serialScreen.text())')
   assert js(s,'return serialScreen.text().replaceAll("\\r","").includes("\\nHTTP_CONTENT_VERIFIED\\n")')
   internet_evidence.append({'pingReplies':2,'dnsAndHttp':True})
 witnesses=[]
 for s in sessions:
  snapshot=asyncjs(s,'desktopNetwork.stats().then(done)');assert snapshot['connectionState']=='connected' and snapshot['discovery']['status']=='ready',snapshot
  policies=js(s,'return __privateTurnPeers.map(pc=>pc.getConfiguration().iceTransportPolicy)')
  assert policies and all(policy==(a.test_native_policy or ('relay' if a.force_relay else server_policy)) for policy in policies),policies
  snapshot['nativeIcePolicies']=policies
  if a.expect_relay_protocol:assert snapshot.get('localCandidateType')==snapshot.get('remoteCandidateType')=='relay' and snapshot.get('localRelayProtocol')==a.expect_relay_protocol,snapshot
  if a.expect_direct:assert snapshot.get('localCandidateType') in ['host','srflx','prflx'] and snapshot.get('remoteCandidateType') in ['host','srflx','prflx'],snapshot
  if a.expect_relay_address:
   allocations=asyncjs(s,'''Promise.all(window.__privateTurnPeers.map(async pc=>{const report=await pc.getStats(),out=[];report.forEach(pair=>{if(pair.type==='candidate-pair'&&pair.state==='succeeded'&&pair.nominated){const local=report.get(pair.localCandidateId),remote=report.get(pair.remoteCandidateId);out.push({local:local.address,remote:remote.address,localPort:local.port,remotePort:remote.port,localType:local.candidateType,remoteType:remote.candidateType,relayProtocol:local.relayProtocol});}});return out;})).then(groups=>done(groups.flat())).catch(error=>done({error:error.message}));''')
   assert isinstance(allocations,list) and allocations,allocations
   assert all(pair['local']==pair['remote']==a.expect_relay_address and pair['localType']==pair['remoteType']=='relay' and pair['relayProtocol']=='tls' and 13500<=pair['localPort']<=a.expect_relay_port_max and 13500<=pair['remotePort']<=a.expect_relay_port_max for pair in allocations),allocations
   snapshot['privateRelayAllocations']=allocations
  witnesses.append(snapshot)
  if not a.wait_delegation_expiry and not a.kill_steward_pid_file and not a.renew_root_dir:click(s,'[data-discovery-action="stop"]')
 crash_evidence=None
 if a.kill_steward_pid_file:
  assert a.require_trust=='test-server' and not a.wait_delegation_expiry
  pid_path=Path(a.kill_steward_pid_file);info=pid_path.lstat()
  assert stat.S_ISREG(info.st_mode) and info.st_uid==os.getuid() and stat.S_IMODE(info.st_mode)==0o600
  worker=json.loads(pid_path.read_text());pid=worker['pid'];assert pid>1 and pid!=os.getpid()
  actual=[part.decode() for part in Path('/proc/'+str(pid)+'/cmdline').read_bytes().removesuffix(b'\0').split(b'\0')]
  assert actual==worker['command'] and str(a.steward_program.resolve(strict=True)) in actual,'Refusing to kill a different process'
  os.kill(pid,signal.SIGKILL)
  after=[]
  for index,s in enumerate(sessions):
   wait(s,'return /^(recovering|closed)/.test(document.querySelector("[data-discovery-status]").textContent)')
   snapshot=asyncjs(s,'desktopNetwork.stats().then(done)');assert snapshot['connectionState']=='connected',snapshot
   ready=[p['connectionId'] for p in snapshot['peers'] if p['state']=='ready']
   assert ready==[p['connectionId'] for p in witnesses[index]['peers'] if p['state']=='ready'] and len(ready)==1
   renewal=asyncjs(s,'''const sid=currentSession.public.sid,key=currentSession.fingerprint,old=currentSession.public.certificate;currentSession.trust.claims.exp=Math.floor(Date.now()/1000)+100;maintainIdentity().then(()=>done({sameSession:currentSession.public.sid===sid,sameKey:currentSession.fingerprint===key,renewed:currentSession.public.certificate!==old,trust:currentSession.trust.level}));''')
   assert renewal=={'sameSession':True,'sameKey':True,'renewed':True,'trust':'test-server'},renewal
   after.append(snapshot)
  with urllib.request.urlopen(a.url+'config.json',context=context,timeout=5) as response:after_config=json.load(response)
  assert after_config['identity']['mode']=='server'
  if a.expect_steward_recovery:
   replacement=json.loads(pid_path.read_text())
   end=time.monotonic()+20
   while replacement['pid']==pid and time.monotonic()<end:
    time.sleep(.1);replacement=json.loads(pid_path.read_text())
   assert replacement['pid']!=pid and replacement['command']==worker['command'] and replacement['privateRun']==worker['privateRun'] and replacement['restarts']==1
   for index,s in enumerate(sessions):
    wait(s,'return document.querySelector("[data-discovery-status]").textContent.startsWith("ready")')
    recovered=asyncjs(s,'desktopNetwork.stats().then(done)')
    assert recovered['discovery']['recoveries']>=1 and recovered['discovery']['stewardKeyId']==witnesses[index]['discovery']['stewardKeyId']
    assert [p['connectionId'] for p in recovered['peers'] if p['state']=='ready']==[p['connectionId'] for p in witnesses[index]['peers'] if p['state']=='ready']
   # Recovered discovery must serve a fresh sample, not merely show ready.
   click(left,'[data-discovery-action="sample"]');wait(left,'return document.querySelector("[data-discovery-sample]").options.length===1')
  crash_evidence={'signal':'SIGKILL','pidIdentityChecked':True,'sameProvisionedWorkerRecovered':a.expect_steward_recovery,'issuerConfigStillServer':True,'issuerRenewedSameKeyAndSession':True,'sameEstablishedPeerConnection':True,'snapshots':after}
 root_evidence=None
 if a.renew_root_dir:
  assert a.require_trust=='test-server' and not a.wait_delegation_expiry
  previous_revision=json.loads(base64.urlsafe_b64decode(config['discovery']['seed'].split('.')[1]+'==='))['revision']
  operator_command=[sys.executable,'-B',str(a.operator_program.resolve(strict=True)),'renew','--runtime-dir',str(a.renew_runtime_dir),'--root-dir',str(a.renew_root_dir)]
  if a.read_only_operator:operator_command=['bwrap','--ro-bind','/','/','--bind',str(a.renew_runtime_dir),str(a.renew_runtime_dir),'--bind',str(a.renew_root_dir),str(a.renew_root_dir),'--proc','/proc','--dev','/dev','--',*operator_command]
  renewed=subprocess.run(operator_command,env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'},capture_output=True,timeout=15)
  assert renewed.returncode==0,'Explicit operator renewal failed'
  issuance=json.loads(renewed.stdout);assert issuance['revision']==previous_revision+1
  end=time.monotonic()+45
  while time.monotonic()<end:
   with urllib.request.urlopen(a.url+'config.json',context=context,timeout=5) as response:after_config=json.load(response)
   if json.loads(base64.urlsafe_b64decode(after_config['discovery']['seed'].split('.')[1]+'==='))['revision']==issuance['revision']:break
   time.sleep(.2)
  else:raise AssertionError('New root policy did not reach public metadata')
  assert after_config['discovery']['pin']==config['discovery']['pin'] and after_config['identity']==config['identity']
  snapshots=[]
  for index,s in enumerate(sessions):
   end=time.monotonic()+80
   while time.monotonic()<end:
    snapshot=asyncjs(s,'desktopNetwork.stats().then(done)')
    if snapshot['discovery']['status']=='ready' and snapshot['discovery']['authorityRevision']==issuance['revision']:break
    time.sleep(.2)
   else:raise AssertionError('Browser did not verify and recover the renewed root policy')
   assert snapshot['connectionState']=='connected' and snapshot['discovery']['stewardKeyId']==witnesses[index]['discovery']['stewardKeyId']
   assert [p['connectionId'] for p in snapshot['peers'] if p['state']=='ready']==[p['connectionId'] for p in witnesses[index]['peers'] if p['state']=='ready']
   assert js(s,'return currentSession.public.sid===tlsSession&&v86Instance===tlsVM')
   snapshots.append(snapshot)
  send(right,'RTC after explicit root renewal');wait(left,'return document.querySelector("[data-chat-history]").textContent.includes("RTC after explicit root renewal")')
  root_evidence={'explicitOperatorRenewal':True,'revision':issuance['revision'],'sameRootPinAndIssuer':True,'sameScopedServiceKey':True,'sameEstablishedPeerConnections':True,'browserVerifiedAndRecovered':True,'messageAfterRenewal':True,'snapshots':snapshots}
 expiry_evidence=None
 if a.wait_delegation_expiry:
  assert a.require_trust=='test-server','Expiry isolation requires a real development issuer'
  deadline=json.loads(base64.urlsafe_b64decode(config['discovery']['seed'].split('.')[1]+'==='))['exp']
  # Wait through an additional publication tick, proving the expired publisher
  # path does not terminate the independent issuer, rather than racing expiry.
  assert 0<deadline+32-time.time()<100,'Use a fresh short-lived fixture for expiry checks'
  while time.time()<deadline+32:time.sleep(.2)
  after=[]
  for s in sessions:
   wait(s,'return document.querySelector("[data-discovery-status]").textContent.startsWith("closed")')
   snapshot=asyncjs(s,'desktopNetwork.stats().then(done)');assert snapshot['connectionState']=='connected' and snapshot['budget']['connections']==1,snapshot
   after.append(snapshot)
   renewal=asyncjs(s,'''const sid=currentSession.public.sid,key=currentSession.fingerprint,old=currentSession.public.certificate;currentSession.trust.claims.exp=Math.floor(Date.now()/1000)+100;maintainIdentity().then(()=>done({sameSession:currentSession.public.sid===sid,sameKey:currentSession.fingerprint===key,renewed:currentSession.public.certificate!==old,trust:currentSession.trust.level}));''')
   assert renewal=={'sameSession':True,'sameKey':True,'renewed':True,'trust':'test-server'},renewal
  with urllib.request.urlopen(a.url+'config.json',context=context,timeout=5) as response:after_config=json.load(response)
  assert after_config['identity']['mode']=='server' and after_config['identity']['authorityKeys']
  expiry_evidence={'delegationExpiredAt':deadline,'checkedAt':time.time(),'discoveryClosed':True,'rtcConnected':True,'remainingPhysicalConnectionsPerBrowser':1,'issuerRenewedSameKeyAndSession':True,'issuerConfigStillServer':True,'snapshots':after}
 send(left,'RTC survives WSS stop');wait(right,'return document.querySelector("[data-chat-history]").textContent.includes("RTC survives WSS stop")')
 room_send(left,'Chess move notation','Nf3','[data-room-send-move]');wait(right,'return document.querySelector("[data-room-moves]").textContent.includes("Nf3")')
 for s in sessions:assert js(s,'return v86Instance===tlsVM&&desktopLab.session.id===tlsSession')
 exported=[]
 for index,s in enumerate(sessions):
  folder=Path(downloads.name)/str(index);folder.mkdir(mode=0o700)
  req('/session/'+s+'/goog/cdp/execute',{'cmd':'Browser.setDownloadBehavior','params':{'behavior':'allow','downloadPath':str(folder),'eventsEnabled':True}})
  wait(s,'return [...surfaces.values()][0].windows.filter(w=>w.app==="rooms").every(w=>!w.roomWorking)')
  click(s,'[data-room-pgn-export]');file=folder/'match.pgn';until=time.monotonic()+30
  while not file.is_file() and time.monotonic()<until:time.sleep(.1)
  assert file.is_file() and 0<file.stat().st_size<=65536,'PGN download did not complete'
  text=file.read_text();assert '1. e4 e5 2. Nf3' in text and 'TLS room conversation only' not in text;exported.append(text)
 assert exported[0]==exported[1]
 result={'status':'PASS','url':a.url,'scope':('Two Chrome contexts on the public HTTPS origin with default certificate trust; development-machine network, not independent WAN/NAT proof' if a.public_tls else 'Two real Chrome contexts, loopback Caddy HTTPS/WSS and actual RTC delivery; configured identity, no WAN/public certificate claim'),'defaultCertificateTrust':a.public_tls,'untrustedCertificateRejected':not a.public_tls,'privatePathsNotServed':True,'foreignWssOriginRejected':True,'secureContext':True,'identityTrust':a.require_trust,'releasePinnedWss':endpoint,'loopbackWsExceptionDisabled':True,'explicitDiscoveryConsent':True,'bidirectionalRTC':True,'separateRoomChatAndMoves':True,'pgnExportMatchesAcrossPeersAndExcludesChat':True,'legalMoves':['e4','e5','Nf3'],'moveAfterWssStop':True,'delegationExpiry':expiry_evidence,'stewardCrash':crash_evidence,'rootPolicyRenewal':root_evidence,'rtcSurvivesWssStop':True,'guestAndIdentityPreserved':True,'guestInternet':internet_evidence,'expectedRelayProtocol':a.expect_relay_protocol,'clientForcedRelay':a.force_relay,'directCandidatesRequired':a.expect_direct,'publicIceTransportPolicy':config.get('rtc',{}).get('iceTransportPolicy'),'witnesses':witnesses}
 result['guestRelayRestart']=restart_evidence
 result['publicPreferredIcePolicy']=server_policy
 result['publicLegacyIcePolicy']=config.get('rtc',{}).get('iceTransportPolicy')
 result['onlyOwnedPeersInvited']=True
 result['testOnlyNativePolicyOverride']=a.test_native_policy
 result['serverPolicyRolloutVerified']=a.expected_server_policy is not None and a.test_native_policy is None
 result['automaticFallbackAfterBlockedDirectProven']=False
except Exception as error:
 result['error']=str(error);result['browserDiagnostics']=[]
 for s in sessions:
  try:result['browserDiagnostics'].append(js(s,'return {lifecycle:window.desktopLab?.lifecycle,guestState:window.desktopLab?.guestState,network:typeof guestNetworkAdapter==="undefined"?null:{mode:guestNetworkAdapter?.mode,controlled:guestNetworkAdapter?.controlled,socket:guestNetworkAdapter?.socket?.readyState},status:window.__networkStatus||[]}'))
  except Exception:pass
  try:
   result.setdefault('iceFailureDiagnostics',[]).append(asyncjs(s,'Promise.all((window.__privateTurnPeers||[]).map(async pc=>{const stats=await pc.getStats(),candidates=[],pairs=[];stats.forEach(x=>{if(["local-candidate","remote-candidate"].includes(x.type))candidates.push({side:x.type,type:x.candidateType,protocol:x.protocol,relayProtocol:x.relayProtocol});if(x.type==="candidate-pair")pairs.push({state:x.state,nominated:x.nominated,requestsSent:x.requestsSent,responsesReceived:x.responsesReceived});});return {connection:pc.connectionState,ice:pc.iceConnectionState,gathering:pc.iceGatheringState,policy:pc.getConfiguration().iceTransportPolicy,candidates,pairs};})).then(peers=>done({peers,errors:window.__privateTurnErrors||[]})).catch(e=>done({error:e.message}));'))
  except Exception:pass
 raise
finally:
 disposed=[]
 for s in sessions:
  try:
   snapshot=asyncjs(s,'desktopNetwork.close();setTimeout(()=>desktopNetwork.stats().then(done),250)')
   disposed.append(snapshot['budget']['closed'] and all(v==0 for k,v in snapshot['budget'].items() if k!='closed'))
  finally:req('/session/'+s,method='DELETE')
 result['disposed']=disposed
 downloads.cleanup()
 if disposed and not all(disposed):result['status']='FAIL'
 result['sha256']={'scripts/owned-tls-discovery-check.py':hashlib.sha256(Path('scripts/owned-tls-discovery-check.py').read_bytes()).hexdigest()}
 result['servedAssetsSHA256']={}
 try:
  context=ssl.create_default_context() if a.public_tls else ssl.create_default_context(cafile=a.ca_file)
  for name in ['app.js',*('network/'+p.name for p in sorted(Path('network').glob('*.mjs')))]:
   with urllib.request.urlopen(a.url+name,context=context,timeout=15) as response:result['servedAssetsSHA256'][name]=hashlib.sha256(response.read()).hexdigest()
 except Exception as error:
  result['status']='FAIL';result['provenanceError']=type(error).__name__+': '+str(error)


 if a.output.exists():a.output.rename(a.output.with_name(a.output.stem+'-before-'+str(time.time_ns())+'.json'))
 a.output.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
assert result['status']=='PASS',result
