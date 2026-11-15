#!/usr/bin/env python3
"""Run a selected Craft workspace's Cargo command with the assembly font checkout."""
import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess


def main():
    root = Path(__file__).resolve().parent.parent
    records = json.loads((root / 'migration/scope.json').read_text())['selected_upstream_forks']
    apps = {record['id']: record['component_path'] for record in records}
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--cargo', default='cargo', help='Cargo executable; defaults to PATH')
    parser.add_argument('app', choices=sorted(apps))
    parser.add_argument('arguments', nargs=argparse.REMAINDER, help='Cargo arguments after --')
    args = parser.parse_args()
    command = args.arguments
    if command[:1] == ['--']:
        command = command[1:]
    if not command:
        parser.error('Supply a Cargo command after --')
    workspace = (root / apps[args.app]).resolve()
    fonts = (root / 'assets/craft-fonts').resolve()
    if not workspace.is_relative_to(root / 'apps') or not (workspace / 'Cargo.toml').is_file():
        parser.error('Selected workspace is unavailable inside this assembly')
    if not fonts.is_relative_to(root / 'assets') or not (fonts / 'fonts/manifest.txt').is_file():
        parser.error('Initialize the assembly craft-fonts submodule first')
    cargo = shutil.which(args.cargo)
    if cargo is None:
        parser.error('Cargo executable unavailable; select a toolchain with --cargo or PATH')
    # Preserve rustup proxy names rather than resolving their symlink to rustup.
    cargo = os.path.abspath(cargo)
    env = dict(os.environ, CRAFT_FONTS_DIR=str(fonts))
    env['PATH'] = str(Path(cargo).parent) + os.pathsep + env.get('PATH', '')
    return subprocess.run([cargo, *command], cwd=workspace, env=env).returncode


if __name__ == '__main__':
    raise SystemExit(main())
