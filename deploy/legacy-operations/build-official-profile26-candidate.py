#!/usr/bin/env python3
"""Build a profile-26 official-issuer candidate from the exact profile-25 release.

This is not a managed deployment: manager compatibility is developed separately.
"""
import hashlib,importlib.util,json,shutil,sys
from pathlib import Path
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'.build/releases/relay-rotation-live-candidate-r1'
DEST=ROOT/'.build/releases/official-issuer-profile26-candidate-r1'
PIN='08262f77465025a138d893e49483a57cca4e3e1327b6b20a96fad7f5221d5f7b'
def module(path):
 spec=importlib.util.spec_from_file_location('candidate_release_contract',path);value=importlib.util.module_from_spec(spec);spec.loader.exec_module(value);return value
assert module(BASE/'origin_service/release.py').verify(BASE)['manifestSHA256']==PIN
assert not DEST.exists();shutil.copytree(BASE,DEST)
try:
 verifier=DEST/'origin_service/release.py';s=verifier.read_text();s=s.replace('range(1,26)','range(1,27)');needle="'codi-connected-development/25':V19_NATIVE}";assert s.count(needle)==1;s=s.replace(needle,"'codi-connected-development/25':V19_NATIVE,'codi-connected-development/26':V19_NATIVE|{'origin_service/official_authority.py'}}");needle=" if manifest['version']=='codi-connected-development/25':verify_hosted_mail_graph(directory,frontend)";assert s.count(needle)==1;s=s.replace(needle," if manifest['version'] in ('codi-connected-development/25','codi-connected-development/26'):verify_hosted_mail_graph(directory,frontend)");verifier.write_text(s)
 launcher=DEST/'scripts/serve-connected.py';s=launcher.read_text();needle="    p.add_argument('--user-files',action='store_true',help='Enable registered-only file identity confirmations; the separate file gateway is required')\n";assert s.count(needle)==1;s=s.replace(needle,needle+"    p.add_argument('--official-channels',action='store_true',help='Enable official-history identity confirmations')\n");needle="            if a.guest_network_policy_sha256 is not None:\n                from origin_service.guest_authority import GuestAuthority\n";assert s.count(needle)==1;s=s.replace(needle,"            if a.official_channels:\n                from origin_service.official_authority import OfficialAuthority\n                application=OfficialAuthority(service,application)\n"+needle);launcher.write_text(s)
 authority=DEST/'origin_service/official_authority.py';shutil.copyfile(ROOT/'origin_service/official_authority.py',authority);contract=module(verifier)
 manifest=DEST/'connected-release.json';value=json.loads(manifest.read_text());value['version']='codi-connected-development/26'
 for p in (verifier,launcher,authority):value['files'][str(p.relative_to(DEST))]=contract.record(p)
 manifest.write_text(json.dumps(value,indent=2)+'\n');result=contract.verify(DEST);assert contract.verify(BASE)['manifestSHA256']==PIN
 print(json.dumps({'status':'PASS','candidate':result,'base':PIN,'managedInstallSupported':False},indent=2))
except BaseException:
 shutil.rmtree(DEST);raise
