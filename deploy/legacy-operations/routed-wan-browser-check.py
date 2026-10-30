#!/usr/bin/env python3
"""Public TLS suites across two home browsers and one real outside Moonpie browser.

Only automation uses the Tailscale SSH forward. A WAN claim additionally requires
actual cross-host desktop links to select TURN/TLS through the public hostname.
Relay mode requests an allowed signed per-session preference; RTC is not mocked.
"""
import argparse,copy,hashlib,importlib.util,json,subprocess,time,urllib.error,urllib.request
from pathlib import Path
from types import SimpleNamespace
from urllib.parse import urlsplit
ROOT=Path(__file__).resolve().parent.parent
SUITES={'group':'routed-group-browser-check.py','history':'routed-history-browser-check.py','scope':'routed-scope-browser-check.py'}
def request(driver,path,data=None,method=None):
 r=urllib.request.Request(driver+path,data=None if data is None else json.dumps(data).encode(),headers={'Content-Type':'application/json'},method=method)
 try:
  with urllib.request.urlopen(r,timeout=150) as response:return json.load(response)['value']
 except urllib.error.HTTPError as error:raise RuntimeError(error.read().decode()) from error
def run(kind,release,relay,base=''):
 index=(release/'index.html').read_bytes();graph=json.loads((release/'assets/desktop/network-release.json').read_text())
 with urllib.request.urlopen('https://ksu.codes'+base+'/index.html',timeout=20) as r:assert r.read()==index,'Publish the exact verified candidate first'
 with urllib.request.urlopen('https://ksu.codes'+base+'/config.json',timeout=20) as r:config=json.load(r)
 assert config.get('routedGroups')=={'version':'codi-routed-room/2'}
 fixture=json.loads((ROOT/'.build/checks/moonpie-browser-fixture.json').read_text());assert fixture['sshTarget']=='maint@100.105.243.29'
 local_ip=subprocess.check_output(['curl','--noproxy','*','--silent','--show-error','--max-time','15','https://api.ipify.org'],text=True,timeout=20).strip()
 remote_ip=subprocess.check_output(['ssh','-o','BatchMode=yes',fixture['sshTarget'],'curl --noproxy "*" --silent --show-error --max-time 15 https://api.ipify.org'],text=True,timeout=25).strip()
 assert local_ip!=remote_ip,'Distinct Internet egress is required'
 outside_driver=fixture.get('localDriverURL','http://127.0.0.1:19516')
 for driver in ['http://127.0.0.1:19515',outside_driver]:assert request(driver,'/status')['ready']
 spec=importlib.util.spec_from_file_location('wan_'+kind,ROOT/'scripts'/SUITES[kind]);suite=importlib.util.module_from_spec(spec);spec.loader.exec_module(suite)
 state=SimpleNamespace(origin='https://ksu.codes',base=base,http_chat=False);sessions={};counter=0;captures=[];peer_states=[];posts=[];capture_errors=[];captured_all=False
 remote_index=1 if kind=='scope' else 2
 def drain(sid):
  for row in request(sessions[sid]['driver'],'/session/'+sid+'/log',{'type':'performance'}):
   m=json.loads(row['message'])['message']
   if m['method']=='Network.requestWillBeSent' and m['params']['request']['method']=='POST':posts.append(urlsplit(m['params']['request']['url']).path)
 def capture(sid):
  code='''const done=arguments[0];(async()=>{
   if(typeof desktopNetwork==='undefined')return [];
   const pool=desktopNetwork.appContext().pool,values=[],states=[];
   const candidates=sdp=>(sdp||'').split(/\\r?\\n/).filter(s=>s.startsWith('a=candidate:')).map(s=>{const p=s.slice(2).split(' ');return {protocol:p[2],address:p[4],port:p[5],type:p[p.indexOf('typ')+1]};});
   for(const e of pool?.list()||[]){const link=pool.get(e.id)?.link,pc=link?.pc;if(!pc)continue;
    const state={sid:currentSession.public.sid,peerSid:e.peerId,entryState:e.state,detail:e.detail,connectionState:pc.connectionState,iceConnectionState:pc.iceConnectionState,iceGatheringState:pc.iceGatheringState,signalingState:pc.signalingState,channel:link.channel?.readyState,sentHello:link.sentHello,receivedHello:link.receivedHello,localCandidates:candidates(pc.localDescription?.sdp),remoteCandidates:candidates(pc.remoteDescription?.sdp),candidatePairs:[]};states.push(state);
    if(pc.connectionState==='closed')continue;
    const report=await pc.getStats();for(const pair of report.values())if(pair.type==='candidate-pair'){
     const local=report.get(pair.localCandidateId),remote=report.get(pair.remoteCandidateId);state.candidatePairs.push({state:pair.state,nominated:pair.nominated,requestsSent:pair.requestsSent,responsesReceived:pair.responsesReceived,bytesSent:pair.bytesSent,bytesReceived:pair.bytesReceived,localType:local?.candidateType,remoteType:remote?.candidateType,relayProtocol:local?.relayProtocol,turnURL:local?.url});
    }
    for(const t of report.values())if(t.type==='transport'&&t.selectedCandidatePairId){
     const pair=report.get(t.selectedCandidatePairId),local=report.get(pair.localCandidateId),remote=report.get(pair.remoteCandidateId);
     values.push({sid:currentSession.public.sid,peerSid:e.peerId,state:pc.connectionState,nativePolicy:pc.getConfiguration().iceTransportPolicy,localType:local?.candidateType,remoteType:remote?.candidateType,relayProtocol:local?.relayProtocol,turnURL:local?.url,localAddress:local?.address,remoteAddress:remote?.address});
    }
   }return {values,states,iceErrors:window.wanICEErrors||[]};
  })().then(value=>done({ok:true,value}),error=>done({ok:false,error:error.message}));'''
  result=request(sessions[sid]['driver'],'/session/'+sid+'/execute/async',{'script':code,'args':[]});assert result['ok'],result
  for value in result['value']['values']:captures.append({'host':sessions[sid]['host'],**value})
  peer_states.append({'host':sessions[sid]['host'],**result['value']})
 def call(path,data=None,method=None):
  nonlocal counter,captured_all
  if path=='/session':
   remote=counter==remote_index;counter+=1;driver=outside_driver if remote else 'http://127.0.0.1:19515';data=copy.deepcopy(data)
   options=data['capabilities']['alwaysMatch'];args=options['goog:chromeOptions']['args'];assert not any('ignore-certificate' in a for a in args)
   args.append('--no-proxy-server');options.setdefault('goog:loggingPrefs',{})['performance']='ALL'
   if remote:
    stamp=str(time.time_ns());args.append('--user-data-dir='+fixture['folder']+'/wan-'+kind+'-'+stamp)
    args.extend(['--enable-logging','--log-file='+fixture['folder']+'/chrome-'+kind+'-'+stamp+'.log'])
   result=request(driver,path,data,method);sid=result['sessionId'];sessions[sid]={'driver':driver,'host':'moonpie' if remote else 'development','prepared':False}
   request(driver,'/session/'+sid+'/goog/cdp/execute',{'cmd':'Network.enable','params':{'maxPostDataSize':1048576}})
   request(driver,'/session/'+sid+'/goog/cdp/execute',{'cmd':'Page.addScriptToEvaluateOnNewDocument','params':{'source':"window.wanICEErrors=[];const NativePC=window.RTCPeerConnection;window.RTCPeerConnection=class extends NativePC{constructor(...a){super(...a);this.addEventListener('icecandidateerror',e=>wanICEErrors.push({url:e.url,errorCode:e.errorCode,errorText:e.errorText,address:e.address,port:e.port}));}};"}})
   return result
  sid=path.split('/')[2];record=sessions[sid];driver=record['driver']
  if data and isinstance(data.get('script'),str):
   data=copy.deepcopy(data);data['script']=data['script'].replace('./network/','./'+graph['directory']+'/')
   if 'close(' in data['script'] or 'closeEntry(' in data['script']:
    if not captured_all:
     # Capture every endpoint BEFORE the first destructive operation. Closing
     # one end can remove the other end's selected pair before its own cleanup.
     captured_all=True
     for capture_sid in sessions:
      try:capture(capture_sid)
      except Exception as error:
       captured_all=False;capture_errors.append({'host':sessions[capture_sid]['host'],'error':str(error)[:1000]})
    try:capture(sid)
    except Exception as error:capture_errors.append({'host':record['host'],'error':str(error)[:1000]})
  if method=='DELETE':drain(sid)
  result=request(driver,path,data,method)
  if path.endswith('/execute/sync') or path.endswith('/execute/async'):
   drain(sid)
   if not record['prepared'] and data and 'guestState===' in data.get('script','') and result:
    if relay:
     prep=request(driver,'/session/'+sid+'/execute/async',{'script':'const done=arguments[0];(async()=>{const vm=v86Instance;identityConfig.rtc.preference.preferred="relay";await changeAccount("anonymous");return {sameVM:v86Instance===vm,policy:currentSession.rtc.iceTransportPolicy,sid:currentSession.public.sid};})().then(value=>done({ok:true,value}),error=>done({ok:false,error:error.stack}));','args':[]})
     assert prep['ok'] and prep['value']['sameVM'] and prep['value']['policy']=='relay',prep
     record['identitySid']=prep['value']['sid']
    else:record['identitySid']=request(driver,'/session/'+sid+'/execute/sync',{'script':'return currentSession.public.sid','args':[]})
    record['prepared']=True
  return result
 suite.call=call
 try:result=suite.browser(state)
 finally:
  diagnostic={'sessions':sessions,'candidatePairs':captures,'peerStates':peer_states,'captureErrors':capture_errors,'HTTPPostPaths':posts,'publicIPs':[local_ip,remote_ip]}
  # An inherited suite can stop its cleanup loop after a crashed tab. Close only
  # the contexts this invocation created, without masking the original failure.
  cleanup=[]
  for sid,record in sessions.items():
   try:request(record['driver'],'/session/'+sid,method='DELETE');cleanup.append({'sid':sid,'closed':True})
   except Exception as error:cleanup.append({'sid':sid,'alreadyClosed':'invalid session id' in str(error),'error':str(error)[:200]})
  diagnostic['ownedSessionCleanup']=cleanup
  (ROOT/'.build/checks'/('routed-wan-'+kind+'-diagnostics-'+str(time.time_ns())+'.json')).write_text(json.dumps(diagnostic,indent=2)+'\n')
 remote_sid=next(v['identitySid'] for v in sessions.values() if v['host']=='moonpie')
 cross=[p for p in captures if (p['host']=='moonpie' or p['peerSid']==remote_sid)]
 assert cross,'No actual cross-host selected candidate pair captured'
 relay_wan=all(p['localType']==p['remoteType']=='relay' and p.get('relayProtocol')=='tls' and p.get('turnURL','').startswith('turns:turn.ksu.codes:443') for p in cross)
 if relay:assert relay_wan,'Forced relay must demonstrate actual public TURN/TLS selection'
 allowed={state.base+'/api/v1/'+n for n in ['challenge','anonymous','renew','logout']};assert set(posts)<=allowed,sorted(set(posts)-allowed)
 return result|{'inheritedSuiteScope':result.get('scope'),'scope':__doc__,'nativeManifestSHA256':hashlib.sha256((release/'connected-release.json').read_bytes()).hexdigest(),'publicTLSValidation':True,'actualBrowserContexts':3,'hosts':{'developmentPublicIP':local_ip,'moonpiePublicIP':remote_ip},'clientRequestedAllowedRelay':relay,'independentWANVerified':relay_wan,'independentWANTested':relay_wan,'publicSiteUsed':True,'crossHostCandidatePairs':cross,'allSelectedDesktopPairs':captures,'HTTPPostPaths':posts,'HTTPChatRelayUsed':False,'suiteSourceSHA256':hashlib.sha256((ROOT/'scripts'/SUITES[kind]).read_bytes()).hexdigest()}
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('suite',choices=SUITES);p.add_argument('--release-dir',type=Path,required=True);p.add_argument('--relay',action='store_true');p.add_argument('--base-path',default='');p.add_argument('--output',type=Path);a=p.parse_args();result={'status':'FAIL','suite':a.suite};assert a.base_path in ('','/hidden')
 try:result.update(run(a.suite,a.release_dir.resolve(),a.relay,a.base_path),basePath=a.base_path)
 finally:
  result['sourceSHA256']=hashlib.sha256(Path(__file__).read_bytes()).hexdigest();out=a.output or ROOT/'.build/checks'/('routed-wan-'+a.suite+('-relay' if a.relay else '-default')+'-result.json')
  if out.exists():out.rename(out.with_name(out.stem+'-before-'+str(time.time_ns())+'.json'))
  out.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
