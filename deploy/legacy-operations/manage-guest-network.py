#!/usr/bin/env python3
"""Manage fixed private guest workers and their owned kernel policy as root."""
import argparse
import json
import os
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parent.parent;sys.path.insert(0,str(ROOT))
from guest_service.operator import Manager,verify_operator,root_file,table

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('action',choices=['configure','start','stop','recover','status','monitor']);parser.add_argument('--config-dir',type=Path,required=True)
    parser.add_argument('--instance');parser.add_argument('--worker',type=Path);parser.add_argument('--worker-sha256');parser.add_argument('--python',type=Path);parser.add_argument('--state-root',type=Path)
    parser.add_argument('--frontend-user',default='codi-guest');parser.add_argument('--anonymous-user',default='codi-net-anonymous');parser.add_argument('--registered-user',default='codi-net-registered')
    parser.add_argument('--issuer-policy',type=Path);parser.add_argument('--egress-policy',type=Path);parser.add_argument('--base-path',default='');parser.add_argument('--fixture-namespace');parser.add_argument('--unit-dir',default='/etc/systemd/system')
    args=parser.parse_args()
    try:
        if os.geteuid()!=0:raise ValueError('Root guest network operator required')
        verify_operator(ROOT);manager=Manager(args.config_dir,ROOT)
        if args.action=='monitor':manager.monitor();return
        with manager.locked():
            if args.action=='configure':
                if any(v is None for v in [args.instance,args.worker,args.worker_sha256,args.python,args.state_root,args.issuer_policy,args.egress_policy]):raise ValueError('Explicit prepared runtime/accounts, public policies and state root required')
                value=manager.configure(instance=args.instance,worker=args.worker,worker_sha256=args.worker_sha256,python=args.python,state_root=args.state_root,frontend_user=args.frontend_user,anonymous_user=args.anonymous_user,registered_user=args.registered_user,issuer_policy=args.issuer_policy,policy=json.loads(root_file(args.egress_policy)),namespace=args.fixture_namespace,unit_dir=args.unit_dir,base_path=args.base_path)
            elif args.action=='status':
                if manager.pending.exists():
                    pending=json.loads(root_file(manager.pending,mode=0o600));value={'status':'pending','operation':pending.get('kind'),'phase':pending.get('phase')}
                else:
                    config=manager.load();value={'status':'inspected','active':manager.active.exists(),'guardFault':manager.fault.exists(),'kernelMatches':table(config)==config['kernelSHA256'],'units':manager.states(config),'bootEnabled':False}
            else:value=getattr(manager,args.action)()
        print(json.dumps(value,indent=2))
    except (ValueError,OSError,KeyError) as error:parser.error(str(error))

if __name__=='__main__':main()
