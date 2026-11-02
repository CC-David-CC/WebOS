import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / 'active-system/scripts/stage-simplified-app-batch.py'


def record(data):
    return {'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest()}


class ReleaseStagingTest(unittest.TestCase):
    def test_reused_files_never_mutate_baseline(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            base = root / ('a' * 64)
            batch = root / 'batch'
            def write(folder, path, data):
                target = folder / path
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(data)
                target.chmod(0o644)
            old_app = {'id': 'example', 'bundleSHA256': 'b' * 64}
            catalog = json.dumps({'apps': [old_app]}).encode()
            old_files = {
                'index.html': b'<html>baseline</html>',
                'app.js': b'old shell',
                'assets/desktop/apps.json': catalog,
                'assets/desktop/apps/example/' + 'b' * 64 + '/index.mjs': b'old',
            }
            for name, data in old_files.items():
                write(base, name, data)
            old = {'id': base.name, 'files': {n: record(v) for n, v in old_files.items()}}
            write(base, 'assets/desktop/cache-manifest.json', json.dumps(old).encode())
            write(base, 'assets/desktop/offline-worker.js', ('// worker\nconst RELEASE=' + json.dumps(old) + ';\n').encode())
            new_app = {'id': 'example', 'bundleSHA256': 'c' * 64, 'files': {'index.mjs': record(b'new')}}
            write(batch, 'apps.json', json.dumps({'apps': [new_app]}).encode())
            write(batch, 'apps/example/' + 'c' * 64 + '/index.mjs', b'new')
            before = {p.relative_to(base): p.read_bytes() for p in base.rglob('*') if p.is_file()}
            replacement = root / 'app.js'
            replacement.write_bytes(b'new shell')
            output = root / 'stage'
            command_registry = root / 'command-registry.mjs'
            command_registry.write_bytes(b'export const ready = true;')
            subprocess.run(['python3', str(SCRIPT), '--baseline', str(base), '--batch', str(batch),
                            '--output', str(output), '--apps', 'example', '--reuse-baseline-files',
                            '--desktop-app', str(replacement), '--desktop-base-sha256', record(b'old shell')['sha256'],
                            '--new-command-registry', str(command_registry)],
                           check=True, capture_output=True)
            self.assertEqual(before, {p.relative_to(base): p.read_bytes() for p in base.rglob('*') if p.is_file()})
            self.assertEqual(os.stat(base / 'index.html').st_ino, os.stat(output / 'index.html').st_ino)
            self.assertEqual((output / 'app.js').read_bytes(), b'new shell')
            self.assertEqual((output / 'assets/desktop/command-registry.mjs').read_bytes(), command_registry.read_bytes())
            self.assertFalse((base / 'assets/desktop/command-registry.mjs').exists())
            self.assertNotEqual(os.stat(base / 'app.js').st_ino, os.stat(output / 'app.js').st_ino)
            self.assertNotEqual(os.stat(base / 'assets/desktop/apps.json').st_ino,
                                os.stat(output / 'assets/desktop/apps.json').st_ino)
            self.assertNotEqual(os.stat(base / 'assets/desktop/offline-worker.js').st_ino,
                                os.stat(output / 'assets/desktop/offline-worker.js').st_ino)
            self.assertEqual((output / 'assets/desktop/apps/example' / ('c' * 64) / 'index.mjs').read_bytes(), b'new')
            manifest = json.loads((output / 'assets/desktop/cache-manifest.json').read_text())
            for name, info in manifest['files'].items():
                self.assertEqual(record((output / name).read_bytes()), info)
            existing_registry = base / 'assets/desktop/command-registry.mjs'
            existing_registry.write_text('existing registry')
            refused = subprocess.run(['python3', str(SCRIPT), '--baseline', str(base), '--batch', str(batch),
                                      '--output', str(root / 'duplicate'), '--apps', 'example',
                                      '--new-command-registry', str(command_registry)], capture_output=True)
            self.assertNotEqual(refused.returncode, 0)
            self.assertFalse((root / 'duplicate').exists())
            existing_registry.unlink()
            (base / 'index.html').chmod(0o600)
            failure = subprocess.run(['python3', str(SCRIPT), '--baseline', str(base), '--batch', str(batch),
                                      '--output', str(root / 'unsafe'), '--apps', 'example', '--reuse-baseline-files'],
                                     capture_output=True)
            self.assertNotEqual(failure.returncode, 0)
            self.assertFalse((root / 'unsafe').exists())


if __name__ == '__main__':
    unittest.main()
