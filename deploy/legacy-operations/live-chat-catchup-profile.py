#!/usr/bin/env python3
"""Measure real public chat catch-up in one disposable browser without guest or speech."""
import importlib.util,json,re,secrets,shlex,subprocess,time,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];spec=importlib.util.spec_from_file_location('driver',ROOT/'scripts/touch-preview-check.py');d=importlib.util.module_from_spec(spec);spec.loader.exec_module(d)
origin='https://ksu.codes';channel='J3iEwhBk3DnYoa_lGb4gVw3kYZe0qYYOtAoGvvN1AR4';name='profile'+secrets.token_hex(5);sid=None
with urllib.request.urlopen(origin+'/official-head?channel='+channel,timeout=15) as response:target=json.load(response)['height']
print('Disposable account:',name,'starting target height:',target,flush=True)
def js(code,args=[]):return d.call('/session/'+sid+'/execute/sync',{'script':code,'args':args})
try:
 sid=d.call('/session',{'capabilities':{'alwaysMatch':{'browserName':'chrome','goog:chromeOptions':{'binary':'/snap/chromium/current/usr/lib/chromium-browser/chrome','args':['--headless=new','--no-sandbox','--disable-dev-shm-usage']}}}})['sessionId']
 def cdp(cmd,params):return d.call('/session/'+sid+'/goog/cdp/execute',{'cmd':cmd,'params':params})
 cdp('Network.enable',{});cdp('Network.setBlockedURLs',{'urls':['*/.build/v86/*','*/assets/speech/*']})
 script='''(()=>{const p=window.catchupProfile={start:performance.now(),digest:{count:0,totalMs:0},archiveWrites:{count:0,totalMs:0},archiveReads:{count:0,totalMs:0},history:[]};const digest=SubtleCrypto.prototype.digest;SubtleCrypto.prototype.digest=function(...a){const start=performance.now();return digest.apply(this,a).finally(()=>{p.digest.count++;p.digest.totalMs+=performance.now()-start;});};const transaction=IDBDatabase.prototype.transaction;IDBDatabase.prototype.transaction=function(...a){const start=performance.now(),tx=transaction.apply(this,a);if(this.name==='codi-device-channel-archive-v1'){const metric=a[1]==='readwrite'?p.archiveWrites:p.archiveReads;tx.addEventListener('complete',()=>{metric.count++;metric.totalMs+=performance.now()-start;});}return tx;};const fetch0=window.fetch.bind(window);window.fetch=async(...args)=>{const url=new URL(args[0] instanceof Request?args[0].url:String(args[0]),location.href),start=performance.now();try{const r=await fetch0(...args);if(url.pathname==='/official-history')p.history.push({status:r.status,ms:Math.round(performance.now()-start),at:Math.round(start-(p.opened||p.start)),height:url.searchParams.get('afterHeight')});return r;}catch(error){if(url.pathname==='/official-history')p.history.push({status:0,ms:Math.round(performance.now()-start),at:Math.round(start-(p.opened||p.start))});throw error;}};})();'''
 cdp('Page.addScriptToEvaluateOnNewDocument',{'source':script});d.call('/session/'+sid+'/url',{'url':origin+'/'});cdp('Browser.setPermission',{'permission':{'name':'persistent-storage'},'setting':'granted','origin':origin});d.wait(lambda:js('return !!document.querySelector(".login-gate");'),30);js('document.querySelector(".login-toggle").click();');js('''const set=(a,v)=>{const n=document.querySelector('.login-gate input[aria-label="'+a+'"]');n.value=v;n.dispatchEvent(new Event('input',{bubbles:true}));};set('Username',arguments[0]);set('Password','1!$?');set('Confirm password','1!$?');document.querySelector('.login-form').requestSubmit();''',[name]);d.wait(lambda:js('return !!currentSession&&!document.documentElement.classList.contains("login-required")&&surfaces.size>0;'),60)
 js('''localStorage.setItem('codi-device-history-consent-v1','accepted-v1');window.profileDesktop=[...surfaces.values()][0];window.profileChat=profileDesktop.launch('chat').id;window.catchupProfile.opened=performance.now();''')
 def snapshot():return js('''const n=document.querySelector('[data-window="'+profileChat+'"]'),t=n?.querySelector('.channel-conversation > details > p')?.textContent||'',m=t.match(/Accepted height (\\d+)/);return {height:m?Number(m[1]):null,text:n?.textContent?.slice(0,400)||''};''')
 def caught():
  value=snapshot()
  if 'Could not load this app' in value['text']:raise RuntimeError(value['text'])
  return value['height'] is not None and value['height']>=target
 d.wait(caught,180);result=js('''const p=window.catchupProfile;return {elapsedMs:Math.round(performance.now()-p.opened),digest:p.digest,archiveWrites:p.archiveWrites,archiveReads:p.archiveReads,history:p.history};''');print(json.dumps({'status':'PASS','target':target,'measurements':result,'scope':'one public Chrome browser; guest and speech assets blocked; digest and transaction durations can overlap'}),flush=True)
finally:
 if sid:
  try:d.call('/session/'+sid,method='DELETE')
  except Exception:pass
 cleanup='''import re,sqlite3,sys\nname=sys.argv[1];assert re.fullmatch(r"profile[0-9a-f]{10}",name)\nd=sqlite3.connect("/var/lib/codi-connected/ksu/issuer/state/accounts.sqlite3",timeout=30);row=d.execute("SELECT subject FROM accounts WHERE username=?",(name,)).fetchone()\nif row:\n d.execute("BEGIN IMMEDIATE");d.execute("DELETE FROM account_policy WHERE subject=?",(row[0],));d.execute("DELETE FROM accounts WHERE username=? AND subject=?",(name,row[0]));d.commit()\nprint("removed disposable profile account")'''
 try:print(subprocess.run(['ssh','-o','BatchMode=yes','box-webhost','sudo','-n','/usr/bin/python3','-B','-c',shlex.quote(cleanup),name],check=True,capture_output=True,text=True,timeout=30).stdout.strip(),flush=True)
 except Exception as error:print('Profile account cleanup failed:',error,'name:',name,flush=True)
