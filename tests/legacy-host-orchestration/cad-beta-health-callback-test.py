#!/usr/bin/env python3
"""Exercise actual signed-health custody callback twice on one bound launcher."""
import hashlib,importlib.util,json,pathlib,sys,types
sys.dont_write_bytecode=True
root=pathlib.Path(__file__).resolve().parents[1]
def load(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
switch=load('cad_switch',root/'research/cad-source-access/beta-switch.py')
health=load('health','/tmp/codi-cad-beta-actor-base/ops/beta_files_host_health.py')
identity={'issuer':'fixture'};policy=json.dumps(identity).encode();health.POLICY_SHA=hashlib.sha256(policy).hexdigest();health.UNITS={}
class Launcher:
 def __init__(self):self.calls=[]
 def main_ready(self,*pins):self.calls.append(pins)
 def protected(self,path):pass
 def read(self,path,*args):return policy
 def verify_beta_worker(self,*args):pass
 def get(self,*args):return 200,json.dumps({'identity':identity,'fileStorage':{'version':'codi-browser-file-content/1','backend':'opfs','databaseVersion':2}}).encode()
class Signed:
 class SignedHealth:
  def __init__(self,**kw):self.kw=kw
  def __call__(self):self.kw['check_custody']();return {'ok':True}
launcher=Launcher();original=launcher.main_ready;bound=switch.bind_main_launcher(launcher)
pre=types.SimpleNamespace(protected_ancestors=lambda *_:None,tree=lambda *_:None);lock=types.SimpleNamespace(check=lambda:None)
run=health.create(lock=lock,launcher=bound,preflight=pre,signed_health=Signed,jose=None)
assert run()=={'ok':True} and run()=={'ok':True}
assert len(launcher.calls)==4 and all(len(x)==2 for x in launcher.calls)
assert launcher.main_ready==original
print('PASS actual custody callback twice with same nonmutating bound launcher; external services stubbed')
