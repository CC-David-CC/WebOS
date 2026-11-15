#!/usr/bin/env python3
"""Real HTTP transient-capacity headers with unchanged eight/600 limits.

Owned fixture fills eight actual actor nonce slots; its volatile source-rate
counter is deliberately saturated to test refusal, then expiry is simulated.
Not a throughput/load, browser, public or8k capacity claim.
"""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import traceback
import urllib.request
from urllib.error import HTTPError

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('capacity_http_fixture',ROOT/'scripts/hosted-room-check.py');fixture=importlib.util.module_from_spec(spec);spec.loader.exec_module(fixture)

def run():
    checks=[];f=None;sources=[Path(__file__),ROOT/'room_service/access.py',ROOT/'room_service/http.py']
    pins={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in sources};result={'status':'FAIL','scope':__doc__,'checks':checks,'wholeGoalComplete':False}
    def check(name,ok):assert ok,name;checks.append(name);print(json.dumps({'check':name}),flush=True)
    def request(path,body):
        req=urllib.request.Request(f.origin+path,data=fixture.jose.dumps(body).encode(),headers={'Content-Type':'application/json','Origin':f.origin})
        try:
            with urllib.request.urlopen(req,timeout=10) as r:return r.status,dict(r.headers),fixture.jose.loads(r.read())
        except HTTPError as r:return r.code,dict(r.headers),fixture.jose.loads(r.read())
    try:
        with tempfile.TemporaryDirectory(prefix='codi-capacity-http-') as directory:
            f=fixture.Fixture(Path(directory));actor=fixture.Actor(f);other=fixture.Actor(f);body={'key':actor.public,'request_sha256':fixture.jose.digest('Owned challenge saturation')}
            nonces=[]
            for _ in range(8):status,headers,value=request('/rooms/challenge',body);assert status==200;nonces.append(value['nonce'])
            status,headers,value=request('/rooms/challenge',body)
            check('the ninth pending actor nonce is refused with a bounded expiry hint rather than an authorization error',status==429 and int(headers['Retry-After'])==60 and 'Actor room challenge capacity' in value['error'])
            independent=request('/rooms/challenge',{'key':other.public,'request_sha256':body['request_sha256']})
            check('another key remains usable while the first key has eight unspent challenges',independent[0]==200)
            f.clock.value+=60;status,headers,value=request('/rooms/challenge',body)
            check('normal expiry releases the slots without resetting or reusing a nonce',status==200 and value['nonce'] not in nonces)
            f.http.rates['127.0.0.1']=(int(f.clock())-58,600);status,headers,value=request('/rooms/challenge',body)
            check('the existing six-hundred ordinary request ceiling returns the actual remaining window',status==429 and int(headers['Retry-After'])==2 and value['error']=='Room transport-rate limit reached')
            f.clock.value+=2;check('the original rate window expires normally without changing its limit',request('/rooms/challenge',body)[0]==200)
            f.reopen(room_bytes=1024);owner=fixture.Actor(f,'quota_owner');created=owner.operation('create',{'request_id':fixture.secrets.token_urlsafe(32),'label':'Configured small quota'});node=fixture.jose.inspect(created['descriptor'],fixture.POLICY_TYPE)[1]['node_id']
            envelope=owner.envelope('accept',{'node_id':node,'grant':created['grant'],'event':owner.origin(created['grant'],1,'One permitted proposal exceeds this small configured history quota')});status,headers,value=request('/rooms/use',envelope)
            check('a logical history quota has no transient retry hint and does not claim the proposal was saved',status==429 and 'Retry-After' not in headers and 'not saved' in value['error'])
            check('read-only description remains usable after a logical quota refusal',fixture.jose.inspect(owner.operation('describe',{'node_id':node})['head'],fixture.HEAD_TYPE)[1]['count']==0)
            result.update(status='PASS',actorPendingLimit=8,ordinaryPerMinuteLimit=600,simulatedExpirySeconds=62,configuredQuotaForRefusalControl=1024)
    except Exception as error:result.update(error=str(error),traceback=traceback.format_exc())
    finally:
        if f:f.close()
    result.update(sourceSHA256=pins,sourceChangedDuringTest=any(hashlib.sha256(Path(n).read_bytes()).hexdigest()!=p for n,p in pins.items()))
    if result['sourceChangedDuringTest']:result['status']='FAIL'
    return result

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args();assert not a.output.exists();v=run();a.output.write_text(json.dumps(v,indent=2)+'\n');print(json.dumps({'status':v['status'],'checks':len(v['checks']),'error':v.get('error')}));raise SystemExit(0 if v['status']=='PASS' else 1)
