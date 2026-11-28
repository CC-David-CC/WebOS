"""Package a clean WebOS editor checkout and record its source and payload hashes."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('app', choices=['prosecraft', 'chiralcraft', 'fontcraft', 'diacraft'])
parser.add_argument('out', type=Path)
args = parser.parse_args()
app = args.app
source = ROOT / 'apps' / app
out = args.out.resolve()
if out.exists() or out.is_relative_to(ROOT):
    raise SystemExit('Choose a new external package directory.')


def run(*cmd, **kwargs):
    return subprocess.check_output(cmd, cwd=source, **kwargs)


if run('git', 'status', '--porcelain'):
    raise SystemExit('Commit the app sources before packaging.')
pin = run('git', 'rev-parse', 'HEAD').decode().strip()
tree = run('git', 'rev-parse', 'HEAD^{tree}').decode().strip()
files = []


def add(name, data):
    destination = out / name
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(data)
    files.append(dict(path=name, bytes=len(data), sha256=hashlib.sha256(data).hexdigest()))


def add_tree(directory, prefix):
    for path in sorted(directory.rglob('*')):
        if path.is_file():
            if path.is_symlink():
                raise ValueError('Symlink in package input')
            add(prefix + '/' + path.relative_to(directory).as_posix(), path.read_bytes())


def external_scripts(html):
    def external(match):
        data = match[1].encode()
        name = 'startup-' + hashlib.sha256(data).hexdigest()[:16] + '.js'
        add('native/' + name, data)
        return '<script src="./' + name + '"></script>'
    return re.sub(r'<script>(.*?)</script>', external, html, flags=re.S)


def prose():
    run('npm', 'ci', '--ignore-scripts', '--no-audit', '--no-fund')
    run('npm', 'run', 'build', env=dict(os.environ, PAGES_BASE='/prosecraft', WEBOS_SOURCE_COMMIT=pin))
    for path in sorted((source / 'build').rglob('*')):
        if not path.is_file():
            continue
        name = path.relative_to(source / 'build').as_posix()
        if name == 'index.html':
            html = external_scripts(path.read_text()).replace('<html lang="en">', '<html lang="en" data-editor="prosecraft">')
            add('native/index.html', html.replace('<head>', '<head><script src="scoped-editor-storage.js"></script>') .encode())
        else:
            add('native/' + name, path.read_bytes())
    notices = []
    for package in sorted((source / 'node_modules').rglob('package.json')):
        for path in sorted(package.parent.glob('*')):
            if path.is_file() and path.name.lower().startswith(('license', 'licence', 'copying', 'ofl', 'notice')):
                notices.append(str(path.relative_to(source)) + '\n\n' + path.read_text(errors='replace'))
    add('legal/dependency-notices.txt', '\n\n'.join(notices).encode())


def wasm(work):
    manifest, binary, extra = {
        'fontcraft': ('webos/Cargo.toml','fontcraft_web',['--lib']),
        'chiralcraft': ('crates/chiralcraft-app/Cargo.toml','chiralcraft',['--bin','chiralcraft']),
        'diacraft': ('apps/diacraft-web/Cargo.toml','diacraft-web',['--bin','diacraft-web']),
    }[app]
    profile = 'web' if app == 'diacraft' else 'release'
    target = Path(os.environ.get('CARGO_TARGET_DIR', work / 'target')).resolve()
    run('cargo','build','--locked','--target-dir',target,'--target','wasm32-unknown-unknown',
        '--profile',profile,'--manifest-path',manifest,*extra)
    artifact = target / 'wasm32-unknown-unknown' / profile / (binary + '.wasm')
    run('wasm-bindgen','--target','web','--no-typescript','--out-name','engine','--out-dir',work / 'bindings',artifact)
    add_tree(work / 'bindings', 'native')
    add_tree(source / 'webos/native', 'native')
    if app == 'diacraft':
        add('native/page.css', (source / 'apps/diacraft-web/page.css').read_bytes())
        assets = {}
        for key, name in [('splash','assets/branding/diacraft-splash.png'), ('cover','assets/branding/diacraft-cover.png'), ('licenses','THIRD-PARTY-LICENSES-WEB.txt')]:
            path = source / name
            data = path.read_bytes()
            sha = hashlib.sha256(data).hexdigest()
            asset = 'assets/' + key + '-' + sha[:16] + path.suffix
            add('native/' + asset, data)
            assets[key] = dict(file=asset, sha256=sha, bytes=len(data))
        add('native/manifest.json', json.dumps(dict(version=1, assets=assets)).encode())
    if app == 'chiralcraft':
        add('legal/source.zip',run('git','archive','--format=zip',pin))


add('index.mjs', (source / 'webos/app.mjs').read_bytes())
for name in ['LICENSE', 'LICENSE-MIT', 'LICENSE-APACHE', 'NOTICE', 'ATTRIBUTION.md', 'THIRD-PARTY-LICENSES-WEB.txt']:
    if (source / name).is_file():
        add('legal/' + name, (source / name).read_bytes())
if app == 'prosecraft':
    prose()
else:
    with tempfile.TemporaryDirectory(prefix='webos-editor-') as scratch:
        wasm(Path(scratch))
if run('git', 'rev-parse', 'HEAD').decode().strip() != pin or run('git','diff','--name-only',pin):
    raise ValueError('Source changed during build')
(out / 'component-build.json').write_text(json.dumps(dict(schema='webos-component-build/1',component=app,
    sourceCommit=pin,sourceTree=tree,files=files),indent=2) + '\n')
