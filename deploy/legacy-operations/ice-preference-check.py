#!/usr/bin/env python3
"""Signed origin ICE-preference capability and retained authentication invariants."""
import hashlib,importlib.util,json,sys,unittest
from pathlib import Path
from dataclasses import replace
ROOT=Path(__file__).resolve().parent.parent;sys.path.insert(0,str(ROOT))
from origin_service.ice_preference import PreferenceService as Service
from origin_service.turn import TurnPolicy
from origin_service.lifecycle import set_disabled,reset_password
from cryptography.hazmat.primitives.asymmetric import ec
from concurrent.futures import ThreadPoolExecutor
from codiauth import jose
spec=importlib.util.spec_from_file_location('ice_reference_tests',ROOT/'codiserver-server-v0.3.0/tests/test_service.py');ref=importlib.util.module_from_spec(spec);spec.loader.exec_module(ref);ref.Service=Service

class PreferenceTests(ref.ServiceTests):
 def enable(self,transport='all'):
  self.s=Service(self.config,clock=lambda:self.t,turn_policy=TurnPolicy(b'x'*32,['turns:fixture.invalid:443?transport=tcp'],transport))
 def choice(self,transport='all',**extra):return {'version':'codi-session-ice/1','transport':transport,**extra}
 def selected(self,transport='all',name=None):
  path='/api/v1/auth' if name else '/api/v1/anonymous'
  data={'username':name,'password':ref.PASSWORD} if name else {}
  data['ice_preference']=self.choice(transport)
  return self.call(path,self.envelope(path,data))
 def test_legacy_default_stays_relay_under_operator_all(self):
  self.enable();self.assertEqual(self.s.config()['rtc']['iceTransportPolicy'],'relay');self.assertEqual(self.enter()['rtc']['iceTransportPolicy'],'relay')
 def test_capability_advertises_operator_all(self):
  self.enable();self.assertEqual(self.s.config()['rtc']['preference'],{'version':'codi-session-ice/1','allowed':['relay','all'],'preferred':'all'})
 def test_signed_modern_all_entry(self):
  self.enable();r=self.selected();self.assertEqual(r['status'],200);self.assertEqual(r['body']['rtc']['iceTransportPolicy'],'all')
 def renew_choice(self,session,transport='relay',key=None,subject=None,token=None):
  path='/api/v1/renew';data={'ice_preference':self.choice(transport)}
  return self.call(path,self.envelope(path,data,key=key,subject=subject or session['identity']['sid']),headers={'HTTP_AUTHORIZATION':'Codi '+(token or session['session_token'])})
 def stored(self,session):return self.s.sessions[jose.digest(session['session_token'])]
 def test_operator_relay_advertises_only_relay(self):
  self.enable('relay');self.assertEqual(self.s.config()['rtc']['preference'],{'version':'codi-session-ice/1','allowed':['relay'],'preferred':'relay'})
 def test_forbidden_choice_creates_no_account_or_session(self):
  self.enable('relay');self.assertEqual(self.selected('all','alice')['status'],403);self.assertFalse(self.s.sessions)
  with ref.sqlite3.connect(self.s.db) as db:self.assertEqual(db.execute('SELECT count(*) FROM accounts').fetchone()[0],0)
 def test_no_turn_cannot_request_preference(self):self.assertEqual(self.selected()['status'],403)
 def test_bad_profiles_and_fields_refused(self):
  self.enable()
  for preference in [None,True,'all',{},self.choice(version='unknown'),self.choice(transport=True),self.choice(transport='auto'),self.choice(url='turns:wrong.invalid:443?transport=tcp')]:
   with self.subTest(preference=preference):self.assertEqual(self.call('/api/v1/anonymous',self.envelope('/api/v1/anonymous',{'ice_preference':preference}))['status'],400)
  self.assertFalse(self.s.sessions)
 def test_internal_empty_renew_retains_all_choice(self):
  self.enable();s=self.selected()['body'];self.assertEqual(self.session_request('/api/v1/renew',s)['body']['rtc']['iceTransportPolicy'],'all')
 def test_signed_renew_updates_choice_without_extending_deadline(self):
  self.enable();s=self.selected()['body'];prior=dict(self.stored(s));self.t+=30;r=self.renew_choice(s)
  self.assertEqual(r['status'],200);self.assertEqual(r['body']['rtc']['iceTransportPolicy'],'relay');self.assertEqual(self.stored(s)['deadline'],prior['deadline']);self.assertEqual(r['body']['identity']['sid'],s['identity']['sid'])
 def test_choice_is_signed_and_tampering_does_not_mutate(self):
  self.enable();s=self.selected()['body'];path='/api/v1/renew';e=self.envelope(path,{'ice_preference':self.choice('relay')},subject=s['identity']['sid']);e['request']=e['request'].replace('relay','all')
  self.assertEqual(self.call(path,e,headers={'HTTP_AUTHORIZATION':'Codi '+s['session_token']})['status'],401);self.assertEqual(self.stored(s)['_ice_preference'],'all')
 def test_wrong_key_token_and_sid_cannot_change_choice(self):
  self.enable();s=self.selected()['body']
  for kwargs in [{'key':ec.generate_private_key(ec.SECP256R1())},{'token':'x'*43},{'subject':'wrong-session'}]:
   self.assertEqual(self.renew_choice(s,**kwargs)['status'],401);self.assertEqual(self.stored(s)['_ice_preference'],'all')
 def test_legacy_and_modern_sessions_keep_independent_choices(self):
  self.enable();a=self.enter();b=self.selected()['body'];self.assertEqual(self.session_request('/api/v1/renew',a)['body']['rtc']['iceTransportPolicy'],'relay');self.assertEqual(self.session_request('/api/v1/renew',b)['body']['rtc']['iceTransportPolicy'],'all')
 def test_logout_does_not_accept_preference_and_does_revoke(self):
  self.enable();s=self.selected()['body'];p='/api/v1/logout';e=self.envelope(p,{'ice_preference':self.choice()},subject=s['identity']['sid'])
  self.assertEqual(self.call(p,e,headers={'HTTP_AUTHORIZATION':'Codi '+s['session_token']})['status'],400);self.assertEqual(self.session_request(p,s)['status'],200);self.assertEqual(self.renew_choice(s)['status'],401)
 def test_disable_and_reenable_do_not_revive_modern_session(self):
  self.enable();s=self.selected(name='alice')['body'];set_disabled(self.config.state_dir,'alice',True);set_disabled(self.config.state_dir,'alice',False);self.assertEqual(self.renew_choice(s)['status'],401)
 def test_password_reset_revokes_modern_session(self):
  self.enable();s=self.selected(name='alice')['body'];reset_password(self.config.state_dir,'alice','another long correct password');self.assertEqual(self.renew_choice(s)['status'],401)
 def test_failed_issue_does_not_change_stored_choice(self):
  self.enable();s=self.selected(name='alice')['body'];set_disabled(self.config.state_dir,'alice',True);self.assertEqual(self.renew_choice(s)['status'],401);self.assertEqual(self.stored(s)['_ice_preference'],'all')
 def test_rejected_entry_context_does_not_affect_next_legacy_entry(self):
  self.enable();data={'ice_preference':self.choice(),'name':'forbidden'};self.assertEqual(self.call('/api/v1/anonymous',self.envelope('/api/v1/anonymous',data))['status'],400);self.assertEqual(self.enter()['rtc']['iceTransportPolicy'],'relay')
 def test_context_does_not_leak_to_concurrent_issuance(self):
  self.enable()
  def entry(modern):return self.s.enter({'ice_preference':self.choice()} if modern else {},self.jwk,'/api/v1/anonymous')['rtc']['iceTransportPolicy']
  choices=[True,False]*12
  with ThreadPoolExecutor(max_workers=8) as pool:results=list(pool.map(entry,choices))
  self.assertEqual(results,['all' if modern else 'relay' for modern in choices])
 def test_corrupt_session_preference_fails_closed(self):
  self.enable();s=self.selected()['body'];self.stored(s)['_ice_preference']='automatic';self.assertEqual(self.session_request('/api/v1/renew',s)['status'],403)
 def test_session_capacity_does_not_leave_unreachable_choice_record(self):
  self.config=replace(self.config,max_sessions=1);self.enable();self.enter();self.assertEqual(self.selected()['status'],429);self.assertEqual(len(self.s.sessions),1)
 def test_modern_choice_keeps_absolute_expiry_and_credential_bound(self):
  self.config=replace(self.config,session_seconds=40);self.enable();s=self.selected()['body'];deadline=self.stored(s)['deadline'];self.t+=39;r=self.renew_choice(s,'all')
  self.assertEqual(r['status'],200);self.assertLessEqual(r['body']['rtc']['expiresAt'],deadline);self.assertLessEqual(r['body']['rtc']['expiresAt'],r['body']['expires_at']);self.t+=1;self.assertEqual(self.renew_choice(s,'all')['status'],401)
 def test_modern_nonce_is_one_use_and_does_not_reapply_mutation(self):
  self.enable();s=self.selected()['body'];p='/api/v1/renew';e=self.envelope(p,{'ice_preference':self.choice('relay')},subject=s['identity']['sid']);headers={'HTTP_AUTHORIZATION':'Codi '+s['session_token']}
  self.assertEqual(self.call(p,e,headers=headers)['status'],200);self.assertEqual(self.call(p,e,headers=headers)['status'],401);self.assertEqual(self.stored(s)['_ice_preference'],'relay')
 def test_restart_keeps_accounts_and_key_but_discards_preference_sessions(self):
  self.enable();s=self.selected(name='alice')['body'];pin=self.s.jwk;self.enable();self.assertEqual(self.s.jwk,pin);self.assertEqual(self.renew_choice(s)['status'],401);self.assertEqual(self.selected(name='alice')['body']['identity']['sub'],s['identity']['sub'])

if __name__=='__main__':
 result=unittest.TextTestRunner(verbosity=1).run(unittest.defaultTestLoader.loadTestsFromTestCase(PreferenceTests))
 names=['origin_service/ice_preference.py','origin_service/lifecycle.py','scripts/ice-preference-check.py','network/ICE-PREFERENCE-PROFILE.md']
 p=ROOT/'.build/checks/ice-preference-result.json';p.write_text(json.dumps({'status':'PASS' if result.wasSuccessful() else 'FAIL','tests':result.testsRun,'failures':len(result.failures),'errors':len(result.errors),'sha256':{n:hashlib.sha256((ROOT/n).read_bytes()).hexdigest() for n in names}},indent=2)+'\n')
 raise SystemExit(0 if result.wasSuccessful() else 1)
