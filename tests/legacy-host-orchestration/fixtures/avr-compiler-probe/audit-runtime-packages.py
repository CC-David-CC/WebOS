#!/usr/bin/env python3
"""Compare the pinned research release's AVR runtime with pinned Ubuntu packages.

Reads archives without extracting files or executing their contents. This is a
narrow byte comparison, not proof of the provenance of the compiler toolchain.
"""
import hashlib
import subprocess
import sys
import tarfile
from pathlib import Path

EXPECTED_RELEASE = '639a745994b00eb8d806f80c2302056f76403c9dc737df0676da81418c7ddd17'
EXPECTED_LIBC = '984d0c38ccdd08fd10761da5e7eb75f9f9572d9a804bc1c4a649051c3aaed09b'
EXPECTED_BINUTILS = 'ebae1564675109969b3dcc6a6d4cb73ee445997e1dc2be05717cdc1d01453e0c'


def digest_file(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def digest_member(archive, member):
    if member.size > 128 * 1024 * 1024:
        raise ValueError('oversized archive member: ' + member.name)
    with archive.extractfile(member) as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def package_hashes(path, wanted):
    found = {}
    proc = subprocess.Popen(['dpkg-deb', '--fsys-tarfile', str(path)], stdout=subprocess.PIPE)
    try:
        with tarfile.open(fileobj=proc.stdout, mode='r|') as archive:
            for member in archive:
                name = member.name.removeprefix('./')
                if name not in wanted:
                    continue
                if name in found or not member.isfile():
                    raise ValueError('duplicate or non-regular package entry: ' + name)
                found[name] = digest_member(archive, member)
    finally:
        proc.stdout.close()
        code = proc.wait()
    if code:
        raise ValueError('could not read package: ' + str(path))
    return found


def main():
    if len(sys.argv) != 4:
        raise SystemExit('usage: audit-runtime-packages.py avrwasm.tar avr-libc.deb binutils-avr.deb')
    release, libc, binutils = map(Path, sys.argv[1:])
    for path, expected in [(release, EXPECTED_RELEASE), (libc, EXPECTED_LIBC), (binutils, EXPECTED_BINUTILS)]:
        if path.is_symlink() or digest_file(path) != expected:
            raise ValueError('unexpected input hash: ' + str(path))
    groups = {'libc': {}, 'binutils': {}}
    with tarfile.open(release, 'r:') as archive:
        for member in archive:
            name = member.name.removeprefix('./')
            prefix = 'sysroot/avr/'
            if not name.startswith(prefix) or name.endswith('.br') or member.isdir():
                continue
            if not member.isfile() or '..' in Path(name).parts:
                raise ValueError('unexpected release entry: ' + name)
            relative = name[len(prefix):]
            group = 'binutils' if relative.startswith('lib/ldscripts/') else 'libc'
            target = 'usr/lib/avr/' + relative
            if target in groups[group]:
                raise ValueError('duplicate release entry: ' + name)
            groups[group][target] = digest_member(archive, member)
    if len(groups['libc']) != 326 or len(groups['binutils']) != 10:
        raise ValueError('unexpected number of runtime files')
    for group, package in [('libc', libc), ('binutils', binutils)]:
        expected = groups[group]
        found = package_hashes(package, set(expected))
        missing = sorted(set(expected) - set(found))
        different = sorted(name for name in found if found[name] != expected[name])
        if missing or different:
            raise ValueError(f'{group}: missing={missing} different={different}')
        print(f'{group}: {len(found)} release files match the pinned package')
    print('This does not establish the source or license status of the WASM tools.')


if __name__ == '__main__':
    main()
