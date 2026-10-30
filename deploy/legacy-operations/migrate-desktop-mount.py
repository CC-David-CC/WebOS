#!/usr/bin/env python3
"""Offline managed mount transition; never configures public hosting or ports."""
import argparse,json,os,sys
from pathlib import Path

sys.dont_write_bytecode=True
sys.path.insert(0,str(Path(__file__).resolve().parent.parent))
from mount_operator.backends import seal

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action',choices=['plan','apply','recover'])
    parser.add_argument('--config',type=Path,required=True)
    parser.add_argument('--native-release',type=Path,required=True)
    parser.add_argument('--native-manifest-sha256',required=True)
    parser.add_argument('--base-path',default='')
    parser.add_argument('--seconds',type=int,default=86400)
    args=parser.parse_args()
    if os.geteuid()!=0:raise ValueError('Protected offline root operator required')
    seal(args.native_release,'connected-release.json',args.native_manifest_sha256,134217728)
    sys.path.insert(0,str(args.native_release))
    from mount_operator.coordinator import load_operator,run
    op=load_operator(args.native_release,args.native_manifest_sha256)
    print(json.dumps(run(op,args.config,args.action,args.base_path,args.seconds),indent=2))
