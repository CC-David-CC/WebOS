#!/usr/bin/env python3
"""Determinism and refusal controls for the uninstalled actor closure."""
import hashlib,json,shutil,subprocess,sys,tempfile
from pathlib import Path
here=Path(__file__).resolve().parent;base,new,gen,inv=map(Path,sys.argv[1:]);builder=here/'build-actor.py'
with tempfile.TemporaryDirectory(prefix='830c-actor-test-') as d:
 root=Path(d)
 def call(b,n,g,i,o):return subprocess.run([sys.executable,'-B',str(builder),str(b),str(n),str(g),str(i),str(o)],capture_output=True,text=True)
 a=call(base,new,gen,inv,root/'a');b=call(base,new,gen,inv,root/'b');assert a.returncode==b.returncode==0,(a.stderr,b.stderr)
 assert (root/'a/inventory.json').read_bytes()==(root/'b/inventory.json').read_bytes();records=json.loads((root/'a/inventory.json').read_bytes());assert len(records)==35
 for name,pin in records.items():assert hashlib.sha256((root/'a'/name).read_bytes()).hexdigest()==pin
 assert call(base,new,gen,inv,root/'a').returncode
 bad=root/'bad';shutil.copyfile(gen,bad);bad.write_bytes(bad.read_bytes()+b'\n');assert call(base,new,bad,inv,root/'rejected').returncode and not (root/'rejected').exists()
print('PASS deterministic actor closure, exact file pins, no-overwrite and generator drift refusal')
