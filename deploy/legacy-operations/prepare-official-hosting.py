#!/usr/bin/env python3
"""Prepare an opt-in official-channel hosting generator from captured live inputs."""
import copy,hashlib,importlib.util,json,shutil,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];base=ROOT/'.build/official-hosting-current';out=ROOT/'.build/official-hosting-candidate-r1'
def load(name,path):
 spec=importlib.util.spec_from_file_location(name,path);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module
assert hashlib.sha256((base/'ops/common.py').read_bytes()).hexdigest()=='6c3dd881d1938512b3934a46984a9192f683becd3795bbb854099f7a3a89bc24'
assert hashlib.sha256((base/'sites.toml').read_bytes()).hexdigest()=='636a4ea3bc0492d1611848e6d4847864baf25a3e231e5bfdcd9c3a8e50d121c4'
assert not out.exists();shutil.copytree(base,out);sys.path.insert(0,str(out/'ops'))
try:
 path=out/'ops/common.py';s=path.read_text();needle="        if 'codi_readers' in s and ";i=s.index(needle);s=s[:i]+"        if 'codi_official' in s and (type(s['codi_official']) is not bool or s['domain']!='ksu.codes' or s['codi_official'] and (not s['enabled'] or not s.get('codi_preview'))):\n            raise ValueError('codi_official requires a boolean on enabled KSU preview only')\n"+s[i:]
 needle="        if 'codi_readers' in s: lines.append(";i=s.index(needle);s=s[:i]+"        if 'codi_official' in s: lines.append('codi_official = '+str(s['codi_official']).lower())\n"+s[i:]
 needle='def room_routes(s, prefix=\'\'):';i=s.index(needle);s=s[:i]+"def official_routes(s, prefix=''):\n    if not s.get('codi_official'): return []\n    paths=('official-head','official-history','official-directory','official-channel','official-ingest/challenge','official-ingest/use')\n    lines=[]\n    for name in paths:\n        lines.append('\\thandle '+prefix+'/'+name+' {')\n        if prefix: lines.append('\\t\\turi strip_prefix '+prefix)\n        lines.extend(['\\t\\treverse_proxy 127.0.0.1:8145','\\t}'])\n    return lines\n\n"+s[i:]
 for call in ("        *room_routes(s, '/hidden'),","        *room_routes(s),"):
  assert s.count(call)==1;s=s.replace(call,call.replace('room_routes','official_routes')+'\n'+call)
 path.write_text(s);before=load('hosting_before',base/'ops/common.py');after=load('hosting_after',path);data=before.load(base/'sites.toml');assert before.caddy(data,'production')==after.caddy(data,'production')
 enabled=copy.deepcopy(data);site=next(x for x in enabled['sites'] if x['domain']=='ksu.codes');site['codi_official']=True;render=after.caddy(enabled,'production');assert 'official-ingest/use' in render and '/internal/official-health' not in render
 (out/'enabled.toml').write_text(after.dump(enabled));assert after.load(out/'enabled.toml')==enabled
 for site in enabled['sites']:
  if site['domain']=='ksu.codes':continue
  bad=copy.deepcopy(enabled);next(x for x in bad['sites'] if x['domain']==site['domain'])['codi_official']=True
  try:after.validate(bad);raise AssertionError('other domain accepted')
  except ValueError:pass
 print(json.dumps({'status':'PASS','candidate':str(out),'generatorSHA256':hashlib.sha256(path.read_bytes()).hexdigest(),'scope':'local candidate; port 8145 not reserved or live-verified'}))
except BaseException:
 shutil.rmtree(out);raise
