#!/usr/bin/env python3
"""Five real desktops remain usable beyond four optional Linux Internet wires."""
import argparse,hashlib,importlib.util,json,time
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
def load(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def run(registered=False):
 vm=load('capacity_vm',ROOT/'scripts/upgrade-signin-native-vm.py');h=load('capacity_helpers',ROOT/'scripts/touch-preview-check.py');before=vm.runtime();i=json.loads(vm.remote('cat /srv/codi-network-fixture/installed-result.json'));sessions=[];witnesses=[]
 def js(s,code):return h.call('/session/'+s+'/execute/sync',{'script':code,'args':[]})
 def task(s,code):
  d=h.call('/session/'+s+'/execute/async',{'script':'const done=arguments[0];(async()=>{'+code+'})().then(value=>done({ok:true,value}),error=>done({ok:false,error:error.stack}));','args':[]});assert d['ok'],d;return d.get('value')
 try:
  for _ in range(5):
   s=h.call('/session',{'capabilities':{'alwaysMatch':{'browserName':'chrome','goog:chromeOptions':{'binary':'/snap/chromium/current/usr/lib/chromium-browser/chrome','args':['--headless=new','--no-sandbox','--disable-dev-shm-usage','--ignore-certificate-errors-spki-list='+i['fixtureSPKI']]},'goog:loggingPrefs':{'browser':'ALL'}}}})['sessionId'];sessions.append(s)
   h.call('/session/'+s+'/url',{'url':i['publicOrigin']+'/hidden/'})
   h.wait(lambda:js(s,'return window.desktopLab?.guestState==="ready"'),150)
   js(s,'window.capacityVM=v86Instance;')
   if registered:
    task(s,'window.capacityName="vmcap_"+crypto.randomUUID().replaceAll("-","").slice(0,12);window.capacityPassword=crypto.randomUUID()+crypto.randomUUID();await changeAccount("register",capacityName,capacityPassword);return true;')
    if len(sessions)<=4:h.wait(lambda:js(s,'return guestNetworkAdapter?.mode==="registered"'),30)
  time.sleep(4)
  for s in sessions:
   witnesses.append(js(s,'return {linux:guestFiles.ready&&v86Instance===capacityVM,kind:currentSession.public.kind,blocked:desktopLab.lifecycle.blocked,guestMode:guestNetworkAdapter?.mode,socketState:guestNetworkAdapter?.socket?.readyState??null,roomsAvailable:!!desktopNetwork.appContext().routedRooms,body:document.body.innerText.slice(-900)}'))
  checks=[]
  healthy=all(w['linux'] and w['kind']==('registered' if registered else 'anonymous') and not w['blocked'] and w['roomsAvailable'] for w in witnesses)
  if registered:
   healthy=healthy and sum(w['guestMode']=='registered' and w['socketState']==1 for w in witnesses)==4
   if healthy:
    fifth=sessions[-1]
    assert task(fifth,'const f=(await serverFileContext()).files;await f.write("relay-capacity-probe.txt","Files work without a Linux Internet slot.");const r=await f.read("relay-capacity-probe.txt");window.capacityFileSHA=r.sha256;return new TextDecoder().decode(r.data)==="Files work without a Linux Internet slot.";')
    checks.append('fifth registered user can save/read an authorized private file while four other Internet wires remain open')
    js(fifth,'window.capacityFetch=fetch;window.fetch=(url,...args)=>String(url).includes("/api/v1/desktop-status")?Promise.reject(Error("Injected issuer-status outage")):capacityFetch(url,...args);')
    h.wait(lambda:js(fifth,'return desktopLab.lifecycle.blocked'),15)
    checks.append('issuer-status outage still locks desktop controls')
    js(fifth,'window.fetch=capacityFetch;');h.wait(lambda:js(fifth,'return !desktopLab.lifecycle.blocked'),15)
    assert js(fifth,'return v86Instance===capacityVM')
    checks.append('status recovery unlocks same Linux even while its optional relay is full')
  else:healthy=healthy and all(w['socketState'] is None for w in witnesses)
  result={'status':'PASS' if healthy else 'FAIL','nativeManifestSHA256':before['manifestSHA256'],'contexts':5,'registered':registered,'relayCapacityUnchanged':4,'checks':checks,'witnesses':witnesses,'webhostChanged':False}
  assert before==vm.runtime()
  return result
 finally:
  for s in sessions:
   try:
    if registered:
     task(s,'if(typeof capacityFetch!=="undefined")window.fetch=capacityFetch;if(typeof capacityFileSHA!=="undefined")await (await serverFileContext()).files.remove("relay-capacity-probe.txt",capacityFileSHA);return true;')
    js(s,'desktopNetwork.close();guestNetworkAdapter?.destroy();v86Instance?.destroy();')
   finally:h.call('/session/'+s,method='DELETE')
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--output',required=True);p.add_argument('--registered',action='store_true');a=p.parse_args();result={'status':'FAIL'}
 try:result.update(run(a.registered))
 finally:
  result['sourceSHA256']=hashlib.sha256(Path(__file__).read_bytes()).hexdigest();path=ROOT/'.build/checks'/a.output;assert not path.exists();path.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
 if result['status']!='PASS':raise SystemExit(1)
