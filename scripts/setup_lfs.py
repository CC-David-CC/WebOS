#!/usr/bin/env python3
"""Configure Git LFS filters locally for the assembled egui checkout; install no hooks."""
import argparse
from pathlib import Path
import shlex
import shutil
import subprocess


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--executable', default=shutil.which('git-lfs'),
                        help='Installed git-lfs executable; defaults to PATH lookup')
    args = parser.parse_args()
    if not args.executable:
        parser.error('Install Git LFS or provide --executable; no global installation is performed')
    executable = Path(args.executable).expanduser().resolve(strict=True)
    subprocess.run([str(executable), 'version'], check=True)
    root = Path(__file__).resolve().parent.parent
    child = root / 'libraries/egui'
    metadata = Path(subprocess.check_output(
        ['git', '-C', str(child), 'rev-parse', '--absolute-git-dir'], text=True).strip())
    if not metadata.resolve().is_relative_to(root / '.git/modules'):
        parser.error('egui must be an initialized submodule owned by this assembly')
    command = shlex.quote(str(executable))
    settings = {'filter.lfs.clean': command + ' clean -- %f',
                'filter.lfs.smudge': command + ' smudge -- %f',
                'filter.lfs.process': command + ' filter-process',
                'filter.lfs.required': 'true'}
    for key, value in settings.items():
        subprocess.run(['git', '-C', str(child), 'config', '--local', key, value], check=True)
    print('Configured egui LFS filters in this checkout only; no hooks or global config changed.')


if __name__ == '__main__':
    main()
