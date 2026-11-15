#!/usr/bin/env python3
"""Serve one fixed-role worker from protected inputs and an inherited Unix FD."""
import argparse
import hashlib
import os
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parent.parent;sys.path.insert(0,str(ROOT))
from guest_service.installation import settings,check_kernel,credential,root_file,verify_runtime
from guest_service.egress import EgressPolicy
from guest_service.usage import Permissions,UsageLedger
from guest_service.unix_transport import inherited_listener,peer_middleware
from guest_service.worker import WireWorker

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--settings',type=Path,required=True);parser.add_argument('--settings-sha256',required=True);parser.add_argument('--kernel-check',action='store_true');args=parser.parse_args()
    try:
        config=settings(args.settings,args.settings_sha256)
        verify_runtime(ROOT,config['runtimeSHA256'])
        if args.kernel_check:
            check_kernel(config);raise SystemExit(0)
        status=dict(line.split(':',1) for line in Path('/proc/self/status').read_text().splitlines())
        if set(map(int,status['Uid'].split()))!={config['uid']} or set(map(int,status['Gid'].split()))!={config['pingGID']} or int(status['CapEff'],16) or status['NoNewPrivs'].strip()!='1':raise ValueError('Unprivileged fixed worker service identity required')
        if hashlib.sha256(root_file('/usr/bin/qemu-system-i386',mode=0o755,maximum=67108864)).hexdigest()!=config['qemuSHA256']:raise ValueError('QEMU runtime pin changed')
        if os.environ.get('LISTEN_FDS')!='1' or os.environ.get('LISTEN_PID')!=str(os.getpid()) or os.environ.get('LISTEN_FDNAMES')!='wire':raise ValueError('One explicitly named inherited worker listener required')
        listener=inherited_listener(3,config['socketPath'],config['frontendUID'],config['pingGID']);os.close(3)
        usage=UsageLedger(Path(config['statePath'])/'usage.sqlite3',config['role'],Permissions(config['permissionsPath']))
        worker=WireWorker(config['role'],config['origin'],EgressPolicy.parse(config['policy']),config['issuerPolicy'],credential(),base_path=config['basePath'],usage=usage)
        from aiohttp import web
        app=worker.app();app.middlewares.append(peer_middleware(config['frontendUID'],config['pingGID']))
        web.run_app(app,sock=listener,access_log=None,print=None,backlog=16,shutdown_timeout=5)
    except (ValueError,OSError) as error:parser.error(str(error))
