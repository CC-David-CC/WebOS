#!/usr/bin/env python3
"""Verify the sealed desktop's actual menu and Chat/Chess app loading."""
import importlib.util,os,secrets,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];spec=importlib.util.spec_from_file_location('driver',ROOT/'scripts/touch-preview-check.py');d=importlib.util.module_from_spec(spec);spec.loader.exec_module(d);origin=os.environ.get('CODI_TEST_URL','http://127.0.0.1:18850/')
sid=d.call('/session',{'capabilities':{'alwaysMatch':{'browserName':'chrome','goog:chromeOptions':{'binary':'/snap/chromium/current/usr/lib/chromium-browser/chrome','args':['--headless=new','--no-sandbox','--disable-dev-shm-usage']}}}})['sessionId']
try:
 def js(code,args=[]):return d.call('/session/'+sid+'/execute/sync',{'script':code,'args':args})
 d.call('/session/'+sid+'/url',{'url':origin});d.call('/session/'+sid+'/goog/cdp/execute',{'cmd':'Browser.setPermission','params':{'permission':{'name':'persistent-storage'},'setting':'granted','origin':origin.rstrip('/')}});d.wait(lambda:js('return !!document.querySelector(".login-gate");'),30)
 js('document.querySelector(".login-toggle").click();');name='load'+secrets.token_hex(5);js('''const set=(a,v)=>{const n=document.querySelector('.login-gate input[aria-label="'+a+'"]');n.value=v;n.dispatchEvent(new Event('input',{bubbles:true}));};set('Username',arguments[0]);set('Password','1!$?');set('Confirm password','1!$?');document.querySelector('.login-form').requestSubmit();''',[name]);d.wait(lambda:js('return !!currentSession&&!document.documentElement.classList.contains("login-required")&&surfaces.size>0;'),60)
 assert js('return desktopMenu.some(x=>x.name==="Chess")&&desktopMenu.some(x=>x.name==="Chat")&&!desktopMenu.some(x=>x.name==="Rooms");')
 js('localStorage.setItem("codi-device-history-consent-v1","accepted-v1");window.loaderDesktop=[...surfaces.values()][0];window.chatId=loaderDesktop.launch("chat").id;window.chessId=loaderDesktop.launch("chess").id;')
 def loaded():
  return js('''const a=document.querySelector('[data-window="'+chatId+'"]'),b=document.querySelector('[data-window="'+chessId+'"]');return {chat:a?.textContent||'',chess:b?.textContent||'',waiting:!a||!b||!!a.querySelector('[data-app-loading]')||!!b.querySelector('[data-app-loading]')};''')
 d.wait(lambda:not loaded()['waiting'],30);state=loaded();assert 'Could not load this app' not in state['chat'] and 'Could not load this app' not in state['chess'],state
 print('PASS sealed desktop retains login, exposes Chat and Chess, and loads both compiled applications')
finally:d.call('/session/'+sid,method='DELETE')
