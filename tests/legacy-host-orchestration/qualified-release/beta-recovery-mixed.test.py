"""Exact installed beta snapshot logic against synthetic mixed main states."""
import contextlib,copy,hashlib,importlib.util,json,sys,tempfile,types,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];OPS=ROOT/'research/beta-isolated-hosting/ops';sys.path.insert(0,str(OPS))
from beta_files_snapshots import build
from opfs_managed import ManagedBinding
from beta_files_assembly import FilesAssembly,IssuerInstall
for name,sha in {'beta_files_snapshots.py':'0bb2dc596120e973b0827749d600806313d2b5899cab19a7737174044d8008a8','opfs_managed.py':'9db8a944745e99a11f9dff2ebdb2298d98fa8a0e2982171bbc3e17757ba7dd6f'}.items():
 actual=hashlib.sha256((OPS/name).read_bytes()).hexdigest()
 if actual!=sha:raise ValueError('Installed beta source differs: '+name)
def load(name,path):
 spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);sys.modules[name]=m;spec.loader.exec_module(m);return m
oldmod=load('test_old_common',OPS/'common_live.py');newmod=load('test_new_common',OPS/'common.py');old=types.SimpleNamespace(source=(OPS/'common_live.py').read_bytes(),module=oldmod);new=types.SimpleNamespace(source=(OPS/'common.py').read_bytes(),module=newmod)
x=build(old=old,new=new,manifest=(OPS/'sites_live.toml').read_bytes(),candidate_manifest=(OPS/'beta_files_candidate.json').read_bytes(),route_table=(OPS.parent/'OPFS-ROUTE-TABLE.json').read_bytes())
NEW='e7e8fb9fc1f964ec1b206462468f91b60e8bac1d8117ed29c5f1099abdac3480'
class Tests(unittest.TestCase):
 def test_gate_refuses_mixed_main_states_without_route_writes(self):
  current=copy.deepcopy(x['candidateData']);next(s for s in current['sites'] if s['domain']=='ksu.codes')['codi_simplified']=NEW;new_manifest=newmod.dump(current).encode();new_caddy=newmod.caddy(current,'production').encode();candidate=x['candidate'];self.assertNotEqual(new_manifest,candidate['manifest']);self.assertNotEqual(new_caddy,candidate['caddy'])
  for manifest,caddy in [(new_manifest,candidate['caddy']),(candidate['manifest'],new_caddy),(new_manifest,new_caddy)]:
   with self.subTest(manifest=manifest==new_manifest,caddy=caddy==new_caddy):
    values={'common':candidate['common'],'manifest':manifest,'caddy':caddy};calls=[]
    def never(*args):calls.append(args);raise AssertionError('route mutation attempted')
    binding=ManagedBinding(lambda:contextlib.nullcontext(),lambda:None,{'baseline':x['normalized'],'gate':x['gate'],'candidate':candidate},never,lambda:values,lambda _:None,lambda:True,lambda *a:None,lambda:None,lambda _:None,lambda _:None,lambda _:None,never)
    self.assertFalse(binding.is_gate())
    with self.assertRaisesRegex(ValueError,'Unknown managed route state'):binding.gate()
    self.assertEqual(calls,[])
 def test_finalized_health_success_and_failure_do_not_change_mixed_routes(self):
  current=copy.deepcopy(x['candidateData']);next(s for s in current['sites'] if s['domain']=='ksu.codes')['codi_simplified']=NEW
  for failing in (False,True):
   with self.subTest(failing=failing),tempfile.TemporaryDirectory() as t:
    folder=Path(t);mixed={'common':x['candidate']['common'],'manifest':newmod.dump(current).encode(),'caddy':x['candidate']['caddy']};calls=[];floor=types.SimpleNamespace(dir=folder,io=None);issuer=types.SimpleNamespace(journal=folder/'issuer-journal');installer=IssuerInstall(issuer,b'old-unit')
    def never(*args):calls.append('mutation');raise AssertionError('unexpected mutation')
    binding=ManagedBinding(lambda:contextlib.nullcontext(),lambda:None,{'baseline':x['normalized'],'gate':x['gate'],'candidate':x['candidate']},never,lambda:mixed,lambda _:None,lambda:True,lambda *a:None,lambda:None,lambda _:None,lambda _:None,installer,never);floor.io=binding
    (folder/'opfs-floor.json').write_text(json.dumps({'version':1,'baseline':'a'*64,'candidate':'b'*64}));(folder/'opfs-floor.json').chmod(0o600)
    def health():
     calls.append('health')
     if failing:raise ValueError('synthetic health failure')
    assembly=FilesAssembly(floor=floor,issuer=issuer,installer=installer,issuer_old=b'old-unit',normal_adapter=object(),normal_journal=folder/'normal-journal',normal_old={},normal_new={},v2_health=health,pre_normalization=lambda:None,pre_normalization_recovery=lambda:None)
    if failing:
     with self.assertRaisesRegex(RuntimeError,'gate closure unverified'):assembly.recover('a'*64,'b'*64)
    else:self.assertEqual(assembly.recover('a'*64,'b'*64),'v2-verified')
    self.assertEqual(calls,['health'])
if __name__=='__main__':unittest.main(verbosity=2)
