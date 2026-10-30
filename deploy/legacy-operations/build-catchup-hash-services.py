#!/usr/bin/env python3
"""Bundle production and test history services from the reviewed local modules."""
import argparse,importlib.util,json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('shared_builder',ROOT/'scripts/build-shared-service.py');builder=importlib.util.module_from_spec(spec);spec.loader.exec_module(builder)
def build(entry,name,out):
 seen=set();todo=[entry]
 while todo:
  path=todo.pop().resolve()
  if path in seen or not path.is_file():continue
  seen.add(path)
  for ref in re.findall(r'''(?:from\s*|import\s*\()\s*['"](\.{1,2}/[^'"]+)['"]''',path.read_text()):
   dependency=(path.parent/ref).resolve()
   if dependency.is_file() and dependency.suffix in ('.mjs','.js'):todo.append(dependency)
 inputs=sorted(path for path in seen if path.is_relative_to(ROOT/'network') or path.is_relative_to(ROOT/'assets/vendor'))
 return builder.build(entry,name,'assets/desktop/'+entry.name,out,inputs)
if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('--revision',default='r1');args=parser.parse_args();assert re.fullmatch(r'r[1-9][0-9]*',args.revision)
 outputs=[('device-history-host.mjs','device-history','catchup-hash-'+args.revision),('device-history-test-entry.mjs','device-history-test','catchup-hash-test-'+args.revision)]
 for entry,name,out in outputs:print(json.dumps(build(ROOT/'assets/desktop'/entry,name,ROOT/'.build/shared-services'/out)))
