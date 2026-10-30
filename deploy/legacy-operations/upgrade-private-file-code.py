#!/usr/bin/env python3
"""Scoped private-files code upgrade using existing native/file operators.

Only worker code and its two managed pins change. A private journal permits code
recovery after interruption; no account, permission or file data is restored.
"""
import argparse,base64,hashlib,importlib.util,json,os,sys
from pathlib import Path

def digest(raw):return hashlib.sha256(raw).hexdigest()
def load(name,path):
 spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);sys.modules[name]=m;spec.loader.exec_module(m);return m

def execute(config,expected,worker=None,worker_pin=None,recover=False,phase=lambda name:None):
 config=Path(config);journal=config.parent/'private-file-code.json'
 if os.geteuid()!=0:raise ValueError('Protected root operator required')
 if recover:
  j=json.loads(journal.read_text());assert j['version']=='codi-private-file-code/1';before=j['nativeBefore'];assert before['manifestSHA256']==expected
 else:before=json.loads(config.read_text())
 release=Path(before['release']);raw=(release/'connected-release.json').read_bytes();assert digest(raw)==expected==before['manifestSHA256'];manifest=json.loads(raw)
 for p in [release,*release.parents,*release.rglob('*')]:
  info=p.lstat();assert not p.is_symlink() and info.st_uid==0 and not info.st_mode&0o022
  if p.is_file() and p.is_relative_to(release) and p.name!='connected-release.json':assert manifest['files'][str(p.relative_to(release))]=={'bytes':info.st_size,'sha256':digest(p.read_bytes())}
 op=load('private_file_native_operator',release/'scripts/manage-services.py')
 from origin_service import maintenance
 with op.locked(config):
  if recover:
   assert op.read_owned(journal,0,0o600);j=json.loads(journal.read_text());before=j['nativeBefore']
  else:
   assert not journal.exists();current=op.load(config);assert current==before;maintenance.require_clean(op,config);maintenance.guard(op,current,config)
  file_module=load('private_file_existing_operator',Path(before['userFiles']['operatorRelease'])/'file_service/operator.py');m=file_module.Manager(Path(before['userFiles']['configFile']).parent)
  if not recover:
   with m.locked():
    old=m.load();after={**old,'release':str(Path(worker).absolute()),'manifestSHA256':worker_pin};m.validate(after);m.check_units(old);assert all(v['ActiveState']=='active' for v in m.states(old).values())
    file_raw=(json.dumps(after,sort_keys=True,indent=2)+'\n').encode();native_after={**before,'userFiles':{**before['userFiles'],'configSHA256':digest(file_raw)}}
    j={'version':'codi-private-file-code/1','phase':'prepared','nativeBefore':before,'nativeAfter':native_after,'fileBefore':old,'fileAfter':after,'nativeRaw':base64.b64encode(config.read_bytes()).decode(),'fileRaw':base64.b64encode(m.config_path.read_bytes()).decode(),'permissionBaseline':m.baseline(old)}
   op.atomic(journal,(json.dumps(j,indent=2)+'\n').encode());phase('prepared')
  # An interrupted pre-commit transition restores only the old code/config pins.
  forward=not recover or j['phase']=='committed';target=j['fileAfter'] if forward else j['fileBefore'];native=j['nativeAfter'] if forward else j['nativeBefore']
  def apply(file_config,native_config):
   op.stop(before,['issuer'])
   with m.locked():
    file_module.systemctl('stop',*reversed(m.names(j['fileBefore'])));m.inactive(j['fileBefore'])
    m.validate(file_config)
    for name,data in m.units(file_config).items():
     p=Path(file_config['unitDir'])/name;existing=file_module.read(p,0o644);assert existing in [m.units(j['fileBefore'])[name],m.units(j['fileAfter'])[name]]
     file_module.atomic(p,data,0o644)
    file_data=(json.dumps(file_config,sort_keys=True,indent=2)+'\n').encode() if file_config==j['fileAfter'] else base64.b64decode(j['fileRaw'])
    file_module.atomic(m.config_path,file_data);file_module.systemctl('daemon-reload');m.load();assert m.baseline(file_config)==j['permissionBaseline']
   phase('files-configured')
   native_data=(json.dumps(native_config,indent=2)+'\n').encode() if native_config==j['nativeAfter'] else base64.b64decode(j['nativeRaw']);op.atomic(config,native_data)
   phase('pins-configured')
   op.installed(native_config)
   with m.locked():m.start()
   op.systemctl('start',op.unit(native_config,'issuer'));op.ready(native_config,['issuer'])
  try:
   apply(target,native);phase('ready')
   if forward:j['phase']='committed';op.atomic(journal,(json.dumps(j,indent=2)+'\n').encode());phase('committed')
  except BaseException:
   if not recover:apply(j['fileBefore'],before)
   raise
  result={'status':'upgraded' if forward else 'code-recovered','workerManifestSHA256':target['manifestSHA256'],'nativeManifestSHA256':expected,'nativeConfigSHA256':digest(config.read_bytes()),'fileConfigSHA256':digest(m.config_path.read_bytes()),'accountOrFileDataRestored':False,'permissionBindingsPreserved':True,'otherNativeRolesRestarted':False}
  op.atomic(config.parent/'private-file-code-last.json',(json.dumps(result,indent=2)+'\n').encode());journal.unlink();maintenance.sync_directory(config.parent);return result

if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('action',choices=['upgrade','recover']);p.add_argument('--config',type=Path,required=True);p.add_argument('--native-manifest-sha256',required=True);p.add_argument('--worker',type=Path);p.add_argument('--worker-manifest-sha256');a=p.parse_args()
 if a.action=='upgrade' and (not a.worker or not a.worker_manifest_sha256):p.error('Exact protected worker and manifest required')
 print(json.dumps(execute(a.config,a.native_manifest_sha256,a.worker,a.worker_manifest_sha256,recover=a.action=='recover'),indent=2))
