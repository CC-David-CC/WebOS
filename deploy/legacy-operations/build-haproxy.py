#!/usr/bin/env python3
"""Build pinned HAProxy TCP ingress runtime in a new tree; never installs it."""
import argparse
import hashlib
import io
import json
import os
from pathlib import Path
import shutil
import subprocess
import tarfile
import urllib.request

ROOT = Path(__file__).resolve().parent.parent
VERSION = '2.8.31'
URL = 'https://www.haproxy.org/download/2.8/src/haproxy-' + VERSION + '.tar.gz'
ARCHIVE = '8f2dd09cfdfe42bdc982c8615e7acb858e1815b10f296dfe5560e7f314dc6c80'


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build(output):
    if output.exists() or output.is_symlink():
        raise ValueError('Choose a new build directory')
    output.mkdir(parents=True)
    with urllib.request.urlopen(URL, timeout=30) as response:
        raw = response.read(16 * 1024 * 1024 + 1)
    if len(raw) > 16 * 1024 * 1024 or hashlib.sha256(raw).hexdigest() != ARCHIVE:
        raise ValueError('Pinned upstream archive differs')
    (output / 'source.tar.gz').write_bytes(raw)
    with tarfile.open(fileobj=io.BytesIO(raw), mode='r:gz') as archive:
        archive.extractall(output / 'source', filter='data')
    source = output / 'source' / ('haproxy-' + VERSION)
    flags = {'TARGET': 'linux-glibc', 'USE_OPENSSL': '', 'USE_LUA': '', 'USE_ZLIB': '',
             'USE_PCRE': '', 'USE_PCRE2': '', 'USE_PROMEX': '', 'USE_QUIC': '',
             'CFLAGS': '-O2 -g0 -fPIE -fstack-protector-strong -D_FORTIFY_SOURCE=3 -fwrapv -ffile-prefix-map=' + str(source) + '=.',
             'LDFLAGS': '-Wl,-z,relro,-z,now -pie'}
    with (output / 'make.log').open('wb') as log:
        subprocess.run(['make', '-j4', *[key + '=' + value for key, value in flags.items()]],
                       cwd=source, env=os.environ.copy(), stdout=log, stderr=subprocess.STDOUT,
                       check=True, timeout=300)
    runtime = output / 'runtime'
    runtime.mkdir()
    for file, name in [(source / 'haproxy', 'haproxy'), (source / 'LICENSE', 'LICENSE-haproxy')]:
        shutil.copyfile(file, runtime / name)
        (runtime / name).chmod(0o755 if name == 'haproxy' else 0o644)
    version = subprocess.run([runtime / 'haproxy', '-vv'], check=True, capture_output=True, text=True).stdout
    assert version.startswith('HAProxy version ' + VERSION + '-')
    libraries = subprocess.run(['ldd', runtime / 'haproxy'], check=True, capture_output=True, text=True).stdout
    assert 'not found' not in libraries
    report = {'version': 'codi-haproxy-runtime/1', 'upstreamRelease': VERSION,
              'archiveURL': URL, 'archiveSHA256': ARCHIVE, 'upstreamSignatureVerified': False,
              'buildFlags': flags, 'compiler': subprocess.run(['cc', '--version'], check=True, capture_output=True, text=True).stdout.splitlines()[0],
              'runtimeVersion': version, 'libraries': libraries,
              'files': {name: {'bytes': (runtime / name).stat().st_size, 'sha256': digest(runtime / name)} for name in ['haproxy', 'LICENSE-haproxy']},
              'builderSHA256': digest(Path(__file__))}
    (runtime / 'runtime.json').write_text(json.dumps(report, sort_keys=True, indent=2) + '\n')
    print(json.dumps({'status': 'PASS', 'runtime': str(runtime), 'manifestSHA256': digest(runtime / 'runtime.json'), **report}, indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    build(args.output.absolute())
