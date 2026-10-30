#!/usr/bin/env python3
"""Actual browser/service/operator disable-enable sequence; no public admin route."""
import hashlib,json,sqlite3,subprocess,time,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent;BASE='http://127.0.0.1:19515'
def req(path,data=None,method=None):
 r=urllib.request.Request(BASE+path,data=None if data is None else json.dumps(data).encode(),headers={'Content-Type':'application/json'},method=method)
 with urllib.request.urlopen(r,timeout=90) as response:return json.load(response)['value']
s=req('/session',{'capabilities':{'alwaysMatch':{'browserName':'chrome','goog:chromeOptions':{'binary':'/snap/chromium/current/usr/lib/chromium-browser/chrome','args':['--headless=new','--no-sandbox','--disable-dev-shm-usage']}}}})['sessionId'];result={'status':'FAIL'}
def js(code):return req('/session/'+s+'/execute/sync',{'script':code,'args':[]})
def asyncjs(code):
 value=req('/session/'+s+'/execute/async',{'script':'const done=arguments[0];(async()=>{'+code+'})().then(value=>done({value})).catch(e=>done({error:e.message}));','args':[]});assert 'error' not in value,value;return value['value']
try:
 req('/session/'+s+'/url',{'url':'http://127.0.0.1:8115/'})
 end=time.monotonic()+90
 while time.monotonic()<end:
  if js('return window.desktopLab?.guestState==="ready"'):break
  time.sleep(.2)
 assert js('return desktopLab.guestState==="ready"&&currentSession.trust.level==="test-server"')
 account=asyncjs('''window.policyName='policy_'+crypto.randomUUID().replaceAll('-','').slice(0,12);window.policyPassword=crypto.randomUUID()+crypto.randomUUID();window.policyOld=await identityModule.beginSession(identityConfig,'registered',policyName,policyPassword);window.policyVM=v86Instance;return policyName;''')
 def operator(action):
  process=subprocess.run([str(ROOT/'.build/auth-venv/bin/python'),str(ROOT/'scripts/origin-account-policy.py'),action,'--state',str(ROOT/'.build/connected-instances/lifecycle-browser/state'),'--username',account],check=True,capture_output=True,text=True);return json.loads(process.stdout)
 disabled=operator('disable');assert disabled['disabled'] and disabled['generation']==1
 blocked=asyncjs('''let renew=false,login=false;try{await identityModule.renewSession(identityConfig,policyOld);}catch{renew=true;}try{await identityModule.beginSession(identityConfig,'registered',policyName,policyPassword);}catch{login=true;}return {renew,login,stillRegistered:policyOld.public.kind==='registered',stillServer:policyOld.trust.level==='test-server'};''')
 assert blocked=={'renew':True,'login':True,'stillRegistered':True,'stillServer':True},blocked
 enabled=operator('enable');assert not enabled['disabled'] and enabled['generation']==2
 fresh=asyncjs('''let oldRejected=false;try{await identityModule.renewSession(identityConfig,policyOld);}catch{oldRejected=true;}window.policyFresh=await identityModule.beginSession(identityConfig,'registered',policyName,policyPassword);await identityModule.renewSession(identityConfig,policyFresh);const result={oldRejected,sameAccount:policyFresh.public.sub===policyOld.public.sub,freshSession:policyFresh.public.sid!==policyOld.public.sid,freshKey:policyFresh.fingerprint!==policyOld.fingerprint,trust:policyFresh.trust.level,guestPreserved:v86Instance===policyVM};await identityModule.logoutSession(identityConfig,policyOld);await identityModule.logoutSession(identityConfig,policyFresh);return result;''')
 assert fresh=={'oldRejected':True,'sameAccount':True,'freshSession':True,'freshKey':True,'trust':'test-server','guestPreserved':True},fresh
 with sqlite3.connect(ROOT/'.build/connected-instances/lifecycle-browser/state/accounts.sqlite3') as blocker:
  blocker.execute('BEGIN IMMEDIATE')
  busy=asyncjs('''const start=performance.now();try{await identityModule.beginSession(identityConfig,'registered',policyName,policyPassword);return {rejected:false};}catch(error){return {rejected:true,message:error.message,elapsedSeconds:(performance.now()-start)/1000,stillServer:identityConfig.identity.mode==='server'&&currentSession.trust.level==='test-server'};}''')
  assert busy['rejected'] and busy['stillServer'] and 'database busy' in busy['message'].lower() and busy['elapsedSeconds']<4.5,busy
  blocker.rollback()
 recovered=asyncjs('''const account=await identityModule.beginSession(identityConfig,'registered',policyName,policyPassword);const same=account.public.sub===policyOld.public.sub;await identityModule.logoutSession(identityConfig,account);return same;''');assert recovered
 result={'status':'PASS','scope':'Actual isolated Chrome + loopback issuer + local owned-state operator CLI; no public account/admin deployment','disableBlocksLoginAndRenewal':True,'databaseContention':busy,'loginRecoversAfterDatabaseUnlock':True,'noSilentIdentityDowngrade':True,'enableDoesNotReviveOldTokens':True,'newLoginStableAccountFreshSessionKey':True,'realGuestPreserved':True}
except Exception as error:result['error']=str(error);raise
finally:
 result['sha256']={name:hashlib.sha256((ROOT/name).read_bytes()).hexdigest() for name in ('origin_service/lifecycle.py','scripts/origin-account-policy.py','scripts/serve-connected.py','scripts/identity-lifecycle-browser-check.py')};(ROOT/'.build/checks/identity-lifecycle-browser-result.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2));req('/session/'+s,method='DELETE')
