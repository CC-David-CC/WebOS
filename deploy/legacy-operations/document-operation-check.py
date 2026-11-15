#!/usr/bin/env python3
"""Actual private-store operation durability, isolation, ACL and crash recovery."""
import concurrent.futures,hashlib,json,os,subprocess,sys,tempfile,time,uuid
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent;sys.path.insert(0,str(ROOT))
from gateway_service.user_store import UserStore,Conflict
from gateway_service.policy import Principal,Denied

def main():
 checks=[]
 def check(name,v):assert v,name;checks.append(name)
 def denied(fn):
  try:fn()
  except (Denied,FileNotFoundError):return True
  return False
 with tempfile.TemporaryDirectory(prefix='document-operation-') as tmp:
  base=Path(tmp);state=base/'state';data=base/'files';state.mkdir(mode=0o700);data.mkdir(mode=0o700);store=UserStore(state,data)
  one=Principal('user:'+str(uuid.uuid4()),'one','registered',{},int(time.time())+600);two=Principal('user:'+str(uuid.uuid4()),'two','registered',{},int(time.time())+600);anon=Principal('anon:test','anon','anonymous',{},int(time.time())+600)
  store.ensure_user(one);store.ensure_user(two);store.mkdir(one,'Documents');text='hello world\n你好 three\n';version=store.put(one,'Documents/note.txt',text.encode())['sha256']
  report=store.word_count(one,'Documents/note.txt',version);raw=store.read(one,report['path'])['bytes'];check('server calculates real UTF-8 document report',b'Words (whitespace separated): 4' in raw and b'Lines: 2' in raw and report['sourceSHA256']==version)
  store=UserStore(state,data);check('worker reopen and duplicate request return same persisted operation',store.word_count(one,'Documents/note.txt',version)==report)
  check('other account cannot read owner report or operate owner document',denied(lambda:store.read(two,report['path'])) and denied(lambda:store.word_count(two,'Documents/note.txt',version)))
  check('anonymous cannot allocate an operation',denied(lambda:store.word_count(anon,'Documents/note.txt',version)))
  store.put(one,'Documents/note.txt',b'changed document',previous_sha256=version)
  check('completed operation remains bound to its accepted source version',store.word_count(one,'Documents/note.txt',version)==report)
  check('unaccepted stale version is refused',denied(lambda:store.word_count(one,'Documents/note.txt','0'*64)))
  store.set_permission(one.sub,'create',False);check('revoked creation permission blocks operation replay',denied(lambda:store.word_count(one,'Documents/note.txt',version)));store.set_permission(one.sub,'create',True)
  store.set_permission(one.sub,'read',False);check('revoked read permission blocks operation',denied(lambda:store.word_count(one,'Documents/note.txt',version)));store.set_permission(one.sub,'read',True)
  for phase in ['accepted','published']:
   path='Documents/crash-'+phase+'.txt';v=store.put(one,path,b'original snapshot words')['sha256']
   code="import sys,os,time;from pathlib import Path;sys.path.insert(0,sys.argv[1]);from gateway_service.user_store import UserStore;from gateway_service.policy import Principal;p=Principal(sys.argv[4],'crash','registered',{},int(time.time())+600);s=UserStore(Path(sys.argv[2]),Path(sys.argv[3]));s.word_count(p,sys.argv[5],sys.argv[6],phase=lambda n:os._exit(73) if n==sys.argv[7] else None)"
   child=subprocess.run([sys.executable,'-B','-c',code,str(ROOT),str(state),str(data),one.sub,path,v,phase]);assert child.returncode==73
   store=UserStore(state,data);store.put(one,path,b'edited after acceptance',previous_sha256=v);completed=store.word_count(one,path,v);saved=store.read(one,completed['path'])['bytes']
   check('real process death after '+phase+' recovers original snapshot once',b'Words (whitespace separated): 3' in saved and completed['sourceSHA256']==v and store.word_count(one,path,v)==completed)
  parallel='Documents/concurrent.txt';v=store.put(one,parallel,b'parallel source')['sha256']
  with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:values=list(pool.map(lambda _:store.word_count(one,parallel,v),range(4)))
  check('concurrent duplicate operations publish one report',all(v==values[0] for v in values))
  store.put(one,report['path'],b'edited report',previous_sha256=report['sha256']);check('edited report is never overwritten by retry',denied(lambda:store.word_count(one,'Documents/note.txt',version)) and store.read(one,report['path'])['bytes']==b'edited report')
  r=values[0];store.delete(one,r['path'],previous_sha256=r['sha256']);check('deleted completed report is not silently recreated',denied(lambda:store.word_count(one,parallel,v)))
  check('traversal input is refused',denied(lambda:store.word_count(one,'../note.txt',version)))
  for name,raw in [('binary',b'a\0b'),('invalid',b'\xff'),('oversized',b'x'*(1024*1024+1))]:
   v=store.put(one,name,raw)['sha256'];check(name+' document is refused',denied(lambda:store.word_count(one,name,v)))
  check('operation DB is private and separate from permissions',(state/'document-operations.sqlite3').stat().st_mode&0o777==0o600 and (state/'permissions.sqlite3').exists())
 return {'status':'PASS','checks':checks,'realProcessCrashPoints':['accepted','published'],'userDataUsed':False}
if __name__=='__main__':
 result={'status':'FAIL'}
 try:result.update(main())
 finally:
  result['sourceSHA256']={n:hashlib.sha256((ROOT/n).read_bytes()).hexdigest() for n in ['gateway_service/user_store.py','gateway_service/http.py','gateway_service/client.mjs','scripts/document-operation-check.py']};out=ROOT/'.build/checks/document-operation-result.json';out.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
