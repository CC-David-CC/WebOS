#!/usr/bin/env python3
"""Refresh discovery-only delegation using a systemd-delivered room credential."""
import argparse
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from reader_service.delegation import refresh

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--policy-directory',type=Path,required=True);p.add_argument('--policy-sha256',required=True)
    a=p.parse_args();print(json.dumps(refresh(a.policy_directory,a.policy_sha256),sort_keys=True))
