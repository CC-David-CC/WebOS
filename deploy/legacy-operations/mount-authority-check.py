#!/usr/bin/env python3
"""Real signed mount changes and durable publisher floors, isolated state only."""
import hashlib,json,os,secrets,sqlite3,sys,tempfile,time,unittest
from copy import deepcopy
from contextlib import closing
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent;sys.path.insert(0,str(ROOT))
from cryptography.hazmat.primitives.asymmetric import ec
from mount_operator import authority as migration
from steward.protocol import jose
from steward.publisher import PublisherState
from steward.root_authority import RootAuthority
from steward.server import StewardServer

class MountAuthorityChecks(unittest.TestCase):
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory(prefix='codi-mount-authority-');self.path=Path(self.temp.name);self.now=int(time.time())
  self.service=ec.generate_private_key(ec.SECP256R1());public=jose.public_jwk(self.service);issuer=jose.public_jwk(ec.generate_private_key(ec.SECP256R1()))
  policy={'mode':'server','apiBase':'/hidden/api/v1','issuer':'https://example.invalid','audience':'codiserver-peers-v1','authorityClass':'development','authorityKeys':[{'kid':jose.thumbprint(issuer),'jwk':issuer}]}
  template={'root_key':None,'realm':secrets.token_urlsafe(32),'endpoint':'wss://example.invalid/hidden/rendezvous','identity_policy':policy,'origins':['https://example.invalid']}
  grant={'key_id':jose.thumbprint(public),'public_key':public,'endpoints':[template['endpoint']],'scopes':[secrets.token_urlsafe(32)],'limits':{'lease_seconds':120,'sample_size':4,'signal_bytes':32768},'failure_domain':'mount-fixture'}
  self.authority=RootAuthority.initialize(self.path/'root',template,grant,1200,clock=lambda:self.now)
  self.before=self.authority.provision();self.keybytes=(self.path/'root/root.pem').read_bytes();self.publisher=PublisherState.initialize(self.path/'publisher')
  self.server(self.before).descriptor()
  for _ in range(4):self.server(self.before).descriptor(renew=True)
  self.oldrow=migration.publisher_row(self.publisher)
 def tearDown(self):self.temp.cleanup()
 def server(self,provision,publisher=None):return StewardServer(**provision,service_key=self.service,publisher_state=publisher or self.publisher,clock=lambda:self.now)
 def plan(self,base='',floor=1):return migration.prepare(self.authority,base,seconds=1200,minimum_revision=floor)
 def unchanged(self):self.assertEqual(self.before,self.authority.provision());self.assertEqual(self.oldrow,migration.publisher_row(self.publisher))
 def test_prepare_is_read_only_and_changes_only_mount_and_forward_epoch(self):
  p=self.plan();old,new,base,target=migration.validate(p);self.unchanged();self.assertEqual((base,target),('/hidden',''));self.assertEqual(new['revision'],2);self.assertEqual(p['after']['endpoint'],'wss://example.invalid/rendezvous');self.assertEqual(p['after']['identity_policy']['apiBase'],'/api/v1')
  self.assertEqual(p['before']['root_key'],p['after']['root_key']);self.assertEqual(p['before']['realm'],p['after']['realm']);self.assertEqual(self.keybytes,(self.path/'root/root.pem').read_bytes())
 def test_root_commit_and_retry_reuse_exact_signed_bytes(self):
  p=self.plan();self.assertTrue(migration.apply(self.authority,p));self.assertFalse(migration.apply(self.authority,p));self.assertEqual(self.authority.provision(),p['after']);self.assertEqual(RootAuthority(self.path/'root').provision(),p['after']);self.assertEqual(self.keybytes,(self.path/'root/root.pem').read_bytes())
 def test_publisher_rebind_preserves_counter_and_cached_token_then_advances(self):
  p=self.plan();row=migration.publisher_plan(self.publisher,p);migration.apply(self.authority,p)
  self.assertTrue(migration.apply_publisher(self.publisher,p,row));self.assertFalse(migration.apply_publisher(self.publisher,p,row))
  current=migration.publisher_row(self.publisher);self.assertEqual(current[3:],self.oldrow[3:])
  token=self.server(p['after']).descriptor();payload=jose.verify(token,jose.public_jwk(self.service),'codi-steward/1')
  self.assertEqual(payload['revision'],self.oldrow[3]+1);self.assertEqual(payload['endpoint'],p['after']['endpoint']);self.assertEqual(token,self.server(p['after']).descriptor())
 def test_rollback_signs_higher_root_and_publisher_revisions_with_original_keys(self):
  first=self.plan();row=migration.publisher_plan(self.publisher,first);migration.apply(self.authority,first);migration.apply_publisher(self.publisher,first,row);self.server(first['after']).descriptor()
  previous=migration.publisher_row(self.publisher)[3];back=self.plan('/hidden',floor=2);row=migration.publisher_plan(self.publisher,back);migration.apply(self.authority,back);migration.apply_publisher(self.publisher,back,row)
  token=self.server(back['after']).descriptor();self.assertEqual(jose.inspect(back['after']['seed'],'codi-seed/1',32768)[1]['revision'],3);self.assertGreater(jose.inspect(token,'codi-steward/1',8192)[1]['revision'],previous)
  self.assertEqual({k:v for k,v in self.before.items() if k!='seed'},{k:v for k,v in back['after'].items() if k!='seed'});self.assertEqual(self.keybytes,(self.path/'root/root.pem').read_bytes())
 def test_trusted_external_floor_is_advanced_without_reset(self):
  p=self.plan(floor=50);migration.apply(self.authority,p);self.assertEqual(jose.inspect(self.authority.provision()['seed'],'codi-seed/1',32768)[1]['revision'],51)
 def test_bad_prefix_and_bad_floor_are_refused_without_writes(self):
  for prefix in ['/','/../x','//evil','https://evil.invalid','/with space']:
   with self.subTest(prefix=prefix),self.assertRaises(ValueError):self.plan(prefix)
  for floor in [True,0,1.5,'1',2**53-1]:
   with self.subTest(floor=floor),self.assertRaises(ValueError):self.plan(floor=floor)
  self.unchanged()
 def test_clock_rollback_refused(self):
  self.now-=1
  with self.assertRaises(ValueError):self.plan()
  self.unchanged()
 def test_issuer_trust_or_origin_replacement_is_rejected(self):
  other=jose.public_jwk(ec.generate_private_key(ec.SECP256R1()))
  for change in [lambda p:p['after']['identity_policy'].update(audience='other'),lambda p:p['after']['identity_policy'].update(authorityKeys=[{'kid':jose.thumbprint(other),'jwk':other}]),lambda p:p['after'].update(origins=['https://evil.invalid'])]:
   p=self.plan();change(p)
   with self.assertRaises(ValueError):migration.apply(self.authority,p)
  self.unchanged()
 def test_valid_root_signature_cannot_change_scope_or_service_key(self):
  other=jose.public_jwk(ec.generate_private_key(ec.SECP256R1()))
  for change in [lambda s:s['stewards'][0].update(scopes=[secrets.token_urlsafe(32)]),lambda s:s['stewards'][0].update(public_key=other,key_id=jose.thumbprint(other))]:
   p=self.plan();seed=jose.inspect(p['after']['seed'],'codi-seed/1',32768)[1];change(seed);p['after']['seed']=jose.sign(seed,self.authority.key,'codi-seed/1')
   with self.assertRaises(ValueError):migration.apply(self.authority,p)
  self.unchanged()
 def test_sibling_prepared_plan_cannot_replace_committed_history(self):
  p=self.plan();sibling=self.plan('/other');migration.apply(self.authority,p)
  with self.assertRaises(ValueError):migration.apply(self.authority,sibling)
  self.assertEqual(self.authority.provision(),p['after'])
 def test_expired_prepared_issuance_refused_without_mutation(self):
  p=self.plan();self.now+=1201
  with self.assertRaises(ValueError):migration.apply(self.authority,p)
  self.unchanged()
 def test_online_publishers_cannot_be_silently_initialized(self):
  empty=PublisherState.initialize(self.path/'staging');p=self.plan()
  with self.assertRaises(ValueError):migration.publisher_plan(empty,p)
  row=migration.publisher_plan(empty,p,allow_unbound=True);migration.apply_publisher(empty,p,row);token=self.server(p['after'],empty).descriptor();self.assertGreaterEqual(jose.inspect(token,'codi-steward/1',8192)[1]['revision'],2)
 def test_unused_staging_publisher_keeps_zero_counter_through_forward_rollback(self):
  empty=PublisherState.initialize(self.path/'unused-staging');p=self.plan()
  first=migration.publisher_plan(empty,p,allow_unbound=True);migration.apply_publisher(empty,p,first);migration.apply(self.authority,p)
  back=migration.prepare(self.authority,'/hidden',seconds=1200,minimum_revision=2)
  with self.assertRaises(ValueError):migration.publisher_plan(empty,back)
  second=migration.publisher_plan(empty,back,allow_unbound=True);migration.apply_publisher(empty,back,second);migration.apply(self.authority,back)
  self.assertEqual(migration.publisher_row(empty)[3:],[0,None,0])
  token=self.server(back['after'],empty).descriptor();self.assertGreaterEqual(jose.inspect(token,'codi-steward/1',8192)[1]['revision'],3)
 def test_sorted_journal_roundtrip_preserves_publisher_plan_binding(self):
  import json
  p=self.plan();prepared=migration.publisher_plan(self.publisher,p)
  saved=json.loads(json.dumps({'authority':p,'publisher':prepared},sort_keys=True,indent=2))
  self.assertEqual(migration.plan_digest(p),migration.plan_digest(saved['authority']))
  migration.apply(self.authority,saved['authority']);migration.apply_publisher(self.publisher,saved['authority'],saved['publisher'])
  token=self.server(saved['authority']['after']).descriptor();self.assertGreater(jose.inspect(token,'codi-steward/1',8192)[1]['revision'],self.oldrow[3])
 def test_already_frozen_or_missing_publisher_is_not_reset(self):
  p=self.plan()
  with self.publisher.transaction() as db:db.execute('UPDATE publisher SET frozen=1')
  with self.assertRaises(ValueError):migration.publisher_plan(self.publisher,p)
  self.assertEqual(migration.publisher_row(self.publisher)[5],1)
  self.publisher.db.unlink()
  with self.assertRaises(FileNotFoundError):migration.publisher_plan(self.publisher,p)
  self.assertFalse(self.publisher.db.exists())
 def test_concurrent_publisher_progress_refuses_stale_preimage(self):
  p=self.plan();row=migration.publisher_plan(self.publisher,p);self.server(self.before).descriptor(renew=True);new=migration.publisher_row(self.publisher)
  with self.assertRaises(ValueError):migration.apply_publisher(self.publisher,p,row)
  self.assertEqual(migration.publisher_row(self.publisher),new)
 def test_prepared_publisher_cannot_reset_counter_or_replace_cached_bytes(self):
  p=self.plan();row=migration.publisher_plan(self.publisher,p)
  for change in [lambda r:r['after'].__setitem__(3,0),lambda r:r['after'].__setitem__(4,None),lambda r:r.update(authorityPlanSHA256='bad')]:
   altered=deepcopy(row);change(altered)
   with self.assertRaises(ValueError):migration.apply_publisher(self.publisher,p,altered)
  self.unchanged()
 def test_corrupt_publisher_token_refused(self):
  p=self.plan()
  with self.publisher.transaction() as db:db.execute("UPDATE publisher SET token='corrupt'")
  with self.assertRaises(ValueError):migration.publisher_plan(self.publisher,p)
 def test_real_child_death_before_authority_commit_leaves_original(self):
  p=self.plan();pid=os.fork()
  if pid==0:
   with self.authority.operator(),closing(self.authority.connection()) as db:
    db.execute('BEGIN IMMEDIATE');db.execute('UPDATE authority SET revision=50');os._exit(71)
  _,status=os.waitpid(pid,0);self.assertEqual(os.waitstatus_to_exitcode(status),71);self.unchanged();migration.apply(self.authority,p);self.assertEqual(self.authority.provision(),p['after'])
 def test_real_child_death_after_authority_commit_retries_same_plan(self):
  p=self.plan();pid=os.fork()
  if pid==0:migration.apply(self.authority,p);os._exit(72)
  _,status=os.waitpid(pid,0);self.assertEqual(os.waitstatus_to_exitcode(status),72);self.assertFalse(migration.apply(self.authority,p));self.assertEqual(self.authority.provision(),p['after'])
 def test_real_child_death_after_publisher_commit_keeps_counter(self):
  p=self.plan();row=migration.publisher_plan(self.publisher,p);migration.apply(self.authority,p);pid=os.fork()
  if pid==0:migration.apply_publisher(self.publisher,p,row);os._exit(73)
  _,status=os.waitpid(pid,0);self.assertEqual(os.waitstatus_to_exitcode(status),73);self.assertFalse(migration.apply_publisher(self.publisher,p,row));self.assertEqual(migration.publisher_row(self.publisher)[3:],self.oldrow[3:])

if __name__=='__main__':
 result=unittest.TextTestRunner(verbosity=1).run(unittest.defaultTestLoader.loadTestsFromTestCase(MountAuthorityChecks));report={'status':'PASS' if result.wasSuccessful() else 'FAIL','scope':__doc__,'tests':result.testsRun,'failures':len(result.failures),'errors':len(result.errors),'liveServicesChanged':False,'VMServiceMigrationTested':False,'sha256':{n:hashlib.sha256((ROOT/n).read_bytes()).hexdigest() for n in ['mount_operator/authority.py','scripts/mount-authority-check.py']}}
 output=ROOT/'.build/checks/mount-authority-result.json'
 if output.exists():output.rename(output.with_name(output.stem+'-before-'+str(time.time_ns())+'.json'))
 output.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2));sys.exit(0 if result.wasSuccessful() else 1)
