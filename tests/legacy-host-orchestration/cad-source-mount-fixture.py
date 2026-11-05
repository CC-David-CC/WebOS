#!/usr/bin/env python3
"""Build disposable actual-mount source-lifetime fixture from an existing CAD dist."""
import argparse, pathlib, shutil, subprocess, sys
root=pathlib.Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('--output',required=True,type=pathlib.Path);p.add_argument('--cad-dist',required=True,type=pathlib.Path);a=p.parse_args()
subprocess.run([sys.executable,str(root/'tests/jsketcher-rectangle-fixture.py'),'--output',str(a.output),'--cad-dist',str(a.cad_dist)],check=True)
for name in ('feature-commands.mjs','source-dialog.mjs'):shutil.copy2(root/'apps/system/jsketcher'/name,a.output/name)
h=a.output/'fixture-host.mjs';s=h.read_text();old='storage:{signedInSubject:';new="storage:{readCadSource:(_owner,_name,{signal})=>new Promise((resolve,reject)=>{window.sourceStarted=true;signal.addEventListener('abort',()=>{window.sourceAborted=true;reject(new DOMException('Cancelled','AbortError'))},{once:true});}),signedInSubject:"
if s.count(old)!=1:raise ValueError('Fixture anchor changed')
h.write_text(s.replace(old,new))
