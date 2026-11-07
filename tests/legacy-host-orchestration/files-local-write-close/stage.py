#!/usr/bin/env python3
"""Code-only private fixture composition; no account or service-state inputs."""
import hashlib,json,pathlib,shutil,sys
source=pathlib.Path(__file__).resolve().parents[2]
base,new,output=map(pathlib.Path,sys.argv[1:])
assert not output.exists()
old=json.loads((base/'apps.json').read_bytes());replacement=json.loads((new/'apps.json').read_bytes())
assert [x['id'] for x in old['apps']]==['files','text','codemirror']
assert [x['id'] for x in replacement['apps']]==['files']
shutil.copytree(base,output)
row=replacement['apps'][0];shutil.copytree(new/'apps/files'/row['bundleSHA256'],output/'apps/files'/row['bundleSHA256'])
catalog={**old,'apps':[row if x['id']=='files' else x for x in old['apps']]}
assert catalog['apps'][1:]==old['apps'][1:]
(output/'apps.json').write_text(json.dumps(catalog,indent=2)+'\n')
for app in catalog['apps']:
 directory=output/pathlib.PurePosixPath(app['path']).relative_to('assets/desktop').parent
 for name,meta in app['files'].items():
  value=(directory/name).read_bytes();assert len(value)==meta['bytes'];assert hashlib.sha256(value).hexdigest()==meta['sha256']
host=['app.js','desktop-apps.js','assets/desktop/app-instance.mjs','assets/desktop/document-operations.mjs','assets/desktop/command-registry.mjs']
pins={'source':'8808b15db','filesBundle':row['bundleSHA256'],'filesIndexSHA256':row['sha256'],'filesCount':len(row['files']),'catalogSHA256':hashlib.sha256((output/'apps.json').read_bytes()).hexdigest(),'host':{name:hashlib.sha256((source/'active-system'/name).read_bytes()).hexdigest() for name in host},'retainedApps':old['apps'][1:],'builderSHA256':hashlib.sha256((source/'active-system/tools/app-builder/build.mjs').read_bytes()).hexdigest(),'scope':'fresh private signed fixture code-only; no deployment/account state'}
(output/'runtime-pins.json').write_text(json.dumps(pins,indent=2)+'\n')
print(json.dumps({k:v for k,v in pins.items() if k!='retainedApps'},indent=2))
