#!/usr/bin/env python3
"""Verify and summarize the private Browser server metadata ledger.

Run as the ledger's service user with a protected signing credential. This
never creates an empty ledger, accepts no content queries, and does not send
reports elsewhere. An independently saved head detects tail rollback.
"""
import argparse
import importlib.util
import json
from pathlib import Path
import re
import sqlite3
import sys
from cryptography.exceptions import InvalidSignature

script=Path(__file__).resolve().with_name('serve-browser-relay.py')
spec=importlib.util.spec_from_file_location('codi_audit_relay',script)
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)

def report(database,key,*,subject=None,expected_head=None):
    if subject is not None and not re.fullmatch(r'user:[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}',subject):raise ValueError('Canonical registered account ID required')
    if expected_head is not None and not re.fullmatch(r'[0-9a-f]{64}',expected_head):raise ValueError('Expected head must be a SHA-256 digest')
    ledger=module.open_audit_ledger(database,key,require_existing=True)
    return {'verification':ledger.verify(expected_head),'subject':subject,'domains':ledger.domains(subject)}

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--database',type=Path,required=True);p.add_argument('--key',type=Path,required=True)
    p.add_argument('--subject',help='Optional registered user:UUID; omit for totals across users')
    p.add_argument('--expected-head',help='Previously saved independent ledger head')
    a=p.parse_args()
    try:print(json.dumps(report(a.database,a.key,subject=a.subject,expected_head=a.expected_head),indent=2))
    except (ValueError,OSError,sqlite3.Error,InvalidSignature) as error:print('Audit verification failed: '+str(error),file=sys.stderr);sys.exit(1)
