#!/usr/bin/env python3
"""Exercise approved live code rollback/forward while retaining an owned local file.

Both releases keep chat paused. Never retry a failed or ambiguous mutation;
inspect its typed publisher/native journal before taking another action.
"""
import argparse,hashlib,importlib.util,json,secrets,shutil,tempfile,time,traceback,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def module(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
h=module('browser_file_cycle_driver',ROOT/'scripts/touch-preview-check.py')
publisher=module('browser_file_cycle_publish',ROOT/'scripts/browser-files-live-publish.py')
def run(commit):
 profile=Path(tempfile.mkdtemp(prefix='codi-browser-cycle-',dir=Path.home()/'snap/chromium/common'));sid=None
 result={'status':'FAIL','scope':__doc__,'checks':[],'mutations':[],'defaultPublicTLS':True,'outsideWAN':False,'wholeGoalComplete':False};checks=result['checks'];text='An on-device file across a real code rollback.';path='/rollback-'+secrets.token_hex(6)+'.txt'
 def js(code,args=[]):return h.call('/session/'+sid+'/execute/sync',{'script':code,'args':args})
 def task(code,args=[]):
  r=h.call('/session/'+sid+'/execute/async',{'script':'const params=Array.from(arguments),done=params.pop();(async()=>{'+code+'})().then(value=>done({ok:true,value}),error=>done({ok:false,error:error.stack}));','args':args});assert r['ok'],r;return r.get('value')
 def check(label,ok):assert ok,label;checks.append(label);print(json.dumps({'check':label}),flush=True)
 try:
  sid=h.call('/session',{'capabilities':{'alwaysMatch':{'browserName':'chrome','goog:chromeOptions':{'binary':'/snap/chromium/current/usr/lib/chromium-browser/chrome','args':['--headless=new','--no-sandbox','--disable-dev-shm-usage','--user-data-dir='+str(profile)]}}}})['sessionId'];h.call('/session/'+sid+'/timeouts',{'script':120000});h.call('/session/'+sid+'/url',{'url':'https://ksu.codes/'})
  h.wait(lambda:js('return window.desktopLab?.guestState==="ready"&&!desktopLab.lifecycle.blocked'),180)
  before=task('const c=await browserFileContext();const saved=await c.files.write(params[0],params[1]);return {owner:c.owner,version:saved.version,sha256:saved.sha256};',[path,text]);check('saved owned browser file before rollback',bool(before['version']))
  step=publisher.run(['rollback'],commit);result['mutations'].append(step);assert step['status']=='PASS',step;check('actual code-only rollback to paused9f preserves authoritative server state',step['steps'][0]['receipt']['afterManifestSHA256']=='9f86587c8590eed2c34bbf3eede2efb109fe0a8401328551a00092f19e3b9fe9')
  base=ROOT/'.build/releases/connected-device-history-host-r4'
  with urllib.request.urlopen('https://ksu.codes/index.html',timeout=25) as r:check('public root serves exact rollback code',r.read()==(base/'index.html').read_bytes())
  # Read via native IndexedDB independently of the still-loaded first-party
  # facade. Code rollback must never clear or rewrite a visitor's local volume.
  kept=task('return await new Promise((resolve,reject)=>{const q=indexedDB.open("codi-browser-files-v1",1);q.onerror=()=>reject(q.error);q.onsuccess=()=>{const db=q.result,t=db.transaction(["entries","contents"],"readonly"),a=t.objectStore("entries").get([params[0],params[1]]),b=t.objectStore("contents").get([params[0],params[1]]);t.oncomplete=()=>{db.close();resolve({version:a.result.version,sha256:a.result.sha256,text:new TextDecoder().decode(b.result.data)})};t.onabort=()=>{db.close();reject(t.error)}}});',[before['owner'],path])
  check('real rollback leaves native browser bytes and CAS version untouched',kept['text']==text and kept['version']==before['version'] and kept['sha256']==before['sha256'])
  step=publisher.run(['activate'],commit);result['mutations'].append(step);assert step['status']=='PASS',step;check('actual forward upgrade preserves current state and keeps chat disabled',step['steps'][0]['receipt']['afterManifestSHA256']=='36868e655bc12c61123ec2e7d8562bea511375aa6136d5f5dd610ca81a751d46' and step['steps'][0]['receipt']['chatDisabled'])
  h.call('/session/'+sid+'/refresh',{});h.wait(lambda:js('return window.desktopLab?.guestState==="ready"&&!desktopLab.lifecycle.blocked'),180)
  check('fresh current desktop reopens same browser owner, bytes and exact saved version',task('const c=await browserFileContext(),f=await c.files.read(params[0]);return c.owner===params[1]&&f.version===params[2]&&f.sha256===params[3]&&new TextDecoder().decode(f.data)===params[4];',[path,before['owner'],before['version'],before['sha256'],text]))
  result['status']='PASS'
 except Exception as e:result.update(error=str(e),traceback=traceback.format_exc(),recovery='Inspect the final explicit native/publisher receipt and current config; never resend an ambiguous mutation.')
 finally:
  if sid:h.call('/session/'+sid,method='DELETE')
  shutil.rmtree(profile);result['ownedProfileRemoved']=not profile.exists();result['scriptSHA256']=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
 return result
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--commit',required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();assert not a.output.exists();r=run(a.commit);a.output.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({'status':r['status'],'checks':len(r['checks']),'error':r.get('error')}));raise SystemExit(r['status']!='PASS')
