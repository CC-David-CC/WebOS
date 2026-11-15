#!/usr/bin/env python3
"""Actual generated Caddy discovery routing and saved-chat exclusion checks."""
import argparse
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import traceback
import urllib.request
from urllib.error import HTTPError,URLError

ROOT=Path(__file__).resolve().parents[1]
def module(name,path):
    s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
separate=module('ingress_coordinator',ROOT/'scripts/reader-coordinator-fixture.py');source=separate.source;fmod=source.fmod

def run(hosting,caddy):
    sys.path.insert(0,str(hosting/'ops'));common=module('coordinator_candidate_common',hosting/'ops/common.py')
    checks=[];f=None;coord=None;temporary=tempfile.TemporaryDirectory(prefix='codi-coordinator-ingress-')
    result={'status':'FAIL','checks':checks,'scope':__doc__,'publicIngressChanged':False,'wholeGoalComplete':False}
    def check(name,ok):assert ok,name;checks.append(name);print(json.dumps({'check':name}),flush=True)
    def refused(fn):
        try:fn()
        except ValueError:return True
        return False
    try:
        base=common.load(hosting/'sites.toml');ksu=next(s for s in base['sites'] if s['domain']=='ksu.codes')
        invalid=[]
        for change in [{'codi_readers':True},{'codi_readers':'unknown'},{'codi_readers':'active','codi_rooms':False},{'codi_readers':'prepare','enabled':False},{'codi_readers':'active','domain':'evil.invalid'}]:
            data=copy.deepcopy(base);s=next(s for s in data['sites'] if s['domain']=='ksu.codes');s.update(change);invalid.append(refused(lambda:common.validate(data)))
        check('manifest rejects boolean/unknown mode, missing rooms, disabled or unrelated hostname',all(invalid))
        check('absent flag preserves exact existing production Caddy bytes',hashlib.sha256(common.caddy(base,'production').encode()).hexdigest()=='42161b4b7235cfaadfdc884b37df2a6fe7a500c5edc897f8bd7d986a769d07c2')
        folder=Path(temporary.name);f=fmod.Fixture(folder,front_origin=separate.front_origin());f.clock.realtime=True;coord=separate.CoordinatorFixture(f,caddy)
        original=f.server.get_app();calls=[]
        def counted(env,start):
            calls.append({'path':env.get('PATH_INFO'),'reader':env.get('HTTP_CODI_READER')});return original(env,start)
        f.server.set_app(counted)
        def front(phase):
            coord.front.terminate();coord.front.wait(timeout=12)
            s={**ksu,'codi_readers':phase};routes='\n'.join(common.room_routes(s)).replace('127.0.0.1:8143','127.0.0.1:'+str(coord.port)).replace('127.0.0.1:8141','127.0.0.1:'+str(f.server.server_port))
            text='{\n admin off\n auto_https off\n}\n'+f.origin+' {\n bind 127.0.0.1\n'+routes+'\n handle /api/* {\n reverse_proxy 127.0.0.1:'+str(f.server.server_port)+'\n }\n handle {\n respond "Not found" 404\n }\n}\n'
            config=coord.folder/'generated.Caddyfile';config.write_text(text)
            with (coord.folder/'generated.log').open('ab') as log:coord.front=subprocess.Popen([str(caddy),'run','--config',str(config),'--adapter','caddyfile'],stdin=subprocess.DEVNULL,stdout=log,stderr=log)
            until=time.monotonic()+10
            while True:
                if coord.front.poll() is not None:raise RuntimeError((coord.folder/'generated.log').read_text()[-3000:])
                try:
                    with urllib.request.urlopen(f.origin+'/rooms/readers/health',timeout=1) as r:assert r.status==200
                    break
                except (URLError,OSError):
                    if time.monotonic()>until:raise
                    time.sleep(.1)
        def request(path,body=None,headers=None):
            req=urllib.request.Request(f.origin+path,data=body,headers={'Content-Type':'application/json','Origin':f.origin,**(headers or {})})
            try:
                with urllib.request.urlopen(req,timeout=5) as r:return r.status,r.read()
            except HTTPError as e:return e.code,e.read()
        front('prepare');status,raw=request('/rooms/readers/authority');metadata=json.loads(raw)
        check('prepare mode serves real independently delegated authority through generated Caddy route',status==200 and metadata['key']==coord.public and metadata['key']!=f.store.public)
        count=len(calls);status,_=request('/rooms/use',b'{}',{'Codi-Reader':'rendezvous/1'})
        check('prepare preserves old discovery path during reader-first transition',status==400 and len(calls)==count+1 and calls[-1]['reader']=='rendezvous/1')
        owner=fmod.Actor(f,'ingress_owner');room=owner.operation('create',{'request_id':fmod.secrets.token_urlsafe(32),'label':'Managed ingress test'})
        node=fmod.jose.inspect(room['descriptor'],fmod.POLICY_TYPE)[1]['node_id']
        check('registered identity and authorized saved-chat create work through generated routes',isinstance(node,str))
        front('active');count=len(calls)
        rejected=[]
        for value in ['rendezvous/1','unknown-profile']:
            status,_=request('/rooms/use',b'{}',{'Codi-Reader':value});rejected.append(status==410)
        check('active mode rejects legacy reader headers at Caddy before saved-chat process',all(rejected) and len(calls)==count)
        for path in ['/rooms/readers/authority','/rooms/readers/health']:
            status,raw=request(path);assert status==200 and json.loads(raw)['key']==coord.public
        count=len(calls);status,_=request('/rooms/readers/use',b'{}',{'Codi-Reader':'rendezvous/1'})
        check('active discovery POST reaches only coordinator validation, never saved-chat process',status==400 and len(calls)==count)
        status,_=request('/rooms/readers/not-a-route');check('undeclared coordinator endpoints remain unavailable',status==404)
        status,_=request('/rooms/readers/use',b'x'*131073,{'Codi-Reader':'rendezvous/1'});check('generated route bounds discovery upload before worker',status==413)
        accepted=owner.operation('accept',{'node_id':node,'grant':room['grant'],'event':owner.origin(room['grant'],1,'Ordinary chat after discovery separation')})
        check('active legacy-reader exclusion retains real authorized saved-chat writes',accepted['accepted'])
        front('prepare');count=len(calls);status,_=request('/rooms/use',b'{}',{'Codi-Reader':'rendezvous/1'})
        check('rollback prepare reopens legacy reader path without restoring saved-chat data',status==400 and len(calls)==count+1)
        result.update(status='PASS',caddySeparateProcess=True,coordinatorSeparateProcess=True,sourceCommonSHA256=hashlib.sha256((hosting/'ops/common.py').read_bytes()).hexdigest(),savedChatCount=1)
    except Exception as e:result.update(error=str(e),traceback=traceback.format_exc())
    finally:
        if coord:coord.close()
        if f:f.close()
        temporary.cleanup()
    return result

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--hosting',type=Path,required=True);p.add_argument('--caddy',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();assert not a.output.exists();v=run(a.hosting.resolve(),a.caddy.resolve());a.output.write_text(json.dumps(v,indent=2)+'\n');print(json.dumps({'status':v['status'],'checks':len(v['checks']),'error':v.get('error')}));raise SystemExit(0 if v['status']=='PASS' else 1)
