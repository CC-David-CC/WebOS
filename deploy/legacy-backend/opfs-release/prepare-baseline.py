#!/usr/bin/env python3
"""Fetch only hash-verified public beta files required for a disposable test."""
import hashlib,json,pathlib,sys,urllib.request
out=pathlib.Path(sys.argv[1]);base='https://beta.ksu.codes/';PINS={'assets/desktop/cache-manifest.json':'18140be41c4f6cd3a1fcdbee39998e00c363ed677223eeffc8cc97c450ba4720','assets/desktop/offline-worker.js':'e49a8667db0e20b8fca90ee3e19eec17b70b964846b916d734391dda93c3f69c','storage/browser/mirror.cbfafe53eae1afdac1f2a9af0bfdbd26cae59b1be8f5d96f6bebec2a56c158ed.mjs':'cbfafe53eae1afdac1f2a9af0bfdbd26cae59b1be8f5d96f6bebec2a56c158ed','gateway/client.mjs':'44da83bdccf43a2b36ae4b3f48eaf94fc1006b88180456e26faba61aae344869'}
if out.exists():raise ValueError('Fresh baseline output required')
out.mkdir(parents=True)
def fetch(path,expected):
 if path.startswith('/') or '..' in pathlib.PurePosixPath(path).parts:raise ValueError('Invalid path')
 data=urllib.request.urlopen(base+path,timeout=30).read()
 if hashlib.sha256(data).hexdigest()!=expected:raise ValueError('Public baseline changed: '+path)
 p=out/path;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data)
for n,h in PINS.items():fetch(n,h)
manifest=json.loads((out/'assets/desktop/cache-manifest.json').read_bytes());assert manifest['id']=='0965a0cbdd022f588061cdc23e10eb6b18fa5977cc3f6a05569439eaf11d2020'
core=['index.html','app.js','style.css','reference.js','terminal.js','desktop-apps.js','bootstrap.js','assets/desktop/apps.mjs','assets/desktop/apps.json','assets/desktop/lifecycle.mjs','assets/desktop/device-cache.mjs','.build/v86/libv86.js','network/crypto.mjs','network/identity.mjs','network/strict-json.mjs']
core+= [n for n in manifest['files'] if n.startswith('assets/desktop/') and n.count('/')==2 and n.endswith(('.mjs','.js','.css')) and n not in ('assets/desktop/offline-worker.js',)]
for n in dict.fromkeys(core):fetch(n,manifest['files'][n]['sha256'])
catalog=json.loads((out/'assets/desktop/apps.json').read_bytes())
for app in catalog['apps']:
 if app['id'] not in ('files','text','codemirror'):continue
 parent=pathlib.PurePosixPath(app['path']).parent
 for n in app['files']:
  name=str(parent/n);fetch(name,manifest['files'][name]['sha256'])
selected=urllib.request.urlopen(base+'desktop-apps.js?simplified=1',timeout=30).read()
if hashlib.sha256(selected).hexdigest()!='0d1cbcb4e6b23beb0c6b7eecce8b35244438fb4341c2e325203c739c64118b81':raise ValueError('Selected loader changed')
(out/'guarded-loader.js').write_bytes(selected)
inputs=out/'candidate-inputs';inputs.mkdir();(inputs/'desktop-apps.js').write_bytes(selected)
for source,target in [('app.js','app.js'),('assets/desktop/apps.json','apps.json'),('assets/desktop/cache-manifest.json','cache-manifest.json'),('assets/desktop/offline-worker.js','offline-worker.js')]:
 (inputs/target).write_bytes((out/source).read_bytes())
print('PASS pinned public baseline',sum(p.stat().st_size for p in out.rglob('*') if p.is_file()),'bytes')
