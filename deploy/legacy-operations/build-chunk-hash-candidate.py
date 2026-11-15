#!/usr/bin/env python3
"""Build a research chunk/incremental-hash worker from exact live code-only baseline.

Input is an already verified code-only copy of the pinned live worker. This
writes only new local directories; it never accesses account or server state.
"""
import argparse,hashlib,json,shutil,tempfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
BASE='8d977a271a776fd7265a775bc5c74d818abed9136049af3ae8adfd04cd9c0257'
OPERATOR={'file_service/__init__.py':'8431c4ea8f8f8ef59bc11e6e177da9dd3fd2adcb11cae2fb2a5056130aacbfa5','scripts/manage-user-files.py':'f6db462426f8b98e1695c18eaa386deaa7bfa51952717147ccea81814f07eafc'}
PINS={'file_service/operator.py': 'e0dcda10d7537d94d8d6bbea1466347428ec89628c812ace398a1160db558b06', 'gateway_service/http.py': '4f2bddf391995dd76d3357d55e3e0d0aa7df11ce157a76d09b41363a7575d839', 'gateway_service/client.mjs': 'c3b4c15fc6571cb28fd21ed8c7a64dad7628125d1d5ff4db253762f0448dd6de', 'gateway_service/delta.py': '43b23a4a739040888d31c7bf5c33b0c820e8f63ba0c299f72fe03b55d8e20d53', 'gateway_service/chunk_sync.py': '2dc64345968e1b44fac55169a5b0a07a67a0d1a5b1037c40064d06cc2d161e8a', 'gateway_service/vendor/js-sha256/core.mjs': '90b245475d95570135d4eba2b92717ac90350944e9ee7a5e6d595e275ebd5299', 'gateway_service/vendor/js-sha256/shared.mjs': '7399a7fe440c202f1d645230654aa86c035ac4adf072452ac718cc44efb44d9d', 'gateway_service/vendor/js-sha256/LICENSE.txt': '2153bd2978793748fbe0eb8f838ae2ae19f03f9d4ee5473dd1628a0c0790e4ab', 'gateway_service/vendor/js-sha256/verify-worker.mjs': 'a9c26f4080a93f2e606699a2495d9d63614a6bb15ebe22136c0eab05fb99070e'}
EXPECTED={'gateway_service/__init__.py','gateway_service/auth.py','gateway_service/policy.py','gateway_service/user_store.py','gateway_service/http.py','gateway_service/transfers.py','gateway_service/client.mjs','codiserver-server-v0.3.0/codiauth/__init__.py','codiserver-server-v0.3.0/codiauth/jose.py','scripts/serve-user-files.py','requirements.lock'}
CHANGED={'gateway_service/http.py','gateway_service/client.mjs','gateway_service/delta.py','gateway_service/chunk_sync.py','gateway_service/vendor/js-sha256/core.mjs','gateway_service/vendor/js-sha256/shared.mjs','gateway_service/vendor/js-sha256/LICENSE.txt','gateway_service/vendor/js-sha256/verify-worker.mjs'}
def sha(raw):return hashlib.sha256(raw).hexdigest()
def make_manifest(version,values):return (json.dumps({'version':version,'files':{name:{'bytes':len(raw),'sha256':sha(raw)} for name,raw in sorted(values.items())}},indent=2,sort_keys=True)+'\n').encode()
def write_tree(target,manifest_name,version,values):
 if target.exists() or target.is_symlink() or not target.parent.is_dir():raise ValueError('Choose a new output directory')
 stage=Path(tempfile.mkdtemp(prefix='.delta-candidate-',dir=target.parent))
 try:
  for name,data in values.items():
   p=stage/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data);p.chmod(0o644)
  raw=make_manifest(version,values);(stage/manifest_name).write_bytes(raw);(stage/manifest_name).chmod(0o644)
  for p in [stage,*(p for p in stage.rglob('*') if p.is_dir())]:p.chmod(0o755)
  stage.rename(target);return sha(raw)
 finally:
  if stage.exists():shutil.rmtree(stage)
def build(base,worker,operator):
 base=Path(base);raw=(base/'files-service.json').read_bytes()
 if sha(raw)!=BASE:raise ValueError('Live baseline manifest differs')
 old=json.loads(raw)
 if set(old)!={'version','files'} or old['version']!='codi-private-file-service/1' or set(old['files'])!=EXPECTED:raise ValueError('Unexpected baseline inventory')
 values={}
 for name,rec in old['files'].items():
  p=base/name
  if p.is_symlink() or not p.is_file():raise ValueError('Invalid baseline file')
  b=p.read_bytes()
  if rec!={'bytes':len(b),'sha256':sha(b)}:raise ValueError('Baseline file differs: '+name)
  values[name]=b
 actual={str(p.relative_to(base)) for p in base.rglob('*') if p.is_file()}
 if actual!=EXPECTED|{'files-service.json'} or any(p.is_symlink() for p in base.rglob('*')):raise ValueError('Unexpected baseline files')
 for name in CHANGED:
  p=ROOT/name
  if p.is_symlink() or not p.is_file():raise ValueError('Invalid candidate file')
  values[name]=p.read_bytes()
  if sha(values[name])!=PINS[name]:raise ValueError('Candidate source differs: '+name)
 # Insert only the reviewed identity helper into the exact live user_store;
 # do not package the unrelated unfinished source changes in this checkout.
 source=(ROOT/'gateway_service/user_store.py').read_text();a=source.index('    def file_identity(');b=source.index('    def open_read_snapshot(',a);method=source[a:b]
 if sha(method.encode())!='def7b1a7499cd27883056c49fa1f2cb24dba2ecfca61aa2f5e9b1359e61c256d':raise ValueError('Identity helper changed')
 marker='    def open_read_snapshot(self,principal,path,*,maximum_bytes):\n';base_store=values['gateway_service/user_store.py'].decode()
 if base_store.count(marker)!=1:raise ValueError('Unexpected baseline storage source')
 values['gateway_service/user_store.py']=base_store.replace(marker,method+marker).encode()
 if sha(values['gateway_service/user_store.py'])!='9ffda906997a5f71785f67914655497fbb79032c256fef2ff068ef6f0387165a':raise ValueError('Unexpected resulting storage source')
 opvalues={}
 for name,pin in OPERATOR.items():
  data=(ROOT/name).read_bytes()
  if sha(data)!=pin:raise ValueError('Unrelated operator source drift: '+name)
  opvalues[name]=data
 opvalues['file_service/operator.py']=(ROOT/'file_service/operator.py').read_bytes()
 if sha(opvalues['file_service/operator.py'])!=PINS['file_service/operator.py']:raise ValueError('Candidate operator source differs')
 workerpin=write_tree(Path(worker),'files-service.json','codi-private-file-service/1',values)
 try:operatorpin=write_tree(Path(operator),'file-operator.json','codi-file-operator/1',opvalues)
 except BaseException:shutil.rmtree(worker);raise
 return {'workerManifestSHA256':workerpin,'operatorManifestSHA256':operatorpin,'preservedLiveStore':old['files']['gateway_service/user_store.py']['sha256'],'workerChanges':sorted(CHANGED|{'gateway_service/user_store.py'}),'operatorChange':'file_service/operator.py','installed':False}
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--baseline',type=Path,required=True);p.add_argument('--worker',type=Path,required=True);p.add_argument('--operator',type=Path,required=True);a=p.parse_args();print(json.dumps(build(a.baseline,a.worker,a.operator),indent=2))
