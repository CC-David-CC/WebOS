#!/usr/bin/env python3
"""Seal the explicit native25/40-module bounded mailbox graph over frozen native24.

No install/state change. Existing profile1..24 validators remain closed and
unchanged; profile25 has a separate exact module roster and graph contract.
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
BASE = ROOT/'.build/releases/connected-history-native-r2'
PIN = 'ba89487b3ea3fbca334abd3cc8f3467b8dd604bab51a141ed221236a4c1871f5'
PROFILE = 'codi-connected-development/25'


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    value = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value


def build(destination):
    util = module('reader_build_records', ROOT/'scripts/build-native-app-update.py')
    previous = module('reader_build_previous', BASE/'origin_service/release.py')
    assert previous.verify(BASE)['manifestSHA256'] == PIN
    old = json.loads((BASE/'assets/desktop/network-release.json').read_bytes())
    modules = set(old['modules']) | {'hosted-reader-directory.mjs'}
    assert len(modules) == 40 and {p.name for p in (ROOT/'network').glob('*.mjs')} == modules
    destination = destination.resolve()
    assert not destination.exists() and destination.is_relative_to(ROOT/'.build/releases')
    stage = Path(tempfile.mkdtemp(prefix='.hosted-readers-native-', dir=destination.parent))
    new = set()
    try:
        shutil.copytree(BASE, stage, dirs_exist_ok=True)

        def put(name, raw):
            assert previous.public_name(name), name
            path = stage/name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(raw if isinstance(raw, bytes) else raw.encode())
            new.add(name)

        sources = {n: (ROOT/'network'/n).read_text() for n in sorted(modules)}
        sources['chess-record.mjs'] = sources['chess-record.mjs'].replace('../assets/vendor/chess/chess.mjs', '../../../vendor/chess/chess.mjs')
        for name, text in sources.items():
            if name == 'gossip-vendor.mjs':
                continue
            for _, target in re.findall(r"(?:\bfrom\s+|\bimport\s*\(|new URL\s*\()(['\"])(.*?)\1", text):
                assert target.startswith('./') and target[2:] in modules or name == 'chess-record.mjs' and target == '../../../vendor/chess/chess.mjs', (name, target)
        records = {n: {'bytes': len(t.encode()), 'sha256': util.sha(t.encode())} for n, t in sources.items()}
        folder = 'assets/desktop/network-v10/'+util.key(records)
        for name, text in sources.items():
            put(folder+'/'+name, text)
        core = {n: (BASE/old['coreDirectory']/n).read_text() for n in old['core']}
        core['networking.js'] = (ROOT/'networking.js').read_text()
        assert 'stateWindows:true,readerOrganization:true,readerDirectory:true' in core['networking.js']
        core['networking.js'] = re.sub(r"import\((['\"])\./([^'\"]+)\1\)", lambda m: 'import(new URL('+repr(m[2])+',document.baseURI))', core['networking.js'])
        core['networking.js'] = re.sub(r"(['\"])network/([^'\"?]+)(?:\?[^'\"]*)?\1", lambda m: repr(folder+'/'+m[2]), core['networking.js'])
        core['app.js'] = core['app.js'].replace(old['directory']+'/', folder+'/')
        core_records = {n: {'bytes': len(t.encode()), 'sha256': util.sha(t.encode())} for n, t in core.items()}
        host = 'assets/desktop/core-v10/'+util.key(core_records)
        for name, text in core.items():
            put(host+'/'+name, text)
        put('index.html', (BASE/'index.html').read_text().replace(old['coreDirectory'], host))
        graph = {**old, 'version': 'codi-network-release/9', 'readerDirectory': 'codi-reader-rendezvous/1', 'mailPolling': 'codi-reader-mail-poll/1', 'modules': records, 'directory': folder, 'core': core_records, 'coreDirectory': host}
        put('assets/desktop/network-release.json', util.encoded(graph))

        def change(name, fn):
            path = stage/name
            before = path.read_text()
            after = fn(before)
            assert before != after, name
            path.write_text(after)

        def extend(text):
            needle = "'codi-connected-development/24')"
            assert needle in text
            return text.replace(needle, "'codi-connected-development/24','codi-connected-development/25')")

        def verifier(text):
            body = text.split('\ndef verify_hosted_directory_graph(', 1)[1]
            assert '\ndef ' not in body
            readers = '\ndef verify_hosted_mail_graph('+body
            readers = readers.replace("'readerDirectory'}", "'readerDirectory','mailPolling'}")
            readers = readers.replace("metadata['version']!='codi-network-release/8'", "metadata['version']!='codi-network-release/9' or metadata['mailPolling']!='codi-reader-mail-poll/1'")
            needle = 'expected=frozenset('+repr(sorted(old['modules']))+')'
            assert needle in readers
            readers = readers.replace(needle, 'expected=frozenset('+repr(sorted(modules))+')')
            readers = readers.replace('assets/desktop/network-v9/', 'assets/desktop/network-v10/').replace('assets/desktop/core-v9/', 'assets/desktop/core-v10/')
            assert "'hosted-reader-directory.mjs'" in readers
            text = text.replace('range(1,25)', 'range(1,26)').replace("'codi-connected-development/24':V19_NATIVE}", "'codi-connected-development/24':V19_NATIVE,'codi-connected-development/25':V19_NATIVE}")
            anchor = " if manifest['version']=='codi-connected-development/24':verify_hosted_directory_graph(directory,frontend)"
            assert text.count(anchor) == 1
            return text.replace(anchor, anchor+"\n if manifest['version']=='codi-connected-development/25':verify_hosted_mail_graph(directory,frontend)")+readers

        change('origin_service/release.py', verifier)
        change('origin_service/deployment.py', extend)
        change('origin_service/turn_management.py', extend)
        change('scripts/manage-services.py', lambda text: extend(text).replace('profile-5..24', 'profile-5..25'))
        cache = json.loads((BASE/'assets/desktop/cache-manifest.json').read_bytes())
        cache['files'] = {n: util.record(stage/n) for n in sorted(set(cache['files']) | new)}
        cache['id'] = util.key(cache['files'])
        put('assets/desktop/cache-manifest.json', util.encoded(cache))
        template = (ROOT/'scripts/templates/device-cache-worker.js').read_text()
        put('assets/desktop/offline-worker.js', template.replace('__PUBLIC_CACHE_MANIFEST__', json.dumps(cache, separators=(',', ':'))))
        public = json.loads((BASE/'release.json').read_bytes())
        public['files'] = {n: util.record(stage/n) for n in sorted(set(public['files']) | new)}
        (stage/'release.json').write_bytes(util.encoded(public))
        full = json.loads((BASE/'connected-release.json').read_bytes())
        full['version'] = PROFILE
        full['files'] = {str(p.relative_to(stage)): util.record(p) for p in sorted(stage.rglob('*')) if p.is_file() and p.name != 'connected-release.json'}
        (stage/'connected-release.json').write_bytes(util.encoded(full))
        checked = module('reader_build_final', stage/'origin_service/release.py').verify(stage)
        changed = [n for n in sorted(previous.V19_NATIVE) if util.record(BASE/n) != util.record(stage/n)]
        assert set(changed) == {'origin_service/release.py', 'origin_service/deployment.py', 'origin_service/turn_management.py', 'scripts/manage-services.py'}
        # The application catalog/bundles, guest policy/runtime, worker and actual
        # service implementation stay byte-identical to the current live release.
        assert all(full['files'][n] == value for n, value in json.loads((BASE/'connected-release.json').read_bytes())['files'].items() if '/apps/' in n)
        stage.rename(destination)
        return dict(status='PASS', directory=str(destination), manifestSHA256=checked['manifestSHA256'], files=checked['files'], networkModules=40, nativeFiles=57, nativeChanged=changed, baseManifestSHA256=PIN, installed=False)
    finally:
        if stage.exists():
            shutil.rmtree(stage)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(build(args.output), indent=2))
