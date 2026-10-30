#!/usr/bin/env python3
"""Atomic authorized public-history sync over real loopback HTTP/SQLite/ES256.

Tests public read, bounded cold/checkpoint/tail paths, authority continuity,
one-use authorizations, independent caller identities and simulated15-day
absence. Not browser/RTC, real15-day wait, deployed backend or8k capacity.
"""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import traceback

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('atomic_sync_fixture',ROOT/'scripts/hosted-room-check.py')
fixture=importlib.util.module_from_spec(spec);spec.loader.exec_module(fixture)
jose=fixture.jose

def run():
    checks=[];f=None;sources=[Path(__file__),ROOT/'scripts/hosted-room-check.py',*sorted((ROOT/'room_service').glob('*.py')),ROOT/'origin_service/room_authority.py']
    pins={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in sources}
    result={'status':'FAIL','scope':__doc__,'checks':checks,'wholeGoalComplete':False}
    def check(name,value):assert value,name;checks.append(name);print(json.dumps({'check':name}),flush=True)
    def sync(actor,after=None,lease=None,tail=False,expected=200):return actor.operation('sync',{'node_id':node,'after':after,'lease':lease,'tail':tail},expected=expected)
    def claims(response):
        assert set(response)=={'version','bootstrap','format','state','continuity'} and response['version']=='codi-hosted-sync/1'
        b=response['bootstrap'];assert set(b)=={'version','descriptor','lease','head'} and b['head']==response['state']['head']
        h=jose.verify(b['head'],f.store.public,fixture.HEAD_TYPE)
        lease=jose.verify(b['lease'],f.store.public,fixture.LEASE_TYPE)
        assert h['node_id']==node and h['lease_revision']==lease['revision'] and h['exp']<=lease['exp']
        assert len(jose.dumps(response).encode())<=131072
        return h,{'index':h['count'],'hash':h['hash']},{'revision':lease['revision'],'hash':fixture.token_id(b['lease'],fixture.LEASE_TYPE)}
    try:
        with tempfile.TemporaryDirectory(prefix='codi-atomic-sync-') as folder:
            f=fixture.Fixture(Path(folder));owner=fixture.Actor(f,'atomic_owner');reader=fixture.Actor(f)
            created=owner.operation('create',{'request_id':fixture.secrets.token_urlsafe(32),'label':'Atomic authorized state'});node=jose.inspect(created['descriptor'],fixture.POLICY_TYPE)[1]['node_id'];grant=created['grant']
            cursors={}
            for sequence in range(1,41):
                receipt=owner.operation('accept',{'node_id':node,'grant':grant,'event':owner.origin(grant,sequence,'Entry '+str(sequence))})['receipt']
                cursors[sequence]={'index':sequence,'hash':fixture.token_id(receipt,fixture.RECEIPT_TYPE)}
            cold=sync(reader);h,floor,lease=claims(cold);state=jose.verify(cold['state']['snapshot'],f.store.public,fixture.SNAPSHOT_TYPE,120000)
            check('anonymous atomic read returns one fresh bootstrap and bounded historical checkpoint without a writing grant',h['count']==40 and cold['format']=='snapshot' and cold['continuity'] is None and state['checkpoint']==floor and len(state['window']['entries'])==32 and state['window']['start']['index']==8 and state['from'] is None and cold['state']['historical'])
            unchanged=sync(reader,floor,lease,True);h,_,_=claims(unchanged)
            check('unchanged verified cursor uses an empty complete tail with the identical signed bootstrap head',unchanged['format']=='tail' and unchanged['state']['entries']==[] and unchanged['state']['next']==floor and unchanged['state']['complete'])
            owner.operation('accept',{'node_id':node,'grant':grant,'event':owner.origin(grant,41,'One new original')})
            tail=sync(reader,floor,lease,True);h,next_floor,next_lease=claims(tail)
            check('one later receipt is returned as one complete tail from the exact retained hash',tail['format']=='tail' and len(tail['state']['entries'])==1 and tail['state']['next']==next_floor and h['count']==41 and jose.verify(tail['state']['entries'][0],f.store.public,fixture.RECEIPT_TYPE)['previous_hash']==floor['hash'])
            old=sync(reader,cursors[1],lease,True);_,_,_=claims(old)
            check('a gap beyond the tail bound fast-forwards through a bounded signed snapshot retaining the requested ancestry',old['format']=='snapshot' and jose.verify(old['state']['snapshot'],f.store.public,fixture.SNAPSHOT_TYPE,120000)['from']==cursors[1])
            bad={'index':floor['index'],'hash':fixture.secrets.token_urlsafe(32)}
            sync(reader,bad,lease,True,409);sync(reader,floor,{'revision':lease['revision'],'hash':fixture.secrets.token_urlsafe(32)},True,409)
            sync(reader,floor,None,True,400);sync(reader,None,None,True,400)
            check('conflicting data/authority cursors and incomplete floor pairs are refused',True)
            envelope=reader.envelope('sync',{'node_id':node,'after':floor,'lease':lease,'tail':True});f.request('/rooms/use',envelope);f.request('/rooms/use',envelope,expected=400)
            check('one-use authorization is still spent by the atomic read',True)
            foreign=owner.operation('create',{'request_id':fixture.secrets.token_urlsafe(32),'label':'Other scope'})
            foreign_lease={'revision':1,'hash':fixture.token_id(foreign['lease'],fixture.LEASE_TYPE)}
            sync(reader,floor,foreign_lease,True,409)
            reader.operation('accept',{'node_id':node,'grant':grant,'event':owner.origin(grant,42,'Forbidden anonymous write')},expected=400)
            check('foreign-room authority and borrowed writing grants confer no permission',jose.inspect(owner.operation('describe',{'node_id':node})['head'],fixture.HEAD_TYPE)[1]['count']==41)
            for _ in range(2):
                f.clock.value+=151;renewed=sync(reader,next_floor,next_lease,True);claims(renewed)
            bridge=sync(reader,next_floor,lease,True);_,_,current_lease=claims(bridge)
            proof=jose.verify(bridge['continuity']['proof'],f.store.public,fixture.LEASE_BRIDGE_TYPE)
            check('multiple authority renewals include the existing signed continuity attestation in the same transaction',current_lease['revision']>=lease['revision']+2 and proof['from']==lease and proof['target']==current_lease and bridge['state']['next']==next_floor)
            f.clock.value+=15*86400;returning=fixture.Actor(f);resumed=sync(returning,next_floor,current_lease,False);h,resumed_floor,_=claims(resumed)
            check('a fresh identity recovers the same accepted history after simulated fifteen days without old live permissions',resumed_floor==next_floor and h['count']==41 and resumed['format']=='snapshot' and 'grant' not in resumed['bootstrap'] and resumed['state']['historical'])
            f.reopen();after_restart=sync(returning,next_floor,current_lease,False);h,_,_=claims(after_restart)
            check('worker reopen preserves accepted history and authority ancestry',h['count']==41)
            fresh_owner=fixture.Actor(f,'atomic_owner',signin=True);large=fresh_owner.operation('create',{'request_id':fixture.secrets.token_urlsafe(32),'label':'Large UTF16 notes'});large_node=jose.inspect(large['descriptor'],fixture.POLICY_TYPE)[1]['node_id']
            empty=returning.operation('sync',{'node_id':large_node,'after':None,'lease':None,'tail':False});empty_head=jose.inspect(empty['bootstrap']['head'],fixture.HEAD_TYPE)[1]
            for seq in range(1,18):fresh_owner.operation('accept',{'node_id':large_node,'grant':large['grant'],'event':fresh_owner.origin(large['grant'],seq,'\U0001f600'*1024)})
            bounded=returning.operation('sync',{'node_id':large_node,'after':{'index':0,'hash':empty_head['hash']},'lease':{'revision':1,'hash':fixture.token_id(empty['bootstrap']['lease'],fixture.LEASE_TYPE)},'tail':True})
            visible=jose.verify(bounded['state']['snapshot'],f.store.public,fixture.SNAPSHOT_TYPE,120000)
            check('byte-heavy complete-tail overflow uses a bounded checkpoint instead of an incomplete atomic response',bounded['format']=='snapshot' and 0<len(visible['window']['entries'])<17 and visible['checkpoint']['index']==17 and len(jose.dumps(bounded).encode())<=131072)
            result.update(status='PASS',simulatedAbsenceDays=15,realLongWait=False,acceptedOriginals=41)
    except Exception as error:result.update(error=str(error),traceback=traceback.format_exc())
    finally:
        if f:f.close()
    result.update(sourceSHA256=pins,sourceChangedDuringTest=any(hashlib.sha256(Path(n).read_bytes()).hexdigest()!=p for n,p in pins.items()))
    if result['sourceChangedDuringTest']:result['status']='FAIL'
    return result

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args();assert not a.output.exists();v=run();a.output.write_text(json.dumps(v,indent=2)+'\n');print(json.dumps({'status':v['status'],'checks':len(v['checks']),'error':v.get('error')}));raise SystemExit(0 if v['status']=='PASS' else 1)
