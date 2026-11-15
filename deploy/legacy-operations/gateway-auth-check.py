#!/usr/bin/env python3
"""Real issuer crypto/SQLite + durable gateway identity and one-use proof tests."""
import concurrent.futures
from dataclasses import replace
import hashlib
import importlib.util
import json
from pathlib import Path
import secrets
import sqlite3
import sys
import time
import unittest

ROOT=Path(__file__).resolve().parent.parent;sys.path.insert(0,str(ROOT))
from origin_service.lifecycle import Service,set_disabled
from origin_service.gateway_authority import GatewayAuthority
from gateway_service.auth import Gatekeeper,AuthorizedUse,initialize_ledger,AUTHORIZE,CHALLENGE,CONFIRMATION_TYPE,USE_TYPE
from gateway_service.policy import Denied
from gateway_service.user_store import UserStore
from codiauth import jose
from codiauth.service import PATHS,PROOF_TYPE
from cryptography.hazmat.primitives.asymmetric import ec
spec=importlib.util.spec_from_file_location('gateway_reference_fixtures',ROOT/'codiserver-server-v0.3.0/tests/test_service.py');reference=importlib.util.module_from_spec(spec);spec.loader.exec_module(reference);reference.Service=Service

class Authorization(unittest.TestCase):
    call=reference.ServiceTests.call;envelope=reference.ServiceTests.envelope;enter=reference.ServiceTests.enter;session_request=reference.ServiceTests.session_request
    def setUp(self):
        reference.ServiceTests.setUp(self);self.addCleanup(self.temp.cleanup)
        self.issuer=self.s;self.s=GatewayAuthority(self.issuer)
        state=self.root/'gateway-state';data=self.root/'gateway-files';state.mkdir(mode=0o700);data.mkdir(mode=0o700)
        self.store=UserStore(state,data,clock=lambda:self.t);initialize_ledger(self.store)
        self.gate=self.gatekeeper();self.raw=jose.dumps({'resource':'my-files','operation':'create','path':'hello.txt','body':'hello'})
    def gatekeeper(self,**kwargs):return Gatekeeper(self.store,self.issuer.config()['identity'],base_path=self.issuer.base_path,clock=lambda:self.t,**kwargs)
    def authorize(self,session,challenge,key=None,authenticated_challenge=False):
        key=key or self.key;path=self.issuer.base_path+AUTHORIZE
        ch=self.call(CHALLENGE,{'key':jose.public_jwk(key),'path':path},headers={'HTTP_AUTHORIZATION':'Codi '+session['session_token']} if authenticated_challenge else None);self.assertEqual(ch['status'],200,ch)
        raw=jose.dumps({'nonce':challenge['nonce'],'request_sha256':challenge['request_sha256']})
        proof={'v':1,'nonce':ch['body']['nonce'],'iss':session['identity']['sid'],'aud':self.config.origin,'method':'POST','path':path,'iat':self.t,'exp':self.t+60,'request_sha256':jose.digest(raw)}
        return self.call(AUTHORIZE,{'request':raw,'proof':jose.sign(proof,key,PROOF_TYPE)},headers={'HTTP_AUTHORIZATION':'Codi '+session['session_token']})
    def use_proof(self,session,confirmation,challenge,key=None,**changes):
        body={'v':1,'iss':session['identity']['sid'],'aud':self.gate.audience,'nonce':challenge['nonce'],'grant_sha256':jose.digest(confirmation),'request_sha256':challenge['request_sha256'],'method':'POST','path':self.gate.use_path,'iat':self.t,'exp':self.t+30,**changes}
        return jose.sign(body,key or self.key,USE_TYPE)
    def grant(self,session=None,key=None,raw=None):
        session=session or self.enter('alice');key=key or self.key;raw=raw or self.raw
        challenge=self.gate.challenge(jose.public_jwk(key),jose.digest(raw));reply=self.authorize(session,challenge,key);self.assertEqual(reply['status'],200,reply)
        token=reply['body']['confirmation'];return session,challenge,token,self.use_proof(session,token,challenge,key)
    def test_registered_identity_unlocks_only_its_own_home(self):
        a,ch,c,p=self.grant();principal,request=self.gate.consume(self.raw,c,p)
        self.assertEqual((principal.sub,principal.sid,principal.kind),(a['identity']['sub'],a['identity']['sid'],'registered'))
        self.store.ensure_user(principal);self.store.put(principal,request['path'],request['body'].encode())
        b=self.enter('bob');_,_,bc,bp=self.grant(b);other,_=self.gate.consume(self.raw,bc,bp);self.store.ensure_user(other)
        with self.assertRaises(FileNotFoundError):self.store.read(other,'hello.txt')
        self.assertEqual(self.store.read(principal,'hello.txt')['bytes'],b'hello')
    def test_other_routes_keep_the_supplied_discovery_application(self):
        seen=[]
        def downstream(env,start):
            seen.append(env['PATH_INFO']);return self.issuer.json_response(start,200,{'discovery':'delegated'})
        self.s=GatewayAuthority(self.issuer,downstream)
        self.assertEqual(self.call('/discovery.json',method='GET')['body'],{'discovery':'delegated'})
        self.assertEqual(seen,['/discovery.json'])
        result=self.call(CHALLENGE,{'key':self.jwk,'path':AUTHORIZE})
        self.assertEqual(result['status'],200);self.assertEqual(seen,['/discovery.json'])
    def test_file_budget_is_bounded_without_spending_login_bootstrap_budget(self):
        self.issuer.c=replace(self.issuer.c,rate_per_minute=3)
        for _ in range(3):self.assertEqual(self.call(CHALLENGE,{'key':self.jwk,'path':AUTHORIZE})['status'],200)
        self.assertEqual(self.call(CHALLENGE,{'key':self.jwk,'path':AUTHORIZE})['status'],429)
        self.assertNotEqual(self.call(AUTHORIZE,{})['status'],429)
        self.assertEqual(self.enter()['identity']['kind'],'anonymous')
    def test_signed_in_accounts_have_separate_bounded_admission(self):
        alice=self.enter('alice');alice2=self.enter('alice');bob=self.enter('bob')
        self.issuer.c=replace(self.issuer.c,rate_per_minute=3)
        def challenge(session):
            return self.call(CHALLENGE,{'key':self.jwk,'path':AUTHORIZE},headers={'HTTP_AUTHORIZATION':'Codi '+session['session_token']})
        for session in (alice,alice2,alice):self.assertEqual(challenge(session)['status'],200)
        self.assertEqual(challenge(alice2)['status'],429,'two sessions share the account budget')
        for _ in range(3):self.assertEqual(challenge(bob)['status'],200,'another account retains its own budget')
        self.assertEqual(challenge(bob)['status'],429)
        self.t+=61
        self.assertEqual(challenge(alice)['status'],200,'budgets expire')

    def test_per_account_authorization_limit_does_not_block_another_account(self):
        alice=self.enter('alice');bob=self.enter('bob')
        self.issuer.c=replace(self.issuer.c,rate_per_minute=3)
        for _ in range(3):
            challenge=self.gate.challenge(self.jwk,jose.digest(self.raw))
            self.assertEqual(self.authorize(alice,challenge,authenticated_challenge=True)['status'],200)
        challenge=self.gate.challenge(self.jwk,jose.digest(self.raw))
        self.assertEqual(self.authorize(bob,challenge,authenticated_challenge=True)['status'],200)
        self.assertEqual(self.issuer.rates['file-authorize-account:'+alice['identity']['sub']][1],3)
        self.assertEqual(self.issuer.rates['file-authorize-account:'+bob['identity']['sub']][1],1)

    def test_hundred_accounts_can_authorize_without_a_shared_proxy_bucket(self):
        # Sequential bounded issuer-only test; this does not test gateway
        # throughput, login bursts, external proxy behavior or 100 browsers.
        accounts=[]
        for i in range(100):
            key=ec.generate_private_key(ec.SECP256R1());accounts.append((self.enter('loaduser'+str(i),key),key))
        self.issuer.c=replace(self.issuer.c,rate_per_minute=6)
        durations=[];start=time.monotonic()
        for account,key in accounts:
            t=time.monotonic();challenge=self.gate.challenge(jose.public_jwk(key),jose.digest(self.raw))
            reply=self.authorize(account,challenge,key,authenticated_challenge=True)
            self.assertEqual(reply['status'],200,reply)
            self.gate.consume(self.raw,reply['body']['confirmation'],self.use_proof(account,reply['body']['confirmation'],challenge,key));durations.append(time.monotonic()-t)
        ordered=sorted(durations)
        print(json.dumps({'scope':'local issuer only; sequential signed requests, not a 100-user capacity test','accounts':100,'authorizationSeconds':round(time.monotonic()-start,3),'p50Milliseconds':round(ordered[49]*1000,2),'p95Milliseconds':round(ordered[94]*1000,2),'maxMilliseconds':round(ordered[-1]*1000,2)}),flush=True)

    def test_invalid_bearer_remains_in_bounded_legacy_budget(self):
        alice=self.enter('alice');self.issuer.c=replace(self.issuer.c,rate_per_minute=2)
        bad={'HTTP_AUTHORIZATION':'Codi '+secrets.token_urlsafe(32)}
        for _ in range(2):self.assertEqual(self.call(CHALLENGE,{'key':self.jwk,'path':AUTHORIZE},headers=bad)['status'],200)
        self.assertEqual(self.call(CHALLENGE,{'key':self.jwk,'path':AUTHORIZE},headers=bad)['status'],429)
        good={'HTTP_AUTHORIZATION':'Codi '+alice['session_token']}
        self.assertEqual(self.call(CHALLENGE,{'key':self.jwk,'path':AUTHORIZE},headers=good)['status'],200)

    def test_account_admission_never_replaces_signed_authorization(self):
        alice=self.enter('alice');other=ec.generate_private_key(ec.SECP256R1())
        challenge=self.call(CHALLENGE,{'key':jose.public_jwk(other),'path':AUTHORIZE},headers={'HTTP_AUTHORIZATION':'Codi '+alice['session_token']})
        self.assertEqual(challenge['status'],200)
        raw=jose.dumps({'nonce':secrets.token_urlsafe(32),'request_sha256':jose.digest(self.raw)})
        proof={'v':1,'nonce':challenge['body']['nonce'],'iss':alice['identity']['sid'],'aud':self.config.origin,'method':'POST','path':AUTHORIZE,'iat':self.t,'exp':self.t+60,'request_sha256':jose.digest(raw)}
        result=self.call(AUTHORIZE,{'request':raw,'proof':jose.sign(proof,other,PROOF_TYPE)},headers={'HTTP_AUTHORIZATION':'Codi '+alice['session_token']})
        self.assertEqual(result['status'],401,'a session token alone cannot authorize a different key')

    def test_global_file_admission_limit_remains_bounded(self):
        alice=self.enter('alice');self.issuer.c=replace(self.issuer.c,rate_per_minute=2)
        self.issuer.rates['file-challenge-global']=(self.t,40)
        result=self.call(CHALLENGE,{'key':self.jwk,'path':AUTHORIZE},headers={'HTTP_AUTHORIZATION':'Codi '+alice['session_token']})
        self.assertEqual(result['status'],429)

    def test_anonymous_certificate_gets_no_confirmation_or_folder(self):
        a=self.enter();challenge=self.gate.challenge(self.jwk,jose.digest(self.raw));self.assertEqual(self.authorize(a,challenge)['status'],403)
        self.assertEqual(list(self.store.users_path.iterdir()),[])
    def test_disabled_account_blocks_new_confirmation(self):
        a,ch,c,p=self.grant();set_disabled(self.config.state_dir,'alice',True)
        challenge=self.gate.challenge(self.jwk,jose.digest(self.raw));self.assertEqual(self.authorize(a,challenge)['status'],401)
        # A previously authorized exact operation is bounded by its 30s grant.
        principal,_=self.gate.consume(self.raw,c,p);self.assertEqual(principal.sub,a['identity']['sub'])
    def test_reenable_does_not_revive_old_session(self):
        a=self.enter('alice');set_disabled(self.config.state_dir,'alice',True);set_disabled(self.config.state_dir,'alice',False)
        ch=self.gate.challenge(self.jwk,jose.digest(self.raw));self.assertEqual(self.authorize(a,ch)['status'],401)
        self.grant(self.enter('alice'))
    def test_logout_blocks_new_confirmation(self):
        a=self.enter('alice');self.assertEqual(self.session_request('/api/v1/logout',a)['status'],200)
        ch=self.gate.challenge(self.jwk,jose.digest(self.raw));self.assertEqual(self.authorize(a,ch)['status'],401)
    def test_expired_session_blocks_confirmation(self):
        a=self.enter('alice');self.t+=self.config.session_seconds+1
        ch=self.gate.challenge(self.jwk,jose.digest(self.raw));self.assertEqual(self.authorize(a,ch)['status'],401)
    def test_unknown_bearer_is_not_identity(self):
        a=self.enter('alice');a['session_token']=secrets.token_urlsafe(32)
        ch=self.gate.challenge(self.jwk,jose.digest(self.raw));self.assertEqual(self.authorize(a,ch)['status'],401)
    def test_issuer_restart_restores_registered_session_but_not_other_key(self):
        a=self.enter('alice');self.issuer=Service(self.config,clock=lambda:self.t);self.s=GatewayAuthority(self.issuer)
        ch=self.gate.challenge(self.jwk,jose.digest(self.raw));self.assertEqual(self.authorize(a,ch)['status'],200)
        ch=self.gate.challenge(self.jwk,jose.digest(self.raw));self.assertEqual(self.authorize(a,ch,ec.generate_private_key(ec.SECP256R1()))['status'],401)
    def test_gateway_restart_preserves_pending_challenge(self):
        _,_,c,p=self.grant();self.assertEqual(self.gatekeeper().consume(self.raw,c,p)[0].kind,'registered')
    def test_replay_refused_across_restart(self):
        _,_,c,p=self.grant();self.gate.consume(self.raw,c,p)
        with self.assertRaises(Denied):self.gatekeeper().consume(self.raw,c,p)
    def test_two_concurrent_consumers_have_one_winner(self):
        _,_,c,p=self.grant()
        def consume(_):
            try:self.gate.consume(self.raw,c,p);return True
            except Denied:return False
        with concurrent.futures.ThreadPoolExecutor(2) as pool:self.assertEqual(sorted(pool.map(consume,range(2))),[False,True])
    def test_tampered_request_refused_without_spending_original(self):
        _,_,c,p=self.grant()
        with self.assertRaises(Denied):self.gate.consume(self.raw+' ',c,p)
        self.gate.consume(self.raw,c,p)
    def test_stolen_confirmation_needs_original_client_key(self):
        a,ch,c,p=self.grant();attacker=ec.generate_private_key(ec.SECP256R1())
        with self.assertRaises(ValueError):self.gate.consume(self.raw,c,self.use_proof(a,c,ch,key=attacker))
        self.gate.consume(self.raw,c,p)
    def test_untrusted_issuer_signature_and_kid_refused(self):
        _,_,c,p=self.grant();claims=jose.inspect(c,CONFIRMATION_TYPE)[1];attacker=ec.generate_private_key(ec.SECP256R1())
        for kid in [self.issuer.kid,'unknown']:
            fake=jose.sign(claims,attacker,CONFIRMATION_TYPE,kid)
            with self.assertRaises(ValueError):self.gate.consume(self.raw,fake,p)
    def test_client_context_and_algorithm_type_confusion_refused(self):
        a,ch,c,p=self.grant()
        for change in [{'iss':'other'},{'aud':'https://other.invalid/gateway'},{'path':'/gateway/use/other'},{'method':'GET'},{'nonce':secrets.token_urlsafe(32)},{'grant_sha256':jose.digest('other')},{'request_sha256':jose.digest('other')},{'v':True}]:
            with self.subTest(change=change),self.assertRaises(ValueError):self.gate.consume(self.raw,c,self.use_proof(a,c,ch,**change))
        claims=jose.inspect(p,USE_TYPE)[1]
        with self.assertRaises(ValueError):self.gate.consume(self.raw,c,jose.sign(claims,self.key,CONFIRMATION_TYPE))
        self.gate.consume(self.raw,c,p)
    def test_issuer_context_lifetime_and_anonymous_claims_refused(self):
        a,ch,c,p=self.grant();original=jose.inspect(c,CONFIRMATION_TYPE)[1]
        for change in [{'iss':'https://other.invalid'},{'aud':self.gate.audience+'/other'},{'session_deadline':self.t+1},{'exp':self.t+31},{'kind':'anonymous'},{'sub':'root'},{'v':True}]:
            claims={**original,**change};fake=jose.sign(claims,self.issuer.key,CONFIRMATION_TYPE,self.issuer.kid)
            with self.subTest(change=change),self.assertRaises(ValueError):self.gate.consume(self.raw,fake,self.use_proof(a,fake,ch))
        self.gate.consume(self.raw,c,p)
    def test_confirmation_expiry_and_store_deadline(self):
        _,_,c,p=self.grant();principal,_=self.gate.consume(self.raw,c,p);self.store.ensure_user(principal)
        self.t+=31
        with self.assertRaises(Denied):self.gate.consume(self.raw,c,p)
        with self.assertRaises(Denied):self.store.put(principal,'expired',b'bad')
    def test_admitted_upload_can_finish_after_grant_expiry_but_not_operation_deadline(self):
        _,_,c,p=self.grant();use=self.gate.begin(c,p,seconds=120)
        self.assertEqual(use.principal.deadline,self.t+120)
        self.store.ensure_user(use.principal);self.t+=31
        self.assertEqual(use.decode(self.raw.encode())['path'],'hello.txt')
        self.store.put(use.principal,'finished',b'valid admitted upload')
        with self.assertRaises(Denied):self.gate.consume(self.raw,c,p)
        self.t+=90
        with self.assertRaises(Denied):self.store.put(use.principal,'late',b'too late')
    def test_authorized_request_rejects_utf16_and_utf8_bom(self):
        for raw in ['{"name":"test"}'.encode('utf-16'),b'\xef\xbb\xbf{"name":"test"}']:
            use=AuthorizedUse(None,jose.b64(hashlib.sha256(raw).digest()))
            with self.assertRaises(Denied):use.decode(raw)
        raw='{"name":"café"}'.encode('utf-8')
        use=AuthorizedUse(None,jose.b64(hashlib.sha256(raw).digest()))
        self.assertEqual(use.decode(raw)['name'],'café')

    def test_admission_does_not_authorize_different_upload_bytes(self):
        _,_,c,p=self.grant();use=self.gate.begin(c,p)
        with self.assertRaises(Denied):use.decode((self.raw+' ').encode())
        with self.assertRaises(Denied):self.gate.begin(c,p)
    def test_confirmation_cannot_outlive_session(self):
        self.issuer.c=replace(self.issuer.c,session_seconds=12)
        _,_,c,_=self.grant();claims=jose.inspect(c,CONFIRMATION_TYPE)[1]
        self.assertEqual(claims['exp'],self.t+12);self.assertEqual(claims['session_deadline'],self.t+12)
    def test_challenge_capacity_is_bounded_and_expires(self):
        gate=self.gatekeeper(capacity=1);gate.challenge(self.jwk,jose.digest(self.raw))
        with self.assertRaises(Denied):gate.challenge(self.jwk,jose.digest(self.raw))
        self.t+=61;gate.challenge(self.jwk,jose.digest(self.raw))
    def test_gateway_proof_nonce_requires_the_bound_key(self):
        a=self.enter('alice');other=ec.generate_private_key(ec.SECP256R1());ch=self.gate.challenge(jose.public_jwk(other),jose.digest(self.raw));reply=self.authorize(a,ch);self.assertEqual(reply['status'],200)
        c=reply['body']['confirmation']
        with self.assertRaises(Denied):self.gate.consume(self.raw,c,self.use_proof(a,c,ch))
    def test_middleware_preserves_reference_routes_and_global_paths(self):
        before=PATHS.copy();self.grant();self.assertEqual(PATHS,before)
        self.assertEqual(self.call('/config.json',method='GET')['status'],200)
        self.assertEqual(self.call('/api/v1/gateway/unknown',{})['status'],404)
    def test_transport_origin_host_method_and_size(self):
        for headers in [{'HTTP_ORIGIN':'https://evil.invalid'},{'HTTP_HOST':'evil.invalid'},{'HTTP_ORIGIN':''}]:self.assertEqual(self.call(CHALLENGE,{},headers=headers)['status'],403)
        self.assertEqual(self.call(CHALLENGE,{},method='GET')['status'],405)
        self.assertEqual(self.call(CHALLENGE,{},headers={'CONTENT_TYPE':'text/plain'})['status'],415)
        self.assertEqual(self.call(CHALLENGE,{},headers={'CONTENT_LENGTH':'20000'})['status'],413)
    def test_explicit_schema_migration_preserves_existing_accounts_files_and_acl(self):
        _,_,c,p=self.grant();principal,_=self.gate.consume(self.raw,c,p);self.store.ensure_user(principal);self.store.put(principal,'retained',b'retain')
        initialize_ledger(self.store)
        self.assertEqual(self.store.read(principal,'retained')['bytes'],b'retain')
        with self.store.db() as db:self.assertEqual(db.execute('SELECT count(*) FROM permissions').fetchone()[0],7);db.execute('DROP TABLE gateway_used_grants')
        with self.assertRaises((ValueError,sqlite3.DatabaseError)):initialize_ledger(self.store)
        self.assertEqual(self.store.read(principal,'retained')['bytes'],b'retain')
    def test_mounted_context_cannot_be_reused_at_root(self):
        # Ordinary fixture envelopes use root paths, so create the session first
        # under the reference root context and then test the mounted grant route.
        a=self.enter('alice')
        self.issuer.base_path='/hidden';self.s=GatewayAuthority(self.issuer);self.gate=self.gatekeeper()
        _,_,c,p=self.grant(a);self.gate.consume(self.raw,c,p)
        root_gate=Gatekeeper(self.store,self.issuer.config()['identity'],clock=lambda:self.t)
        with self.assertRaises(Denied):root_gate.consume(self.raw,c,p)

if __name__=='__main__':
    result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(Authorization))
    report={'status':'PASS' if result.wasSuccessful() else 'FAIL','tests':result.testsRun,'failures':len(result.failures),'errors':len(result.errors),
            'scope':'Local real issuer WSGI/ES256/SQLite and durable gateway proofs, file isolation, process-object restart and concurrent replay tests; no public API or deployment',
            'sha256':{name:hashlib.sha256((ROOT/name).read_bytes()).hexdigest() for name in ['gateway_service/auth.py','origin_service/gateway_authority.py','origin_service/lifecycle.py','gateway_service/user_store.py','scripts/gateway-auth-check.py']}}
    output=ROOT/'.build/checks/gateway-auth-result.json'
    if output.exists() and json.loads(output.read_text()).get('status')=='FAIL':output.rename(output.with_name('gateway-auth-before-'+str(time.time_ns())+'.json'))
    output.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2));raise SystemExit(0 if result.wasSuccessful() else 1)
