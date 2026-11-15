#!/usr/bin/env python3
"""Exercise renewal classification with real signatures and no live data."""
import secrets,sys,tempfile,unittest
from pathlib import Path
from cryptography.hazmat.primitives.asymmetric import ec
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from origin_service.expired_root_steps import make_checkpoint
from origin_service.live_root_renewal import inspect
from steward.protocol import jose
from steward.root_authority import RootAuthority


class LiveRenewal(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory(prefix='codi-live-renewal-');self.addCleanup(self.tmp.cleanup)
  key=jose.public_jwk(ec.generate_private_key(ec.SECP256R1()));endpoint='wss://fixture.invalid/rendezvous'
  template={'root_key':None,'realm':secrets.token_urlsafe(32),'endpoint':endpoint,'identity_policy':{'mode':'local-development'},'origins':['https://fixture.invalid']}
  grant={'key_id':jose.thumbprint(key),'public_key':key,'endpoints':[endpoint],'scopes':[secrets.token_urlsafe(32)],'limits':{'lease_seconds':120,'sample_size':4,'signal_bytes':32768},'failure_domain':'fixture'}
  self.clock=100000;self.authority=RootAuthority.initialize(Path(self.tmp.name)/'root',template,grant,600,clock=lambda:self.clock)
  self.old=self.authority.provision();self.checkpoint=make_checkpoint(self.old)
 def decision(self,root=None,staged=None,live=None,**kw):
  args={'fence_revision':1,'now':self.clock,'steward_running':True,'ledger_verified':True,'renewal_window':120};args.update(kw)
  return inspect(self.old,root or self.old,staged or self.old,live or self.old,self.checkpoint,**args)
 def test_window_and_stopped_expired_refusals(self):
  self.assertEqual(self.decision(),'wait');self.clock+=480;self.assertEqual(self.decision(),'renew-once')
  with self.assertRaises(ValueError):self.decision(steward_running=False)
  self.clock+=120
  with self.assertRaises(ValueError):self.decision()
 def test_committed_epoch_resumes_without_second_signing(self):
  self.clock+=500;new=self.authority.renew(600)
  self.assertEqual(self.decision(new,fence_revision=2),'export-committed')
  self.assertEqual(self.decision(new,new,self.old,fence_revision=2),'export-committed')
  self.assertEqual(self.decision(new,new,new,fence_revision=2),'verify-running')
  self.assertEqual(self.decision(new,new,new,fence_revision=2,steward_running=False),'start-steward')
  with self.assertRaises(ValueError):self.decision(new,new,new,fence_revision=1)
  self.clock+=600
  with self.assertRaises(ValueError):self.decision(new,new,new,fence_revision=2)
 def test_invalid_or_unverified_inputs_refused(self):
  self.clock+=500;new=self.authority.renew(600)
  with self.assertRaises(ValueError):self.decision(new,self.old,new,fence_revision=2)
  with self.assertRaises(ValueError):self.decision(ledger_verified=False)
  with self.assertRaises(ValueError):self.decision(now=99999)
  with self.assertRaises(ValueError):self.decision(renewal_window=True)
  damaged=dict(self.old);damaged['seed']=self.old['seed'][:-1]+'!'
  with self.assertRaises(ValueError):self.decision(damaged)

if __name__=='__main__':unittest.main()
