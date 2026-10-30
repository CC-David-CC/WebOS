#!/usr/bin/env python3
"""Real HTTP/signatures/SQLite reauthorization of original missed chat proposals.

Fresh consent extends the current chosen-controller head without replacing the
old event ID/signature or erasing its author sequence. Simulated fifteen days,
not independent replica consensus, durable chess, public deployment or8k proof.
"""
import argparse
from concurrent.futures import ThreadPoolExecutor
import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import traceback

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('recovery_http_fixture',ROOT/'scripts/hosted-room-check.py');fmod=importlib.util.module_from_spec(spec);spec.loader.exec_module(fmod)


def run():
    checks=[];f=None;sources=[Path(__file__),ROOT/'scripts/hosted-room-check.py',*sorted((ROOT/'room_service').glob('*.py'))]
    pins={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in sources}
    result={'status':'FAIL','scope':__doc__,'checks':checks,'wholeGoalComplete':False}
    def check(name,condition):assert condition,name;checks.append(name);print(json.dumps({'check':name}),flush=True)
    def payload(token,kind):return fmod.jose.inspect(token,kind)[1]
    def event_id(event):return fmod.token_id(event,fmod.ORIGIN_TYPE,16384)
    def head(actor,node):return payload(actor.operation('describe',{'node_id':node})['head'],fmod.HEAD_TYPE)
    def proposal(actor,grant,sequence,text):return actor.origin(grant,sequence,text,changes={'iat':created_at,'exp':created_at+60})
    def arguments(actor,grant,event,base,*,proof_changes=None):
        p={'version':fmod.RECOVERY_VERSION,'node_id':node,'descriptor_hash':descriptor,'event_id':event_id(event),'grant_hash':fmod.token_id(grant,fmod.MEMBER_TYPE,8192),'requester_session_id':actor.sid,'base':{'index':base['count'],'hash':base['hash']},'iat':int(f.clock()),'exp':int(f.clock())+25}
        if proof_changes:p.update(proof_changes)
        return {'node_id':node,'grant':grant,'event':event,'reauthorization':fmod.jose.sign(p,actor.key,fmod.REAUTHORIZE_TYPE)}
    def flip(token):
        parts=token.split('.');parts[2]=('A' if parts[2][0]!='A' else 'B')+parts[2][1:];return '.'.join(parts)
    try:
        with tempfile.TemporaryDirectory(prefix='codi-recovery-') as temporary:
            f=fmod.Fixture(Path(temporary));a=fmod.Actor(f,'original_owner');b=fmod.Actor(f,'original_member')
            recover=f.store._recover
            def observed_recovery(*args,**kw):
                try:return recover(*args,**kw)
                except Exception as error:result['lastServerRefusal']=str(error);raise
            f.store._recover=observed_recovery
            created=a.operation('create',{'request_id':fmod.secrets.token_urlsafe(32),'label':'Original missed operations'});policy=payload(created['descriptor'],fmod.POLICY_TYPE);node=policy['node_id'];descriptor=fmod.token_id(created['descriptor'],fmod.POLICY_TYPE);grant=created['grant'];created_at=int(f.clock())
            original=proposal(a,grant,1,'Original branch message');child=proposal(a,grant,2,'Original dependent child');long=proposal(a,grant,3,'Original after long absence');initial=head(a,node)
            a.operation('recover',arguments(a,grant,original,initial),expected=400)
            check('a live ordinary proposal cannot bypass accept through the recovery path',head(a,node)['count']==0)
            work=b.operation('join_challenge',{'node_id':node});member=b.operation('join',{'node_id':node,'proof':fmod.solve(work['challenge'])})['grant'];member_child=proposal(b,member,2,'Member missed branch')
            accepted=b.operation('accept',{'node_id':node,'grant':member,'event':proposal(b,member,1,'Winning accepted branch')});f.clock.value+=61
            a.operation('recover',arguments(a,grant,original,initial),expected=409)
            check('an old accepted head cannot authorize inserting a missed proposal at a different head',head(a,node)['count']==1)
            restored=a.operation('recover',arguments(a,grant,original,head(a,node)));r=payload(restored['receipt'],fmod.RECEIPT_TYPE)
            check('a valid missed message appends to the winning current branch with its exact original ID and signature',r['index']==2 and r['event']==original and r['event_id']==event_id(original) and r['previous_hash']==fmod.token_id(accepted['receipt'],fmod.RECEIPT_TYPE) and r['accepted_at']>payload(original,fmod.ORIGIN_TYPE)['exp'] and r['recovery']['grant']==grant)
            duplicate=a.operation('recover',arguments(a,grant,original,head(a,node)))
            check('fresh reauthorization of an already accepted original returns exactly the prior receipt once',duplicate['duplicate'] and duplicate['receipt']==restored['receipt'] and head(a,node)['count']==2)
            gap=proposal(a,grant,4,'Missing dependencies');fork=proposal(a,grant,1,'Conflicting old author sequence')
            a.operation('recover',arguments(a,grant,gap,head(a,node)),expected=409);a.operation('recover',arguments(a,grant,fork,head(a,node)),expected=409)
            check('sequence gaps and conflicting same-sequence branches remain rejected without erasing the original floor',head(a,node)['count']==2)
            # Fresh sessions keep negative-case nonce accounting independent;
            # the real eight-unspent-challenge bound is never raised/reset.
            fresh=fmod.Actor(f,'original_owner',signin=True)
            wrong=b
            wrong.operation('recover',arguments(wrong,grant,child,head(wrong,node)),expected=400)
            bad=arguments(fresh,grant,child,head(fresh,node));bad['event']=flip(child);fresh.operation('recover',bad,expected=400)
            bad=arguments(fresh,grant,child,head(fresh,node));bad['grant']=flip(grant);fresh.operation('recover',bad,expected=400)
            bad=arguments(fresh,grant,child,head(fresh,node));bad['reauthorization']=flip(bad['reauthorization']);fresh.operation('recover',bad,expected=400)
            check('another member, tampered origin, tampered old grant and forged fresh consent cannot recover the branch',head(fresh,node)['count']==2)
            fresh2=fmod.Actor(f,'original_owner',signin=True)
            chess=proposal(a,grant,2,'Wrong lane');p=payload(chess,fmod.ORIGIN_TYPE);p['lane']='chess';chess=fmod.jose.sign(p,a.key,fmod.ORIGIN_TYPE)
            fresh2.operation('recover',arguments(fresh2,grant,chess,head(fresh2,node)),expected=400)
            bad=arguments(fresh2,grant,child,head(fresh2,node),proof_changes={'base':None});fresh2.operation('recover',bad,expected=400)
            bad=arguments(fresh2,grant,child,head(fresh2,node),proof_changes={'event_id':fmod.secrets.token_urlsafe(32)});fresh2.operation('recover',bad,expected=400)
            bad=arguments(fresh2,grant,child,head(fresh2,node),proof_changes={'iat':int(f.clock())-31,'exp':int(f.clock())-1});fresh2.operation('recover',bad,expected=400)
            check('foreign lanes, omitted heads, substituted IDs and expired consent are always refused',head(fresh2,node)['count']==2)
            one=fmod.Actor(f,'original_owner',signin=True);two=fmod.Actor(f,'original_owner',signin=True);base=head(one,node)
            envelopes=[actor.envelope('recover',arguments(actor,grant,child,base)) for actor in [one,two]]
            with ThreadPoolExecutor(max_workers=2) as pool:concurrent=list(pool.map(lambda envelope:f.request('/rooms/use',envelope),envelopes))
            child_receipt=concurrent[0]['receipt'];c=payload(child_receipt,fmod.RECEIPT_TYPE)
            check('two fresh sessions of the same registered account race without duplicating or re-signing the original',concurrent[0]['receipt']==concurrent[1]['receipt'] and sorted(v['duplicate'] for v in concurrent)==[False,True] and c['author']['sid']==a.sid and c['event']==child and c['recovery']['requester']['sid'] in [one.sid,two.sid] and head(one,node)['count']==3)
            one.operation('set_member',{'node_id':node,'subject':b.identity['sub'],'allowed':False})
            b.operation('recover',arguments(b,member,member_child,head(b,node)),expected=400)
            check('a formerly valid signed branch cannot override current revoked membership',head(one,node)['count']==3)
            one.operation('set_member',{'node_id':node,'subject':b.identity['sub'],'allowed':True})
            resumed=b.operation('recover',arguments(b,member,member_child,head(b,node)))
            check('explicit permission restoration allows fresh consent without replacing the old signed event',payload(resumed['receipt'],fmod.RECEIPT_TYPE)['event']==member_child and head(one,node)['count']==4)
            f.clock.value+=15*86400;f.reopen();returned=fmod.Actor(f,'original_owner',signin=True)
            returned.operation('accept',{'node_id':node,'grant':grant,'event':long},expected=400)
            recovered=returned.operation('recover',arguments(returned,grant,long,head(returned,node)));last=payload(recovered['receipt'],fmod.RECEIPT_TYPE)
            check('a returning account after simulated fifteen days uses fresh issuer consent while keeping the original old-session proposal',last['event']==long and last['author']['sid']==a.sid and last['recovery']['requester']['sid']==returned.sid and last['recovery']['requester']['sub']==a.identity['sub'] and last['accepted_at']-created_at>=15*86400 and head(returned,node)['count']==5)
            f.reopen();lookup=returned.operation('lookup',{'node_id':node,'event_id':event_id(long)})
            with f.store.lock(),f.store.db() as db:
                counts=db.execute('SELECT count(*) FROM events WHERE node=?',(node,)).fetchone()[0];highest=db.execute('SELECT highest FROM streams WHERE node=? AND sid=?',(node,a.sid)).fetchone()[0]
            check('worker reopen preserves recovered receipts, exact original author sequence and accepted head',lookup['receipt']==recovered['receipt'] and counts==5 and highest==3)
            result.update(status='PASS',acceptedMessages=counts,originalAuthorSequence=highest,simulatedAbsenceDays=15,originalNode=node,originalDescriptor=created['descriptor'],originalEvent=long,originalGrant=grant,finalReceipt=recovered['receipt'],finalBootstrap=returned.operation('describe',{'node_id':node}),policy=f.policy,controllerKey=f.store.public,now=int(f.clock()))
    except Exception as error:result.update(error=str(error),traceback=traceback.format_exc())
    finally:
        if f:f.close()
    result.update(sourceSHA256=pins,sourceChangedDuringTest=any(hashlib.sha256(Path(p).read_bytes()).hexdigest()!=h for p,h in pins.items()))
    if result['sourceChangedDuringTest']:result['status']='FAIL'
    return result


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args();assert not a.output.exists();v=run();a.output.write_text(json.dumps(v,indent=2)+'\n');print(json.dumps({'status':v['status'],'checks':len(v['checks']),'error':v.get('error')}));raise SystemExit(0 if v['status']=='PASS' else 1)
