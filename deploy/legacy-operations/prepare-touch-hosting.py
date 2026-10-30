#!/usr/bin/env python3
"""Prepare a manifest-controlled frontend and independent-shell guest overlay under /hidden only."""
import argparse,copy,hashlib,importlib.util,json,sys
from pathlib import Path
def module(path,name):
 spec=importlib.util.spec_from_file_location(name,path);value=importlib.util.module_from_spec(spec);spec.loader.exec_module(value);return value
def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--source',type=Path,required=True);p.add_argument('--manifest',type=Path,required=True);p.add_argument('--frontend',type=Path,required=True);p.add_argument('--output-dir',type=Path,required=True);a=p.parse_args()
 sys.path.insert(0,str(a.source.resolve().parent))
 original=a.source.read_text();old=module(a.source,'hosting_before_touch');data=old.load(a.manifest);frontend=json.loads((a.frontend/'frontend.json').read_text());key=digest(a.frontend/'frontend.json')
 assert frontend['version']=='codi-frontend-assets/3' and set(frontend['files'])=={'app.js','style.css','terminal.js','assets/terminal-initramfs.cpio.gz','desktop-apps.js','networking.js'}
 for name,record in frontend['files'].items():assert record=={'bytes':(a.frontend/name).stat().st_size,'sha256':digest(a.frontend/name)}
 anchor="        if type(s['enabled']) is not bool:\n            raise ValueError('enabled must be boolean')\n";assert original.count(anchor)==1
 existing="if 'codi_frontend' in s" in original
 candidate=original if existing else original.replace(anchor,anchor+"        if 'codi_frontend' in s and (not isinstance(s['codi_frontend'],str) or not re.fullmatch('[0-9a-f]{64}',s['codi_frontend']) or s['domain']!='ksu.codes' or not s['enabled'] or not s.get('codi_preview',False)):\n            raise ValueError('codi_frontend requires a SHA256 on enabled KSU preview only')\n")
 anchor="        if 'codi_preview' in s: lines.append('codi_preview = '+str(s['codi_preview']).lower())\n";assert candidate.count(anchor)==1
 if not existing:candidate=candidate.replace(anchor,anchor+"        if 'codi_frontend' in s: lines.append('codi_frontend = '+json.dumps(s['codi_frontend']))\n")
 anchor="        '\\t\\t\\t@codi_identity path /api/* /discovery.json /.well-known/codi-issuer.json',\n";assert candidate.count(anchor)==1
 insert="        *(['\\t\\t\\t@codi_frontend path /app.js /style.css /terminal.js', '\\t\\t\\thandle @codi_frontend {', '\\t\\t\\t\\troot * /srv/codi-connected/frontends/'+s['codi_frontend'], '\\t\\t\\t\\tfile_server', '\\t\\t\\t}'] if s.get('codi_frontend') else []),\n"
 if not existing:candidate=candidate.replace(anchor,insert+anchor)
 old_paths='/app.js /style.css /terminal.js'
 four_paths=old_paths+' /assets/terminal-initramfs.cpio.gz'
 new_paths=four_paths+' /desktop-apps.js /networking.js'
 previous_paths=next(paths for paths in [new_paths,four_paths,old_paths] if '@codi_frontend path '+paths in original)
 if new_paths not in candidate:candidate=candidate.replace('@codi_frontend path '+previous_paths,'@codi_frontend path '+new_paths)
 compile(candidate,'common.touch.py','exec')
 output=a.output_dir;output.mkdir(parents=True,exist_ok=True);source=output/'common.touch.py';manifest=output/'sites.touch.toml';assert not source.exists() and not manifest.exists();source.write_text(candidate)
 new=module(source,'hosting_touch');proposed=copy.deepcopy(data);next(s for s in proposed['sites'] if s['domain']=='ksu.codes')['codi_frontend']=key
 new.validate(proposed);manifest.write_text(new.dump(proposed));assert new.load(manifest)==proposed
 extra='\t\t\t@codi_frontend path '+new_paths+'\n\t\t\thandle @codi_frontend {\n\t\t\t\troot * /srv/codi-connected/frontends/'+key+'\n\t\t\t\tfile_server\n\t\t\t}\n'
 previous=next(s for s in data['sites'] if s['domain']=='ksu.codes').get('codi_frontend')
 for mode in ['prepare','production']:
  prior=old.caddy(data,mode);assert new.caddy(data,mode)==prior.replace('@codi_frontend path '+previous_paths,'@codi_frontend path '+new_paths)
  rendered=new.caddy(proposed,mode);baseline=prior.replace(extra.replace(key,previous).replace(new_paths,previous_paths),'') if previous else prior;assert rendered.count(extra)==1 and rendered.replace(extra,'')==baseline
  assert '\t\tredir * /hidden/ 308' in rendered
  (output/('Caddyfile.'+mode)).write_text(rendered)
 for site in data['sites']:assert old.unit(site)==new.unit(site)
 for domain,value in [('ksu.codes','../../bad'),('ksu.codes',True),('python.coach',key)]:
  bad=copy.deepcopy(data);next(s for s in bad['sites'] if s['domain']==domain)['codi_frontend']=value
  try:new.validate(bad)
  except ValueError:pass
  else:raise AssertionError('Invalid frontend reference accepted')
 report={'status':'PASS','scope':'Offline generator invariants: six matched frontend/guest assets under existing hidden route only; index/cookie/config/websockets/native services preserved','originalGeneratorSHA256':digest(a.source),'originalManifestSHA256':digest(a.manifest),'candidateGeneratorSHA256':digest(source),'candidateManifestSHA256':digest(manifest),'frontendManifestSHA256':key,'frontendFiles':frontend['files']}
 (output/'candidate-result.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
if __name__=='__main__':main()
