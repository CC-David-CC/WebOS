import copy,importlib.util,os,sys,tempfile,tomllib,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];OPS=ROOT/'research/beta-isolated-hosting/ops';sys.path.insert(0,str(OPS));import common
spec=importlib.util.spec_from_file_location('main_inventory',Path(__file__).with_name('render-inventory.py'));m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
OLD='0965a0cbdd022f588061cdc23e10eb6b18fa5977cc3f6a05569439eaf11d2020';NEW='e7e8fb9fc1f964ec1b206462468f91b60e8bac1d8117ed29c5f1099abdac3480'
class Tests(unittest.TestCase):
 def test_exact_target_and_drift(self):
  old=tomllib.loads((OPS/'sites_live.toml').read_text());old['codi_beta_maintenance']=False;old['codi_beta_opfs']='3ad04c48e60caa559e7b4c56ff624b50a23c093f0dacbc339ca8df147fd009bc';new=copy.deepcopy(old);next(x for x in new['sites'] if x['domain']=='ksu.codes')['codi_simplified']=NEW
  with tempfile.TemporaryDirectory() as t:
   root=Path(t)/'hosting';etc=Path(t)/'etc';root.mkdir();etc.mkdir();args=dict(owner_uid=os.getuid(),owner_gid=os.getgid(),caddy_uid=os.getuid(),caddy_gid=os.getgid())
   inv=m.MainRenderInventory(root,etc,common,old,new,OLD,NEW,**args)
   for path,(a,b,meta) in inv.targets.items():path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(a);path.chmod(meta[2])
   inv.check(old);inv.check(new,recovery=True)
   for path,(a,b,meta) in inv.targets.items():path.write_bytes(b);path.chmod(meta[2])
   inv.check(new,after=True);p=next(iter(inv.targets));p.write_bytes(b'drift')
   with self.assertRaises(ValueError):inv.check(new,after=True)
   bad=copy.deepcopy(new);bad['codi_beta_simplified']='f'*64
   with self.assertRaises(ValueError):m.MainRenderInventory(root,etc,common,old,bad,OLD,NEW,**args)
   bad=copy.deepcopy(new);next(x for x in bad['sites'] if x['domain']=='python.coach')['workers']+=1
   with self.assertRaises(ValueError):m.MainRenderInventory(root,etc,common,old,bad,OLD,NEW,**args)
if __name__=='__main__':unittest.main(verbosity=2)
