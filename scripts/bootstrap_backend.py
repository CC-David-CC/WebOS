#!/usr/bin/env python3
"""Install the pinned development backend into a new private environment; start no service."""
import argparse
import os
from pathlib import Path
import shutil
import subprocess


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--venv', required=True, type=Path, help='New environment outside the source checkout')
    args = parser.parse_args()
    root = Path(__file__).resolve().parent.parent
    target = args.venv.expanduser().absolute()
    if target.exists() or target.is_symlink():
        parser.error('Environment destination already exists; inspect it before choosing a new destination')
    if target.is_relative_to(root) or root.is_relative_to(target):
        parser.error('Environment must be outside the source checkout')
    if '..' in target.parts or any(p.is_symlink() for p in target.parents):
        parser.error('Use a direct environment path without symlink ancestors')
    if not shutil.which('uv'):
        parser.error('uv is required; no global dependency installation is performed')
    for component, module in [('accounts', 'webos_accounts'), ('storage', 'webos_storage')]:
        if not (root / component / 'src' / module / '__init__.py').is_file():
            parser.error('Required packaged backend source is unavailable: ' + component)
    os.umask(0o077)
    subprocess.run(['uv', 'venv', str(target)], check=True)
    # Every third-party dependency is listed in this lock. Component sources
    # are the two trusted local checkouts, never a similarly named registry package.
    subprocess.run(['uv', 'pip', 'install', '--python', str(target / 'bin/python'),
                    '--no-deps', '-r', str(root / 'deploy/backend-requirements.lock'),
                    '-e', str(root / 'accounts'), '-e', str(root / 'storage')], check=True)
    print('Development backend environment ready: ' + str(target / 'bin/python'))
    print('No server was started; no account state or production deployment was changed.')


if __name__ == '__main__':
    main()
