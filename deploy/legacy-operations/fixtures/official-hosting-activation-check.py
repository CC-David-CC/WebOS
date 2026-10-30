#!/usr/bin/env python3
"""Fault-test hosting activation against temporary files and mocked controller."""
import contextlib,hashlib,importlib.util,io,json,tempfile
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[2];spec=importlib.util.spec_from_file_location('activate',ROOT/'scripts/activate-official-hosting.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
with tempfile.TemporaryDirectory() as tmp:
 root=Path(tmp);(root/'ops').mkdir();(root/'.controller.lock').touch();m.HOST=root;m.COMMON=root/'ops/common.py';m.MANIFEST=root/'sites.toml';m.CADDY=root/'Caddyfile';candidate=root/'candidate.py'
 old=b'old-generator';new=b'new-generator';manifest={'sites':[{'domain':'ksu.codes'}]};m.COMMON.write_bytes(old);m.MANIFEST.write_text(json.dumps(manifest));m.CADDY.write_bytes(b'old');candidate.write_bytes(new);m.BEFORE_COMMON=hashlib.sha256(old).hexdigest();m.BEFORE_MANIFEST=m.sha(m.MANIFEST);m.CANDIDATE=hashlib.sha256(new).hexdigest()
 class Common:
  def load(self):return json.loads(m.MANIFEST.read_text())
  def caddy(self,data,mode):return 'new' if data['sites'][0].get('codi_official') else 'old'
 common=Common()
 class Controller:
  fail=False
  def snapshot(self,path):return root/('backup-'+path.name)
  def owner(self):return SimpleNamespace(pw_uid=0,pw_gid=0)
  def write(self,path,data,*args):Path(path).write_bytes(data if isinstance(data,bytes) else data.encode())
  def caddy_apply(self,data,mode):
   m.CADDY.write_text(common.caddy(data,mode))
   if self.fail:self.fail=False;raise RuntimeError('injected apply failure')
  def save_manifest(self,data):m.MANIFEST.write_text(json.dumps(data))
 controller=Controller()
 with patch.object(m.os,'geteuid',return_value=0),patch.object(m.socket,'gethostname',return_value='box-webhost'),patch.object(m,'modules',return_value=(common,controller)),contextlib.redirect_stdout(io.StringIO()):
  controller.fail=True
  try:m.main(candidate);raise AssertionError('injected failure was ignored')
  except RuntimeError as e:assert 'injected' in str(e)
  assert m.COMMON.read_bytes()==old and json.loads(m.MANIFEST.read_text())==manifest and m.CADDY.read_bytes()==b'old'
  m.main(candidate);assert m.COMMON.read_bytes()==new and json.loads(m.MANIFEST.read_text())['sites'][0]['codi_official'] is True and m.CADDY.read_bytes()==b'new'
  try:m.main(candidate);raise AssertionError('changed hosting pins accepted')
  except ValueError:pass
print('PASS: apply, injected post-apply rollback, and changed-state refusal (mocked controller)')
