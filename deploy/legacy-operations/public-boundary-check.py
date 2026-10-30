#!/usr/bin/env python3
"""Check public allowlists on both live loopback servers without reading secrets."""
import json,urllib.request,urllib.error
from pathlib import Path
result={}
for port in [8097,8098]:
    checks={}
    for path in ['/issuer.pem','/.build/downloads/chess.js-1.4.0.tgz','/accounts.sqlite3','/scripts/serve-connected.py','/.build/connected-state/issuer.pem','/.build/auth-venv/pyvenv.cfg','/codiserver-server-v0.3.0/codiauth/service.py','/%2e%2e/desktop-preview/.build/connected-state/issuer.pem']:
        try:
            with urllib.request.urlopen(urllib.request.Request(f'http://127.0.0.1:{port}'+path,method='HEAD')) as response:status=response.status
        except urllib.error.HTTPError as error:status=error.code
        checks[path]=status
        assert status in (403,404),(port,path,status)
    for path in ['/','/app.js','/network/crypto.mjs','/network/pgn-worker.mjs','/assets/vendor/chess/chess.mjs','/.build/v86/vmlinuz']:
        with urllib.request.urlopen(urllib.request.Request(f'http://127.0.0.1:{port}'+path,method='HEAD')) as response:assert response.status==200
    result[str(port)]=checks
Path('.build/checks/public-boundary.json').write_text(json.dumps(result,indent=2)+'\n')
print('PASS both loopback servers reject private/source paths and serve public assets')
