#!/usr/bin/env python3
"""Manage sealed discovery services; does not publish routes or change saved chat."""
import argparse
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from reader_service.operator import Manager

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('action',choices=['configure','recover-configure','start','stop','health','refresh'])
    p.add_argument('--directory',type=Path,required=True);p.add_argument('--request',type=Path)
    a=p.parse_args();manager=Manager(a.directory)
    with manager.locked():
        if a.action in ['configure','recover-configure']:
            if a.request is None:p.error('A protected exact configuration request is required')
            from reader_service.operator import safe
            value=manager.configure(**json.loads(safe.read(a.request)),recover=a.action=='recover-configure')
        else:value=getattr(manager,a.action)(manager.load())
    print(json.dumps(value,sort_keys=True))
