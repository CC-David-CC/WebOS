#!/usr/bin/env python3
"""Actual previous worker HTTP reads/writes retained recovered receipts.

Same private fixture SQLite/key, separate interpreter loading the exact870 graph.
No authority/data restore, production installation, independent replica or8k claim.
"""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import traceback
import urllib.request
from urllib.parse import urlsplit

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('recovery_rollback_fixture',ROOT/'scripts/hosted-room-check.py');fmod=importlib.util.module_from_spec(spec);spec.loader.exec_module(fmod)
OLD='870df3f9fd7efc2dbb1d5256da98476662c1ea5df95ae987c75e1472ebfd14d4'
CHILD='''import json,sys
from pathlib import Path
d=json.loads(sys.stdin.readline());root=Path(d['release']);sys.path[:0]=[str(root),str(root/'codiserver-server-v0.3.0')]
from room_service.store import RoomStore
from room_service.http import RoomHTTP
from wsgiref.simple_server import make_server,WSGIRequestHandler
assert not hasattr(RoomStore,'_recover')
store=RoomStore(Path(d['state']),d['policy'],clock=lambda:d['now'])
class Quiet(WSGIRequestHandler):
 def log_message(self,*_):pass
with make_server('127.0.0.1',0,RoomHTTP(store),handler_class=Quiet) as server:
 print(json.dumps({'port':server.server_port,'recoveryAPI':False}),flush=True);server.serve_forever()
'''

def run(old):
    checks=[];f=None;child=None;temporary=tempfile.TemporaryDirectory(prefix='codi-recovery-rollback-')
    result={'status':'FAIL','scope':__doc__,'checks':checks,'wholeGoalComplete':False,'oldWorkerManifestSHA256':OLD}
    def check(name,ok):assert ok,name;checks.append(name);print(json.dumps({'check':name}),flush=True)
    try:
        raw=(old/'room-worker.json').read_bytes();assert hashlib.sha256(raw).hexdigest()==OLD
        manifest=json.loads(raw)
        for n,r in manifest['files'].items():
            p=old/n;assert r=={'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
        f=fmod.Fixture(Path(temporary.name));owner=fmod.Actor(f,'rollback_owner')
        boot=owner.operation('create',{'request_id':fmod.secrets.token_urlsafe(32),'label':'Recovery survives code rollback'});grant=boot['grant'];node=fmod.jose.inspect(boot['descriptor'],fmod.POLICY_TYPE)[1]['node_id']
        original=owner.origin(grant,1,'Keep the original proposal');event_id=fmod.token_id(original,fmod.ORIGIN_TYPE,16384);f.clock.value+=61
        fresh=fmod.Actor(f,'rollback_owner',signin=True);head=fmod.jose.inspect(fresh.operation('describe',{'node_id':node})['head'],fmod.HEAD_TYPE)[1];now=int(f.clock())
        consent={'version':fmod.RECOVERY_VERSION,'node_id':node,'descriptor_hash':fmod.token_id(boot['descriptor'],fmod.POLICY_TYPE),'event_id':event_id,'grant_hash':fmod.token_id(grant,fmod.MEMBER_TYPE,8192),'requester_session_id':fresh.sid,'base':{'index':head['count'],'hash':head['hash']},'iat':now,'exp':now+25}
        recovered=fresh.operation('recover',{'node_id':node,'grant':grant,'event':original,'reauthorization':fmod.jose.sign(consent,fresh.key,fmod.REAUTHORIZE_TYPE)})
        before_key=hashlib.sha256((f.state/'controller.pem').read_bytes()).hexdigest()
        child=subprocess.Popen([sys.executable,'-I','-B','-c',CHILD],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
        child.stdin.write(json.dumps({'release':str(old),'state':str(f.state),'policy':f.policy,'now':now})+'\n');child.stdin.flush()
        line=child.stdout.readline()
        assert line,child.stderr.read(4000)
        ready=json.loads(line);assert ready['recoveryAPI'] is False
        def request(op,args):
            envelope=fresh.envelope(op,args);req=urllib.request.Request('http://127.0.0.1:'+str(ready['port'])+'/rooms/use',data=fmod.jose.dumps(envelope).encode(),headers={'Host':urlsplit(f.origin).netloc,'Origin':f.origin,'Content-Type':'application/json'})
            with urllib.request.urlopen(req,timeout=10) as response:return fmod.jose.loads(response.read())
        lookup=request('lookup',{'node_id':node,'event_id':event_id})
        check('exact previous worker authenticates a new request and returns the unchanged recovered receipt',lookup['receipt']==recovered['receipt'])
        snapshot=request('sync',{'node_id':node,'after':None,'lease':None,'tail':False})
        checkpoint=fmod.jose.verify(snapshot['state']['snapshot'],f.store.public,fmod.SNAPSHOT_TYPE)
        check('previous worker produces a signed checkpoint over recovered history without rewriting it',checkpoint['checkpoint']['index']==1 and checkpoint['window']['entries']==[recovered['receipt']] and snapshot['state']['head']==snapshot['bootstrap']['head'])
        admitted=fresh.operation('join',{'node_id':node,'proof':None})['grant'];normal=fresh.origin(admitted,1,'Normal message while recovery API is rolled back')
        accepted=request('accept',{'node_id':node,'grant':admitted,'event':normal})
        check('old worker accepts a normal fresh-session message after a recovered original',accepted['accepted'] and fmod.jose.inspect(accepted['receipt'],fmod.RECEIPT_TYPE)[1]['index']==2)
        child.terminate();child.wait(timeout=5);child=None;f.reopen()
        unchanged=fresh.operation('lookup',{'node_id':node,'event_id':event_id})
        with f.store.lock(),f.store.db() as db:
            highest=dict(db.execute('SELECT sid,highest FROM streams WHERE node=?',(node,)));count=db.execute('SELECT count(*) FROM events WHERE node=?',(node,)).fetchone()[0]
        check('return to new worker retains both original stream floors and all accepted data exactly once',unchanged['receipt']==recovered['receipt'] and count==2 and highest[owner.sid]==highest[fresh.sid]==1 and hashlib.sha256((f.state/'controller.pem').read_bytes()).hexdigest()==before_key)
        result.update(status='PASS',acceptedMessages=count,oldWorkerHadRecoveryAPI=False,dataRestored=False)
    except Exception as e:result.update(error=str(e),traceback=traceback.format_exc())
    finally:
        if child:child.terminate();child.wait(timeout=5)
        if f:f.close()
        temporary.cleanup()
    return result

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--old-worker',type=Path,default=ROOT/'.build/room-workers/atomic-sync-r1');p.add_argument('--output',type=Path,required=True);a=p.parse_args();assert not a.output.exists();v=run(a.old_worker.resolve());a.output.write_text(json.dumps(v,indent=2)+'\n');print(json.dumps({'status':v['status'],'checks':len(v['checks']),'error':v.get('error')}));raise SystemExit(0 if v['status']=='PASS' else 1)
