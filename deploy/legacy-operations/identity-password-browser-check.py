#!/usr/bin/env python3
"""Real browser password reset with secret on operator stdin, never argv."""
import hashlib,json,secrets,subprocess,time,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent;BASE='http://127.0.0.1:19515'
def req(path,data=None,method=None):
 r=urllib.request.Request(BASE+path,data=None if data is None else json.dumps(data).encode(),headers={'Content-Type':'application/json'},method=method)
 with urllib.request.urlopen(r,timeout=90) as response:return json.load(response)['value']
s=req('/session',{'capabilities':{'alwaysMatch':{'browserName':'chrome','goog:chromeOptions':{'binary':'/snap/chromium/current/usr/lib/chromium-browser/chrome','args':['--headless=new','--no-sandbox','--disable-dev-shm-usage']}}}})['sessionId'];result={'status':'FAIL'}
def js(code):return req('/session/'+s+'/execute/sync',{'script':code,'args':[]})
def asyncjs(code,args=None):
 value=req('/session/'+s+'/execute/async',{'script':'const params=arguments,done=params[params.length-1];(async()=>{'+code+'})().then(value=>done({value})).catch(e=>done({error:e.message}));','args':args or []});assert 'error' not in value,value;return value['value']
try:
 req('/session/'+s+'/url',{'url':'http://127.0.0.1:8115/'})
 end=time.monotonic()+90
 while time.monotonic()<end:
  if js('return window.desktopLab?.guestState==="ready"'):break
  time.sleep(.2)
 assert js('return desktopLab.guestState==="ready"&&currentSession.trust.level==="test-server"')
 name=asyncjs('''window.resetName='reset_'+crypto.randomUUID().replaceAll('-','').slice(0,12);window.resetOldPassword=crypto.randomUUID()+crypto.randomUUID();window.resetOld=await identityModule.beginSession(identityConfig,'registered',resetName,resetOldPassword);window.resetVM=v86Instance;return resetName;''')
 def operator(action,secret=None):
  command=[str(ROOT/'.build/auth-venv/bin/python'),str(ROOT/'scripts/origin-account-policy.py'),action,'--state',str(ROOT/'.build/connected-instances/lifecycle-browser/state'),'--username',name]
  response=subprocess.run(command,input=None if secret is None else secret.encode()+b'\n',capture_output=True,check=True)
  if secret is not None:assert secret.encode() not in response.stdout+response.stderr
  return json.loads(response.stdout)
 password=secrets.token_urlsafe(36);changed=operator('reset-password',password);assert changed['generation']==1 and not changed['disabled']
 actual=asyncjs('''let revoked=false,oldPasswordRejected=false;try{await identityModule.renewSession(identityConfig,resetOld);}catch{revoked=true;}try{await identityModule.beginSession(identityConfig,'registered',resetName,resetOldPassword);}catch{oldPasswordRejected=true;}window.resetFresh=await identityModule.beginSession(identityConfig,'registered',resetName,params[0]);await identityModule.renewSession(identityConfig,resetFresh);return {revoked,oldPasswordRejected,sameAccount:resetFresh.public.sub===resetOld.public.sub,newSession:resetFresh.public.sid!==resetOld.public.sid,newKey:resetFresh.fingerprint!==resetOld.fingerprint,trust:resetFresh.trust.level};''',[password])
 assert actual=={'revoked':True,'oldPasswordRejected':True,'sameAccount':True,'newSession':True,'newKey':True,'trust':'test-server'},actual
 assert operator('disable')['generation']==2
 next_password=secrets.token_urlsafe(36);changed=operator('reset-password',next_password);assert changed['disabled'] and changed['generation']==3
 assert asyncjs('''try{await identityModule.beginSession(identityConfig,'registered',resetName,params[0]);return false;}catch{return true;}''',[next_password])
 assert operator('enable')['generation']==4
 assert asyncjs('''const account=await identityModule.beginSession(identityConfig,'registered',resetName,params[0]);const same=account.public.sub===resetOld.public.sub;await identityModule.logoutSession(identityConfig,account);await identityModule.logoutSession(identityConfig,resetFresh);await identityModule.logoutSession(identityConfig,resetOld);await identityModule.renewSession(identityConfig,currentSession);return same&&v86Instance===resetVM;''',[next_password])
 result={'status':'PASS','scope':'Actual isolated Chrome/issuer plus private state-owner CLI; no HTTP reset endpoint or public accounts','oldPasswordRejected':True,'oldSessionsRevoked':True,'newPasswordStableAccountFreshSessionKey':True,'resetDoesNotEnableDisabledAccount':True,'operatorSecretPassedOnStdinNotArgv':True,'noSecretInOperatorOutput':True,'anonymousRenewalAndGuestPreserved':True}
except Exception as error:result['error']=str(error);raise
finally:
 result['sha256']={name:hashlib.sha256((ROOT/name).read_bytes()).hexdigest() for name in ('origin_service/lifecycle.py','scripts/origin-account-policy.py','scripts/identity-password-browser-check.py')};(ROOT/'.build/checks/identity-password-browser-result.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2));req('/session/'+s,method='DELETE')
