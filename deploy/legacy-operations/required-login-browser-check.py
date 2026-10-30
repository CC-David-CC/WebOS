#!/usr/bin/env python3
"""Exercise the real sign-in gate and issuer in a disposable loopback browser."""
import json,os,secrets,time,urllib.request
BASE='http://127.0.0.1:19515'
def req(path,data=None,method=None):
 q=urllib.request.Request(BASE+path,data=None if data is None else json.dumps(data).encode(),headers={'Content-Type':'application/json'},method=method)
 with urllib.request.urlopen(q,timeout=90) as r:return json.load(r)['value']
s=req('/session',{'capabilities':{'alwaysMatch':{'browserName':'chrome','goog:chromeOptions':{'binary':'/snap/chromium/current/usr/lib/chromium-browser/chrome','args':['--headless=new','--no-sandbox','--disable-dev-shm-usage']}}}})['sessionId']
def js(code,args=[]):return req('/session/'+s+'/execute/sync',{'script':code,'args':args})
def wait(code,seconds=30):
 end=time.monotonic()+seconds
 while time.monotonic()<end:
  v=js(code)
  if v:return v
  time.sleep(.1)
 raise AssertionError('Timed out: '+code)
name='test'+secrets.token_hex(5)
print('Temporary test account: '+name,flush=True)
try:
 req('/session/'+s+'/url',{'url':os.environ.get('CODI_TEST_URL','http://127.0.0.1:18850/')})
 wait('return !!document.querySelector(".login-gate");')
 assert js('return document.documentElement.classList.contains("login-required")&&!currentSession&&!v86Instance;')
 assert js('const n=document.querySelector(".login-gate input[aria-label=Username]");return n.maxLength===28&&n.pattern==="[A-Za-z][A-Za-z0-9]{2,27}";')
 js('document.querySelector(".login-toggle").click();')
 valid=js('const n=document.querySelector(".login-gate input[aria-label=Username]");return ["abc","a1"+"a".repeat(26),"a1"+"a".repeat(27),"1abc","a_b","a-b"].map(v=>{n.value=v;return n.checkValidity()});')
 assert valid==[True,True,False,False,False,False],valid
 js('''const set=(a,v)=>{const n=document.querySelector('.login-gate input[aria-label="'+a+'"]');n.value=v;n.dispatchEvent(new Event('input',{bubbles:true}));};set('Username',arguments[0]);set('Password','1!$?');set('Confirm password','1!$?');document.querySelector('.login-form').requestSubmit();''',[name])
 wait('return !!currentSession&&currentSession.public.kind==="registered"&&!document.documentElement.classList.contains("login-required");',60)
 print('PASS login gate blocks anonymous boot; alphanumeric boundaries; four-character symbol password creates a registered session')
 js('endSession();')
 wait('return !!document.querySelector(".login-gate")&&!currentSession;',45)
 js('''const set=(a,v)=>{const n=document.querySelector('.login-gate input[aria-label="'+a+'"]');n.value=v;n.dispatchEvent(new Event('input',{bubbles:true}));};set('Username',arguments[0]);set('Password','1!$?');document.querySelector('.login-form').requestSubmit();''',[name])
 wait('return !!currentSession&&currentSession.public.kind==="registered"&&!document.documentElement.classList.contains("login-required");',60)
 print('PASS sign-out returns to gate and sign-in accepts the same password')
 js('endSession();')
 wait('return !!document.querySelector(".login-gate")&&!currentSession;',45)
finally:req('/session/'+s,method='DELETE')
