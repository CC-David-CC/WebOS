#!/usr/bin/env python3
"""Actual native14 upgrade/policy switch with cached R16 and modern Chrome/v86.

Private retained VM only. Its fixture TURN endpoint is deliberately invalid;
native RTC preferences are checked, not real TURN connectivity or public trust.
Real account/private-file, systemd restart, guest wire and memory retention run.
"""
import argparse,hashlib,importlib.util,json,shlex,subprocess,time
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
def module(name,path):
 spec=importlib.util.spec_from_file_location(name,ROOT/path);v=importlib.util.module_from_spec(spec);spec.loader.exec_module(v);return v
candidate=module('ice_upgrade_vm','scripts/upgrade-native-network-vm.py');helpers=module('ice_vm_browser','scripts/touch-preview-check.py');call,wait=helpers.call,helpers.wait

def operator(action,transport=None):
 code='''import json,pathlib,subprocess
c=json.loads(pathlib.Path('/etc/codi-native-fixture/managed.json').read_text());args=[c['python'],'-I','-B',c['release']+'/scripts/manage-services.py',ACTION,'--config','/etc/codi-native-fixture/managed.json']
if TRANSPORT is not None:
 assert c['turn']['secretFile']=='/etc/codi-fixture-turn/turn.secret'
 args+=['--turn-secret-file',c['turn']['secretFile'],'--turn-url','turns:fixture.invalid:443?transport=tcp','--turn-transport-policy',TRANSPORT]
r=subprocess.run(args,capture_output=True,text=True,check=True);print(r.stdout)
'''.replace('ACTION',repr(action)).replace('TRANSPORT',repr(transport))
 return json.loads(candidate.remote('/usr/bin/python3 -I -B -c '+shlex.quote(code)))

def ingress():
 source=(ROOT/'scripts/native-network-vm-services.py').read_text()
 code='''import hashlib,pathlib,subprocess,sys,json
p=pathlib.Path('/srv/codi-network-fixture/tools/native-network-vm-services.py');raw=sys.stdin.buffer.read();compile(raw.decode(),str(p),'exec');p.write_bytes(raw);p.chmod(0o644)
unit=pathlib.Path('/etc/systemd/system/codi-fixture-ingress.service');text=unit.read_text();flag=' --legacy-release /srv/codi-network-fixture/candidate-abb67a1f7a2e718c'
lines=text.splitlines();lines=[line.split(' --legacy-release ')[0]+flag if line.startswith('ExecStart=') else line for line in lines];unit.write_text(chr(10).join(lines)+chr(10))
subprocess.run(['systemd-analyze','verify',str(unit)],check=True,capture_output=True)
subprocess.run(['systemctl','daemon-reload'],check=True);subprocess.run(['systemctl','restart',unit.name],check=True)
print(json.dumps({'status':'PASS','fixtureIngressSHA256':hashlib.sha256(raw).hexdigest()}))
'''
 return json.loads(candidate.remote('/usr/bin/python3 -I -B -c '+shlex.quote(code),source))

def run(release):
 candidate.vm.status();original=candidate.runtime();operator('configure-turn','relay');initial_rollback=None
 expected=hashlib.sha256((Path(release)/'connected-release.json').read_bytes()).hexdigest()
 resume_staged=original['manifestSHA256']==expected
 if resume_staged:
  initial_rollback=operator('rollback');original=candidate.runtime()
  assert original['manifestSHA256']=='ce00294efbc58d835308fd4d4703e6422c199f40c5ee110f56d5c67296138442','Only the known preserved private VM baseline may be resumed'
 proxy=ingress()
 installed=json.loads(candidate.remote('cat /srv/codi-network-fixture/installed-result.json'));sessions=[];checks=[];upgraded=False
 def js(s,code,args=[]):return call('/session/'+s+'/execute/sync',{'script':code,'args':args})
 def task(s,code):
  v=call('/session/'+s+'/execute/async',{'script':'const done=arguments[0];(async()=>{'+code+'})().then(value=>done({ok:true,value}),error=>done({ok:false,error:error.message}));','args':[]});assert v['ok'],v;return v.get('value')
 def check(name,value):assert value,name;checks.append(name)
 def notice(phase):
  code="import json,pathlib,subprocess;c=json.loads(pathlib.Path('/etc/codi-native-fixture/managed.json').read_text());print(subprocess.check_output([c['python'],'-I','-B',c['release']+'/scripts/desktop-maintenance.py','--directory','/var/lib/codi-native-fixture/public',PHASE,'--duration','600'],text=True))".replace('PHASE',repr(phase))
  return json.loads(candidate.remote('/usr/bin/python3 -I -B -c '+shlex.quote(code)))
 def open_client(build):
  sid=call('/session',{'capabilities':{'alwaysMatch':{'browserName':'chrome','goog:chromeOptions':{'binary':'/snap/chromium/current/usr/lib/chromium-browser/chrome','args':['--headless=new','--no-sandbox','--disable-dev-shm-usage','--ignore-certificate-errors-spki-list='+installed['fixtureSPKI']]}}}})['sessionId'];sessions.append(sid)
  call('/session/'+sid+'/timeouts',{'script':120000});call('/session/'+sid+'/url',{'url':installed['publicOrigin']+'/hidden/?build='+build})
  wait(lambda:js(sid,'return window.desktopLab?.guestState==="ready"&&desktopLab.lifecycle?.epoch&&!desktopLab.lifecycle.blocked&&!!navigator.serviceWorker.controller'),150)
  return sid
 def save_ram(s):
  js(s,'window.savedVM=v86Instance;window.savedFS=v86Instance.fs9p;window.oldSession=currentSession.id;window.d=[...surfaces.values()][0];d.launch("text")');wait(lambda:js(s,'return !!document.querySelector(".guest-editor")'),20)
  js(s,'window.savedEditor=document.querySelector(".guest-editor");savedEditor.value="unsaved native14 draft";savedEditor.dispatchEvent(new Event("input",{bubbles:true}));savedEditor.focus();savedEditor.setSelectionRange(2,7)')
  js(s,'sendTerminal(2,arguments[0])',["export ICE_VM_KEEP=shell_kept; printf file_kept > /home/guest/ice-kept.txt; printf '\\nICE_NATIVE_READY\\n'\r"]);wait(lambda:js(s,'return serialScreen.text().includes("\\nICE_NATIVE_READY\\n")'),30)
 def retained(s):
  check('same Linux, filesystem, editor draft and selection',js(s,'return v86Instance===savedVM&&v86Instance.fs9p===savedFS&&savedEditor.isConnected&&savedEditor.value==="unsaved native14 draft"&&savedEditor.selectionStart===2&&savedEditor.selectionEnd===7'))
  token='VM_ICE_'+str(time.time_ns());js(s,'sendTerminal(2,arguments[0])',['printf "\\n'+token+'=%s:" "$ICE_VM_KEEP"; cat /home/guest/ice-kept.txt\r']);wait(lambda:js(s,'return serialScreen.text().includes(arguments[0])',['\n'+token+'=shell_kept:file_kept']),30)
 def policy(s,value):
  check('native browser RTC policy '+value,task(s,'const {PeerLink}=await import("./network/peer.mjs");const link=new PeerLink(currentSession,identityConfig);try{link.create();return link.pc.getConfiguration().iceTransportPolicy}finally{link.close()}')==value)
 def signin(s):return task(s,'await changeAccount("signin",qaName,qaPassword);return currentSession.public.kind;')
 try:
  old=open_client('legacy');check('original R16 identity module actually loaded',task(old,'return !("icePreference" in await import("./network/identity.mjs"))'))
  check('original R16 worker cache exists',task(old,'return (await caches.keys()).some(k=>k.includes("1224e578c8f30cce633a593cbad0990513ac35f349d8dd7c868166d7f202ee66"))'))
  name='qa_ice_'+__import__('uuid').uuid4().hex[:12];password=__import__('secrets').token_urlsafe(32)
  js(old,'window.qaName=arguments[0];window.qaPassword=arguments[1]',[name,password]);task(old,'await changeAccount("register",qaName,qaPassword);const context=await serverFileContext();await context.files.write("native14-saved.txt",new TextEncoder().encode("explicit saved version"));return true;');save_ram(old)
  notice('active');wait(lambda:js(old,'return desktopLab.lifecycle.blocked'),8)
  upgrade=candidate.upgrade(release,resume_staged=resume_staged);upgraded=True;after_upgrade=candidate.runtime()
  check('actual installed native14 code upgrade completed',upgrade['status']=='PASS' and original['manifestSHA256']!=after_upgrade['manifestSHA256'])
  notice('cancelled');wait(lambda:js(old,'return !desktopLab.lifecycle.blocked&&currentSession.id!==oldSession'),30);retained(old);policy(old,'relay')
  check('legacy sign-in works after real code upgrade',signin(old)=='registered')
  check('private saved file retained after actual code upgrade',task(old,'return new TextDecoder().decode((await (await serverFileContext()).files.read("native14-saved.txt")).data)==="explicit saved version";'))
  modern=open_client('modern');js(modern,'window.qaName=arguments[0];window.qaPassword=arguments[1]',[name,password]);check('modern sign-in works on native14',signin(modern)=='registered');save_ram(modern)
  for s in [old,modern]:js(s,'window.oldSession=currentSession.id')
  before_policy=candidate.runtime();notice('active');change=operator('configure-turn','all');after_policy=candidate.runtime()
  check('policy switch restarts only actual issuer',before_policy['nativePIDs']['issuer']!=after_policy['nativePIDs']['issuer'] and all(before_policy['nativePIDs'][r]==after_policy['nativePIDs'][r] for r in ['steward','guest']))
  notice('cancelled')
  for s in [old,modern]:wait(lambda:js(s,'return !desktopLab.lifecycle.blocked&&currentSession.id!==oldSession'),30);retained(s)
  policy(old,'relay');policy(modern,'all')
  for s in [old,modern]:
   check('both versions can sign in again without replacing Linux',signin(s)=='registered');retained(s)
   check('both versions read the same saved account file',task(s,'return new TextDecoder().decode((await (await serverFileContext()).files.read("native14-saved.txt")).data)==="explicit saved version";'))
  task(modern,'const files=(await serverFileContext()).files;const saved=await files.read("native14-saved.txt");await files.remove("native14-saved.txt",saved.sha256);return true;')
  return {'status':'PASS','scope':__doc__,'checks':checks,'originalRuntime':original,'runtimeAfterUpgrade':after_upgrade,'runtimeAfterPolicy':after_policy,'codeUpgrade':upgrade,'initialCodeOnlyRollback':initial_rollback,'policyChange':change,'fixtureIngress':proxy,'oldR16ActuallyCachedBeforeUpgrade':True,'oldAndModernNoReload':True,'privateFileSavedAndRecovered':True,'testFileRemovedWithExpectedVersion':True,'TURNConnectivityProven':False,'publicDefaultTLSVerified':False,'liveWebhostChanged':False,'hostFirewallChanged':False}
 finally:
  notice('cancelled')
  for s in sessions:
   try:js(s,'desktopLifecycle?.stop();desktopNetwork.close();guestNetworkAdapter?.destroy();v86Instance?.destroy()')
   finally:call('/session/'+s,method='DELETE')

if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--release-dir',required=True,type=Path);a=p.parse_args();value={'status':'FAIL','scope':__doc__}
 try:value.update(run(a.release_dir))
 finally:
  names=['scripts/ice-preference-vm-check.py','scripts/native-network-vm-services.py','scripts/upgrade-native-network-vm.py','origin_service/ice_preference.py','app.js','network/identity.mjs','assets/desktop/recovery-policy.mjs']
  value['sha256']={n:hashlib.sha256((ROOT/n).read_bytes()).hexdigest() for n in names};output=ROOT/'.build/checks/ice-preference-vm-result.json'
  if output.exists():output.rename(output.with_name(output.stem+'-before-'+str(time.time_ns())+'.json'))
  output.write_text(json.dumps(value,indent=2)+'\n');print(json.dumps(value,indent=2))
