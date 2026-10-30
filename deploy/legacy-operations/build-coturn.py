#!/usr/bin/env python3
"""Build pinned upstream Coturn in a new private build tree; never installs it."""
import argparse
import hashlib
import io
import json
import os
import shutil
import subprocess
import tarfile
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
COMMIT = '23c6c1d32a3d2b21a56cee65d3203bcc4ea82d2b'
ARCHIVE = 'd7e2ee337b5298c30cc5cd365c3173d05b97c749d28e9416afa4ca907925ce15'
URL = 'https://codeload.github.com/coturn/coturn/tar.gz/' + COMMIT


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def build(output):
    if output.exists() or output.is_symlink():
        raise ValueError('Choose a new build directory')
    output.mkdir(parents=True)
    with urllib.request.urlopen(URL, timeout=30) as response:
        raw = response.read(16 * 1024 * 1024 + 1)
    if len(raw) > 16 * 1024 * 1024 or hashlib.sha256(raw).hexdigest() != ARCHIVE:
        raise ValueError('Pinned upstream archive hash differs')
    (output / 'source.tar.gz').write_bytes(raw)
    with tarfile.open(fileobj=io.BytesIO(raw), mode='r:gz') as archive:
        archive.extractall(output / 'source', filter='data')
    source = output / 'source' / ('coturn-' + COMMIT)
    flags = {name: '1' for name in ['TURN_NO_SQLITE', 'TURN_NO_PQ', 'TURN_NO_MYSQL', 'TURN_NO_MONGO', 'TURN_NO_HIREDIS', 'TURN_NO_PROMETHEUS', 'TURN_NO_SYSTEMD', 'TURN_NO_SCTP']}
    flags.update(CFLAGS='-O2 -g0 -fPIE -fstack-protector-strong -D_FORTIFY_SOURCE=3 -ffile-prefix-map=' + str(source) + '=.', LDFLAGS='-Wl,-z,relro,-z,now -pie')
    env = {**os.environ, **flags}
    def command(name, argv):
        with (output / (name + '.log')).open('wb') as log:
            subprocess.run(argv, cwd=source, env=env, stdout=log, stderr=subprocess.STDOUT, check=True, timeout=180)
    command('configure', ['./configure', '--prefix=/opt/codi-turn', '--disable-rpath'])
    command('make', ['make', '-j4', 'bin/turnserver'])
    runtime = output / 'runtime'
    runtime.mkdir()
    for file, name in [(source / 'bin/turnserver', 'turnserver'), (source / 'LICENSE', 'LICENSE-coturn')]:
        shutil.copyfile(file, runtime / name)
        (runtime / name).chmod(0o755 if name == 'turnserver' else 0o644)
    version = subprocess.run([runtime / 'turnserver', '--version'], capture_output=True, text=True, timeout=5)
    if version.returncode or version.stdout.strip() != '4.18.0':
        raise ValueError('Built runtime version differs: ' + repr(version.stdout[:100]))
    libs = subprocess.run(['ldd', runtime / 'turnserver'], check=True, capture_output=True, text=True).stdout
    if 'not found' in libs:
        raise ValueError('Missing runtime dependency')
    report = {'version': 'codi-coturn-runtime/1', 'upstreamRelease': '4.18.0', 'upstreamCommit': COMMIT, 'archiveURL': URL, 'archiveSHA256': ARCHIVE, 'upstreamTagSignatureVerified': False, 'buildEnvironment': flags, 'compiler': subprocess.run(['cc', '--version'], capture_output=True, text=True, check=True).stdout.splitlines()[0], 'libraries': libs, 'files': {name: {'bytes': (runtime / name).stat().st_size, 'sha256': sha(runtime / name)} for name in ['turnserver', 'LICENSE-coturn']}, 'builderSHA256': sha(Path(__file__))}
    (runtime / 'runtime.json').write_text(json.dumps(report, sort_keys=True, indent=2) + '\n')
    print(json.dumps({'status': 'PASS', 'runtime': str(runtime), 'manifestSHA256': sha(runtime / 'runtime.json'), **report}, indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    try:
        build(args.output.absolute())
    except (ValueError, OSError, subprocess.SubprocessError) as error:
        parser.exit(1, str(error) + '\n')
