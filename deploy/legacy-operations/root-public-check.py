#!/usr/bin/env python3
"""Direct ordinary-TLS browser acceptance against the actual domain-root release."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import secrets
import time
from types import SimpleNamespace
import urllib.request

ROOT = Path(__file__).resolve().parent.parent
RELEASE = ROOT/'.build/releases/connected-root-cache-r2'


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    value = importlib.util.module_from_spec(spec);spec.loader.exec_module(value)
    return value


def run(kind):
    with urllib.request.urlopen('https://ksu.codes/index.html', timeout=20) as response:
        assert response.read() == (RELEASE/'index.html').read_bytes()
    with urllib.request.urlopen('https://ksu.codes/config.json', timeout=20) as response:
        identity = json.load(response)['identity']
        assert identity['mode'] == 'server' and identity['apiBase'] == '/api/v1'
    if kind == 'documents':
        source = ROOT/'scripts/document-workflow-browser-check.py'
        suite = module('public_root_documents', source)
        ledger = {'names': ['qa_doc_'+secrets.token_hex(6) for _ in range(2)], 'subjects': {}, 'ownedFilesRemoved': False}
        try:
            result = suite.browser('https://ksu.codes', [], ledger, base='')
        finally:
            (ROOT/'.build/checks/root-document-public-fixtures.json').write_text(json.dumps(ledger, indent=2)+'\n')
    else:
        source = ROOT/'scripts'/('xterm-browser-check.py' if kind == 'terminal' else 'public-app-lifecycle-stress-check.py')
        suite = module('public_root_'+kind, source)
        result = suite.browser(SimpleNamespace(origin='https://ksu.codes', base=''))
    return result|{'actualURL': 'https://ksu.codes/', 'basePath': '', 'defaultPublicTLS': True,
                   'releaseSHA256': hashlib.sha256((RELEASE/'connected-release.json').read_bytes()).hexdigest(),
                   'suiteSourceSHA256': hashlib.sha256(source.read_bytes()).hexdigest()}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('suite', choices=['terminal', 'documents', 'lifecycle'])
    args = parser.parse_args();result = {'status': 'FAIL', 'suite': args.suite}
    try:result.update(run(args.suite))
    finally:
        result['sourceSHA256'] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
        path = ROOT/'.build/checks'/('root-public-'+args.suite+'-result.json')
        if path.exists():path.rename(path.with_name(path.stem+'-before-'+str(time.time_ns())+'.json'))
        path.write_text(json.dumps(result, indent=2)+'\n');print(json.dumps(result, indent=2))
