#!/usr/bin/env python3
"""Prepare a manifest-controlled shared80/443 candidate without changing a host."""
import argparse
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from ingress_service.configuration import GLOBAL_OPTIONS, LISTENER_WRAPPERS, haproxy, service, caddy_dependency


def module(file, name):
    spec = importlib.util.spec_from_file_location(name, file)
    value = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value


def digest(file):
    return hashlib.sha256(file.read_bytes()).hexdigest()


def prepare(source, manifest, runtime, output):
    assert not output.exists()
    sys.path.insert(0, str(source.resolve().parent))
    before = module(source, 'hosting_before_ingress')
    data = before.load(manifest)
    assert not data.get('codi_shared_ingress', False)
    raw = source.read_text()
    assert 'codi_shared_ingress' not in raw
    ksu = next(s for s in data['sites'] if s['domain'] == 'ksu.codes')
    assert ksu['enabled'] and ksu.get('codi_preview') and ksu.get('codi_turn_certificate')
    anchor = "    seen = {k: set() for k in ['domain', 'slug', 'port', 'service', 'user']}\n"
    assert raw.count(anchor) == 1
    checks = "    if 'codi_shared_ingress' in data and type(data['codi_shared_ingress']) is not bool:\n        raise ValueError('codi_shared_ingress must be boolean')\n    if data.get('codi_shared_ingress') and not any(s['domain']=='ksu.codes' and s['enabled'] and s.get('codi_preview') and s.get('codi_turn_certificate') for s in data['sites']):\n        raise ValueError('Shared ingress requires the enabled KSU preview/certificate profile')\n"
    candidate = raw.replace(anchor, checks + anchor)
    anchor = "    lines = ['schema_version = 1', '']\n"
    assert candidate.count(anchor) == 1
    candidate = candidate.replace(anchor, "    lines = ['schema_version = 1', *(['codi_shared_ingress = '+str(data['codi_shared_ingress']).lower()] if 'codi_shared_ingress' in data else []), '']\n")
    anchor = "'\\tadmin unix//run/caddy/admin.sock', '\\tservers {', '\\t\\tprotocols h1 h2',"
    assert candidate.count(anchor) == 1
    replacement = "'\\tadmin unix//run/caddy/admin.sock', *(" + repr(GLOBAL_OPTIONS) + " if data.get('codi_shared_ingress') and mode=='production' else []), '\\tservers {', '\\t\\tprotocols h1 h2', *(" + repr(LISTENER_WRAPPERS) + " if data.get('codi_shared_ingress') and mode=='production' else []),"
    candidate = candidate.replace(anchor, replacement)
    anchor = "    lines += [':80 {']\n"
    assert candidate.count(anchor) == 1
    candidate = candidate.replace(anchor, "    lines += [':8080 {' if data.get('codi_shared_ingress') and mode=='production' else ':80 {']\n")
    output.mkdir(parents=True)
    generator = output / 'common.ingress.py'
    generator.write_text(candidate)
    after = module(generator, 'hosting_with_ingress')
    proposed = copy.deepcopy(data)
    proposed['codi_shared_ingress'] = True
    after.validate(proposed)
    target = output / 'sites.ingress.toml'
    target.write_text(after.dump(proposed))
    assert after.load(target) == proposed
    added = '\n'.join(GLOBAL_OPTIONS) + '\n'
    wrapper = '\n'.join(LISTENER_WRAPPERS) + '\n'
    for mode in ['prepare', 'production']:
        prior = before.caddy(data, mode)
        assert after.caddy(data, mode) == prior
        rendered = after.caddy(proposed, mode)
        if mode == 'prepare':
            assert rendered == prior
        else:
            assert rendered.count(added) == rendered.count(wrapper) == 1
            assert rendered.replace(added, '').replace(wrapper, '').replace(':8080 {', ':80 {') == prior
        (output / ('Caddyfile.' + mode)).write_text(rendered)
    for site in data['sites']:
        assert before.unit(site) == after.unit(site)
    for value in [1, 'true', [], None]:
        bad = copy.deepcopy(proposed)
        bad['codi_shared_ingress'] = value
        try:
            after.validate(bad)
        except ValueError:
            pass
        else:
            raise AssertionError('Invalid shared ingress flag accepted')
    metadata = json.loads((runtime / 'runtime.json').read_text())
    key = digest(runtime / 'runtime.json')
    assert metadata['version'] == 'codi-haproxy-runtime/1' and metadata['upstreamRelease'] == '2.8.31'
    assert set(p.name for p in runtime.iterdir()) == {'runtime.json', 'haproxy', 'LICENSE-haproxy'}
    for name, record in metadata['files'].items():
        assert not (runtime / name).is_symlink() and record == {'bytes': (runtime / name).stat().st_size, 'sha256': digest(runtime / name)}
    installed = '/srv/codi-ingress/runtimes/' + key
    (output / 'haproxy.cfg').write_text(haproxy())
    (output / 'codi-shared-ingress.service').write_text(service(installed + '/haproxy', '/etc/codi-ingress/haproxy.cfg'))
    (output / '30-codi-ingress.conf').write_text(caddy_dependency())
    report = {'status': 'PASS', 'scope': 'Offline shared ingress flag, unchanged preparation mode, all existing website blocks/routes/units preserved; only production listener topology changes',
              'originalGeneratorSHA256': digest(source), 'originalManifestSHA256': digest(manifest),
              'runtimeManifestSHA256': key, 'runtimeFiles': metadata['files'],
              'candidateFilesSHA256': {p.name: digest(p) for p in output.iterdir() if p.is_file()},
              'siteDomains': sorted(s['domain'] for s in data['sites'] if s['enabled']),
              'nativeUnitsEnabledForBoot': False, 'ingressFollowsExistingCaddyBoot': True,
              'routerFirewallAndPublicPortsChanged': False, 'sourceSHA256': {'scripts/prepare-shared-ingress.py': digest(Path(__file__)), 'ingress_service/configuration.py': digest(ROOT / 'ingress_service/configuration.py')}}
    (output / 'candidate-result.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, required=True)
    parser.add_argument('--manifest', type=Path, required=True)
    parser.add_argument('--runtime', type=Path, required=True)
    parser.add_argument('--output-dir', type=Path, required=True)
    args = parser.parse_args()
    prepare(args.source, args.manifest, args.runtime, args.output_dir)
