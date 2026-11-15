#!/usr/bin/env python3
"""Prepare a KSU-only personal-files route while retaining other body limits."""
import argparse
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

ROUTE = ('\thandle /hidden/gateway/* {\n'
         '\t\turi strip_prefix /hidden\n'
         '\t\trequest_body {\n\t\t\tmax_size 12MiB\n\t\t}\n'
         '\t\treverse_proxy 127.0.0.1:8140\n\t}\n')

def module(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def prepare(source, manifest, output):
    sys.path.insert(0, str(source.resolve().parent))
    old = module(source, 'common')
    sys.modules['common'] = old  # Existing hardware/cardboard profiles import it.
    data = old.load(manifest)
    original = source.read_text()
    assert "'codi_files'" not in original
    anchor = "        if type(s['enabled']) is not bool:\n            raise ValueError('enabled must be boolean')\n"
    assert original.count(anchor) == 1
    candidate = original.replace(anchor, anchor + "        if 'codi_files' in s and (type(s['codi_files']) is not bool or s['domain']!='ksu.codes' or s['codi_files'] and (not s['enabled'] or not s.get('codi_preview',False))):\n            raise ValueError('codi_files requires a boolean on enabled KSU preview only')\n")
    anchor = "        if 'codi_preview' in s: lines.append('codi_preview = '+str(s['codi_preview']).lower())\n"
    assert candidate.count(anchor) == 1
    candidate = candidate.replace(anchor, anchor + "        if 'codi_files' in s: lines.append('codi_files = '+str(s['codi_files']).lower())\n")
    anchor = "        '\\thandle_path /hidden/* {',\n"
    assert candidate.count(anchor) == 1
    insertion = '        *(' + repr(ROUTE.rstrip('\n').split('\n')) + " if s.get('codi_files') else []),\n"
    candidate = candidate.replace(anchor, insertion + anchor)
    compile(candidate, 'common.files.py', 'exec')
    output.mkdir(parents=True, exist_ok=False)
    dest = output/'common.files.py'
    dest.write_text(candidate)
    new = module(dest, 'files_hosting')
    proposed = copy.deepcopy(data)
    next(s for s in proposed['sites'] if s['domain']=='ksu.codes')['codi_files'] = True
    new.validate(proposed)
    proposed_manifest = output/'sites.files.toml'
    proposed_manifest.write_text(new.dump(proposed))
    assert new.load(proposed_manifest) == proposed
    for mode in ['prepare','production']:
        baseline = old.caddy(data, mode)
        assert new.caddy(data, mode) == baseline
        rendered = new.caddy(proposed, mode)
        assert rendered.count(ROUTE) == 1 and rendered.replace(ROUTE, '') == baseline
        assert '\t\tredir * /hidden/ 308' in rendered
        assert '\t\t\tmax_size 64KiB' in rendered
        (output/('Caddyfile.'+mode)).write_text(rendered)
    for site in data['sites']:
        assert old.unit(site) == new.unit(site)
    for domain, value, preview, enabled in [('python.coach',True,True,True),('ksu.codes','true',True,True),('ksu.codes',True,False,True),('ksu.codes',True,True,False)]:
        bad = copy.deepcopy(data)
        site = next(s for s in bad['sites'] if s['domain']==domain)
        site.update(codi_files=value,codi_preview=preview,enabled=enabled)
        try:
            new.validate(bad)
        except ValueError:
            pass
        else:
            raise AssertionError('Invalid file route accepted')
    report = {'status':'PASS','scope':'Generator retains all existing Caddy blocks/units, adds only KSU gateway prefix with independent 12MiB envelope limit; existing 64KiB issuer limit retained',
              'originalGeneratorSHA256':sha(source),'originalManifestSHA256':sha(manifest),
              'candidateGeneratorSHA256':sha(dest),'candidateManifestSHA256':sha(proposed_manifest),
              'siteDomains':sorted(s['domain'] for s in data['sites'] if s['enabled'])}
    (output/'candidate-result.json').write_text(json.dumps(report,indent=2)+'\n')
    return report

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--source',required=True,type=Path)
    p.add_argument('--manifest',required=True,type=Path)
    p.add_argument('--output-dir',required=True,type=Path)
    a=p.parse_args()
    print(json.dumps(prepare(a.source,a.manifest,a.output_dir),indent=2))
