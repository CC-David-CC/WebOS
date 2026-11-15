"""A second preview must not replace an active preview's staged assets."""
from pathlib import Path
import socket
import subprocess
import sys

root = Path(__file__).resolve().parents[1]
with socket.socket() as listener:
    listener.bind(('127.0.0.1', 0))
    listener.listen()
    port = listener.getsockname()[1]
    runtime = root / 'active-system' / '.build' / f'simplified-local-test-{port}'
    if runtime.exists():
        raise RuntimeError('Test chose an existing preview directory')
    public = runtime / 'public'
    public.mkdir(parents=True)
    marker = public / 'test-marker'
    marker.write_text('unchanged')
    try:
        result = subprocess.run([sys.executable, str(root / 'active-system/scripts/run-simplified-local.py'), '--port', str(port), '--isolated'], capture_output=True, text=True, timeout=15, cwd=root)
        assert result.returncode != 0, result.stdout
        assert 'Address already in use' in result.stderr, result.stderr
        assert marker.read_text() == 'unchanged'
        print('PASS occupied preview port is rejected before staging mutates assets')
    finally:
        marker.unlink(missing_ok=True)
        public.rmdir()
        runtime.rmdir()
