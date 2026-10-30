#!/usr/bin/env python3
"""Real xterm/nano public Chrome tests with default certificate trust, owned tab only."""
import argparse,hashlib,importlib.util,json,time,urllib.request
from pathlib import Path
from types import SimpleNamespace
ROOT=Path(__file__).resolve().parent.parent
RELEASE=ROOT/'.build/releases/connected-routed-r8'
if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('--release-dir',type=Path,default=RELEASE);args=parser.parse_args();RELEASE=args.release_dir.resolve()
 result={'status':'FAIL','url':'https://ksu.codes/hidden/','defaultPublicTLS':True}
 try:
  for name in ['index.html','assets/terminal/v2/image.json']:
   with urllib.request.urlopen(result['url']+name,timeout=20) as response:assert response.read()==(RELEASE/name).read_bytes()
  s=importlib.util.spec_from_file_location('xterm_public_suite',ROOT/'scripts/xterm-browser-check.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m);result.update(m.browser(SimpleNamespace(origin='https://ksu.codes',base='/hidden')),releaseSHA256=hashlib.sha256((RELEASE/'connected-release.json').read_bytes()).hexdigest())
 finally:
  result['sourceSHA256']=hashlib.sha256(Path(__file__).read_bytes()).hexdigest();out=ROOT/'.build/checks/xterm-public-result.json'
  if out.exists():out.rename(out.with_name(out.stem+'-before-'+str(time.time_ns())+'.json'))
  out.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
