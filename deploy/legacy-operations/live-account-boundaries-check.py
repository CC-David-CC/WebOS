#!/usr/bin/env python3
"""Verify live registration and sign-in at the requested account limits."""
import importlib.util,secrets,shlex,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];spec=importlib.util.spec_from_file_location('driver',ROOT/'scripts/touch-preview-check.py');d=importlib.util.module_from_spec(spec);spec.loader.exec_module(d)
name='edge'+secrets.token_hex(12);password='🔑'+'a'*27+'!$?9';assert len(name)==28 and len(password)==32;sid=None
def js(code,args=[]):return d.call('/session/'+sid+'/execute/sync',{'script':code,'args':args})
try:
 sid=d.call('/session',{'capabilities':{'alwaysMatch':{'browserName':'chrome','goog:chromeOptions':{'binary':'/snap/chromium/current/usr/lib/chromium-browser/chrome','args':['--headless=new','--no-sandbox','--disable-dev-shm-usage']}}}})['sessionId'];d.call('/session/'+sid+'/url',{'url':'https://ksu.codes/'});d.wait(lambda:js('return !!document.querySelector(".login-gate");'),30);js('document.querySelector(".login-toggle").click();')
 assert js('''const n=document.querySelector('.login-gate input[aria-label="Username"]');return ['ab','1abc','ab-c','ab_c'].every(v=>{n.value=v;return !n.checkValidity();});''')
 js('''const n=document.querySelector('.login-gate input[aria-label="Username"]');n.value=arguments[0];n.dispatchEvent(new Event('input',{bubbles:true}));''',[name])
 def fill_and_submit(value):js('''for(const label of ['Password','Confirm password']){const n=document.querySelector('.login-gate input[aria-label="'+label+'"]');n.value=arguments[0];n.dispatchEvent(new Event('input',{bubbles:true}));}document.querySelector('.login-form').requestSubmit();''',[value])
 for invalid in ('abc','x'*33):
  fill_and_submit(invalid);d.wait(lambda:js('return document.querySelector(".login-gate")?.textContent.includes("Password must be 4–32");'),10)
 fill_and_submit(password);d.wait(lambda:js('return !!currentSession&&!document.documentElement.classList.contains("login-required")&&surfaces.size>0;'),60)
 print('PASS 28-character username and 32-character mixed Unicode/symbol password registered',flush=True)
 d.call('/session/'+sid+'/refresh',{},'POST');d.wait(lambda:js('return !!document.querySelector(".login-gate");'),30)
 js('''for(const [label,value] of [['Username',arguments[0]],['Password',arguments[1]]]){const n=document.querySelector('.login-gate input[aria-label="'+label+'"]');n.value=value;n.dispatchEvent(new Event('input',{bubbles:true}));}document.querySelector('.login-form').requestSubmit();''',[name,password]);d.wait(lambda:js('return !!currentSession&&!document.documentElement.classList.contains("login-required")&&surfaces.size>0;'),60)
 print('PASS same account signed in after refresh; invalid names and short/long passwords refused in UI',flush=True)
finally:
 if sid:
  try:d.call('/session/'+sid,method='DELETE')
  except Exception:pass
 cleanup='''import re,sqlite3,sys\nname=sys.argv[1];assert re.fullmatch(r"edge[0-9a-f]{24}",name)\nd=sqlite3.connect("/var/lib/codi-connected/ksu/issuer/state/accounts.sqlite3",timeout=30);row=d.execute("SELECT subject FROM accounts WHERE username=?",(name,)).fetchone()\nif row:\n subject=row[0];d.execute("BEGIN IMMEDIATE");d.execute("DELETE FROM registered_sessions WHERE json_extract(record, '$.sub')=?",(subject,));d.execute("DELETE FROM account_policy WHERE subject=?",(subject,));d.execute("DELETE FROM accounts WHERE username=? AND subject=?",(name,subject));d.commit()\nprint("removed disposable account and sessions")'''
 try:print(subprocess.run(['ssh','-o','BatchMode=yes','box-webhost','sudo','-n','/usr/bin/python3','-B','-c',shlex.quote(cleanup),name],check=True,capture_output=True,text=True,timeout=30).stdout.strip(),flush=True)
 except Exception as error:print('Disposable account cleanup failed:',name,error,flush=True);raise
