#!/usr/bin/env python3
"""Verify the relay operator's exact source allowlist and mutation refusals."""
import hashlib
import importlib.util
import json
import shutil
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location('relay_export', ROOT / 'scripts/export-relay-operator.py')
exporter = importlib.util.module_from_spec(spec)
spec.loader.exec_module(exporter)
checks = []
parent = Path(tempfile.mkdtemp(prefix='relay-export-check-', dir=ROOT / '.build/checks'))
try:
    folder = parent / 'operator'
    report = exporter.export(folder)
    assert exporter.verify(folder) == report
    checks.append('exact five-file certificate-capable source export verifies')
    def refuses(fn):
        try:
            fn()
        except (ValueError, OSError):
            return
        raise AssertionError('Mutation accepted')
    refuses(lambda: exporter.export(folder))
    checks.append('existing output refused')
    manager = folder / 'relay_service/manager.py'
    original = manager.read_bytes()
    manager.write_bytes(original + b'\n')
    refuses(lambda: exporter.verify(folder))
    manager.write_bytes(original)
    checks.append('changed source refused')
    extra = folder / 'turn.secret'
    extra.write_text('fixture-nonsecret-placeholder')
    refuses(lambda: exporter.verify(folder))
    extra.unlink()
    checks.append('unlisted credential-shaped file refused')
    manager.unlink()
    manager.symlink_to(ROOT / 'relay_service/manager.py')
    refuses(lambda: exporter.verify(folder))
    manager.unlink()
    manager.write_bytes(original)
    checks.append('linked code refused')
    manifest = folder / 'relay-operator.json'
    raw = manifest.read_bytes()
    value = json.loads(raw)
    value['files']['not-allowed'] = {'bytes': 0, 'sha256': '0' * 64}
    manifest.write_text(json.dumps(value))
    refuses(lambda: exporter.verify(folder))
    manifest.write_bytes(raw)
    checks.append('expanded manifest allowlist refused')
    saved = manager.read_bytes()
    manager.unlink()
    refuses(lambda: exporter.verify(folder))
    manager.write_bytes(saved)
    checks.append('missing input refused')
    assert exporter.verify(folder) == report
    result = {'status': 'PASS', 'checks': checks, 'sha256': {name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest() for name in ['scripts/export-relay-operator.py', 'scripts/relay-operator-check.py']}}
finally:
    shutil.rmtree(parent)
result['fixtureRemoved'] = not parent.exists()
(ROOT / '.build/checks/relay-operator-result.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps(result, indent=2))
