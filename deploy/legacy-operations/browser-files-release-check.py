#!/usr/bin/env python3
"""Run the existing 21-check real Chrome workflow using a sealed candidate core.

The fixture still provides window rendering/guest placeholders. It does not
claim a full Linux desktop, real login, mobile or live deployment test.
"""
import argparse,importlib.util,json,shutil
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def module(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def run(candidate):
 composer=module('browser_release_check_composer',ROOT/'scripts/build-browser-files-release.py');boundary=composer.verify_boundaries(ROOT/'.build/releases/connected-device-history-host-r4',candidate)
 graph=json.loads((candidate/'assets/desktop/network-release.json').read_bytes());catalog=composer.catalog(candidate)
 driver_path=ROOT/'scripts/browser-files-check.py';source=driver_path.read_text();needle="payloads={n:(ROOT/n).read_bytes() for n in"
 assert source.count(needle)==1;source=source.replace(needle,"payloads={n:candidate_payload(n) for n in")
 namespace={'__file__':str(driver_path),'__name__':'browser_files_candidate_driver'};exec(compile(source,str(driver_path),'exec'),namespace)
 def payload(n):
  return (candidate/graph['coreDirectory']/n).read_bytes() if n in ['app.js','desktop-apps.js'] else (ROOT/n).read_bytes()
 namespace['candidate_payload']=payload
 def built(source,output,apps,node):
  output.mkdir(parents=True,exist_ok=True);(output/'apps.json').write_text(json.dumps(catalog))
  for app in catalog['apps']:
   for name in app['files']:
    relative=Path(app['path']).parent/name;target=output/str(relative).removeprefix('assets/desktop/');target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(candidate/relative,target)
  return {'status':'PASS','source':'sealed immutable candidate; no app rebuild','manifestSHA256':boundary['manifestSHA256']}
 namespace['builder'].build=built
 handler=namespace['Quiet'];original=handler.translate_path
 def translated(self,path):
  primary=Path(original(self,path))
  if primary.is_file():return str(primary)
  relative=primary.relative_to(Path(self.directory));fallback=candidate/relative
  return str(fallback) if fallback.is_file() else str(primary)
 handler.translate_path=translated
 result=namespace['run'](ROOT/'.build/shared-services/browser-files-r1');result.update(candidateManifestSHA256=boundary['manifestSHA256'],sealedCandidateCoreAndCatalog=True,actualCandidateCoreSHA256=graph['core'],candidateBoundaryVerification=boundary)
 return result
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--candidate',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();assert not a.output.exists();r=run(a.candidate.resolve());a.output.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({'status':r['status'],'checks':len(r['checks']),'error':r.get('error')}));raise SystemExit(r['status']!='PASS')
