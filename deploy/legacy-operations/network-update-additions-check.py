#!/usr/bin/env python3
"""Verify explicit standalone/bundled module packaging and refusal paths.

Uses a pinned local release and temporary inactive candidates. No live changes.
"""
import hashlib,importlib.util,json,shutil,tempfile,traceback
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('release_builder',ROOT/'scripts/build-network-update.py');builder=importlib.util.module_from_spec(spec);spec.loader.exec_module(builder)
def run():
 checks=[];report={'status':'FAIL','scope':__doc__,'checks':checks,'productionChanged':False,'releaseReady':False};base=ROOT/'.build/releases/connected-browser-files-r1';pin='36868e655bc12c61123ec2e7d8562bea511375aa6136d5f5dd610ca81a751d46';proof=ROOT/'.build/checks/account-floor-bundled-proof-r1-result.json';p=json.loads(proof.read_bytes());bundled=[n.removeprefix('network/') for n in p['sourceSHA256']];services=[ROOT/'.build/shared-services'/n for n in ['browser-files-r1','device-account-interface-r1','account-rendezvous-r2','account-links-floor-r3']]
 def check(name,value):assert value,name;checks.append(name);print(json.dumps({'check':name}),flush=True)
 def refused(name,additional,bundle,receipts):
  output=ROOT/'.build/releases'/('account-floor-invalid-'+str(len(checks)));assert not output.exists()
  try:builder.build(base,pin,output,['desktop-apps.js'],services,additional,bundle,receipts)
  except (AssertionError,KeyError,ValueError):pass
  else:raise AssertionError('Unreviewed package was accepted: '+name)
  check(name,not output.exists())
 try:
  refused('unlisted new modules are rejected',[],[],[])
  refused('an incomplete bundled list is rejected',[],bundled[:-1],[proof])
  refused('duplicate bundled entries are rejected',[],bundled+[bundled[0]],[proof])
  refused('an existing module cannot be redeclared as an addition',['crypto.mjs'],bundled,[proof])
  refused('bundled modules without build proof are rejected',[],bundled,[])
  with tempfile.TemporaryDirectory(prefix='codi-package-proof-',dir=ROOT/'.build/checks') as temp:
   bad=Path(temp)/'proof.json';bad.write_text(json.dumps({**p,'compiledSHA256':'0'*64}));refused('proof for another service artifact is rejected',[],bundled,[bad])
   source=dict(p['sourceSHA256']);source['network/'+bundled[0]]='0'*64;bad.write_text(json.dumps({**p,'sourceSHA256':source}));refused('proof for changed bundled source is rejected',[],bundled,[bad])
  bad_raw='device-account-admission.mjs';refused('a standalone module with an unbound desktop import is rejected',[bad_raw],[x for x in bundled if x!=bad_raw],[proof])
  extra='device-operation-set.mjs';refused('the pinned validator refuses even a self-contained standalone addition',[extra],[n for n in bundled if n!=extra],[proof])
  candidate=ROOT/'.build/releases/account-floor-package-r3';n=json.loads((candidate/'assets/desktop/network-release.json').read_bytes());registry=json.loads((candidate/'assets/desktop/shared-services.json').read_bytes());entries={v['name']:v for v in registry['services']};host=candidate/n['coreDirectory'];desktop=(host/'desktop-apps.js').read_text();network=(host/'networking.js').read_text()
  check('candidate maps both new services through the existing host loader',entries['account-links']['path'] in desktop and entries['account-discovery']['path'] in network and 'const disabled=true;' in network)
  check('bundled-only modules are not published as loose network files',len(n['modules'])==40 and all(x not in n['modules'] for x in bundled))
  report['status']='PASS';report['candidateManifestSHA256']=hashlib.sha256((candidate/'connected-release.json').read_bytes()).hexdigest()
 except Exception:report['error']=traceback.format_exc()
 report['sourceSHA256']={n:hashlib.sha256((ROOT/n).read_bytes()).hexdigest() for n in ['scripts/build-network-update.py','scripts/network-update-additions-check.py']};path=ROOT/'.build/checks/network-update-additions-r2-result.json';assert not path.exists();path.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'status':report['status'],'checks':len(checks),'error':report.get('error')}),flush=True)
 if report['status']!='PASS':raise SystemExit(1)
if __name__=='__main__':run()
