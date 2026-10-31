#!/usr/bin/env python3
"""Create exact-live-derived issuer and file-worker candidates; no activation."""
import argparse,hashlib,importlib.util,json,os,shutil,sys,tempfile
from pathlib import Path
ISSUER_BASE='0aaf61849fa03e41376d63a36496c83e83adbc97c14aeafe366100ff9e530af2'
WORKER_BASE='8ed6e9ab142e00b58c5902bb0be8e8b608b43a4cd630dc86ee15477f9c0dc576'
ISSUER_OLD='ba0dc2591bd3131b739aff1137b7372388dedc2a64426fbb822458967e506eef'
CLIENT_OLD='216c5b99e29cb55ce79c9b9e16a099bbbc1dcd60f0c14949aac0c1e8075c2f8e'
def sha(data):return hashlib.sha256(data).hexdigest()
def verifier(root):
 spec=importlib.util.spec_from_file_location('pinned_connected_release',root/'origin_service/release.py');module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module
def worker_manifest(root):
 raw=(root/'files-service.json').read_bytes();manifest=json.loads(raw)
 if manifest.get('version')!='codi-private-file-service/1' or not isinstance(manifest.get('files'),dict):raise ValueError('Invalid worker manifest')
 found=set()
 for p in root.rglob('*'):
  if p.is_symlink():raise ValueError('Worker has a symbolic link')
  if not p.is_file():continue
  name=p.relative_to(root).as_posix()
  if name=='files-service.json':continue
  data=p.read_bytes()
  if manifest['files'].get(name)!={'bytes':len(data),'sha256':sha(data)}:raise ValueError('Worker file differs: '+name)
  found.add(name)
 if found!=set(manifest['files']):raise ValueError('Worker files missing')
 return sha(raw),manifest
def create(base,out,manifest_name,manifest,name,source):
 if out.exists() or out.is_symlink() or not out.parent.is_dir() or base in out.parents or out in base.parents:raise ValueError('Choose a new disjoint output')
 stage=Path(tempfile.mkdtemp(prefix='.file-admission-',dir=out.parent))
 try:
  shutil.copytree(base,stage,dirs_exist_ok=True);content=source.read_bytes();(stage/name).write_bytes(content)
  manifest['files'][name]={'bytes':len(content),'sha256':sha(content)}
  (stage/manifest_name).write_text(json.dumps(manifest,indent=2,sort_keys=manifest_name=='files-service.json')+'\n')
  for p in [stage,*stage.rglob('*')]:p.chmod(0o755 if p.is_dir() else 0o644)
  stage.rename(out)
 finally:
  if stage.exists():shutil.rmtree(stage)
def main():
 p=argparse.ArgumentParser(description=__doc__)
 for arg in ('issuer-base','issuer-output','worker-base','worker-output','issuer-source','client-source'):p.add_argument('--'+arg,type=Path,required=True)
 p.add_argument('--issuer-source-sha256',required=True);p.add_argument('--client-source-sha256',required=True);a=p.parse_args()
 ib=a.issuer_base.resolve();wb=a.worker_base.resolve();io=a.issuer_output.absolute();wo=a.worker_output.absolute()
 if sha(a.issuer_source.read_bytes())!=a.issuer_source_sha256 or sha(a.client_source.read_bytes())!=a.client_source_sha256:raise ValueError('Candidate source hash mismatch')
 if verifier(ib).verify(ib)['manifestSHA256']!=ISSUER_BASE or sha((ib/'origin_service/gateway_authority.py').read_bytes())!=ISSUER_OLD:raise ValueError('Unexpected issuer baseline')
 wp,wm=worker_manifest(wb)
 if wp!=WORKER_BASE or sha((wb/'gateway_service/client.mjs').read_bytes())!=CLIENT_OLD:raise ValueError('Unexpected worker baseline')
 create(ib,io,'connected-release.json',json.loads((ib/'connected-release.json').read_text()),'origin_service/gateway_authority.py',a.issuer_source)
 try:
  issuer=verifier(io).verify(io);create(wb,wo,'files-service.json',wm,'gateway_service/client.mjs',a.client_source);worker,_=worker_manifest(wo)
 except Exception:
  shutil.rmtree(io);raise
 print(json.dumps({'issuer':issuer,'worker':{'directory':str(wo),'manifestSHA256':worker},'changed':['origin_service/gateway_authority.py','gateway_service/client.mjs']},indent=2))
if __name__=='__main__':sys.dont_write_bytecode=True;main()
