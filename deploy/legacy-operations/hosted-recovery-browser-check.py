#!/usr/bin/env python3
"""Real Chrome verifies new recovered receipts and controller-signed bad branches.

Every adversarial receipt has a matching freshly signed head, so a rejection
cannot be credited merely to an outer hash mismatch. Local HTTP/SQLite and real
WebCrypto; simulated time, no live messages/moves, v86, public or8k claim.
"""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import tempfile
import traceback

ROOT=Path(__file__).resolve().parents[1]
def module(name,path):
    s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
fixture=module('recovery_browser_http',ROOT/'scripts/hosted-room-check.py');driver=module('recovery_browser_driver',ROOT/'scripts/touch-preview-check.py')


def run(legacy):
    checks=[];sid=None;f=None;sources=[Path(__file__),*sorted((ROOT/'network').glob('*.mjs')),*sorted((ROOT/'room_service').glob('*.py'))]
    pins={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in sources};result={'status':'FAIL','scope':__doc__,'checks':checks,'actualBrowserInstances':1,'actualV86Desktops':0,'wholeGoalComplete':False}
    def js(code,args=[]):return driver.call('/session/'+sid+'/execute/sync',{'script':code,'args':args})
    def task(code,args=[]):
        r=driver.call('/session/'+sid+'/execute/async',{'script':'const params=Array.from(arguments),done=params.pop();(async()=>{'+code+'})().then(value=>done({ok:true,value}),error=>done({ok:false,error:error.stack}));','args':args});assert r['ok'],r;return r.get('value')
    def check(name,ok):assert ok,name;checks.append(name);print(json.dumps({'check':name}),flush=True)
    def inspect(token,kind):return fixture.jose.inspect(token,kind)[1]
    def token_id(token,kind):return fixture.token_id(token,kind)
    try:
        with tempfile.TemporaryDirectory(prefix='codi-recovery-browser-') as temp:
            folder=Path(temp);f=fixture.Fixture(folder);owner=fixture.Actor(f,'recovery_browser_owner');other=fixture.Actor(f,'recovery_browser_other')
            boot=owner.operation('create',{'request_id':fixture.secrets.token_urlsafe(32),'label':'Recovered original browser check'});node=inspect(boot['descriptor'],fixture.POLICY_TYPE)['node_id'];grant=boot['grant'];original=owner.origin(grant,1,'Original signed branch survives fifteen days')
            puzzle=other.operation('join_challenge',{'node_id':node});joined=other.operation('join',{'node_id':node,'proof':fixture.solve(puzzle['challenge'])})['grant'];normal=other.operation('accept',{'node_id':node,'grant':joined,'event':other.origin(joined,1,'Normal accepted first record')})['receipt']
            f.clock.value+=15*86400;fresh=fixture.Actor(f,'recovery_browser_owner',signin=True);alien=fixture.Actor(f,'recovery_browser_other',signin=True);boot=fresh.operation('describe',{'node_id':node});h=inspect(boot['head'],fixture.HEAD_TYPE);now=int(f.clock())
            proof={'version':fixture.RECOVERY_VERSION,'node_id':node,'descriptor_hash':fixture.token_id(boot['descriptor'],fixture.POLICY_TYPE),'event_id':token_id(original,fixture.ORIGIN_TYPE),'grant_hash':token_id(grant,fixture.MEMBER_TYPE),'requester_session_id':fresh.sid,'base':{'index':h['count'],'hash':h['hash']},'iat':now,'exp':now+25}
            accepted=fresh.operation('recover',{'node_id':node,'grant':grant,'event':original,'reauthorization':fixture.jose.sign(proof,fresh.key,fixture.REAUTHORIZE_TYPE)})
            boot=fresh.operation('describe',{'node_id':node});record=inspect(accepted['receipt'],fixture.RECEIPT_TYPE)
            def packet(r):
                token=fixture.jose.sign(r,f.store.key,fixture.RECEIPT_TYPE);p=inspect(boot['head'],fixture.HEAD_TYPE);p['hash']=token_id(token,fixture.RECEIPT_TYPE)
                return {'bootstrap':{**boot,'head':fixture.jose.sign(p,f.store.key,fixture.HEAD_TYPE)},'receipt':token,'after':{'index':r['index']-1,'hash':r['previous_hash']},'now':now}
            good=packet(record);bad=[]
            def adversary(name,change,*,signer=fresh):
                r=fixture.jose.loads(fixture.jose.dumps(record));change(r)
                if r.get('recovery') and isinstance(r['recovery'].get('proof'),dict):r['recovery']['proof']=fixture.jose.sign(r['recovery']['proof'],signer.key,fixture.REAUTHORIZE_TYPE)
                bad.append({'name':name,**packet(r)})
            def consent(r):r['recovery']['proof']=dict(proof);return r['recovery']['proof']
            adversary('no recovery evidence',lambda r:r.pop('recovery'))
            def foreign(r):r['recovery']['requester']=fixture.binding(alien.identity);consent(r)['requester_session_id']=alien.sid
            adversary('another registered account',foreign,signer=alien)
            def expired(r):p=consent(r);p['iat']=now-25;p['exp']=now-1
            adversary('expired fresh consent',expired)
            def wrong_base(r):consent(r)['base']={'index':1,'hash':fixture.secrets.token_urlsafe(32)}
            adversary('wrong accepted predecessor',wrong_base)
            def wrong_id(r):consent(r)['event_id']=fixture.secrets.token_urlsafe(32)
            adversary('substituted original ID',wrong_id)
            def wrong_role(r):
                p=inspect(grant,fixture.MEMBER_TYPE);p['role']='chess';r['recovery']['grant']=fixture.jose.sign(p,f.store.key,fixture.MEMBER_TYPE);consent(r)['grant_hash']=token_id(r['recovery']['grant'],fixture.MEMBER_TYPE)
            adversary('controller-signed foreign lane grant',wrong_role)
            def forged(r):
                parts=r['event'].split('.');parts[2]=('A' if parts[2][0]!='A' else 'B')+parts[2][1:];r['event']='.'.join(parts)
            adversary('invalid original signature',forged)
            normal_payload=inspect(normal,fixture.RECEIPT_TYPE);normal_chunk={'entries':[normal],'next':{'index':1,'hash':token_id(normal,fixture.RECEIPT_TYPE)},'complete':False,'head':boot['head'],'historical':True}
            data={'key':f.store.public,'policy':f.policy,'good':good,'bad':bad,'normal':normal_chunk,'proposal':{'version':'codi-hosted-proposal/1','node_id':node,'event':original,'grant':grant}}
            public=folder/'public';shutil.copytree(ROOT/'network',public/'network',ignore=shutil.ignore_patterns('*.md'));shutil.copytree(legacy,public/'legacy',ignore=shutil.ignore_patterns('*.md'))
            (public/'index.html').write_text('<!doctype html><title>Recovered original verifier</title>');(public/'fixture.json').write_text(json.dumps(data))
            sid=driver.call('/session',{'capabilities':{'alwaysMatch':{'browserName':'chrome','goog:chromeOptions':{'binary':'/snap/chromium/current/usr/lib/chromium-browser/chrome','args':['--headless=new','--no-sandbox','--disable-dev-shm-usage']}}}})['sessionId'];driver.call('/session/'+sid+'/timeouts',{'script':120000});driver.call('/session/'+sid+'/url',{'url':f.origin+'/'})
            observed=task("""window.d=await(await fetch('/fixture.json')).json();window.v=await import('/network/hosted-room-authority.mjs');window.room=await v.verifyHostedRoom(d.good.bootstrap,d.key,d.policy,{now:d.good.now});const p=await v.verifyHostedProposal(d.proposal,room,{now:d.good.now,requireExpired:true});const chunk={entries:[d.good.receipt],next:{index:room.head.count,hash:room.head.hash},complete:true,head:d.good.bootstrap.head,historical:true};window.verified=await v.verifyHostedChunk(chunk,room,{after:d.good.after,now:d.good.now});return {eventId:p.eventId,records:verified.records};""")
            check('actual WebCrypto verifies the original historical grant/signature and fresh recovery receipt after fifteen simulated days',observed['records'][0]['recovered'] and observed['records'][0]['eventId']==observed['eventId']==proof['event_id'] and observed['records'][0]['text']=='Original signed branch survives fifteen days' and observed['records'][0]['author']['sid']==owner.sid)
            rejected=task("""const out=[];for(const b of d.bad){const room=await v.verifyHostedRoom(b.bootstrap,d.key,d.policy,{now:b.now});const chunk={entries:[b.receipt],next:{index:room.head.count,hash:room.head.hash},complete:true,head:b.bootstrap.head,historical:true};try{await v.verifyHostedChunk(chunk,room,{after:b.after,now:b.now});out.push({name:b.name,rejected:false});}catch(error){out.push({name:b.name,rejected:true,error:error.message});}}return out;""")
            result['adversarialBranches']=rejected
            for item in rejected:check('matching signed head does not rescue '+item['name'],item['rejected'])
            check('the same verifier retains ordinary accepted history as historical records without recovery metadata',task("const x=await v.verifyHostedChunk(d.normal,room,{now:d.good.now});return x.records.length===1&&!x.records[0].recovered&&x.records[0].historical;"))
            legacy_control=task("const old=await import('/legacy/hosted-room-authority.mjs'),r=await old.verifyHostedRoom(d.good.bootstrap,d.key,d.policy,{now:d.good.now});await old.verifyHostedChunk(d.normal,r,{now:d.good.now});try{await old.verifyHostedChunk({entries:[d.good.receipt],next:{index:r.head.count,hash:r.head.hash},complete:true,head:d.good.bootstrap.head,historical:true},r,{after:d.good.after,now:d.good.now});return false;}catch{return true;}")
            check('published legacy verifier remains valid for old records but fails closed on new recovery evidence',legacy_control)
            check('archive verification does not dispatch chat, chess or a live operation',js('return verified.historical&&verified.records.every(r=>r.historical)&&!window.client&&!window.pool;'))
            result.update(status='PASS',legacyMigrationRequired=True,originalID=proof['event_id'],simulatedAbsenceDays=15)
    except Exception as error:result.update(error=str(error),traceback=traceback.format_exc())
    finally:
        if sid:driver.call('/session/'+sid,method='DELETE');result['ownedBrowserContextsClosed']=1
        if f:f.close()
    result.update(sourceSHA256=pins,sourceChangedDuringTest=any(hashlib.sha256(Path(p).read_bytes()).hexdigest()!=h for p,h in pins.items()))
    if result['sourceChangedDuringTest']:result['status']='FAIL'
    return result


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--legacy-network',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();assert not a.output.exists();v=run(a.legacy_network.resolve());a.output.write_text(json.dumps(v,indent=2)+'\n');print(json.dumps({'status':v['status'],'checks':len(v['checks']),'error':v.get('error')}));raise SystemExit(0 if v['status']=='PASS' else 1)
