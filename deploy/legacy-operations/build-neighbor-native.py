#!/usr/bin/env python3
"""Seal explicit native18 introductions over native17; retain prior contracts.

Only builds immutable public/native code. Does not install, sign, migrate state,
change hosting, or amend the frozen native17 graph contract.
"""
import argparse
import importlib.util
import json
from pathlib import Path
import re
import shutil
import sys
import tempfile

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('neighbor_build_utilities', ROOT / 'scripts/build-mesh-native.py')
util = importlib.util.module_from_spec(spec)
spec.loader.exec_module(util)
BASE = ROOT / '.build/releases/connected-mesh-native-r1'
PIN = '8a90a16ecab32e897f5cd811c6e3aadedcaf574d47debedf9338659346546bdb'
PROFILE = 'codi-connected-development/18'
MODULES = util.MODULES | {'mesh-introductions.mjs'}
record, encoded, key = util.record, util.encoded, util.key
GRAPH_VERIFIER = util.GRAPH_VERIFIER.replace('def verify_mesh_graph(', 'def verify_neighbor_graph(').replace(
    "{'version','profile','modules','directory','core','coreDirectory'}", "{'version','profile','modules','directory','core','coreDirectory','automaticNeighbors'}").replace(
    "metadata['version']!='codi-network-release/2'", "metadata['version']!='codi-network-release/3' or metadata['automaticNeighbors']!='codi-peer-introductions/1'").replace(
    "expected=frozenset(" + repr(sorted(util.MODULES)) + ')', "expected=frozenset(" + repr(sorted(MODULES)) + ')').replace(
    'assets/desktop/network-v3/', 'assets/desktop/network-v4/').replace('assets/desktop/core-v3/', 'assets/desktop/core-v4/')
assert GRAPH_VERIFIER != util.GRAPH_VERIFIER and 'mesh-introductions.mjs' in GRAPH_VERIFIER


def patch_native(stage):
    def change(name, transform):
        p = stage / name
        old = p.read_text()
        new = transform(old)
        assert new != old, name
        p.write_text(new)

    def extend(text):
        assert "'codi-connected-development/17')" in text
        return text.replace("'codi-connected-development/17')", "'codi-connected-development/17','codi-connected-development/18')")

    def verifier(text):
        assert text.count('range(1,18)') == 1 and text.count("'codi-connected-development/17':V15_NATIVE}") == 1
        text = text.replace('range(1,18)', 'range(1,19)').replace(
            "'codi-connected-development/17':V15_NATIVE}", "'codi-connected-development/17':V15_NATIVE,'codi-connected-development/18':V15_NATIVE}")
        anchor = " if manifest['version']=='codi-connected-development/17':verify_mesh_graph(directory,frontend)"
        assert text.count(anchor) == 1
        return text.replace(anchor, anchor + "\n if manifest['version']=='codi-connected-development/18':verify_neighbor_graph(directory,frontend)") + GRAPH_VERIFIER

    change('origin_service/release.py', verifier)

    def operator(text):
        text = extend(text).replace('profile-5..17', 'profile-5..18')
        anchor = "  if role=='issuer' and json.loads((source/'connected-release.json').read_text())['version']=='codi-connected-development/17':command+=['--mesh-public-groups']"
        assert text.count(anchor) == 1
        return text.replace(anchor, anchor + "\n  if role=='issuer' and json.loads((source/'connected-release.json').read_text())['version']=='codi-connected-development/18':command+=['--mesh-auto-neighbors']")

    change('scripts/manage-services.py', operator)
    change('origin_service/deployment.py', extend)
    change('origin_service/turn_management.py', extend)

    def issuer(text):
        anchor = "    public_groups.add_argument('--mesh-public-groups',action='store_true',help='Enable bounded public mesh3 and consented browser admission')"
        assert text.count(anchor) == 1
        text = text.replace(anchor, anchor + "\n    public_groups.add_argument('--mesh-auto-neighbors',action='store_true',help='Enable bounded mesh3 peer introductions on the shared pool')")
        anchor = "                    if a.mesh_public_groups:config['meshGroups']={'version':'codi-public-mesh/3'}"
        assert text.count(anchor) == 1
        return text.replace(anchor, anchor + "\n                    if a.mesh_auto_neighbors:config['meshGroups']={'version':'codi-public-mesh/3','automaticNeighbors':'codi-peer-introductions/1'}")

    change('scripts/serve-connected.py', issuer)


def build(destination):
    old = util.contract(BASE / 'origin_service/release.py')
    assert old.verify(BASE)['manifestSHA256'] == PIN
    destination = Path(destination).resolve()
    assert not destination.exists() and destination.is_relative_to(ROOT / '.build/releases')
    stage = Path(tempfile.mkdtemp(prefix='.neighbor-native-', dir=destination.parent))
    try:
        shutil.copytree(BASE, stage, dirs_exist_ok=True)
        changed = set()

        def put(name, raw):
            assert old.public_name(name), name
            p = stage / name
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_bytes(raw if isinstance(raw, bytes) else raw.encode())
            changed.add(name)

        assert {p.name for p in (ROOT / 'network').glob('*.mjs')} == MODULES
        vendor = json.loads((ROOT / 'assets/vendor/gossip/manifest.json').read_bytes())
        assert record(ROOT / 'network/gossip-vendor.mjs') == vendor['output']
        assert record(ROOT / 'assets/vendor/gossip/LICENSES.txt') == vendor['legal']
        sources = {n: (ROOT / 'network' / n).read_text() for n in sorted(MODULES)}
        anchor = '../assets/vendor/chess/chess.mjs'
        assert sources['chess-record.mjs'].count(anchor) == 1
        sources['chess-record.mjs'] = sources['chess-record.mjs'].replace(anchor, '../../../vendor/chess/chess.mjs')
        for name, text in sources.items():
            if name == 'gossip-vendor.mjs':
                continue
            for _, target in re.findall(r"(?:\bfrom\s+|\bimport\s*\(|new URL\s*\()(['\"])(.*?)\1", text):
                assert (target.startswith('./') and target[2:] in MODULES) or (name == 'chess-record.mjs' and target == '../../../vendor/chess/chess.mjs'), (name, target)
        records = {n: {'bytes': len(t.encode()), 'sha256': util.sha(t.encode())} for n, t in sources.items()}
        folder = 'assets/desktop/network-v4/' + key(records)
        for name, text in sources.items():
            put(folder + '/' + name, text)
        legal = ROOT / 'network/gossip-vendor.mjs.LEGAL.txt'
        if legal.exists():
            put(folder + '/' + legal.name, legal.read_bytes())

        graph = json.loads((BASE / 'assets/desktop/network-release.json').read_bytes())
        previous = graph['coreDirectory']
        core = {n: (BASE / previous / n).read_text() for n in graph['core']}
        for name in ['app.js', 'networking.js']:
            assert graph['directory'] + '/' in core[name]
            core[name] = core[name].replace(graph['directory'] + '/', folder + '/')
        records_core = {n: {'bytes': len(t.encode()), 'sha256': util.sha(t.encode())} for n, t in core.items()}
        host = 'assets/desktop/core-v4/' + key(records_core)
        for name, text in core.items():
            put(host + '/' + name, text)
        put('index.html', (BASE / 'index.html').read_text().replace(previous, host))
        put('assets/desktop/network-release.json', encoded({'version': 'codi-network-release/3',
            'profile': 'codi-public-mesh/3', 'automaticNeighbors': 'codi-peer-introductions/1',
            'modules': records, 'directory': folder, 'core': records_core, 'coreDirectory': host}))
        patch_native(stage)
        cache = json.loads((BASE / 'assets/desktop/cache-manifest.json').read_bytes())
        cache['files'] = {n: record(stage / n) for n in sorted(set(cache['files']) | changed)}
        cache['id'] = key(cache['files'])
        template = (ROOT / 'scripts/templates/device-cache-worker.js').read_text()
        assert template.count('__PUBLIC_CACHE_MANIFEST__') == 1
        put('assets/desktop/cache-manifest.json', encoded(cache))
        put('assets/desktop/offline-worker.js', template.replace('__PUBLIC_CACHE_MANIFEST__', json.dumps(cache, separators=(',', ':'))))
        public = json.loads((BASE / 'release.json').read_bytes())
        public['files'] = {n: record(stage / n) for n in sorted(set(public['files']) | changed)}
        (stage / 'release.json').write_bytes(encoded(public))
        full = json.loads((BASE / 'connected-release.json').read_bytes())
        full['version'] = PROFILE
        full['files'] = {str(p.relative_to(stage)): record(p) for p in sorted(stage.rglob('*')) if p.is_file() and p.name != 'connected-release.json'}
        (stage / 'connected-release.json').write_bytes(encoded(full))
        actual = {n for n in old.V15_NATIVE if record(stage / n) != record(BASE / n)}
        assert actual == util.NATIVE_CHANGES
        for n, value in json.loads((BASE / 'release.json').read_bytes())['files'].items():
            if n not in {'index.html', 'assets/desktop/network-release.json', 'assets/desktop/cache-manifest.json', 'assets/desktop/offline-worker.js'}:
                assert record(stage / n) == value, n
        current = util.contract(stage / 'origin_service/release.py')
        verified = current.verify(stage)
        assert current.verify(BASE)['manifestSHA256'] == PIN
        assert current.verify(util.BASE)['manifestSHA256'] == util.PIN
        for p in [stage, *stage.rglob('*')]:
            p.chmod(0o755 if p.is_dir() else 0o644)
        stage.rename(destination)
        return verified | {'status': 'PASS', 'directory': str(destination), 'baseManifestSHA256': PIN,
            'nativeChanges': sorted(actual), 'unchangedNativeFiles': len(old.V15_NATIVE) - len(actual),
            'native16And17Verified': True, 'productionChanged': False}
    finally:
        if stage.exists():
            shutil.rmtree(stage)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(build(args.output), indent=2))
