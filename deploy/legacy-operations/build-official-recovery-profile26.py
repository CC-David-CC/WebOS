#!/usr/bin/env python3
"""Add official journal recovery to a local sealed profile26 candidate."""
import importlib.util,json,shutil,sys
from pathlib import Path
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[1];BASE=ROOT/'.build/releases/official-managed-profile26-candidate-r1';OUT=ROOT/'.build/releases/official-recovery-profile26-candidate-r4'
def load(p):
 s=importlib.util.spec_from_file_location('official_contract',p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
assert load(BASE/'origin_service/release.py').verify(BASE)['manifestSHA256']=='846047934950e39755f9757d1ed1a7d098355b857d2fbd14829709927ac8fc91';assert not OUT.exists();shutil.copytree(BASE,OUT)
try:
 contractfile=OUT/'origin_service/release.py';s=contractfile.read_text();needle="'codi-connected-development/26':V19_NATIVE|{'origin_service/official_authority.py'}";assert s.count(needle)==1;s=s.replace(needle,"'codi-connected-development/26':V19_NATIVE|{'origin_service/official_authority.py','origin_service/official_management.py','origin_service/official_backend_custody.py'}");contractfile.write_text(s)
 maintenance=OUT/'origin_service/maintenance.py';s=maintenance.read_text();needle=" if initial.get('version')=='codi-hosted-rooms-transition/1':\n";assert s.count(needle)==1;s=s.replace(needle," if initial.get('version')=='codi-official-issuer-transition/1':\n  from origin_service import official_management\n  return official_management.recover(op,config,config_path)\n"+needle);maintenance.write_text(s)
 module=OUT/'origin_service/official_management.py';shutil.copyfile(ROOT/'origin_service/official_management.py',module)
 custody=OUT/'origin_service/official_backend_custody.py';shutil.copyfile(ROOT/'origin_service/official_backend_custody.py',custody)
 manager=OUT/'scripts/manage-services.py';s=manager.read_text()
 needle="'recover-guest-signin','configure-hosted-rooms']";assert s.count(needle)==1;s=s.replace(needle,"'recover-guest-signin','configure-hosted-rooms','configure-official-channels']")
 needle="  if name=='configure-hosted-rooms':\n";assert s.count(needle)==1;s=s.replace(needle,"  if name=='configure-official-channels':\n   cmd.add_argument('--disable',action='store_true');cmd.add_argument('--backend-port',type=int);cmd.add_argument('--backend-unit');cmd.add_argument('--backend-unit-path',type=Path);cmd.add_argument('--backend-unit-sha256');cmd.add_argument('--backend-uid',type=int);cmd.add_argument('--backend-argv',action='append')\n"+needle)
 needle="    elif args.action=='configure-hosted-rooms':\n";assert s.count(needle)==1;s=s.replace(needle,"    elif args.action=='configure-official-channels':\n     from origin_service import official_management\n     values=(args.backend_port,args.backend_unit,args.backend_unit_path,args.backend_unit_sha256,args.backend_uid,args.backend_argv)\n     if args.disable and any(value is not None for value in values):raise ValueError('Disable cannot configure an official backend')\n     if not args.disable and any(value is None for value in values):raise ValueError('Explicit official backend custody pins required')\n     pins=None if args.disable else dict(unit=args.backend_unit,unit_path=args.backend_unit_path,unit_sha256=args.backend_unit_sha256,uid=args.backend_uid,argv=args.backend_argv)\n     result=official_management.configure(sys.modules[__name__],config,args.config,not args.disable,backend_port=args.backend_port,backend_custody=pins)\n"+needle)
 needle="'network-failed-rolled-back'):raise SystemExit(1)";assert s.count(needle)==1;s=s.replace(needle,"'network-failed-rolled-back','official-switch-rolled-back'):raise SystemExit(1)")
 manager.write_text(s)
 contract=load(contractfile);manifest=OUT/'connected-release.json';value=json.loads(manifest.read_text())
 for p in (contractfile,maintenance,module,custody,manager):value['files'][str(p.relative_to(OUT))]=contract.record(p)
 manifest.write_text(json.dumps(value,indent=2)+'\n');print(json.dumps({'status':'PASS','release':contract.verify(OUT),'enableActionAvailable':True},indent=2))
except BaseException:
 shutil.rmtree(OUT);raise
