"""Disposable checks for every managed webctl render target."""
import copy,importlib.util,os,sys,tempfile,tomllib,unittest
from pathlib import Path
root=Path(__file__).resolve().parents[1];sys.path.insert(0,str(root/'ops'))
def load(name,path):
 spec=importlib.util.spec_from_file_location(name,path);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module
inventory=load('inventory',root/'ops/render_inventory.py');newgen=load('newgen',root/'ops/common.py');livegen=load('livegen',root/'ops/common_live.py')
class Old:
 @staticmethod
 def validate(data):return newgen.validate(data)
 @staticmethod
 def caddy(data,mode):return newgen.caddy(data,mode)
 @staticmethod
 def unit(site):return newgen.unit(site)
class Check(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory(prefix='beta-inventory-');self.addCleanup(self.tmp.cleanup);self.root=Path(self.tmp.name);old=tomllib.loads((root/'sites.toml').read_text());new=copy.deepcopy(old);new['codi_beta_simplified']='a'*64
  self.obj=inventory.RenderInventory(self.root/'hosting',self.root/'etc-caddy',Old,newgen,old,new,owner_uid=os.getuid(),owner_gid=os.getgid(),caddy_uid=os.getuid(),caddy_gid=os.getgid())
  for p,(before,after,meta) in self.obj.targets.items():p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(before);p.chmod(meta[2])
 def test_all_targets_and_recovery_mixture(self):
  self.assertEqual(len(self.obj.targets),14);self.obj.check(self.obj.newdata,recovery=False)
  p=next(x for x in self.obj.targets if x.name=='Caddyfile.production');p.write_bytes(self.obj.targets[p][1]);p.chmod(self.obj.targets[p][2][2])
  with self.assertRaisesRegex(ValueError,'Unexpected generated'):self.obj.check(self.obj.newdata,recovery=False)
  self.obj.check(self.obj.newdata,recovery=True)
  with self.assertRaisesRegex(ValueError,'Unexpected generated'):self.obj.check(self.obj.newdata,recovery=True,after=True)
  p.write_bytes(b'external')
  with self.assertRaisesRegex(ValueError,'Unexpected generated'):self.obj.check(self.obj.newdata,recovery=True)
 def test_active_beta_baseline(self):
  current=self.obj.newdata
  obj=inventory.RenderInventory(self.root/'hosting',self.root/'etc-caddy',newgen,newgen,current,copy.deepcopy(current),owner_uid=os.getuid(),owner_gid=os.getgid(),caddy_uid=os.getuid(),caddy_gid=os.getgid(),baseline_only=True)
  for p,(_,after,meta) in obj.targets.items():p.write_bytes(after);p.chmod(meta[2])
  obj.check(current)
  with self.assertRaisesRegex(ValueError,'Active beta baseline'):inventory.RenderInventory(self.root/'hosting',self.root/'etc-caddy',newgen,newgen,current,self.obj.olddata,owner_uid=os.getuid(),owner_gid=os.getgid(),caddy_uid=os.getuid(),caddy_gid=os.getgid(),baseline_only=True)
 def test_explicit_maintenance_only_policy_and_negative_controls(self):
  baseline=copy.deepcopy(self.obj.newdata);baseline['codi_beta_maintenance']=False;gated=copy.deepcopy(baseline);gated['codi_beta_maintenance']=True
  kw=dict(owner_uid=os.getuid(),owner_gid=os.getgid(),caddy_uid=os.getuid(),caddy_gid=os.getgid())
  def create(a,b,**flags):return inventory.RenderInventory(self.root/'hosting',self.root/'etc-caddy',newgen,newgen,a,b,**kw,**flags)
  obj=create(baseline,gated,maintenance_only=True);self.assertEqual(len(obj.targets),14)
  before={p:p.read_bytes() for p in self.obj.targets}
  invalid=[]
  v=copy.deepcopy(gated);v['codi_beta_simplified']='b'*64;invalid.append(v)
  v=copy.deepcopy(gated);v['sites'][0]['description']='changed';invalid.append(v)
  v=copy.deepcopy(gated);v['codi_shared_ingress']=False;invalid.append(v)
  v=copy.deepcopy(gated);v['unexpected_new_top_level']='unsafe';invalid.append(v)
  v=copy.deepcopy(gated);v['codi_beta_maintenance']='yes';invalid.append(v)
  v=copy.deepcopy(gated);del v['codi_beta_maintenance'];invalid.append(v)
  for v in invalid:
   with self.assertRaises(ValueError):create(baseline,v,maintenance_only=True)
  invalid_old=copy.deepcopy(baseline);invalid_old['codi_beta_maintenance']=0
  with self.assertRaises(ValueError):create(invalid_old,gated,maintenance_only=True)
  with self.assertRaises(ValueError):create(baseline,gated)
  with self.assertRaises(ValueError):create(baseline,gated,baseline_only=True,maintenance_only=True)
  self.assertEqual(before,{p:p.read_bytes() for p in self.obj.targets})
 def test_normalization_only_and_negative_controls(self):
  before=copy.deepcopy(self.obj.newdata);assert 'codi_beta_maintenance' not in before
  after=copy.deepcopy(before);after['codi_beta_maintenance']=False
  kw=dict(owner_uid=os.getuid(),owner_gid=os.getgid(),caddy_uid=os.getuid(),caddy_gid=os.getgid())
  def create(a,b,oldgen=newgen,nextgen=newgen,**flags):return inventory.RenderInventory(self.root/'hosting',self.root/'etc-caddy',oldgen,nextgen,a,b,**kw,**flags)
  obj=create(before,after,normalize_maintenance=True);assert all(a==b for a,b,_ in obj.targets.values())
  original={p:p.read_bytes() for p in self.obj.targets};bad=[]
  v=copy.deepcopy(after);v['codi_beta_simplified']='b'*64;bad.append((before,v))
  v=copy.deepcopy(after);v['codi_beta_maintenance']=True;bad.append((before,v))
  v=copy.deepcopy(after);v['codi_beta_maintenance']=0;bad.append((before,v))
  v=copy.deepcopy(after);del v['codi_beta_maintenance'];bad.append((before,v))
  v=copy.deepcopy(after);v['sites'][0]['description']='changed';bad.append((before,v))
  v=copy.deepcopy(after);v['unexpected']='anything';bad.append((before,v))
  v=copy.deepcopy(before);v['codi_beta_maintenance']=False;bad.append((v,after))
  for a,b in bad:
   with self.assertRaises(ValueError):create(a,b,normalize_maintenance=True)
  with self.assertRaises(ValueError):create(before,after)
  class Different:
   validate=staticmethod(newgen.validate)
   caddy=staticmethod(lambda data,mode:newgen.caddy(data,mode)+'\n# changed')
   unit=staticmethod(newgen.unit)
  with self.assertRaisesRegex(ValueError,'changed generated output'):create(before,after,nextgen=Different,normalize_maintenance=True)
  class DifferentUnit:
   validate=staticmethod(newgen.validate)
   caddy=staticmethod(newgen.caddy)
   unit=staticmethod(lambda site:newgen.unit(site)+'\n# changed')
  with self.assertRaisesRegex(ValueError,'changed generated output'):create(before,after,nextgen=DifferentUnit,normalize_maintenance=True)
  self.assertEqual(original,{p:p.read_bytes() for p in self.obj.targets})
 def test_opfs_only_inventory_requires_exact_candidate_and_beta_only_output(self):
  before=copy.deepcopy(self.obj.newdata);before['codi_beta_maintenance']=False
  after=copy.deepcopy(before);after['codi_beta_opfs']='3ad04c48e60caa559e7b4c56ff624b50a23c093f0dacbc339ca8df147fd009bc'
  # Existing guarded loader is necessary to preserve the v1 floor.
  overlay='1'*64;before['codi_beta_active_overlay']=overlay;before['codi_beta_retained_overlays']=[overlay+':'+'2'*64+':'+'3'*64];after=copy.deepcopy(before);after['codi_beta_opfs']='3ad04c48e60caa559e7b4c56ff624b50a23c093f0dacbc339ca8df147fd009bc'
  kw=dict(owner_uid=os.getuid(),owner_gid=os.getgid(),caddy_uid=os.getuid(),caddy_gid=os.getgid())
  def create(a,b,nextgen=newgen,**flags):return inventory.RenderInventory(self.root/'hosting',self.root/'etc-caddy',newgen,nextgen,a,b,**kw,**flags)
  result=create(before,after,opfs_only=True);self.assertEqual(len(result.targets),14)
  original={p:p.read_bytes() for p in self.obj.targets}
  for mut in ('candidate','release','main','maintenance','overlay'):
   x=copy.deepcopy(after)
   if mut=='candidate':x['codi_beta_opfs']='a'*64
   if mut=='release':x['codi_beta_simplified']='b'*64
   if mut=='main':x['sites'][0]['description']='changed'
   if mut=='maintenance':x['codi_beta_maintenance']=True
   if mut=='overlay':x['codi_beta_active_overlay']='4'*64
   with self.assertRaises(ValueError):create(before,x,opfs_only=True)
  with self.assertRaises(ValueError):create(before,after)
  class Different:
   validate=staticmethod(newgen.validate)
   caddy=staticmethod(lambda data,mode:newgen.caddy(data,mode).replace('python.coach {','python.coach {\n respond 500',1))
   unit=staticmethod(newgen.unit)
  with self.assertRaisesRegex(ValueError,'non-beta output'):create(before,after,nextgen=Different,opfs_only=True)
  self.assertEqual(original,{p:p.read_bytes() for p in self.obj.targets})
 def test_gated_opfs_inventory_restricts_exact_exit(self):
  before=copy.deepcopy(self.obj.newdata);before['codi_beta_maintenance']=True;overlay='1'*64;before['codi_beta_active_overlay']=overlay;before['codi_beta_retained_overlays']=[overlay+':'+'2'*64+':'+'3'*64]
  after=copy.deepcopy(before);after['codi_beta_maintenance']=False;after['codi_beta_opfs']='3ad04c48e60caa559e7b4c56ff624b50a23c093f0dacbc339ca8df147fd009bc'
  kw=dict(owner_uid=os.getuid(),owner_gid=os.getgid(),caddy_uid=os.getuid(),caddy_gid=os.getgid())
  def create(a,b,**flags):return inventory.RenderInventory(self.root/'hosting',self.root/'etc-caddy',newgen,newgen,a,b,**kw,**flags)
  obj=inventory.RenderInventory(self.root/'hosting',self.root/'etc-caddy',livegen,newgen,before,after,**kw,opfs_from_gate=True);self.assertEqual(len(obj.targets),14);original={p:p.read_bytes() for p in self.obj.targets}
  for change in ('release','main','overlay','wronghash','stillgate'):
   x=copy.deepcopy(after)
   if change=='release':x['codi_beta_simplified']='b'*64
   if change=='main':x['sites'][0]['description']='changed'
   if change=='overlay':x['codi_beta_active_overlay']='4'*64
   if change=='wronghash':x['codi_beta_opfs']='a'*64
   if change=='stillgate':x['codi_beta_maintenance']=True
   with self.assertRaises(ValueError):create(before,x,opfs_from_gate=True)
  with self.assertRaises(ValueError):create(before,after)
  class DuplicateBeta:
   validate=staticmethod(newgen.validate)
   caddy=staticmethod(lambda data,mode:newgen.caddy(data,mode)+'\nbeta.ksu.codes {\n respond 200\n}\n')
   unit=staticmethod(newgen.unit)
  with self.assertRaisesRegex(ValueError,'Exactly one beta'):inventory.RenderInventory(self.root/'hosting',self.root/'etc-caddy',livegen,DuplicateBeta,before,after,**kw,opfs_from_gate=True)
  notgated=copy.deepcopy(before);notgated['codi_beta_maintenance']=False
  with self.assertRaises(ValueError):create(notgated,after,opfs_from_gate=True)
  self.assertEqual(original,{p:p.read_bytes() for p in self.obj.targets})
 def test_opfs_to_gate_inventory_is_explicit_and_restricts_destination(self):
  after=copy.deepcopy(self.obj.newdata);after['codi_beta_maintenance']=True;overlay='1'*64;after['codi_beta_active_overlay']=overlay;after['codi_beta_retained_overlays']=[overlay+':'+'2'*64+':'+'3'*64]
  before=copy.deepcopy(after);before['codi_beta_maintenance']=False;before['codi_beta_opfs']='3ad04c48e60caa559e7b4c56ff624b50a23c093f0dacbc339ca8df147fd009bc'
  kw=dict(owner_uid=os.getuid(),owner_gid=os.getgid(),caddy_uid=os.getuid(),caddy_gid=os.getgid())
  def create(a,b,**flags):return inventory.RenderInventory(self.root/'hosting',self.root/'etc-caddy',newgen,livegen,a,b,**kw,**flags)
  obj=create(before,after,opfs_to_gate=True);self.assertEqual(len(obj.targets),14);original={p:p.read_bytes() for p in self.obj.targets}
  for change in ('release','main','overlay','notgate','retainedopfs'):
   x=copy.deepcopy(after)
   if change=='release':x['codi_beta_simplified']='b'*64
   if change=='main':x['sites'][0]['description']='changed'
   if change=='overlay':x['codi_beta_active_overlay']='4'*64
   if change=='notgate':x['codi_beta_maintenance']=False
   if change=='retainedopfs':x['codi_beta_opfs']=before['codi_beta_opfs']
   with self.assertRaises(ValueError):create(before,x,opfs_to_gate=True)
  with self.assertRaises(ValueError):create(before,after)
  self.assertEqual(original,{p:p.read_bytes() for p in self.obj.targets})
 def test_links_and_metadata_refused(self):
  p=next(iter(self.obj.targets));p.unlink();p.symlink_to(self.root/'outside')
  with self.assertRaises(OSError):self.obj.check(self.obj.newdata)
  p.unlink();p.write_bytes(self.obj.targets[p][0]);p.chmod(0o600)
  with self.assertRaisesRegex(ValueError,'Unexpected generated'):self.obj.check(self.obj.newdata)
if __name__=='__main__':unittest.main(verbosity=2)
