#!/usr/bin/env python3
"""Check runtime refuses unsafe state before binding a listener."""
import socket,subprocess,sys,tempfile
from pathlib import Path
root=Path(__file__).resolve().parents[2];admin=root/'scripts/official-admin.py';runtime=root/'scripts/run-official-runtime.py'
with tempfile.TemporaryDirectory(prefix='official-runtime-path-') as tmp:
 state=Path(tmp)/'state';assert subprocess.run([sys.executable,str(admin),'--state',str(state),'init'],capture_output=True).returncode==0
 policy=Path(tmp)/'policy';policy.write_text('{}')
 with socket.socket() as sock:sock.bind(('127.0.0.1',0));port=sock.getsockname()[1]
 def run(db,ledger):return subprocess.run([sys.executable,str(runtime),'--database',str(db),'--ledger',str(ledger),'--issuer-policy',str(policy),'--port',str(port)],capture_output=True,text=True,timeout=10)
 db=state/'official.sqlite';ledger=state/'access.sqlite';db.chmod(0o644);bad=run(db,ledger);assert bad.returncode and 'private owned regular' in bad.stderr;db.chmod(0o600)
 link=Path(tmp)/'linked';link.symlink_to(state,target_is_directory=True);bad=run(link/'official.sqlite',link/'access.sqlite');assert bad.returncode and 'symlinks' in bad.stderr
 bad=run(db,Path(tmp)/'access.sqlite');assert bad.returncode and 'share the designated state' in bad.stderr
 with socket.socket() as sock:sock.bind(('127.0.0.1',port))
print('PASS: insecure permissions, symlinked state and split databases refused before listener startup')
