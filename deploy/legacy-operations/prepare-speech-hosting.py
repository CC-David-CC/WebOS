#!/usr/bin/env python3
"""Prepare one KSU-only static speech route under the existing hidden preview."""
import argparse,copy,hashlib,importlib.util,json
from pathlib import Path
def module(path,name):
 spec=importlib.util.spec_from_file_location(name,path);result=importlib.util.module_from_spec(spec);spec.loader.exec_module(result);return result
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def route(key):return '\t\t\thandle_path /assets/speech/* {\n\t\t\t\troot * /srv/codi-connected/speech/'+key+'\n\t\t\t\tfile_server\n\t\t\t}\n'
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--source',type=Path,required=True);p.add_argument('--manifest',type=Path,required=True);p.add_argument('--speech',type=Path,required=True);p.add_argument('--output-dir',type=Path,required=True);a=p.parse_args()
 exporter=module(Path(__file__).with_name('export-speech.py'),'speech_export');speech=exporter.verify(a.speech);key=speech['manifestSHA256']
 old=module(a.source,'speech_hosting_old');data=old.load(a.manifest);source=a.source.read_text();candidate=source
 anchor="        if type(s['enabled']) is not bool:\n            raise ValueError('enabled must be boolean')\n";assert candidate.count(anchor)==1
 existing="if 'codi_speech' in s" in candidate
 if not existing:
  candidate=candidate.replace(anchor,anchor+"        if 'codi_speech' in s and (not isinstance(s['codi_speech'],str) or not re.fullmatch('[0-9a-f]{64}',s['codi_speech']) or s['domain']!='ksu.codes' or not s['enabled'] or not s.get('codi_preview',False)):\n            raise ValueError('codi_speech requires a SHA256 on enabled KSU preview only')\n")
  anchor="        if 'codi_frontend' in s: lines.append('codi_frontend = '+json.dumps(s['codi_frontend']))\n";assert candidate.count(anchor)==1
  candidate=candidate.replace(anchor,anchor+"        if 'codi_speech' in s: lines.append('codi_speech = '+json.dumps(s['codi_speech']))\n")
  anchor="        '\\t\\t\\t@codi_identity path /api/* /discovery.json /.well-known/codi-issuer.json',\n";assert candidate.count(anchor)==1
  candidate=candidate.replace(anchor,"        *(['\\t\\t\\thandle_path /assets/speech/* {','\\t\\t\\t\\troot * /srv/codi-connected/speech/'+s['codi_speech'],'\\t\\t\\t\\tfile_server','\\t\\t\\t}'] if s.get('codi_speech') else []),\n"+anchor)
 a.output_dir.mkdir(parents=True,exist_ok=False);out=a.output_dir/'common.speech.py';out.write_text(candidate);new=module(out,'speech_hosting_new');proposed=copy.deepcopy(data);ksu=next(s for s in proposed['sites'] if s['domain']=='ksu.codes');previous=ksu.get('codi_speech');ksu['codi_speech']=key
 new.validate(proposed);manifest=a.output_dir/'sites.speech.toml';manifest.write_text(new.dump(proposed));assert new.load(manifest)==proposed
 for mode in ['prepare','production']:
  prior=old.caddy(data,mode);assert new.caddy(data,mode)==prior;rendered=new.caddy(proposed,mode);assert rendered.replace(route(key),'')==(prior.replace(route(previous),'') if previous else prior)
  assert rendered.count(route(key))==1 and '\t\tredir * /hidden/ 308' in rendered
  (a.output_dir/('Caddyfile.'+mode)).write_text(rendered)
 for site in data['sites']:assert old.unit(site)==new.unit(site)
 for domain,value in [('ksu.codes','../bad'),('ksu.codes',True),('python.coach',key)]:
  bad=copy.deepcopy(data);next(s for s in bad['sites'] if s['domain']==domain)['codi_speech']=value
  try:new.validate(bad)
  except ValueError:pass
  else:raise AssertionError('Invalid speech flag accepted')
 report={'status':'PASS','originalGeneratorSHA256':digest(a.source),'originalManifestSHA256':digest(a.manifest),'candidateGeneratorSHA256':digest(out),'candidateManifestSHA256':digest(manifest),'speechManifestSHA256':key,'speechFiles':speech['files']}
 (a.output_dir/'candidate-result.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items() if k!='speechFiles'},indent=2))
if __name__=='__main__':main()
