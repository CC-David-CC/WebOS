#!/usr/bin/env python3
"""Real signed expired-root renewal and interrupted-export fixture; no live writes."""
import hashlib,importlib.util,json,secrets,sqlite3,sys,tempfile,time,unittest
from argparse import Namespace
from pathlib import Path
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ec
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from origin_service.expired_root_steps import next_step,make_checkpoint,inspect_signed_exports,verify_publisher
from steward.root_authority import RootAuthority,atomic_private
from steward.publisher import PublisherState
from steward.protocol import jose
from steward.provision import verified_seed
spec=importlib.util.spec_from_file_location('fixture_provision',ROOT/'scripts/provision-connected.py');provision=importlib.util.module_from_spec(spec);spec.loader.exec_module(provision)

class InterruptedExport(unittest.TestCase):
 def test_expired_committed_seed_is_exported_without_second_signature(self):
  with tempfile.TemporaryDirectory(prefix='codi-expired-root-') as folder:
   root=Path(folder)/'authority';runtime=Path(folder)/'runtime';runtime.mkdir(mode=0o700);private=runtime/'steward-private/provisioned';private.mkdir(mode=0o700,parents=True);(runtime/'steward-private').chmod(0o700)
   service=ec.generate_private_key(ec.SECP256R1());public=jose.public_jwk(service);realm=secrets.token_urlsafe(32);scope=secrets.token_urlsafe(32);endpoint='wss://fixture.invalid/rendezvous'
   template={'root_key':None,'realm':realm,'endpoint':endpoint,'identity_policy':{'mode':'local-development'},'origins':['https://fixture.invalid']}
   grant={'key_id':jose.thumbprint(public),'public_key':public,'endpoints':[endpoint],'scopes':[scope],'limits':{'lease_seconds':120,'sample_size':4,'signal_bytes':32768},'failure_domain':'fixture'}
   authority=RootAuthority.initialize(root,template,grant,30,clock=lambda:int(time.time())-120);old=authority.provision();atomic_private(private/'service.pem',service.private_bytes(serialization.Encoding.PEM,serialization.PrivateFormat.PKCS8,serialization.NoEncryption()));atomic_private(private/'provision.json',jose.dumps(old).encode());publisher=PublisherState.initialize(private/'ledger')
   old_claim=jose.inspect(old['seed'],'codi-seed/1',32768)[1];publisher_binding={'realm':realm,'root_key_id':jose.thumbprint(old['root_key']),'service_key_id':grant['key_id'],'endpoint':endpoint};publisher.bind(publisher_binding,old_claim)
   template_descriptor={'version':'codi-steward/1','realm':realm,'key_id':grant['key_id'],'exp':old_claim['exp'],'endpoint':endpoint,'scopes':grant['scopes'],'limits':{'lease_seconds':120,'sample_size':4,'signal_bytes':32768}}
   publisher.publish(template_descriptor,service,old_claim,now=old_claim['iat'],minimum_revision=1)
   with sqlite3.connect(private/'ledger/publisher.sqlite3') as db:row=db.execute('SELECT binding,seed_revision,seed_hash,revision,token,frozen FROM publisher WHERE id=1').fetchone()
   checkpoint=make_checkpoint(old);key_before=(root/'root.pem').read_bytes();ledger_before=(private/'ledger/publisher.sqlite3').read_bytes();new=RootAuthority(root).renew(600);self.assertEqual(jose.inspect(new['seed'],'codi-seed/1',32768)[1]['revision'],2)
   def classify(staged,live):
    unpack=lambda x:jose.inspect(x['seed'],'codi-seed/1',32768)[1]['revision'];digest=lambda x:hashlib.sha256(x['seed'].encode()).hexdigest()
    return next_step(base_revision=1,target_revision=2,root_revision=unpack(new),fence_revision=2,staged_revision=unpack(staged),live_revision=unpack(live),base_hash=digest(old),root_hash=digest(new),staged_hash=digest(staged),live_hash=digest(live),root_expired=False,steward_running=False,bindings_verified=True,ledger_verified=True)
   self.assertEqual(classify(old,old),'export-committed')
   inspect=lambda staged,live:inspect_signed_exports(new,staged,live,checkpoint,fence_revision=2,now=int(time.time()),steward_running=False,ledger_verified=True)
   self.assertEqual(inspect(old,old),'export-committed')
   self.assertEqual(verify_publisher(row,new,old,checkpoint,minimum_revision=1),{'seedRevision':1,'publisherRevision':1})
   for index,value in [(0,jose.dumps({**publisher_binding,'endpoint':'wss://other.invalid/rendezvous'})),(2,'wrong'),(3,0),(4,'invalid-token'),(5,1)]:
    broken=list(row);broken[index]=value
    with self.assertRaises(ValueError):verify_publisher(broken,new,old,checkpoint,minimum_revision=1)
   target=list(row);target[1]=2;target[2]=jose.digest(jose.dumps(jose.inspect(new['seed'],'codi-seed/1',32768)[1]))
   with self.assertRaises(ValueError):verify_publisher(target,new,old,checkpoint,minimum_revision=1)
   with self.assertRaises(ValueError):inspect_signed_exports(new,old,old,checkpoint,fence_revision=2,now=1,steward_running=False,ledger_verified=True)
   with self.assertRaises(ValueError):inspect(old,{**old,'realm':'other-realm'})
   with self.assertRaises(ValueError):inspect(old,{**old,'seed':old['seed'][:-1]+('A' if old['seed'][-1]!='A' else 'B')})
   claims=jose.inspect(new['seed'],'codi-seed/1',32768)[1];claims['stewards'][0]['scopes']=[secrets.token_urlsafe(32)];different_grant={**new,'seed':jose.sign(claims,authority.key,'codi-seed/1')}
   with self.assertRaises(ValueError):inspect_signed_exports(different_grant,old,old,checkpoint,fence_revision=2,now=int(time.time()),steward_running=False,ledger_verified=True)
   claims=jose.inspect(old['seed'],'codi-seed/1',32768)[1];claims['exp']+=1;claims['stewards'][0]['exp']+=1;different_old={**old,'seed':jose.sign(claims,authority.key,'codi-seed/1')}
   with self.assertRaises(ValueError):inspect(different_old,different_old)
   args=Namespace(runtime_dir=runtime,root_dir=root,command='export');exported=provision.update(args);self.assertEqual(exported,new);self.assertEqual(classify(exported,old),'export-committed');self.assertEqual(classify(exported,exported),'start-steward')
   self.assertEqual(inspect(exported,old),'export-committed');self.assertEqual(inspect(exported,exported),'start-steward')
   self.assertEqual(verify_publisher(target,new,exported,checkpoint,minimum_revision=1),{'seedRevision':2,'publisherRevision':1})
   self.assertEqual(verified_seed(exported['seed'],exported['root_key'],realm,int(time.time()))['revision'],2);self.assertEqual((root/'root.pem').read_bytes(),key_before);self.assertEqual((private/'ledger/publisher.sqlite3').read_bytes(),ledger_before)
   self.assertEqual(RootAuthority(root).provision()['seed'],new['seed'])
if __name__=='__main__':
 result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(InterruptedExport));sys.exit(not result.wasSuccessful())
