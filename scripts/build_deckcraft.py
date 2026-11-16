#!/usr/bin/env python3
"""Build the selected DeckCraft browser component with required assembly inputs."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import tomllib


def digest(file):
    value = hashlib.sha256()
    with file.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            value.update(block)
    return value.hexdigest()


def git(repo, *arguments):
    return subprocess.check_output(['git', '--no-optional-locks', '-c', 'core.fsmonitor=false',
                                    '-c', 'core.hooksPath=/dev/null', '-C', str(repo), *arguments],
                                   text=True).strip()


def direct(path):
    if '..' in path.parts:
        raise ValueError('Parent traversal is not an accepted build path')
    if any(parent.is_symlink() for parent in (path, *path.parents)):
        raise ValueError('Direct output and input paths required')


def main():
    os.umask(0o077)
    root = Path(__file__).resolve().parent.parent
    source, fonts, core = root / 'apps/deckcraft', root / 'assets/craft-fonts', root / 'libraries/craft-libs'
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True, type=Path, help='New external component site')
    parser.add_argument('--target-dir', required=True, type=Path, help='External Cargo output/cache')
    parser.add_argument('--cargo', default='cargo')
    parser.add_argument('--wasm-bindgen', default='wasm-bindgen')
    parser.add_argument('--node', default='node')
    parser.add_argument('--offline', action='store_true')
    args = parser.parse_args()
    output, target = args.output.absolute(), args.target_dir.absolute()
    stage = output.with_name(output.name + '.build')
    for path in (root, output, target, stage):
        direct(path)
    if any(path.is_relative_to(root) or root.is_relative_to(path) for path in (output, target, stage)):
        parser.error('Build outputs must be outside the source assembly')
    if output.exists() or stage.exists():
        parser.error('Unknown or existing output/staging collision; preserve and inspect it')
    if not (fonts / 'fonts/latin-manifest.txt').is_file():
        parser.error('Initialize the selected shared fonts, including the Latin catalogue')
    selected = {name: git(repo, 'rev-parse', 'HEAD') for name, repo in [('deckcraft', source), ('fonts', fonts), ('core', core)]}
    for repo in (source, fonts, core):
        if git(repo, 'status', '--porcelain'):
            parser.error('Build inputs must be clean committed components')
    tools = {name: shutil.which(value) for name, value in [('cargo', args.cargo), ('wasm-bindgen', args.wasm_bindgen), ('node', args.node)]}
    if not all(tools.values()):
        parser.error('Cargo, matching wasm-bindgen and Node executables are required')
    lock = tomllib.loads((source / 'Cargo.lock').read_text())
    expected_bindgen = next(package['version'] for package in lock['package'] if package['name'] == 'wasm-bindgen')
    versions = {name: subprocess.check_output([tool, '--version'], text=True).strip() for name, tool in tools.items()}
    if versions['wasm-bindgen'] != 'wasm-bindgen ' + expected_bindgen:
        parser.error('wasm-bindgen must match the selected Cargo.lock exactly')
    if shutil.disk_usage(output.parent).free < 200 * 1024 * 1024:
        parser.error('At least 200 MiB output headroom required; compiler cache needs separate capacity')
    lock_sha = digest(source / 'Cargo.lock')
    stage.mkdir(mode=0o700)
    raw_site = stage / 'bindgen-site'; raw_site.mkdir(mode=0o700)
    env = dict(os.environ, CRAFT_FONTS_DIR=str(fonts), CRAFT_REQUIRE_FONTS='1', CARGO_INCREMENTAL='0')
    env['PATH'] = str(Path(tools['cargo']).absolute().parent) + os.pathsep + env.get('PATH', '')
    command = [tools['cargo'], 'build', '--release', '--locked', '--jobs', '1', '-p', 'deckcraft-web',
               '--target', 'wasm32-unknown-unknown', '--target-dir', str(target)]
    if args.offline:
        command.append('--offline')
    subprocess.run(command, cwd=source, env=env, check=True)
    raw = target / 'wasm32-unknown-unknown/release/deckcraft-web.wasm'
    raw_sha = digest(raw)
    subprocess.run([tools['wasm-bindgen'], '--target', 'web', '--out-dir', str(raw_site),
                    '--out-name', 'deckcraft', '--no-typescript', str(raw)], check=True)
    html = (source / 'apps/deckcraft-web/index.html').read_text()
    rust = '<link data-trunk rel="rust" data-bin="deckcraft-web" data-wasm-opt="z" data-weak-refs />'
    icon = '<link data-trunk rel="icon" href="../../assets/app-icon/deckcraft.ico" />'
    if html.count(rust) != 1 or html.count(icon) != 1:
        raise ValueError('Native browser HTML changed; inspect its build inputs')
    html = html.replace(rust, '<script type="module">import init from "./deckcraft.js"; await init();</script>')
    html = html.replace(icon, '<link rel="icon" href="./deckcraft.ico" />')
    (raw_site / 'index.html').write_text(html)
    shutil.copyfile(source / 'assets/app-icon/deckcraft.ico', raw_site / 'deckcraft.ico')
    for name in ('ATTRIBUTION.md', 'NOTICE', 'LICENSE-MIT', 'LICENSE-APACHE'):
        shutil.copyfile(source / name, raw_site / name)
    packaged = subprocess.check_output([tools['node'], str(source / 'webos/package-browser.mjs'),
                                        str(raw_site), str(output)], text=True)
    package = json.loads(packaged)
    if digest(source / 'Cargo.lock') != lock_sha or digest(raw) != raw_sha:
        raise ValueError('Build inputs/output changed during packaging')
    for name, repo in [('deckcraft', source), ('fonts', fonts), ('core', core)]:
        if git(repo, 'rev-parse', 'HEAD') != selected[name] or git(repo, 'status', '--porcelain'):
            raise ValueError('Selected source changed during build')
    receipt = {'schema': 'webos-component-build/1', 'component': 'deckcraft',
               'sourceCommit': selected['deckcraft'], 'cargoLockSha256': lock_sha,
               'nativeBuild': {'sourceCommit': selected['deckcraft'], 'target': 'wasm32-unknown-unknown',
                               'profile': 'release', 'rawSha256': raw_sha, 'rawBytes': raw.stat().st_size,
                               'toolVersions': versions, 'sharedCoreCommit': selected['core'],
                               'fontsCommit': selected['fonts'], 'coldBuildClaimed': False},
               'packaging': package['transformation'], 'files': package['files'],
               'totalBytes': sum(file['bytes'] for file in package['files'])}
    with (output / 'component-build.json').open('x') as stream:
        json.dump(receipt, stream, indent=2); stream.write('\n')
    print(json.dumps({'component': 'deckcraft', 'sourceCommit': selected['deckcraft'],
                      'files': len(receipt['files']), 'totalBytes': receipt['totalBytes']}))


if __name__ == '__main__':
    main()
