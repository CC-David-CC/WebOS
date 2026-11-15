#!/usr/bin/env python3
"""Prepare and check a manifest-controlled /hidden hosting generator candidate."""
import argparse,copy,hashlib,importlib.util,json
from pathlib import Path
ROUTES=r'''
def connected_preview(s):
    # Only the validated KSU flag can activate these fixed loopback targets.
    return [
        '\t@codi_preview path /hidden /hidden/*',
        '\theader @codi_preview >Cache-Control "no-store"',
        '\theader @codi_preview >Content-Security-Policy "default-src \'none\'; script-src \'self\' \'wasm-unsafe-eval\'; connect-src \'self\' wss://ksu.codes; style-src \'self\' \'unsafe-inline\'; img-src \'self\' data:; font-src \'self\'; worker-src \'self\' blob:; base-uri \'none\'; frame-ancestors \'none\'; form-action \'none\'"',
        '\thandle /hidden {', '\t\tredir * /hidden/ 308', '\t}',
        '\thandle /hidden/rendezvous {', '\t\treverse_proxy 127.0.0.1:8119', '\t}',
        '\thandle_path /hidden/* {',
        '\t\trequest_body {', '\t\t\tmax_size 64KiB', '\t\t}',
        '\t\troute {',
        '\t\t\t@codi_identity path /api/* /discovery.json /.well-known/codi-issuer.json',
        '\t\t\treverse_proxy @codi_identity 127.0.0.1:8118',
        '\t\t\treverse_proxy 127.0.0.1:8132', '\t\t}', '\t}',
    ]

'''
def module(path,name):
 spec=importlib.util.spec_from_file_location(name,path);value=importlib.util.module_from_spec(spec);spec.loader.exec_module(value);return value
def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def block(text,domain,mode):
 address=('http://' if mode=='prepare' else '')+domain+' {\n';start=text.index(address);end=text.index('\n}\n',start)+3;return text[start:end]
def main():
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--source',type=Path,required=True);parser.add_argument('--manifest',type=Path,required=True);parser.add_argument('--output-dir',type=Path,required=True);a=parser.parse_args()
 original=a.source.read_text();old=module(a.source,'hosting_original');data=old.load(a.manifest)
 anchor="        if type(s['enabled']) is not bool:\n            raise ValueError('enabled must be boolean')\n"
 assert original.count(anchor)==1
 candidate=original.replace(anchor,anchor+"        if 'codi_preview' in s and (type(s['codi_preview']) is not bool or s['domain']!='ksu.codes'):\n            raise ValueError('codi_preview must be a boolean on ksu.codes only')\n")
 anchor="        lines.append('')\n    return '\\n'.join(lines)\n";assert candidate.count(anchor)==1
 candidate=candidate.replace(anchor,"        if 'codi_preview' in s: lines.append('codi_preview = '+str(s['codi_preview']).lower())\n"+anchor)
 anchor='def caddy(data, mode):';assert candidate.count(anchor)==1;candidate=candidate.replace(anchor,ROUTES+anchor)
 lines=candidate.splitlines(keepends=True);indices=[i for i,line in enumerate(lines) if line.startswith("        lines += ['\\timport site_defaults'")];assert len(indices)==1
 replacement=r'''        lines += ['\timport site_defaults', '\tlog {', f"\t\toutput file /var/log/caddy/{s['slug']}.json {{", '\t\t\troll_size 10MiB', '\t\t\troll_keep 3', '\t\t\troll_keep_for 168h', '\t\t}', '\t\tformat json', '\t}']
        upstream = [f"\treverse_proxy 127.0.0.1:{s['port']} {{", '\t\ttransport http {', '\t\t\tkeepalive 4s', '\t\t}', '\t}']
        if s.get('codi_preview',False):
            lines += connected_preview(s)
            upstream = ['\thandle {']+['\t'+line for line in upstream]+['\t}']
        lines += upstream+['}', '']
'''
 lines[indices[0]]=replacement;candidate=''.join(lines);compile(candidate,'common.preview.py','exec')
 output=a.output_dir;output.mkdir(parents=True,exist_ok=True);source=output/'common.preview.py';manifest=output/'sites.preview.toml'
 assert not source.exists() and not manifest.exists();source.write_text(candidate);new=module(source,'hosting_preview')
 changed=copy.deepcopy(data);next(site for site in changed['sites'] if site['domain']=='ksu.codes')['codi_preview']=True
 new.validate(changed);manifest.write_text(new.dump(changed));assert new.load(manifest)==changed
 assertions=[]
 for mode in ['prepare','production']:
  prior=old.caddy(data,mode);assert new.caddy(data,mode)==prior
  off=copy.deepcopy(changed);next(site for site in off['sites'] if site['domain']=='ksu.codes')['codi_preview']=False;assert new.caddy(off,mode)==prior
  rendered=new.caddy(changed,mode);assert rendered.count('handle_path /hidden/*')==1 and rendered.count('127.0.0.1:8132')==1
  for site in data['sites']:
   assert old.unit(site)==new.unit(site)
   if site['domain']!='ksu.codes':assert block(prior,site['domain'],mode)==block(rendered,site['domain'],mode)
  ksu=block(rendered,'ksu.codes',mode)
  assert [line for line in ksu.splitlines() if '@desktop' in line]==[line for line in block(prior,'ksu.codes',mode).splitlines() if '@desktop' in line]
  assert 'reverse_proxy 127.0.0.1:8013' in ksu and 'max_size 64KiB' in ksu and 'wss://ksu.codes' in ksu
  (output/('Caddyfile.'+mode)).write_text(rendered);assertions.append(mode+': unchanged when off; seven other sites, desktop CSP and all units unchanged when on')
 for domain,value in [('python.coach',True),('ksu.codes','true'),('ksu.codes',1)]:
  bad=copy.deepcopy(data);next(site for site in bad['sites'] if site['domain']==domain)['codi_preview']=value
  try:new.validate(bad)
  except ValueError:pass
  else:raise AssertionError('Invalid preview flag accepted')
 result={'status':'PASS','scope':'Offline hosting generator/manifest/unit invariants; no live proxy or browser claim','originalGeneratorSHA256':digest(a.source),'originalManifestSHA256':digest(a.manifest),'candidateGeneratorSHA256':digest(source),'candidateManifestSHA256':digest(manifest),'assertions':assertions,'fixedBackendPorts':[8118,8119,8132],'candidateDirectory':str(output.resolve())}
 (output/'candidate-result.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
