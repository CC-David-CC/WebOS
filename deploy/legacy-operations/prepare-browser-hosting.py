#!/usr/bin/env python3
"""Derive opt-in Browser/large-file hosting from an exact reviewed generator.

Writes only the candidate file named by the caller. Installation, ingress
verification, private socket provisioning and managed activation are separate.
"""
from pathlib import Path
import sys

def replace_once(source,old,new,label):
    if source.count(old)!=1:raise ValueError(label+': expected one exact anchor')
    return source.replace(old,new,1)

def derive(source):
    anchor="        if 'codi_simplified_mode' in s and "
    validation="""        for flag in ('codi_browser_relay','codi_large_files','codi_login_filter'):
            if flag in s and (type(s[flag]) is not bool or s['domain']!='ksu.codes' or not s['enabled'] or not s.get('codi_simplified') or s.get('codi_simplified_mode')!='active'):
                raise ValueError(flag+' requires the active KSU Simplified site')
"""
    source=replace_once(source,anchor,validation+anchor,'flag validation')
    anchor="        if 'codi_simplified_mode' in s: lines.append('codi_simplified_mode = '+json.dumps(s['codi_simplified_mode']))"
    source=replace_once(source,anchor,anchor+"\n        for flag in ('codi_browser_relay','codi_large_files','codi_login_filter'):\n            if flag in s: lines.append(flag+' = '+str(s[flag]).lower())",'flag serialization')
    anchor="'\\t\\tnot path '+WEBSITE_PATHS+' /hidden /hidden/* /assets/desktop/apps/notebook/*', '\\t}',"
    replacement="'\\t\\tnot path '+WEBSITE_PATHS+' /hidden /hidden/* /assets/desktop/apps/notebook/*'+(' /assets/desktop/apps/browser/*/src/engine-worker.js' if s.get('codi_browser_relay') else ''), '\\t}',"
    source=replace_once(source,anchor,replacement,'scoped worker exclusion')
    anchor="        '\\t@codi_simplified_notebook {', *cookie, '\\t\\tpath /assets/desktop/apps/notebook/*', '\\t}',"
    addition="""        *(['\\t@codi_browser_worker {', '\\t\\tpath /assets/desktop/apps/browser/*/src/engine-worker.js', '\\t}',
           '\\theader @codi_browser_worker >Content-Security-Policy "'+normal.replace("script-src 'self' 'wasm-unsafe-eval'", "script-src 'self' blob: 'wasm-unsafe-eval'")+'"',
           '\\theader @codi_browser_worker >Cache-Control "no-store"',
           '\\theader @codi_browser_worker >Cross-Origin-Opener-Policy "same-origin"',
           '\\theader @codi_browser_worker >Cross-Origin-Embedder-Policy "require-corp"'] if s.get('codi_browser_relay') else []),
"""
    source=replace_once(source,anchor,anchor+'\n'+addition.rstrip(),'scoped worker CSP')
    anchor="        *simplified_routes(s),\n        '\\thandle /rendezvous {'"
    route="""        *simplified_routes(s),
        *(['\\thandle /browser-relay/* {', '\\t\\treverse_proxy unix//run/codi-browser/relay.sock {',
           '\\t\\t\\theader_up X-Codi-Client-IP {http.request.remote.host}', '\\t\\t}', '\\t}'] if s.get('codi_browser_relay') else []),
        '\\thandle /rendezvous {'"""
    source=replace_once(source,anchor,route,'private relay route')
    anchor="        *(['\\thandle /gateway/* {', '\\t\\trequest_body {', '\\t\\t\\tmax_size 12MiB', '\\t\\t}', '\\t\\treverse_proxy 127.0.0.1:8140', '\\t}'] if s.get('codi_files') else []),"
    replacement="        *(['\\thandle /gateway/* {', '\\t\\trequest_body {', ('\\t\\t\\tmax_size 192MiB' if s.get('codi_large_files') else '\\t\\t\\tmax_size 12MiB'), '\\t\\t}', '\\t\\treverse_proxy 127.0.0.1:8140', '\\t}'] if s.get('codi_files') else []),"
    source=replace_once(source,anchor,replacement,'large-file body limit')
    anchor="        '\\thandle @codi_identity {', '\\t\\trequest_body {', '\\t\\t\\tmax_size 64KiB', '\\t\\t}', '\\t\\treverse_proxy 127.0.0.1:8118', '\\t}',"
    replacement="""        '\\thandle @codi_identity {', '\\t\\trequest_body {', '\\t\\t\\tmax_size 64KiB', '\\t\\t}',
        *(['\\t\\treverse_proxy 127.0.0.1:8118 {', '\\t\\t\\theader_up X-Codi-Client-IP {http.request.remote.host}', '\\t\\t}'] if s.get('codi_login_filter') else ['\\t\\treverse_proxy 127.0.0.1:8118']), '\\t}',"""
    source=replace_once(source,anchor,replacement,'trusted login address')
    return source

if __name__=='__main__':
    if len(sys.argv)!=3:raise SystemExit('Usage: prepare-browser-hosting.py INPUT OUTPUT')
    Path(sys.argv[2]).write_text(derive(Path(sys.argv[1]).read_text()))
