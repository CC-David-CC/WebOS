#!/usr/bin/env python3
"""Build a disposable test-only CAD app override; never use for deployment."""
import argparse
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

p=argparse.ArgumentParser()
p.add_argument('--base-bundle',type=Path,required=True)
p.add_argument('--cad-dist',type=Path,required=True)
p.add_argument('--output',type=Path,required=True)
p.add_argument('--builder',type=Path,required=True)
p.add_argument('--node',type=Path,required=True)
p.add_argument('--wasm-name',default='a2b2f7daf6a4eb98b975.wasm',help='Exact emitted test runtime basename')
a=p.parse_args()
if not __import__('re').fullmatch(r'[a-f0-9]{20}\.wasm',a.wasm_name):p.error('Expected emitted WASM basename')
root=Path(__file__).resolve().parents[1]
base=a.base_bundle.resolve(strict=True); dist=a.cad_dist.resolve(strict=True)
if a.output.exists():p.error('Output must not exist')
base_catalog=json.loads((base/'apps.json').read_text())
old=next(x for x in base_catalog['apps'] if x['id']=='jsketcher')
old_app=base/'apps/jsketcher'/old['bundleSHA256']/'node_modules/jsketcher-build'
with tempfile.TemporaryDirectory(prefix='codi-rectangle-override-') as temp:
    tmp=Path(temp);app=tmp/'src/system/jsketcher';app.parent.mkdir(parents=True)
    shutil.copytree(root/'apps/system/jsketcher',app,ignore=shutil.ignore_patterns('node_modules'))
    (app/'node_modules').mkdir()
    target=app/'node_modules/jsketcher-build';shutil.copytree(old_app,target)
    manifest=json.loads((app/'app.json').read_text());assets=manifest['assets']
    assets[:]=[x for x in assets if 'static/sketch-solver.' not in x and 'static/project-validator.' not in x]
    # The baseline's old OCC WASM is not referenced by the replacement app.
    # Remove this exact test-fixture input before adding the new runtime so the
    # bounded app builder does not retain two 35 MiB engines.
    obsolete='node_modules/jsketcher-build/static/c39793b8aff34dc548b5.wasm'
    assets[:]=[x for x in assets if x!=obsolete]
    old_wasm=target/'static/c39793b8aff34dc548b5.wasm'
    if old_wasm.exists():old_wasm.unlink()
    for rel in ['index-webos.html','static/index.bundle.js','static/sketcher.bundle.js']:
        if (dist/rel).is_file():shutil.copy2(dist/rel,target/rel)
    for pattern in ['static/sketch-solver.*.js','static/project-validator.*.js']:
        workers=list(dist.glob(pattern))
        if len(workers)!=1:raise RuntimeError('Expected one '+pattern)
        for worker in workers:
            shutil.copy2(worker,target/'static'/worker.name)
            assets.append('node_modules/jsketcher-build/static/'+worker.name)
    # Test-only versioned worker prism assets. The release packager must do
    # its own closed-inventory and source/notice qualification.
    for rel in ['static/oci-verified-worker.js','static/occ-portable.js',
                'static/profile-topology.mjs','static/rectangleProfileRequest.mjs',
                'static/authoredRegions.mjs','static/profilePlan.mjs',
                'static/centeredHolePlan.mjs','static/centeredHoleTopology.mjs',
                'static/boundedPrismBoundary.mjs','static/enclosurePlan.mjs','static/enclosureMesh.mjs','static/enclosureManufacturingMesh.mjs','static/enclosureLabelContact.mjs','static/fourCornerHolePlan.mjs',
                'static/fourCornerHoleTopology.mjs','static/fourCornerHoleProvenance.mjs']:
        shutil.copy2(dist/rel,target/rel)
        assets.append('node_modules/jsketcher-build/'+rel)
    for pattern in ['static/prism-semantic.*.js','static/manufacturing-hash.*.js','static/'+a.wasm_name]:
        workers=list(dist.glob(pattern))
        if len(workers)!=1:raise RuntimeError('Expected one '+pattern)
        for worker in workers:
            shutil.copy2(worker,target/'static'/worker.name)
            assets.append('node_modules/jsketcher-build/static/'+worker.name)
    # Include split application chunks from this exact build, including the
    # secondary engine. Never use the browser test helper as a public asset.
    for pattern in ['static/*.bundle.js','static/*.wasm']:
        for chunk in dist.glob(pattern):
            if chunk.name=='webosTest.bundle.js':continue
            shutil.copy2(chunk,target/'static'/chunk.name)
            assets.append('node_modules/jsketcher-build/static/'+chunk.name)
    assets[:]=sorted(set(assets));(app/'app.json').write_text(json.dumps(manifest,indent=2)+'\n')
    entries=tmp/'entries.json';entries.write_text(json.dumps({'jsketcher':'system/jsketcher/index.mjs'}))
    built=tmp/'built';built.mkdir()
    subprocess.run([sys.executable,str(a.builder),'--source',str(tmp/'src'),'--output',str(built),'--apps','jsketcher','--node',str(a.node),'--entries',str(entries)],check=True,stdout=subprocess.DEVNULL)
    replacement=json.loads((built/'apps.json').read_text())['apps'][0]
    shutil.copytree(base,a.output)
    shutil.copytree(built/'apps/jsketcher'/replacement['bundleSHA256'],a.output/'apps/jsketcher'/replacement['bundleSHA256'])
    base_catalog['apps']=[replacement if x['id']=='jsketcher' else x for x in base_catalog['apps']]
    (a.output/'apps.json').write_text(json.dumps(base_catalog,indent=2)+'\n')
    print('TEST-ONLY jsketcher bundle:',replacement['bundleSHA256'])
