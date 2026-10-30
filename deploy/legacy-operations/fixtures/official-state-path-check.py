#!/usr/bin/env python3
"""Exercise operator state-path preflight in an owned disposable directory."""
import os,subprocess,sys,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];script=ROOT/'scripts/official-admin.py';checks=[]
with tempfile.TemporaryDirectory(prefix='official-state-path-') as temp:
 root=Path(temp);state=root/'state'
 def call(path,*args):return subprocess.run([sys.executable,str(script),'--state',str(path),*args],capture_output=True,text=True)
 assert call(state,'init').returncode==0;assert call(state,'list').returncode==0;checks.append('private initialized state works')
 link=root/'linked';link.symlink_to(state,target_is_directory=True);assert call(link,'list').returncode!=0;checks.append('symlinked state refused')
 state.chmod(0o755);assert call(state,'list').returncode!=0;state.chmod(0o700);checks.append('shared state directory refused')
 db=state/'official.sqlite';db.chmod(0o644);assert call(state,'list').returncode!=0;db.chmod(0o600);checks.append('shared database refused')
 linked=root/'db-link';os.link(db,linked);assert call(state,'list').returncode!=0;linked.unlink();checks.append('hard-linked database refused')
 saved=root/'saved';db.rename(saved);db.symlink_to(saved);assert call(state,'list').returncode!=0;db.unlink();saved.rename(db);checks.append('symlinked database refused')
 sidecar=state/'official.sqlite-wal';sidecar.symlink_to(db);assert call(state,'list').returncode!=0;sidecar.unlink();checks.append('symlinked SQLite sidecar refused')
 parentlink=root/'parent-link';parentlink.symlink_to(root,target_is_directory=True);assert call(parentlink/'new','init').returncode!=0;checks.append('symlinked initialization parent refused')
 unsafe=root/'shared';unsafe.mkdir(mode=0o777);unsafe.chmod(0o777);assert call(unsafe/'new','init').returncode!=0;checks.append('shared initialization parent refused')
 assert call(state,'list').returncode==0;checks.append('restored private state still works')
print('PASS:',', '.join(checks))
