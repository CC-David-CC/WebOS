#!/usr/bin/env python3
"""Derive the scoped Simplified KSU generator from a reviewed baseline."""
from pathlib import Path
import sys
p=Path(sys.argv[1]);s=p.read_text()
needle="        if 'codi_turn_certificate' in s and "
insert="""        if 'codi_simplified' in s and (not isinstance(s['codi_simplified'],str) or not re.fullmatch('[0-9a-f]{64}',s['codi_simplified']) or s['domain']!='ksu.codes' or not s['enabled'] or s.get('codi_mount')!=''):
            raise ValueError('Simplified release requires root KSU desktop')
        if 'codi_simplified_mode' in s and (s['codi_simplified_mode'] not in ('preview','active') or not s.get('codi_simplified')):
            raise ValueError('Simplified mode requires a release')
"""
assert s.count(needle)==1;s=s.replace(needle,insert+needle)
needle="        if 'codi_speech' in s: lines.append('codi_speech = '+json.dumps(s['codi_speech']))"
assert s.count(needle)==1;s=s.replace(needle,needle+"\n        if 'codi_simplified' in s: lines.append('codi_simplified = '+json.dumps(s['codi_simplified']))\n        if 'codi_simplified_mode' in s: lines.append('codi_simplified_mode = '+json.dumps(s['codi_simplified_mode']))")
needle='def connected_root(s):'
insert='''SIMPLIFIED_CSP = "default-src 'self'; script-src 'self' 'wasm-unsafe-eval'; style-src 'self' 'unsafe-inline'; img-src 'self' data: blob:; media-src 'self' blob:; connect-src 'self' wss://ksu.codes; font-src 'self' data:; frame-src 'self' blob:; worker-src 'self' blob:; object-src 'none'; base-uri 'none'; form-action 'self'; frame-ancestors 'self'"

def simplified_routes(s):
    if not s.get('codi_simplified'):
        return []
    cookie = ['\\t\\theader Cookie *codi_simplified_preview=1*'] if s.get('codi_simplified_mode')=='preview' else []
    normal = SIMPLIFIED_CSP
    notebook = normal.replace("script-src 'self' 'wasm-unsafe-eval'", "script-src 'self' 'unsafe-eval' 'wasm-unsafe-eval'")
    return [
        '\\t@codi_simplified_normal {', *cookie, '\\t\\tnot path '+WEBSITE_PATHS+' /hidden /hidden/* /assets/desktop/apps/notebook/*', '\\t}',
        '\\t@codi_simplified_notebook {', *cookie, '\\t\\tpath /assets/desktop/apps/notebook/*', '\\t}',
        '\\theader @codi_simplified_normal >Content-Security-Policy "'+normal+'"',
        '\\theader @codi_simplified_notebook >Content-Security-Policy "'+notebook+'"',
        '\\theader @codi_simplified_normal >Cross-Origin-Opener-Policy "same-origin"',
        '\\theader @codi_simplified_normal >Cross-Origin-Embedder-Policy "require-corp"',
        '\\theader @codi_simplified_notebook >Cross-Origin-Opener-Policy "same-origin"',
        '\\theader @codi_simplified_notebook >Cross-Origin-Embedder-Policy "require-corp"',
        '\\t@codi_simplified_worker {', *cookie, '\\t\\tpath /assets/desktop/offline-worker.js', '\\t}',
        '\\theader @codi_simplified_worker >Service-Worker-Allowed "/"',
        '\\t@codi_simplified_assets {', *cookie,
        '\\t\\tpath / /index.html /bootstrap.js /app.js /reference.js /desktop-apps.js /style.css /terminal.js /.build/v86/* /assets/* /network/* /storage/*',
        '\\t\\tnot path /assets/speech/*', '\\t}',
        '\\thandle @codi_simplified_assets {',
        '\\t\\troot * /srv/codi-connected/simplified/'+s['codi_simplified'],
        '\\t\\tfile_server', '\\t}',
        '\\thandle /codi-guest-cookie {', '\\t\\trewrite * /', '\\t\\treverse_proxy 127.0.0.1:8132', '\\t}',
    ]

'''
assert s.count(needle)==1;s=s.replace(needle,insert+needle)
needle="        '\\t@codi_root {', '\\t\\tnot path '+WEBSITE_PATHS+' /hidden /hidden/*', '\\t}',"
replace="        '\\t@codi_root {', '\\t\\tnot path '+WEBSITE_PATHS+' /hidden /hidden/*', *(['\\t\\tnot header Cookie *codi_simplified_preview=1*'] if s.get('codi_simplified_mode')=='preview' else []), *(['\\t\\tnot path / /index.html /bootstrap.js /app.js /reference.js /desktop-apps.js /style.css /terminal.js /.build/v86/* /assets/* /network/* /storage/* /config.json /api/* /gateway/* /codi-guest-cookie /guest-access/* /guest-network'] if s.get('codi_simplified_mode')=='active' else []), '\\t}',"
assert s.count(needle)==1;s=s.replace(needle,replace)
needle="        '\\thandle /rendezvous {'"
assert s.count(needle)==1;s=s.replace(needle,"        *simplified_routes(s),\n"+needle)
Path(sys.argv[2]).write_text(s)
