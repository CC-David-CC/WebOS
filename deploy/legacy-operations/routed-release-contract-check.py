#!/usr/bin/env python3
"""Reject incomplete/mixed network graphs even when outer file hashes are updated."""
import copy,hashlib,importlib.util,json,shutil,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
RELEASE=ROOT/'.build/releases/connected-routed-r8'
def key(records):return hashlib.sha256(json.dumps(records,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def run():
 spec=importlib.util.spec_from_file_location('routed_release_contract',RELEASE/'origin_service/release.py');c=importlib.util.module_from_spec(spec);spec.loader.exec_module(c)
 actual=c.verify(RELEASE);baseline=c.verify(ROOT/'.build/releases/connected-document-r2')
 original=json.loads((RELEASE/'assets/desktop/network-release.json').read_text());frontend=json.loads((RELEASE/'release.json').read_text());checks=[]
 def trial(name,mutate,rejected=True):
  with tempfile.TemporaryDirectory(prefix='routed-contract-') as temporary:
   p=Path(temporary);metadata=copy.deepcopy(original);public=copy.deepcopy(frontend)
   for folder in [original['directory'],original['coreDirectory']]:shutil.copytree(RELEASE/folder,p/folder)
   shutil.copyfile(RELEASE/'index.html',p/'index.html');(p/'assets/desktop').mkdir(parents=True,exist_ok=True)
   mutate(p,metadata,public);(p/'assets/desktop/network-release.json').write_text(json.dumps(metadata))
   try:c.verify_routed_graph(p,public)
   except (ValueError,FileNotFoundError,KeyError):
    assert rejected,name
   else:assert not rejected,name
   checks.append(name)
 trial('matched versioned host and all modules accepted',lambda *a:None,False)
 trial('missing history module refused',lambda p,m,f:m['modules'].pop('routed-history.mjs'))
 trial('unknown routing profile refused',lambda p,m,f:m.update(profile='codi-routed-room/999'))
 trial('unbound network directory refused',lambda p,m,f:m.update(directory='assets/desktop/network-v2/'+'0'*64))
 trial('changed module bytes refused',lambda p,m,f:(p/m['directory']/'resource-budget.mjs').write_text('export const sessionBudget=()=>({});'))
 trial('mixed host entrypoint refused',lambda p,m,f:(p/'index.html').write_text((p/'index.html').read_text().replace(m['coreDirectory'],'assets/desktop/core-v2/'+'1'*64)))
 def unversioned(p,m,f):
  old=m['coreDirectory'];text=(p/old/'app.js').read_text().replace(m['directory']+'/identity.mjs','network/identity.mjs');(p/old/'app.js').write_text(text)
  m['core']['app.js']={'bytes':len(text.encode()),'sha256':hashlib.sha256(text.encode()).hexdigest()};new='assets/desktop/core-v2/'+key(m['core']);(p/old).rename(p/new);m['coreDirectory']=new
  for n,r in m['core'].items():f['files'][new+'/'+n]=r
  (p/'index.html').write_text((p/'index.html').read_text().replace(old,new))
 trial('rehashed host importing a second unversioned identity graph refused',unversioned)
 return {'status':'PASS','checks':checks,'nativeManifestSHA256':actual['manifestSHA256'],'baselineContractStillAccepted':baseline['manifestSHA256'],'sourceSHA256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
if __name__=='__main__':
 result=run();(ROOT/'.build/checks/routed-release-contract-result.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
