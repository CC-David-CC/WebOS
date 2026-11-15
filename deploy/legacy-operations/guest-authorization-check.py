#!/usr/bin/env python3
"""Real issuer/ES256/SQLite checks for guest-wire authorization and separation."""
from dataclasses import replace
import concurrent.futures
import hashlib
import importlib.util
import json
from pathlib import Path
import secrets
import sys
import time
import unittest
from cryptography.hazmat.primitives.asymmetric import ec

ROOT=Path(__file__).resolve().parent.parent;sys.path.insert(0,str(ROOT))
from origin_service.lifecycle import Service,set_disabled
from origin_service.guest_authority import GuestAuthority
from origin_service.gateway_authority import GatewayAuthority
from guest_service.authorization import AUTHORIZE,CHALLENGE,GRANT_TYPE,PROOF_TYPE,WireAuthorization
from codiauth.service import PATHS,PROOF_TYPE as REQUEST_TYPE
from codiauth import jose
spec=importlib.util.spec_from_file_location('guest_authority_fixture',ROOT/'codiserver-server-v0.3.0/tests/test_service.py');ref=importlib.util.module_from_spec(spec);spec.loader.exec_module(ref);ref.Service=Service

class Authorization(unittest.TestCase):
    call=ref.ServiceTests.call;envelope=ref.ServiceTests.envelope;enter=ref.ServiceTests.enter;session_request=ref.ServiceTests.session_request
    def setUp(self):
        ref.ServiceTests.setUp(self);self.addCleanup(self.temp.cleanup)
        self.issuer=self.s;self.policy_sha=hashlib.sha256(b'operator-only-network-policy').hexdigest()
        self.s=GuestAuthority(self.issuer,self.policy_sha)
        self.wire=self.new_wire()
    def new_wire(self,**changes):
        return WireAuthorization(self.issuer.config()['identity'],self.policy_sha,base_path=self.issuer.base_path,clock=lambda:self.t,**changes)
    def authorize(self,session,ch,key=None,**changes):
        key=key or self.key;path=self.issuer.base_path+AUTHORIZE
        nonce=self.call(CHALLENGE,{'key':jose.public_jwk(key),'path':path});self.assertEqual(nonce['status'],200,nonce)
        body={k:ch[k] for k in ['nonce','connection_id','policy_sha256']};body.update(changes);raw=jose.dumps(body)
        proof={'v':1,'nonce':nonce['body']['nonce'],'iss':session['identity']['sid'],'aud':self.config.origin,'method':'POST','path':path,'iat':self.t,'exp':self.t+60,'request_sha256':jose.digest(raw)}
        return self.call(AUTHORIZE,{'request':raw,'proof':jose.sign(proof,key,REQUEST_TYPE)},headers={'HTTP_AUTHORIZATION':'Codi '+session['session_token']})
    def proof(self,session,grant,ch,key=None,**changes):
        claims=jose.inspect(grant,GRANT_TYPE)[1]
        body={'v':1,'iss':session['identity']['sid'],'aud':self.wire.audience,'nonce':ch['nonce'],'grant_sha256':jose.digest(grant),
              'connection_id':ch['connection_id'],'policy_sha256':ch['policy_sha256'],'method':'CONNECT','path':self.wire.path,'iat':self.t,'exp':claims['exp'],**changes}
        return jose.sign(body,key or self.key,PROOF_TYPE)
    def grant(self,session=None,key=None):
        session=session or self.enter('alice');ch=self.wire.challenge();result=self.authorize(session,ch,key)
        self.assertEqual(result['status'],200,result);grant=result['body']['grant']
        return session,ch,grant,self.proof(session,grant,ch,key)
    def test_default_has_no_registered_privilege(self):
        self.assertIsNone(self.wire.principal);self.assertFalse(self.wire.registered)
        with self.assertRaises(ValueError):self.wire.accept('x','y')
    def test_registered_grant_is_exact_live_account_and_key(self):
        a,ch,g,p=self.grant();principal=self.wire.accept(g,p)
        self.assertEqual((principal.subject,principal.sid,principal.kind),(a['identity']['sub'],a['identity']['sid'],'registered'))
        self.assertEqual(principal.key,self.jwk);self.assertTrue(self.wire.registered)
    def test_anonymous_grant_never_promotes(self):
        a,ch,g,p=self.grant(self.enter());principal=self.wire.accept(g,p)
        self.assertEqual(principal.subject,a['identity']['sub']);self.assertTrue(principal.subject.startswith('anon:'));self.assertEqual(principal.kind,'anonymous');self.assertFalse(self.wire.registered)
        import sqlite3
        with sqlite3.connect(self.issuer.db) as db:self.assertEqual(db.execute('SELECT count(*) FROM accounts').fetchone()[0],0)
    def test_replay_same_connection_and_other_wire_refused(self):
        _,_,g,p=self.grant();self.wire.accept(g,p)
        with self.assertRaises(ValueError):self.wire.accept(g,p)
        other=self.new_wire();other.challenge()
        with self.assertRaises(ValueError):other.accept(g,p)
        self.assertFalse(other.registered)
    def test_concurrent_replay_has_only_one_winner(self):
        _,_,g,p=self.grant()
        def consume(_):
            try:self.wire.accept(g,p);return True
            except ValueError:return False
        with concurrent.futures.ThreadPoolExecutor(2) as pool:self.assertEqual(sorted(pool.map(consume,range(2))),[False,True])
    def test_restart_replaces_connection_nonce_without_disk_ledger(self):
        _,_,g,p=self.grant();old_id=self.wire.connection_id;self.wire.close();self.wire=self.new_wire();self.wire.challenge()
        self.assertNotEqual(self.wire.connection_id,old_id)
        with self.assertRaises(ValueError):self.wire.accept(g,p)
    def test_stolen_grant_needs_original_signing_key(self):
        a,ch,g,p=self.grant();other=ec.generate_private_key(ec.SECP256R1())
        with self.assertRaises(ValueError):self.wire.accept(g,self.proof(a,g,ch,key=other))
        self.wire.accept(g,p)
    def test_other_session_key_cannot_get_a_live_confirmation(self):
        a=self.enter('alice');ch=self.wire.challenge();other=ec.generate_private_key(ec.SECP256R1())
        self.assertEqual(self.authorize(a,ch,key=other)['status'],401)
    def test_unknown_bearer_and_issuer_restart_fail_closed(self):
        a=self.enter('alice');original=a['session_token'];a['session_token']=secrets.token_urlsafe(32)
        self.assertEqual(self.authorize(a,self.wire.challenge())['status'],401)
        a['session_token']=original;self.issuer=Service(self.config,clock=lambda:self.t);self.s=GuestAuthority(self.issuer,self.policy_sha)
        self.assertEqual(self.authorize(a,self.wire.challenge())['status'],401)
    def test_untrusted_authority_and_known_kid_forgery_refused(self):
        a,ch,g,p=self.grant();claims=jose.inspect(g,GRANT_TYPE)[1];other=ec.generate_private_key(ec.SECP256R1())
        for kid in ['untrusted',self.issuer.kid,{},[],True]:
            fake=jose.sign(claims,other,GRANT_TYPE,kid)
            with self.assertRaises(ValueError):self.wire.accept(fake,self.proof(a,fake,ch))
        self.wire.accept(g,p)
    def test_client_context_and_type_confusion_refused(self):
        a,ch,g,p=self.grant()
        for change in [{'v':True},{'iss':'other'},{'aud':'https://other.invalid/guest-network'},{'path':self.wire.path+'/other'},{'method':'POST'},
                       {'nonce':secrets.token_urlsafe(32)},{'connection_id':secrets.token_urlsafe(32)},{'policy_sha256':'0'*64},{'grant_sha256':jose.digest('other')},{'exp':self.t+31}]:
            with self.subTest(change=change),self.assertRaises(ValueError):self.wire.accept(g,self.proof(a,g,ch,**change))
        claims=jose.inspect(p,PROOF_TYPE)[1]
        with self.assertRaises(ValueError):self.wire.accept(g,jose.sign(claims,self.key,GRANT_TYPE))
        self.wire.accept(g,p)
    def test_grant_context_and_lifetime_shapes_refused(self):
        a,ch,g,p=self.grant();original=jose.inspect(g,GRANT_TYPE)[1]
        changes=[{'v':True},{'iss':'https://other.invalid'},{'aud':self.wire.audience+'/file'},{'kind':'admin'},{'kind':'anonymous'},{'sub':'root'},
                 {'session_deadline':self.t+1},{'exp':self.t+31},{'iat':self.t+6},{'jti':'x'},{'nonce':secrets.token_urlsafe(32)},
                 {'connection_id':secrets.token_urlsafe(32)},{'policy_sha256':'0'*64},{'cnf':{'jwk':self.jwk,'extra':True}}]
        for change in changes:
            fake=jose.sign({**original,**change},self.issuer.key,GRANT_TYPE,self.issuer.kid)
            with self.subTest(change=change),self.assertRaises(ValueError):self.wire.accept(fake,self.proof(a,fake,ch))
        self.wire.accept(g,p)
    def test_reset_immediately_drops_access_and_old_grant(self):
        _,_,g,p=self.grant();self.wire.accept(g,p);self.assertTrue(self.wire.registered)
        self.wire.reset();self.assertFalse(self.wire.registered);self.wire.challenge()
        with self.assertRaises(ValueError):self.wire.accept(g,p)
        self.assertIsNone(self.wire.principal)
    def test_closed_wire_never_reopens(self):
        _,_,g,p=self.grant();self.wire.accept(g,p);self.wire.close()
        self.assertIsNone(self.wire.principal)
        with self.assertRaises(ValueError):self.wire.challenge()
        with self.assertRaises(ValueError):self.wire.accept(g,p)
    def test_expiry_removes_privilege_at_exact_boundary(self):
        _,_,g,p=self.grant();self.wire.accept(g,p);self.t+=29;self.assertTrue(self.wire.registered)
        self.wire.challenge();self.t+=1;self.assertFalse(self.wire.registered);self.assertIsNone(self.wire.principal)
    def test_expired_pending_challenge_and_superseded_nonce_refused(self):
        _,_,g,p=self.grant();self.wire.challenge()
        with self.assertRaises(ValueError):self.wire.accept(g,p)
        self.t+=30
        with self.assertRaises(ValueError):self.wire.accept(g,p)
    def test_refresh_preserves_identity_and_extends_only_with_new_grant(self):
        a,_,g,p=self.grant();self.wire.accept(g,p);old=self.wire.principal;self.t+=15
        a,ch,g,p=self.grant(a);self.assertEqual(self.wire.principal,old)
        self.wire.accept(g,p);self.assertEqual(self.wire.principal.subject,old.subject);self.assertEqual(self.wire.principal.sid,old.sid)
        self.assertEqual(self.wire.principal.deadline,old.deadline+15)
    def test_same_wire_can_change_identity_only_with_fresh_proof(self):
        _,_,g,p=self.grant();self.wire.accept(g,p);self.wire.reset()
        a,ch,g,p=self.grant(self.enter());self.wire.accept(g,p);self.assertFalse(self.wire.registered)
        self.assertEqual(self.wire.principal.sid,a['identity']['sid'])
    def test_logout_stops_new_grants_and_existing_lease_is_bounded(self):
        a,ch,g,p=self.grant();self.wire.accept(g,p);self.session_request('/api/v1/logout',a)
        self.assertEqual(self.authorize(a,self.wire.challenge())['status'],401);self.assertTrue(self.wire.registered)
        self.t+=30;self.assertFalse(self.wire.registered)
    def test_disable_and_reenable_never_revive_old_token(self):
        a=self.enter('alice');set_disabled(self.config.state_dir,'alice',True)
        self.assertEqual(self.authorize(a,self.wire.challenge())['status'],401)
        set_disabled(self.config.state_dir,'alice',False)
        self.assertEqual(self.authorize(a,self.wire.challenge())['status'],401)
        self.grant(self.enter('alice'))
    def test_no_grant_outlives_session_deadline(self):
        self.issuer.c=replace(self.issuer.c,session_seconds=12)
        _,_,g,p=self.grant();self.wire.accept(g,p);self.assertEqual(self.wire.principal.deadline,self.t+12)
        self.t+=12;self.assertFalse(self.wire.registered)
    def test_policy_hash_is_pinned_at_both_issuer_and_wire(self):
        a=self.enter('alice');ch=self.wire.challenge()
        self.assertEqual(self.authorize(a,ch,policy_sha256='f'*64)['status'],403)
    def test_bounded_challenges_do_not_extend_current_lease(self):
        _,_,g,p=self.grant();self.wire.accept(g,p)
        for _ in range(7):self.wire.challenge()
        with self.assertRaises(ValueError):self.wire.challenge()
        self.t+=60;self.assertFalse(self.wire.registered);self.wire.challenge()
    def test_guest_rate_budget_is_separate_from_files_and_login(self):
        self.issuer.c=replace(self.issuer.c,rate_per_minute=2)
        self.s=GuestAuthority(self.issuer,self.policy_sha,GatewayAuthority(self.issuer))
        for _ in range(2):self.assertEqual(self.call(CHALLENGE,{'key':self.jwk,'path':AUTHORIZE})['status'],200)
        self.assertEqual(self.call(CHALLENGE,{'key':self.jwk,'path':AUTHORIZE})['status'],429)
        self.assertNotEqual(self.call(AUTHORIZE,{})['status'],429)
        self.assertEqual(self.call('/api/v1/gateway/challenge',{'key':self.jwk,'path':'/api/v1/gateway/authorize'})['status'],200)
        self.assertEqual(self.enter()['identity']['kind'],'anonymous')
    def test_file_grant_cannot_authorize_guest_or_reverse(self):
        from gateway_service.auth import Gatekeeper,initialize_ledger,CONFIRMATION_TYPE
        from gateway_service.user_store import UserStore
        a=self.enter('alice');state=self.root/'files-state';data=self.root/'files-data';state.mkdir(mode=0o700);data.mkdir(mode=0o700)
        store=UserStore(state,data,clock=lambda:self.t);initialize_ledger(store);gate=Gatekeeper(store,self.issuer.config()['identity'],clock=lambda:self.t)
        _,ch,g,p=self.grant(a);file_ch=gate.challenge(self.jwk,jose.digest('{}'))
        with self.assertRaises(ValueError):gate.consume('{}',g,p)
        file_claims={'v':1,'iss':self.config.origin,'aud':gate.audience,'sub':a['identity']['sub'],'sid':a['identity']['sid'],'kind':'registered','cnf':{'jwk':self.jwk},'iat':self.t,'exp':self.t+30,'jti':secrets.token_urlsafe(32),'nonce':file_ch['nonce'],'request_sha256':file_ch['request_sha256'],'session_deadline':self.t+600}
        file_grant=jose.sign(file_claims,self.issuer.key,CONFIRMATION_TYPE,self.issuer.kid)
        with self.assertRaises(ValueError):self.wire.accept(file_grant,p)
        self.assertEqual(list(store.users_path.iterdir()),[])
    def test_mounted_grant_cannot_be_used_at_root(self):
        a=self.enter('alice');self.issuer.base_path='/hidden';self.s=GuestAuthority(self.issuer,self.policy_sha);self.wire=self.new_wire()
        _,_,g,p=self.grant(a);self.wire.accept(g,p)
        root=WireAuthorization(self.issuer.config()['identity'],self.policy_sha,clock=lambda:self.t);root.challenge()
        with self.assertRaises(ValueError):root.accept(g,p)
    def test_route_composition_and_reference_paths_unchanged(self):
        paths=PATHS.copy();seen=[]
        def downstream(env,start):seen.append(env['PATH_INFO']);return self.issuer.json_response(start,200,{'other':'ok'})
        self.s=GuestAuthority(self.issuer,self.policy_sha,GatewayAuthority(self.issuer,downstream))
        self.assertEqual(self.call('/discovery.json',method='GET')['body'],{'other':'ok'});self.assertEqual(seen,['/discovery.json']);self.assertEqual(PATHS,paths)
    def test_transport_origin_method_type_length_and_duplicate_keys(self):
        for headers in [{'HTTP_ORIGIN':'https://evil.invalid'},{'HTTP_ORIGIN':''},{'HTTP_HOST':'evil.invalid'}]:self.assertEqual(self.call(CHALLENGE,{},headers=headers)['status'],403)
        self.assertEqual(self.call(CHALLENGE,{},method='GET')['status'],405)
        for headers,expected in [({'CONTENT_TYPE':'text/plain'},415),({'CONTENT_LENGTH':'20000'},413),({'HTTP_TRANSFER_ENCODING':'chunked'},400)]:self.assertEqual(self.call(CHALLENGE,{},headers=headers)['status'],expected)
        self.assertEqual(self.call(CHALLENGE,raw=b'{"key":1,"key":2}')['status'],400)

if __name__=='__main__':
    result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(Authorization))
    report={'status':'PASS' if result.wasSuccessful() else 'FAIL','tests':result.testsRun,'failures':len(result.failures),'errors':len(result.errors),
            'scope':'Local real issuer WSGI/ES256/SQLite and guest-wire state; no public routes, packet forwarding or kernel deployment',
            'sha256':{name:hashlib.sha256((ROOT/name).read_bytes()).hexdigest() for name in ['guest_service/authorization.py','origin_service/guest_authority.py','origin_service/lifecycle.py','scripts/guest-authorization-check.py','codiserver-server-v0.3.0/tests/test_service.py','codiserver-server-v0.3.0/codiauth/jose.py','codiserver-server-v0.3.0/codiauth/service.py']}}
    output=ROOT/'.build/checks/guest-authorization-result.json'
    if output.exists():output.rename(output.with_name('guest-authorization-before-'+str(time.time_ns())+'.json'))
    output.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2));raise SystemExit(0 if result.wasSuccessful() else 1)
