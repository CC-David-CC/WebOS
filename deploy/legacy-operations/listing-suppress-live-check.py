#!/usr/bin/env python3
"""Test a public channel reference across a real steward restart on the live site."""
import argparse,importlib.util,json,shutil,subprocess,tempfile,time,traceback,uuid
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sp=importlib.util.spec_from_file_location('driver',ROOT/'scripts/touch-preview-check.py');d=importlib.util.module_from_spec(sp);sp.loader.exec_module(d)
def run():
 sessions={};profiles={};selectors={};label='Directory test '+uuid.uuid4().hex;checks=[];result={'status':'FAIL','scope':'Live site, two fresh browsers on one host; directory service restarted; not an independent-network test.','checks':checks,'temporaryLabel':label};record=None
 def js(side,code,args=[]):return d.call('/session/'+sessions[side]+'/execute/sync',{'script':code,'args':args})
 def wait(side,code,args=[],seconds=90):return d.wait(lambda:js(side,code,args),seconds)
 def check(name):checks.append(name);print(json.dumps({'check':name}),flush=True)
 def db(mode):
  code='import sqlite3,sys,json; p="/var/lib/codi-connected/ksu/steward/ledger/public-channels.sqlite3"; db=sqlite3.connect(p); label=sys.argv[1]; mode=sys.argv[2]; rows=db.execute("SELECT scope,channel,issued,verified_at FROM channel_directory WHERE label=?",(label,)).fetchall(); assert len(rows)<=1; db.execute("DELETE FROM channel_directory WHERE label=?",(label,)) if mode=="delete" else None; db.commit(); print(json.dumps(rows))'
  import shlex
  out=subprocess.check_output(['ssh','-o','BatchMode=yes','box-webhost','sudo','-n','runuser','-u','codi-steward','--','/usr/bin/python3','-c',shlex.quote(code),shlex.quote(label),mode],text=True,timeout=30);return json.loads(out)
 def start(side):
  if side not in profiles:profiles[side]=Path(tempfile.mkdtemp(prefix='codi-live-directory-',dir=Path.home()/'snap/chromium/common'))
  sessions[side]=d.call('/session',{'capabilities':{'alwaysMatch':{'browserName':'chrome','goog:chromeOptions':{'binary':'/snap/chromium/current/usr/lib/chromium-browser/chrome','args':['--headless=new','--no-sandbox','--disable-dev-shm-usage','--user-data-dir='+str(profiles[side])]}}}})['sessionId']
  if side=='a':
   probe="""(()=>{const send=WebSocket.prototype.send,interval=window.setInterval;window.codiListingProbe=[];window.codiListingTicks=0;window.setInterval=function(fn,ms,...rest){if(typeof fn==='function'&&String(fn).includes('refreshOwnedListings')){const original=fn;fn=function(...args){window.codiListingTicks++;return original.apply(this,args);};}return interval.call(this,fn,ms,...rest);};WebSocket.prototype.send=function(value){try{if(typeof value==='string'){const parts=value.split('.');if(parts.length===3){const payload=JSON.parse(new TextDecoder().decode(Uint8Array.from(atob(parts[1].replace(/-/g,'+').replace(/_/g,'/')),c=>c.charCodeAt(0))));if(payload.operation==='INDEX_PUBLISH_BATCH')window.codiListingProbe.push(...payload.body.wires);}}}catch{}return send.call(this,value);};})();"""
   d.call('/session/'+sessions[side]+'/goog/cdp/execute',{'cmd':'Page.addScriptToEvaluateOnNewDocument','params':{'source':probe}})
  d.call('/session/'+sessions[side]+'/url',{'url':'https://ksu.codes/'});wait(side,'return !!window.desktopLab?.session&&desktopLab.surfaces.size>0;');d.call('/session/'+sessions[side]+'/goog/cdp/execute',{'cmd':'Browser.setPermission','params':{'permission':{'name':'persistent-storage'},'setting':'granted','origin':'https://ksu.codes'}})
  wid=js(side,'return [...desktopLab.surfaces.values()][0].launch("chat").id;');selectors[side]='[data-window="'+str(wid)+'"]';sel=selectors[side];wait(side,'return !!document.querySelector(arguments[0])?.querySelector(".storage-consent button:not(:disabled),[data-device-channels]");',[sel])
  if not js(side,'return !!document.querySelector(arguments[0]).querySelector("[data-device-channels]");',[sel]):
   el=d.call('/session/'+sessions[side]+'/element',{'using':'css selector','value':sel+' .storage-consent button:not(:disabled)'})['element-6066-11e4-a52e-4f735466cecf'];d.call('/session/'+sessions[side]+'/element/'+el+'/click',{})
  wait(side,'return !!document.querySelector(arguments[0]).querySelector("[data-device-channels]");',[sel])
 try:
  start('a');js('a','const n=document.querySelector(arguments[0]);[...n.querySelectorAll("input")].find(x=>x.getAttribute("aria-label")==="Device channel label").value=arguments[1];n.querySelector("[data-directory-create]").click();',[selectors['a'],label]);wait('a','return !!document.querySelector(arguments[0]).querySelector("[data-device-select]").value;',[selectors['a']]);deadline=time.monotonic()+90
  while time.monotonic()<deadline:
   record=db('read')
   if record:break
   time.sleep(.5)
  assert record,'listing was not saved';time.sleep(12);record=db('read');assert record;time.sleep(18);after=db('read');probe=js('a','return {count:window.codiListingProbe.length,unique:new Set(window.codiListingProbe).size,ticks:window.codiListingTicks};');result['refreshProbe']=probe;assert after==record and probe['ticks']>=3 and 1<=probe['count']<=2 and probe['unique']==1,'listing refresh did not suppress repeated requests';check('multiple refresh ticks sent at most two copies of one signature')
  d.call('/session/'+sessions.pop('a'),method='DELETE');check('live channel reference persisted and owner went offline')
  subprocess.run(['ssh','-o','BatchMode=yes','box-webhost','sudo','-n','systemctl','restart','codi-ksu-hidden-steward'],check=True,timeout=45);check('live introduction service restarted')
  start('b');js('b','const q=document.querySelector(arguments[0]).querySelector("input[type=search]");q.value=arguments[1];q.dispatchEvent(new Event("input",{bubbles:true}));',[selectors['b'],label]);wait('b','return [...document.querySelector(arguments[0]).querySelectorAll("[data-channel-results] button")].some(x=>x.textContent==="Join");',[selectors['b']],90);check('fresh browser found offline channel without a shared code')
  start('a');wait('a','return !!document.querySelector(arguments[0]).querySelector("[data-device-select]")?.value;',[selectors['a']],90);js('b','[...document.querySelector(arguments[0]).querySelectorAll("[data-channel-results] button")].find(x=>x.textContent==="Join").click();',[selectors['b']]);wait('b','return !!document.querySelector(arguments[0]).querySelector("[data-device-select]").value;',[selectors['b']],90)
  for side,other in [('a','b'),('b','a')]:
   msg='Directory live '+side;wait(side,'return !document.querySelector(arguments[0]).querySelector("[data-device-queue]").disabled;',[selectors[side]]);js(side,'const n=document.querySelector(arguments[0]);n.querySelector("[data-device-draft]").value=arguments[1];n.querySelector("[data-device-queue]").click();',[selectors[side],msg]);wait(other,'return document.querySelector(arguments[0]).querySelector("[data-device-history]").textContent.includes(arguments[1]);',[selectors[other],msg],120)
  check('both live browsers joined and exchanged messages');result['status']='PASS'
 except Exception as e:
  result.update(error=str(e),traceback=traceback.format_exc())
  for side in sessions:
   try:result.setdefault('diagnostics',{})[side]=js(side,'return document.body.innerText.slice(-3500);')
   except Exception:pass
 finally:
  for sid in sessions.values():
   try:d.call('/session/'+sid,method='DELETE')
   except Exception as e:result['status']='FAIL';result['cleanupError']=str(e)
  for p in profiles.values():shutil.rmtree(p,ignore_errors=True)
  try:
   removed=db('delete');result['removedTestReference']=len(removed);assert not record or [x[:2] for x in removed]==[x[:2] for x in record];assert not db('read')
  except Exception as e:result['status']='FAIL';result['databaseCleanupError']=str(e)
  result['profilesRemoved']=all(not p.exists() for p in profiles.values())
 return result
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args();assert not a.output.exists();r=run();a.output.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({'status':r['status'],'error':r.get('error'),'checks':r['checks']}));raise SystemExit(r['status']!='PASS')
