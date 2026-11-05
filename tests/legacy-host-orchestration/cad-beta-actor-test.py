#!/usr/bin/env python3
"""Check successor closure, fixed process arguments and unchanged route assets."""
import ast,hashlib,json,pathlib,sys,tempfile,subprocess
root=pathlib.Path(__file__).resolve().parents[1];base=pathlib.Path(sys.argv[1] if len(sys.argv)>1 else '/tmp/codi-cad-beta-actor-base')
with tempfile.TemporaryDirectory() as tmp:
 out=pathlib.Path(tmp)/'actor';subprocess.run([sys.executable,str(root/'research/cad-source-access/build-beta-actor.py'),str(base),str(out)],check=True)
 manifest=json.loads((out/'inventory.json').read_bytes());assert all(hashlib.sha256((out/k).read_bytes()).hexdigest()==v for k,v in manifest.items())
 launcher=ast.parse((out/'ops/asset-launch.py').read_text());pins=next(ast.literal_eval(n.value) for n in launcher.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='PINS' for t in n.targets))
 for name,pin in pins.items():assert hashlib.sha256((out/'ops'/f'{name}.py').read_bytes()).hexdigest()==pin, name
 for path in ('OPFS-ROUTE-TABLE.json','ops/asset_manifest.json','ops/asset_router.py','ops/asset_floor.py','ops/asset_select.py'):
  assert (base/path).read_bytes()==(out/path).read_bytes(),path
 host=(out/'ops/beta_launcher.py').read_text();adapter=(out/'ops/beta_worker_adapter.py').read_text();health=(out/'ops/beta_files_host_health.py').read_text()
 assert 'a626ef11bf57a039529abc806a4b39a5881f470557d49f8c715a742c06b5ae08' in host
 assert "if release=='a626ef11bf57a039529abc806a4b39a5881f470557d49f8c715a742c06b5ae08'" in adapter
 assert '2996df15296726a801ce252df37bad63cc6dc8eb0aec0639be5d56bb2d32d557' in health
 assert 'source registry inventory changed' in health
 print('PASS actor inventory/internal pins; fixed worker/args/unit; unchanged route/floor source')
