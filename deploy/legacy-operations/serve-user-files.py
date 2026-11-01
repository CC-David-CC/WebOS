#!/usr/bin/env python3
"""Initialize private file-service ledgers or serve on loopback; never a public root."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import stat
import sys
from aiohttp import web

ROOT=Path(__file__).resolve().parent.parent;sys.path.insert(0,str(ROOT))
from gateway_service.auth import initialize_ledger
from gateway_service.transfers import initialize_transfers,Pacer
from gateway_service.user_store import UserStore, DEFAULT_ACCOUNT_FOLDERS
from gateway_service.http import FileGateway

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action',choices=['initialize','serve']);parser.add_argument('--state-root',type=Path,required=True);parser.add_argument('--data-root',type=Path,required=True)
    parser.add_argument('--issuer-policy',type=Path,required=True);parser.add_argument('--issuer-policy-sha256',required=True)
    parser.add_argument('--base-path',default='');parser.add_argument('--port',type=int,default=8140)
    parser.add_argument('--seconds-per-use',type=int,default=900);parser.add_argument('--bytes-per-second',type=int,default=4*1024*1024)
    args=parser.parse_args()
    if not 1<=args.port<=65535:parser.error('Valid loopback port required')
    try:
        path=args.issuer_policy.absolute()
        for p in [path,*path.parents]:
            info=p.lstat()
            if stat.S_ISLNK(info.st_mode) or info.st_uid not in (0,os.geteuid()) or info.st_mode&0o022 and not (stat.S_ISDIR(info.st_mode) and info.st_mode&stat.S_ISVTX):
                raise ValueError('Protected operator policy required')
        info=path.stat()
        if not stat.S_ISREG(info.st_mode) or info.st_nlink!=1 or info.st_size>32768:raise ValueError('Bounded regular policy required')
        raw=path.read_bytes()
        if hashlib.sha256(raw).hexdigest()!=args.issuer_policy_sha256:raise ValueError('Issuer policy pin changed')
        value=json.loads(raw);policy=value.get('identity',value)
        store=UserStore(args.state_root,args.data_root,initial_folders=DEFAULT_ACCOUNT_FOLDERS)
        if args.action=='initialize':
            initialize_ledger(store);initialize_transfers(store)
            print(json.dumps({'status':'initialized','publicServiceStarted':False,'anonymousFolders':0}));raise SystemExit(0)
        gateway=FileGateway(store,policy,base_path=args.base_path,seconds_per_use=args.seconds_per_use,pacer=Pacer(per_second=args.bytes_per_second))
        web.run_app(gateway.app(),host='127.0.0.1',port=args.port,access_log=None,print=None,backlog=16,shutdown_timeout=10)
    except (ValueError,OSError) as error:parser.error(str(error))
