#!/usr/bin/env python3
"""Check the short SYSTEM command validates and passes text through stdin."""
import importlib.util,json,subprocess
from pathlib import Path
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1];spec=importlib.util.spec_from_file_location('system_admin',ROOT/'scripts/codi-system-admin.py');admin=importlib.util.module_from_spec(spec);spec.loader.exec_module(admin)
def run(command,**kw):
 assert command[:4]==['/usr/sbin/runuser','-u','codi-official','--'] and command[-1]=='system-post'
 assert kw['input']=='Maintenance: café ♟'.encode() and kw['check'] is True
 return subprocess.CompletedProcess(command,0,json.dumps({'status':'posted','height':3}).encode(),b'')
with patch.object(admin.subprocess,'run',side_effect=run):assert admin.publish('Maintenance: café ♟'.encode())['height']==3
for raw in (b'',b' '*10,b'\xff',b'a'*4097,b'a\x00b'):
 try:admin.publish(raw)
 except ValueError:continue
 raise AssertionError('Invalid announcement accepted')
print('PASS bounded UTF-8 stdin and fixed unprivileged publisher command')
