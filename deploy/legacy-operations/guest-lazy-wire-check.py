#!/usr/bin/env python3
"""Actual installed strict gateway: lazy wire, hostile opt-out and cancelled login."""
import hashlib,importlib.util,json,re,time
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
def load(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def run():
 vm=load('lazy_wire_vm',ROOT/'scripts/upgrade-signin-native-vm.py');h=load('lazy_wire_helpers',ROOT/'scripts/touch-preview-check.py');runtime=vm.runtime();i=json.loads(vm.remote('cat /srv/codi-network-fixture/installed-result.json'));checks=[]
 sid=h.call('/session',{'capabilities':{'alwaysMatch':{'browserName':'chrome','goog:chromeOptions':{'binary':'/snap/chromium/current/usr/lib/chromium-browser/chrome','args':['--headless=new','--no-sandbox','--disable-dev-shm-usage','--ignore-certificate-errors-spki-list='+i['fixtureSPKI']]}}}})['sessionId']
 def js(code,args=[]):return h.call('/session/'+sid+'/execute/sync',{'script':code,'args':args})
 def task(code):
  r=h.call('/session/'+sid+'/execute/async',{'script':'const done=arguments[0];(async()=>{'+code+'})().then(value=>done({ok:true,value}),error=>done({ok:false,error:error.stack}));','args':[]});assert r['ok'],r;return r.get('value')
 def check(name,value):assert value,name;checks.append(name)
 def ping(success):
  marker='LAZY_WIRE_'+str(time.time_ns())
  js('sendTerminal(2,arguments[0]);',['ping -c 1 -W 1 1.1.1.2 >/tmp/lazy-wire-probe 2>&1; wire_rc=$?; printf "\\n'+marker+'=%s\\n" "$wire_rc"\r'])
  h.wait(lambda:js('return terminalSessions.get(2).screen.text().includes(arguments[0])',['\n'+marker+'=']),20)
  match=re.search(r'\n'+marker+r'=(\d+)\n',js('return terminalSessions.get(2).screen.text()'));assert match
  assert (int(match[1])==0)==success,match[0]
 try:
  h.call('/session/'+sid+'/timeouts',{'script':120000});h.call('/session/'+sid+'/url',{'url':i['publicOrigin']+'/hidden/'})
  h.wait(lambda:js('return window.desktopLab?.guestState==="ready"&&!desktopLab.lifecycle.blocked'),150)
  check('anonymous Linux has no network socket or reconnect timer',js('return guestNetworkAdapter.localOnly&&guestNetworkAdapter.socket===null&&guestNetworkAdapter.timer===null&&guestNetworkAdapter.linkReady'))
  js('window.wireVM=v86Instance;window.wireName="vmwire_"+crypto.randomUUID().replaceAll("-","").slice(0,12);window.wirePassword=crypto.randomUUID()+crypto.randomUUID();')
  task('await changeAccount("register",wireName,wirePassword);return true;');h.wait(lambda:js('return guestNetworkAdapter.mode==="registered"'),30);ping(True)
  check('registered signed grant enables actual controlled ICMP on same VM',js('return v86Instance===wireVM'))
  task('await changeAccount("anonymous");return true;');h.wait(lambda:js('return guestNetworkAdapter.socket===null&&guestNetworkAdapter.mode==="anonymous"'),15)
  # Deliberately bypass the browser optimization. Enforcement must still be
  # server-side, even when an anonymous client opens a real Ethernet wire.
  js('guestNetworkAdapter.signinOnly=false;guestNetworkAdapter.syncSession();')
  h.wait(lambda:js('return guestNetworkAdapter.socket?.readyState===WebSocket.OPEN'),30)
  js('window.wireBytes=0;const socket=guestNetworkAdapter.socket,send=socket.send.bind(socket);socket.send=value=>{if(value instanceof Uint8Array||value instanceof ArrayBuffer)wireBytes+=value.byteLength;return send(value);};')
  ping(False)
  check('bypassing client optimization sends actual anonymous frames but server still denies Internet',js('return wireBytes>0&&guestNetworkAdapter.socket.readyState===WebSocket.OPEN&&guestNetworkAdapter.mode==="anonymous"'))
  js('guestNetworkAdapter.signinOnly=true;guestNetworkAdapter.syncSession();')
  h.wait(lambda:js('return guestNetworkAdapter.socket===null'),10)
  check('restoring anonymous policy releases its wire without blocking desktop',js('return !desktopLab.lifecycle.blocked&&v86Instance===wireVM'))
  js('''window.wireFetch=fetch;window.wireRelease=null;
window.fetch=async (url,options)=>{if(new URL(String(url),location.href).pathname==='/hidden/'){await new Promise(resolve=>wireRelease=resolve);}return wireFetch(url,options);};''')
  task('await changeAccount("signin",wireName,wirePassword);return true;')
  h.wait(lambda:js('return typeof wireRelease==="function"'),15)
  task('await changeAccount("anonymous");return true;')
  js('window.fetch=wireFetch;wireRelease();')
  h.wait(lambda:js('return guestNetworkAdapter.connecting===null'),15)
  check('logout cancels pending cookie/connect operation with no late socket or retry timer',js('return guestNetworkAdapter.localOnly&&guestNetworkAdapter.socket===null&&guestNetworkAdapter.timer===null&&guestNetworkAdapter.mode==="anonymous"&&v86Instance===wireVM'))
  assert runtime==vm.runtime()
  return {'status':'PASS','checks':checks,'nativeManifestSHA256':runtime['manifestSHA256'],'realSignedIssuerAndInstalledKernelGateway':True,'controlledFixtureDestination':'1.1.1.2','liveWebhostChanged':False}
 except Exception:
  try:(ROOT/'.build/checks'/('guest-lazy-wire-failure-'+str(time.time_ns())+'.json')).write_text(json.dumps(js('return {mode:guestNetworkAdapter?.mode,localOnly:guestNetworkAdapter?.localOnly,text:document.body.innerText.slice(-3500)}'),indent=2)+'\n')
  except Exception:pass
  raise
 finally:
  try:js('if(typeof wireFetch!=="undefined")window.fetch=wireFetch;if(typeof wireRelease==="function")wireRelease();desktopNetwork.close();guestNetworkAdapter?.destroy();v86Instance?.destroy();')
  finally:h.call('/session/'+sid,method='DELETE')
if __name__=='__main__':
 result={'status':'FAIL'}
 try:result.update(run())
 finally:
  result['sourceSHA256']=hashlib.sha256(Path(__file__).read_bytes()).hexdigest();p=ROOT/'.build/checks/guest-lazy-wire-result.json'
  if p.exists():p.rename(p.with_name(p.stem+'-before-'+str(time.time_ns())+'.json'))
  p.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
