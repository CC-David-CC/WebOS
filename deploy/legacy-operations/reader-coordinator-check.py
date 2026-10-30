#!/usr/bin/env python3
"""Separate actual discovery process/key, signed bootstrap and saved-chat failure isolation.

Owned HTTP/SQLite/keys fixture, no deployment, installed sandbox, browser/WAN or
capacity claim. Production DAC/units and browser integration need separate proof.
"""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import os
import signal
import subprocess
import sys
import tempfile
import time
import traceback
import urllib.request
from urllib.error import HTTPError,URLError
from urllib.parse import urlsplit
from cryptography.hazmat.primitives import serialization

ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
s=importlib.util.spec_from_file_location('coordinator_fixture',ROOT/'scripts/hosted-room-check.py');fmod=importlib.util.module_from_spec(s);s.loader.exec_module(fmod)
from reader_service.contract import issue,verify,DELEGATION,paths,VERSION
from room_service.rendezvous import VERSION as WIRE,BOOTSTRAP,REQUEST,WORK,TICKET

CHILD='''import json,sys,time,os
from pathlib import Path
d=json.loads(sys.stdin.readline());sys.path.insert(0,d['source'])
from room_service.contract import jose
from reader_service.http import ReaderHTTP
from cryptography.hazmat.primitives import serialization
from wsgiref.simple_server import make_server,WSGIRequestHandler
key=serialization.load_pem_private_key(Path(d['key']).read_bytes(),password=None);app=ReaderHTTP(key,d['policy'],d['roomKey'],d['delegation'],delegation_provider=lambda:Path(d['authority']).read_text())
class Quiet(WSGIRequestHandler):
 def log_message(self,*_):pass
assert 'room_service.store' not in sys.modules
with make_server('127.0.0.1',0,app,handler_class=Quiet) as server:
 print(json.dumps({'port':server.server_port,'pid':os.getpid(),'roomStoreImported':False}),flush=True);server.serve_forever()
'''

def run():
    checks=[];child=None;f=None;stopped=False;temporary=tempfile.TemporaryDirectory(prefix='codi-coordinator-')
    result={'status':'FAIL','scope':__doc__,'checks':checks,'wholeGoalComplete':False}
    def check(name,ok):assert ok,name;checks.append(name);print(json.dumps({'check':name}),flush=True)
    def refused(fn):
        try:fn();return False
        except Exception:return True
    try:
        folder=Path(temporary.name);f=fmod.Fixture(folder);f.clock.realtime=True
        owner=fmod.Actor(f,'coordinator_owner');reader=fmod.Actor(f)
        boot=owner.operation('create',{'request_id':fmod.secrets.token_urlsafe(32),'label':'Separate coordinator test'});descriptor=fmod.jose.inspect(boot['descriptor'],fmod.POLICY_TYPE)[1];node=descriptor['node_id'];node_hash=fmod.token_id(boot['descriptor'],fmod.POLICY_TYPE)
        key=fmod.ec.generate_private_key(fmod.ec.SECP256R1());public=fmod.jose.public_jwk(key);now=int(time.time());delegation=issue(f.store.key,public,f.policy,'',now)
        assert verify(delegation,f.store.public,public,f.policy,'',now)['scope']=='public-reader-introductions-only/1'
        foreign=fmod.ec.generate_private_key(fmod.ec.SECP256R1());claims=fmod.jose.inspect(delegation,DELEGATION)[1]
        invalid=[]
        for change in [{'scope':'saved-chat-write'},{'path':'/rooms/use'},{'exp':now},{'exp':now+21601}]:
            token=fmod.jose.sign({**claims,**change},f.store.key,DELEGATION);invalid.append(refused(lambda:verify(token,f.store.public,public,f.policy,'',now)))
        invalid.append(refused(lambda:verify(delegation,f.store.public,fmod.jose.public_jwk(foreign),f.policy,'',now)))
        invalid.append(refused(lambda:verify(delegation,public,public,f.policy,'',now)))
        check('delegation rejects wrong purpose/path/key, expired and excessive lifetime even when controller-signed',all(invalid))
        own=folder/'coordinator';own.mkdir(mode=0o700);keyfile=own/'key.pem';keyfile.write_bytes(key.private_bytes(serialization.Encoding.PEM,serialization.PrivateFormat.PKCS8,serialization.NoEncryption()));keyfile.chmod(0o600);authority=own/'delegation.jws';authority.write_text(delegation)
        child=subprocess.Popen([sys.executable,'-I','-B','-c',CHILD],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
        child.stdin.write(json.dumps({'source':str(ROOT),'key':str(keyfile),'policy':f.policy,'roomKey':f.store.public,'delegation':delegation,'authority':str(authority)})+'\n');child.stdin.flush();line=child.stdout.readline();assert line,child.stderr.read(4000);ready=json.loads(line)
        check('coordinator runs in a separate interpreter without importing saved-chat storage',ready['pid']==child.pid!=os.getpid() and ready['roomStoreImported'] is False)
        audience,path=paths(f.policy,'')
        def http(p,body=None,expected=200):
            req=urllib.request.Request('http://127.0.0.1:'+str(ready['port'])+p,data=None if body is None else fmod.jose.dumps(body).encode(),headers={'Host':urlsplit(f.origin).netloc,'Origin':f.origin,'Content-Type':'application/json','Codi-Reader':'rendezvous/1'})
            try:
                with urllib.request.urlopen(req,timeout=3) as r:status,value=r.status,json.load(r)
            except HTTPError as e:status,value=e.code,json.load(e)
            assert status==expected,(p,status,value,expected);return value
        metadata=http('/rooms/readers/authority');check('public authority exposes only its independently delegated discovery key',metadata['key']==public and metadata['key']!=f.store.public and metadata['delegation']==delegation)
        nodes=[{'node_id':node,'descriptor_hash':node_hash,'descriptor':boot['descriptor']}]
        def bootstrap(operation,work=None,selected=nodes,expected=200):
            raw=fmod.jose.dumps({'version':WIRE,'operation':operation,'nodes':selected,'work':work});t=int(time.time())
            proof=fmod.jose.sign({'v':1,'iss':reader.sid,'aud':audience,'method':'POST','path':path,'iat':t,'exp':t+25,'request_sha256':fmod.jose.digest(raw)},reader.key,BOOTSTRAP)
            return http(path,{'request':raw,'identity':reader.identity,'proof':proof},expected)
        puzzle=bootstrap('challenge');p=fmod.jose.verify(puzzle['challenge'],public,WORK,4096)
        digest=fmod.token_id(puzzle['challenge'],WORK);counter=next(n for n in range(131072) if (lambda d:d[0]==0 and d[1]>>6==0)(hashlib.sha256(fmod.jose.dumps(['codi-admission-work/1',digest,n]).encode()).digest()))
        ticket=bootstrap('ticket',{'challenge_id':p['challenge_id'],'counter':counter});claims=fmod.jose.verify(ticket['ticket'],public,TICKET,8192)
        check('fresh browser identity and real light work obtain discovery-only tickets for controller-signed rooms',claims['sid']==reader.sid and claims['aud']==audience and claims['scopes']=={node:node_hash})
        t=int(time.time());presence=fmod.jose.sign({'version':'codi-hosted-readers/1','node_id':node,'descriptor_hash':node_hash,'reader':reader.sid,'iat':t,'exp':t+50},reader.key,'codi-hosted-reader+jws')
        raw=fmod.jose.dumps({'version':WIRE,'sequence':1,'interests':[{'node_id':node,'descriptor_hash':node_hash,'presence':presence,'known':[]}],'outbox':None,'ack':[]})
        proof=fmod.jose.sign({'v':1,'iss':reader.sid,'aud':audience,'method':'POST','path':path,'iat':t,'exp':t+25,'ticket_sha256':fmod.jose.digest(ticket['ticket']),'request_sha256':fmod.jose.digest(raw),'sequence':1},reader.key,REQUEST)
        poll=http(path,{'request':raw,'ticket':ticket['ticket'],'proof':proof})
        check('separate coordinator accepts signed public-reader presence without a member grant',poll['sequence']==1 and poll['rooms'][0]['node_id']==node)
        http('/rooms/use',{'request':'{}'},expected=404);bootstrap('create',expected=400)
        fake=fmod.jose.sign({'version':'codi-hosted-room/1'},key,fmod.RECEIPT_TYPE)
        check('discovery role has no saved-chat API or key able to sign accepted room receipts',refused(lambda:fmod.jose.verify(fake,f.store.public,fmod.RECEIPT_TYPE)))
        os.kill(child.pid,signal.SIGSTOP);stopped=True
        accepted=owner.operation('accept',{'node_id':node,'grant':boot['grant'],'event':owner.origin(boot['grant'],1,'Saved chat works with coordinator stopped')})
        check('actual saved-chat write remains available while coordinator process is stopped',accepted['accepted'])
        os.kill(child.pid,signal.SIGCONT);stopped=False
        check('resumed coordinator retains its own ephemeral discovery state',http('/rooms/readers/health')['ready'] is True)
        result.update(status='PASS',actualCoordinatorProcess=True,discoveryKeyDiffersFromRoomKey=True,savedChatWritableDuringCoordinatorStop=True,sandboxOrDACProven=False,servicesDeployed=False)
    except Exception as e:result.update(error=str(e),traceback=traceback.format_exc())
    finally:
        if child:
            if stopped:os.kill(child.pid,signal.SIGCONT)
            child.terminate();child.wait(timeout=5)
        if f:f.close()
        temporary.cleanup()
    return result

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args();assert not a.output.exists();v=run();a.output.write_text(json.dumps(v,indent=2)+'\n');print(json.dumps({'status':v['status'],'checks':len(v['checks']),'error':v.get('error')}));raise SystemExit(0 if v['status']=='PASS' else 1)
