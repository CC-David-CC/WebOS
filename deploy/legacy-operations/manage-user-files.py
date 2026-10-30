#!/usr/bin/env python3
"""Manage isolated private file services from a protected, sealed root operator."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parent.parent;sys.path.insert(0,str(ROOT))
from file_service.operator import Manager,protected,read

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('action',choices=['configure','initialize','recover','start','stop','status']);parser.add_argument('--config-dir',type=Path,required=True)
    parser.add_argument('--instance');parser.add_argument('--user',default='codi-gateway');parser.add_argument('--release',type=Path);parser.add_argument('--manifest-sha256');parser.add_argument('--python',type=Path);parser.add_argument('--state-root',type=Path);parser.add_argument('--data-root',type=Path);parser.add_argument('--issuer-policy',type=Path);parser.add_argument('--base-path',default='');parser.add_argument('--port',type=int,default=8140);parser.add_argument('--unit-dir',default='/etc/systemd/system')
    args=parser.parse_args()
    try:
        if os.geteuid()!=0:raise ValueError('Root native operator required')
        protected(ROOT,directory=True)
        metadata=json.loads(read(ROOT/'file-operator.json',0o644))
        expected={'file_service/__init__.py','file_service/operator.py','scripts/manage-user-files.py'}
        if metadata.get('version')!='codi-file-operator/1' or set(metadata.get('files',{}))!=expected:raise ValueError('Sealed file operator required')
        for name,record in metadata['files'].items():
            raw=read(ROOT/name,0o644,262144)
            if record!={'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()}:raise ValueError('File operator code pin changed')
        manager=Manager(args.config_dir)
        with manager.locked(args.instance if args.action=='configure' else None):
            if args.action=='configure':
                if any(value is None for value in [args.instance,args.release,args.manifest_sha256,args.python,args.state_root,args.data_root,args.issuer_policy]):raise ValueError('Explicit instance, worker/pin, environment, roots and policy required')
                result=manager.configure(instance=args.instance,user=args.user,release=args.release,manifest_sha256=args.manifest_sha256,python=args.python,state_root=args.state_root,data_root=args.data_root,issuer_policy=args.issuer_policy,base_path=args.base_path,port=args.port,unit_dir=args.unit_dir)
            elif args.action=='status':
                config=manager.load();result={'status':'inspected','units':manager.states(config)}
            else:result=getattr(manager,args.action)()
        print(json.dumps(result,indent=2))
    except (ValueError,OSError,KeyError) as error:parser.error(str(error))

if __name__=='__main__':main()
