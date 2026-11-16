#!/usr/bin/env python3
"""Isolated binding controls; host paths/services/custody are test doubles."""
import hashlib,json,sys,types
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'ops'))
import beta_files_host_health as h
policy={'issuer':h.ORIGIN,'mode':'server','authorityKeys':[{'kid':'test'}]};raw=json.dumps({'identity':policy}).encode();h.POLICY_SHA=hashlib.sha256(raw).hexdigest()
class Lock:
 held=False
 def check(self):
  if not self.held:raise ValueError('lock missing')
class Launch:
 fail=None
 def protected(self,p):
  if self.fail=='custody':raise ValueError('unsafe custody')
 def read(self,p,*args):
  if p==h.POLICY:return raw
  return b'unit'
 def verify_beta_worker(self,path,pin):
  if self.fail=='worker':raise ValueError('worker mismatch')
 def main_ready(self):pass
 def unit_state(self,n):
  role=n.removeprefix('codi-beta-').removesuffix('.service');user='codi-beta-'+role
  return {'ActiveState':'inactive' if self.fail=='service' else 'active','MainPID':'123','FragmentPath':'/etc/systemd/system/'+n,'DropInPaths':'','NeedDaemonReload':'no','User':user,'Group':user}
 def get(self,port,path):
  return 200,json.dumps({'identity':policy if self.fail!='identity' else {},'fileStorage':{'version':'codi-browser-file-content/1','backend':'opfs','databaseVersion':2}}).encode()
class Preflight:
 def protected_ancestors(self,p):pass
 def tree(self,*args):
  if launcher.fail=='native':raise ValueError('native mismatch')
class Signed:
 class SignedHealth:
  def __init__(self,**kw):self.kw=kw
  def __call__(self):self.kw['check_lock']();self.kw['check_custody']();return {'bytes':1}
h.os.geteuid=lambda:0  # fixture only; production requires actual root
lock=Lock();launcher=Launch();h.UNITS={n:hashlib.sha256(b'unit').hexdigest() for n in h.UNITS};health=h.create(lock=lock,launcher=launcher,preflight=Preflight(),signed_health=Signed,jose=types.SimpleNamespace())
try:health();raise AssertionError('missing lock accepted')
except ValueError as e:assert 'lock missing' in str(e)
lock.held=True
assert health()=={'bytes':1}
for failure in ('custody','worker','native','service','identity'):
 launcher.fail=failure
 try:health();raise AssertionError(failure+' accepted')
 except ValueError:pass
launcher.fail=None
print('PASS protected host-health binding controls (simulated host/services)')
