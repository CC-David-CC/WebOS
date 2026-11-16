"""Post-floor family-selection contract against exact installed beta snapshots."""
import contextlib,copy,hashlib,importlib.util,itertools,sys,types,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];OPS=ROOT/'research/beta-isolated-hosting/ops';sys.path.insert(0,str(OPS))
from beta_transaction import _encode
from opfs_managed import HeldAdapter,ManagedBinding
def load(name,path):
 spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);sys.modules[name]=m;spec.loader.exec_module(m);return m
source=load('beta_mixed',Path(__file__).with_name('beta-recovery-mixed.test.py'));succ=load('beta_successor',Path(__file__).with_name('beta-successor.py'));families=succ.families(source.x,source.old,source.new)
floor={'version':1,'baseline':hashlib.sha256(families[succ.OLD]['normalized']['manifest']).hexdigest(),'candidate':succ.BETA}
def journal(a,b,gate):
 j={'version':2 if gate else 1,'phase':'prepared','old':_encode(a),'new':_encode(b),'timer':{'active':False,'enabled':False},'caddy_started':True,'backup':'fixture'}
 if gate:j['policy']='gate-only'
 return j
class Tests(unittest.TestCase):
 def test_exact_and_main_fence(self):
  for family in families:
   for name in ('gate','candidate'):
    current=families[family][name];self.assertEqual(succ.select(families,current,floor=floor,main_journal_present=False)[0],family)
    with self.assertRaisesRegex(ValueError,'Main restriction'):succ.select(families,current,floor=floor,main_journal_present=True)
  with self.assertRaises(ValueError):succ.select(families,families[succ.NEW]['candidate'],floor={**floor,'baseline':'0'*64},main_journal_present=False)
 def test_same_main_mixed_recovery_and_cross_main_refusal(self):
  for family in families:
   gate,candidate=families[family]['gate'],families[family]['candidate']
   for first,second,policy in ((candidate,gate,True),(gate,candidate,False)):
    j=journal(first,second,policy)
    for bits in itertools.product((0,1),repeat=3):
     state={k:(first if bit==0 else second)[k] for k,bit in zip(('common','manifest','caddy'),bits)}
     self.assertEqual(succ.select(families,state,floor=floor,main_journal_present=False,nested_journal=j)[0],family)
    other=families[succ.NEW if family==succ.OLD else succ.OLD]
    for k in ('manifest','caddy'):
     crossed=dict(first);crossed[k]=other['candidate'][k]
     with self.assertRaises(ValueError):succ.select(families,crossed,floor=floor,main_journal_present=False,nested_journal=j)
    bad=dict(j);bad['phase']='unknown'
    with self.assertRaises(ValueError):succ.select(families,first,floor=floor,main_journal_present=False,nested_journal=bad)
    bad=dict(j);bad['version']=True
    with self.assertRaises(ValueError):succ.select(families,first,floor=floor,main_journal_present=False,nested_journal=bad)
 def test_beta_gate_and_restore_preserve_new_main(self):
  f=families[succ.NEW];current=dict(f['candidate']);calls=[];check=lambda:None
  class FakeTx:
   def __init__(self):self.io=HeldAdapter(object(),check)
   def apply_gate(self,a,b):self.apply(a,b)
   def apply(self,a,b):
    selftest.assertEqual(current,a);current.clear();current.update(b);calls.append('transition')
  selftest=self
  binding=ManagedBinding(lambda:contextlib.nullcontext(),check,{'baseline':f['normalized'],'gate':f['gate'],'candidate':f['candidate']},lambda a,b:FakeTx(),lambda:current,lambda _:None,lambda:True,lambda *a:None,lambda:None,lambda _:None,lambda _:None,lambda _:None,lambda:None)
  binding.gate();self.assertEqual(current,f['gate']);self.assertIn(succ.NEW.encode(),current['manifest']);binding.forward({});self.assertEqual(current,f['candidate']);self.assertIn(succ.NEW.encode(),current['manifest']);self.assertEqual(calls,['transition','transition'])
if __name__=='__main__':unittest.main(verbosity=2)
