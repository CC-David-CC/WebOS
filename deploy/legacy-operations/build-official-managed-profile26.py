#!/usr/bin/env python3
"""Create a local profile26 manager candidate; not an activation tool."""
import importlib.util,json,shutil,sys
from pathlib import Path
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[1];BASE=ROOT/'.build/releases/official-issuer-profile26-candidate-r1';OUT=ROOT/'.build/releases/official-managed-profile26-candidate-r1'
def load(path):
 s=importlib.util.spec_from_file_location('profile26_contract',path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
contract=load(BASE/'origin_service/release.py');assert contract.verify(BASE)['manifestSHA256']=='ded7f04fc6ed6f2b72f5a88aedd5b5669481d0616c89f0285995d93502bad237';assert not OUT.exists();shutil.copytree(BASE,OUT)
try:
 changed=[]
 for name in ('scripts/manage-services.py','origin_service/deployment.py','origin_service/turn_management.py'):
  p=OUT/name;s=p.read_text();needle="'codi-connected-development/25')";count=s.count(needle);assert count>0;s=s.replace(needle,"'codi-connected-development/25','codi-connected-development/26')")
  if name=='scripts/manage-services.py':
   needle=" if config['version'] in ('codi-managed-instance/3','codi-managed-instance/4','codi-managed-instance/5'):\n";idx=s.index(needle,s.index('def installed('));s=s[:idx]+" if config.get('officialChannels') is True and profile!='codi-connected-development/26':raise ValueError('Disable official channels before rolling back below profile26')\n"+s[idx:]
   needle="  if role=='issuer' and config.get('guestNetwork'):";assert s.count(needle)==1;s=s.replace(needle,"  if role=='issuer' and config.get('officialChannels') is True:command+=['--official-channels']\n"+needle)
   needle="   if 'userFiles' in config:expected.add('userFiles')\n";assert s.count(needle)==1;s=s.replace(needle,needle+"   if 'officialChannels' in config:\n    if type(config['officialChannels']) is not bool:raise ValueError('Official channel setting must be boolean')\n    expected.add('officialChannels')\n")
  elif name=='origin_service/deployment.py':
   needle=" target=json.loads((Path(after['release'])/'connected-release.json').read_text())['version']\n";assert s.count(needle)==1;s=s.replace(needle,needle+" if before.get('officialChannels') is True and target!='codi-connected-development/26':raise ValueError('Disable official channels before code rollback below profile26')\n")
  p.write_text(s);changed.append(name)
 manifest=OUT/'connected-release.json';value=json.loads(manifest.read_text());contract=load(OUT/'origin_service/release.py')
 for name in changed:value['files'][name]=contract.record(OUT/name)
 manifest.write_text(json.dumps(value,indent=2)+'\n');print(json.dumps({'status':'PASS','release':contract.verify(OUT),'changed':changed,'managedTransitionTested':False},indent=2))
except BaseException:
 shutil.rmtree(OUT);raise
