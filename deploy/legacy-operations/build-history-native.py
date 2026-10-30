#!/usr/bin/env python3
"""Native24 policy-history repair over immutable native23, identical public assets."""
import argparse
import importlib.util
import json
from pathlib import Path
import shutil
import tempfile

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'.build/releases/connected-reader-directory-native-r2'
PIN='a2086017e7dcc87a7c1126bb7c71b62fd5ae0e7c1f94567444491850d1862a34'
CHANGED={'origin_service/release.py','origin_service/deployment.py','origin_service/turn_management.py','origin_service/room_management.py','scripts/manage-services.py'}

def module(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m

def patch_history(s,n):
 start=s.index('JOURNAL=');s=s[:start]+'HISTORY_MAXIMUM=4*1048576\n'+s[start:]
 old='h=json.loads(op.read_owned(p,0,0o600))'if n=='room'else'value=json.loads(op.read_owned(file,0,0o600))'
 assert s.count(old)==1;s=s.replace(old,old[:-2]+',HISTORY_MAXIMUM))')
 name='rooms'if n=='room'else n;path='path'if n=='room'else'config_path';value='h'if n=='room'else'value';old="write(op,slot("+path+",'"+name+"-history.json'),"+value+")";assert s.count(old)==1;s=s.replace(old,'write_history'+old[5:])
 helper="""def write_history(op,path,value):
    raw=(json.dumps(value,sort_keys=True,indent=2)+'\\n').encode()
    if len(raw)>HISTORY_MAXIMUM:raise ValueError('Policy history exceeds bounded storage')
    op.atomic(path,raw)

""";s=s.replace('def history(op,config,config_path):',helper+'def history(op,config,config_path):')
 indent=' 'if n=='turn'else'    ';start=s.index('def configure(');loc=s.index('\n'+indent,start)+1;call='history(op,c,path)'if n=='room'else'history(op,config,config_path)';s=s[:loc]+indent+call+'\n'+s[loc:];return s

def build(dest):
 util=module('history_build_records',ROOT/'scripts/build-native-app-update.py');old=module('history_old_contract',BASE/'origin_service/release.py');assert old.verify(BASE)['manifestSHA256']==PIN
 dest=dest.resolve();assert not dest.exists() and dest.is_relative_to(ROOT/'.build/releases');stage=Path(tempfile.mkdtemp(prefix='.native-history-',dir=dest.parent))
 try:
  shutil.copytree(BASE,stage,dirs_exist_ok=True)
  for name in ['room']:
   p=stage/('origin_service/'+name+'_management.py');p.write_text(patch_history(p.read_text(),name))
  def extend(s):
   needle="'codi-connected-development/23')";assert needle in s;return s.replace(needle,"'codi-connected-development/23','codi-connected-development/24')")
  for name in ['origin_service/deployment.py','origin_service/turn_management.py','scripts/manage-services.py']:
   p=stage/name;p.write_text(extend(p.read_text()).replace('profile-5..23','profile-5..24'))
  p=stage/'origin_service/release.py';s=p.read_text();s=s.replace('range(1,24)','range(1,25)').replace("'codi-connected-development/23':V19_NATIVE}","'codi-connected-development/23':V19_NATIVE,'codi-connected-development/24':V19_NATIVE}")
  anchor=" if manifest['version']=='codi-connected-development/23':verify_hosted_directory_graph(directory,frontend)";assert s.count(anchor)==1;s=s.replace(anchor,anchor+"\n if manifest['version']=='codi-connected-development/24':verify_hosted_directory_graph(directory,frontend)");p.write_text(s)
  full=json.loads((BASE/'connected-release.json').read_bytes());full['version']='codi-connected-development/24';full['files']={str(p.relative_to(stage)):util.record(p)for p in sorted(stage.rglob('*'))if p.is_file() and p.name!='connected-release.json'};(stage/'connected-release.json').write_bytes(util.encoded(full))
  check=module('history_final_contract',stage/'origin_service/release.py').verify(stage);before=json.loads((BASE/'connected-release.json').read_bytes())['files'];changed={n for n,v in before.items()if full['files'][n]!=v};assert changed==CHANGED
  stage.rename(dest);return dict(status='PASS',manifestSHA256=check['manifestSHA256'],files=check['files'],nativeChanged=sorted(changed),publicAssetsChanged=False,baseManifestSHA256=PIN,installed=False)
 finally:
  if stage.exists():shutil.rmtree(stage)

if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args();print(json.dumps(build(a.output),indent=2))
