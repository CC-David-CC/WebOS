#!/usr/bin/env python3
"""Native18 composition, native16/17 compatibility and hostile graph mutations."""
import argparse
import hashlib
import importlib.util
import itertools
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('neighbor_check_util', ROOT / 'scripts/mesh-native-release-check.py')
util = importlib.util.module_from_spec(spec)
spec.loader.exec_module(util)
BASE = ROOT / '.build/releases/connected-mesh-native-r1'


def run(release):
    checks = []

    def check(name, value):
        assert value, name
        checks.append(name)

    c = util.load(release / 'origin_service/release.py')
    verified = c.verify(release)
    check('native18 verifies its complete sealed bytes', json.loads((release / 'connected-release.json').read_bytes())['version'] == 'codi-connected-development/18')
    check('new verifier retains native17 without widening its32-module contract', c.verify(BASE)['manifestSHA256'] == '8a90a16ecab32e897f5cd811c6e3aadedcaf574d47debedf9338659346546bdb')
    check('native16 actual-root verification remains intact', c.verify(util.BASE)['manifestSHA256'] == 'c23b1b73df68ffb25da810a7db73074d09297f0ccc06c459e8bc9c0430ca30c1')
    expected = {'origin_service/release.py', 'origin_service/deployment.py', 'origin_service/turn_management.py', 'scripts/manage-services.py', 'scripts/serve-connected.py'}
    check('48 native account file guest cookie and authority implementations are unchanged', len(c.V15_NATIVE) == 53 and {n for n in c.V15_NATIVE if util.record(release / n) != util.record(BASE / n)} == expected)
    old_public = json.loads((BASE / 'release.json').read_bytes())['files']
    exceptions = {'index.html', 'assets/desktop/network-release.json', 'assets/desktop/cache-manifest.json', 'assets/desktop/offline-worker.js'}
    check('all retained public assets survive except four active metadata entries', all(util.record(release / n) == value for n, value in old_public.items() if n not in exceptions))
    graph = json.loads((release / 'assets/desktop/network-release.json').read_bytes())
    old_graph = json.loads((BASE / 'assets/desktop/network-release.json').read_bytes())
    check('33-module graph explicitly binds automatic neighbor policy and its worker dependencies', len(graph['modules']) == 33 and graph['version'] == 'codi-network-release/3' and graph['automaticNeighbors'] == 'codi-peer-introductions/1' and {'mesh-introductions.mjs', 'admission-work-worker.mjs'} <= set(graph['modules']))
    for n in graph['core']:
        if n == 'desktop-apps.js':
            continue  # Its catalog changes through the generic app merger.
        old = (BASE / old_graph['coreDirectory'] / n).read_text()
        check('active host preserves reviewed native17 behavior for ' + n, (release / graph['coreDirectory'] / n).read_text() == old.replace(old_graph['directory'] + '/', graph['directory'] + '/'))
    import re

    def catalog(folder, g):
        text = (folder / g['coreDirectory'] / 'desktop-apps.js').read_text()
        loader = re.search(r'assets/desktop/apps-v2-[a-f0-9]+\.mjs', text)[0]
        path = re.search(r'apps-v2-[a-f0-9]+\.json', (folder / loader).read_text())[0]
        return {a['id']: a for a in json.loads((folder / 'assets/desktop' / path).read_bytes())['apps']}

    a, b = catalog(BASE, old_graph), catalog(release, graph)
    check('only Rooms changes among seven public apps and terminal remains identical', set(a) == set(b) and [k for k in a if a[k] != b[k]] == ['rooms'] and a['terminal'] == b['terminal'])
    for app in b.values():
        for name, value in app['files'].items():
            assert util.record(release / Path(app['path']).parent / name) == value
    check('generic merged API2 catalog binds each module sibling asset and stylesheet', bool(b['rooms']['styles']))
    node = ROOT / '.build/tools/node-v24.22.1-linux-x64/bin/node'
    for n in graph['core']:
        subprocess.run([str(node), '--check', str(release / graph['coreDirectory'] / n)], capture_output=True, check=True)
    for n in expected:
        compile((release / n).read_text(), n, 'exec')
    check('active host and changed native modules parse', True)
    python = ROOT.parent / '.build/auth-venv/bin/python'
    entry = release / 'scripts/serve-connected.py'
    flags = ['--mesh-auto-neighbors', '--mesh-public-groups', '--routed-public-groups']
    help_run = subprocess.run([str(python), '-B', str(entry), '--help'], capture_output=True, text=True)
    check('actual issuer advertises the three explicit retained group policies', help_run.returncode == 0 and all(f in help_run.stdout for f in flags))
    for x, y in itertools.combinations(flags, 2):
        value = subprocess.run([str(python), '-B', str(entry), x, y], capture_output=True, text=True)
        check('actual issuer rejects simultaneous ' + x + ' and ' + y, value.returncode == 2 and 'not allowed with argument' in value.stderr)

    def reject(name, mutate, original=release, expected_error=None):
        with tempfile.TemporaryDirectory(prefix='neighbor-graph-mutation-', dir=ROOT / '.build') as tmp:
            folder = Path(tmp) / 'release'
            shutil.copytree(original, folder)
            mutate(folder)
            public = json.loads((folder / 'release.json').read_bytes())
            full = json.loads((folder / 'connected-release.json').read_bytes())
            public['files'] = {n: util.record(folder / n) for n in public['files']}
            (folder / 'release.json').write_bytes(util.encoded(public))
            full['files'] = {n: util.record(folder / n) for n in full['files']}
            (folder / 'connected-release.json').write_bytes(util.encoded(full))
            try:
                c.verify(folder)
            except (ValueError, KeyError) as error:
                if expected_error:
                    assert expected_error in str(error), error
                check(name, True)
            else:
                raise AssertionError(name)

    def metadata(folder, action):
        p = folder / 'assets/desktop/network-release.json'
        value = json.loads(p.read_bytes())
        action(value)
        p.write_bytes(util.encoded(value))

    reject('native18 refuses missing introduction code after outer rehash', lambda p: metadata(p, lambda g: g['modules'].pop('mesh-introductions.mjs')))
    reject('native18 refuses a different introduction policy after outer rehash', lambda p: metadata(p, lambda g: g.update(automaticNeighbors='unsupported')))
    reject('native18 refuses an older graph version after outer rehash', lambda p: metadata(p, lambda g: g.update(version='codi-network-release/2')))
    reject('native18 refuses a substituted graph path after outer rehash', lambda p: metadata(p, lambda g: g.update(directory='assets/desktop/network-v4/' + '0' * 64)))
    reject('native18 refuses unbound active host bytes after outer rehash', lambda p: (p / graph['coreDirectory'] / 'networking.js').write_text('throw Error("substituted host");'))

    def widen17(folder):
        path = old_graph['directory'] + '/mesh-introductions.mjs'
        shutil.copyfile(release / graph['directory'] / 'mesh-introductions.mjs', folder / path)
        value = util.record(folder / path)
        for filename in ['release.json', 'connected-release.json']:
            p = folder / filename
            data = json.loads(p.read_bytes())
            data['files'][path] = value
            p.write_bytes(util.encoded(data))
        metadata(folder, lambda g: g['modules'].update({'mesh-introductions.mjs': value}))

    reject('new verifier still refuses silently widening a native17 graph', widen17, BASE, 'Incomplete mesh graph')
    return {'status': 'PASS', 'checks': checks, 'nativeManifestSHA256': verified['manifestSHA256'],
            'productionChanged': False, 'nativeServicesStarted': False}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--release', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    result = {'status': 'FAIL'}
    try:
        result.update(run(args.release.resolve()))
    finally:
        result['sourceSHA256'] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
        args.output.write_text(json.dumps(result, indent=2) + '\n')
        print(json.dumps(result, indent=2))
