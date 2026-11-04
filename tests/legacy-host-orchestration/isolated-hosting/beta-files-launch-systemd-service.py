#!/usr/bin/env python3
"""Systemd fixture trampoline; execs only caller-provided sealed test releases."""
import hashlib,os,subprocess,sys
from pathlib import Path
role,python,old,new,gateway,root,prefix,fixture_data=sys.argv[1:]
origin='http://127.0.0.1:19771';base=['--origin',origin]
if role=='issuer':
 runtime=(Path('/run')/(prefix+'-issuer')).resolve(strict=True)
 release=new if (Path(root)/'issuer-next').exists() else old
 args=[python,'-B',release+'/scripts/serve-connected.py','--port','19772','--runtime-dir',str(runtime),*base,'--user-files']
 if release==new:args.append('--beta-opfs-file-content')
elif role=='frontend':args=[python,'-B',old+'/guest-relay/server.py','--port','19773',*base,'--identity-config-port','19772','--no-guest-network']
elif role=='gateway':
 runtime=Path(fixture_data);state=runtime/'state';data=runtime/'data';temporary=runtime/'tmp'
 for path in (state,data,temporary):path.mkdir(mode=0o700,exist_ok=True)
 policy=Path(root)/'fixture-systemd-policy.json';digest=hashlib.sha256(policy.read_bytes()).hexdigest();script=gateway+'/scripts/serve-user-files.py';flags=['--state-root',str(state),'--data-root',str(data),'--issuer-policy',str(policy),'--issuer-policy-sha256',digest,'--port','19776']
 if not (state/'permissions.sqlite3').exists():subprocess.run([python,'-B',script,'initialize',*flags],check=True)
 args=[python,'-B',script,'serve',*flags]
else:raise ValueError('unknown fixture role')
os.execv(python,args)
