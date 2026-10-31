#!/usr/bin/env python3
"""Add a KSU-only, exact-file source/notice route to the pinned generator.

Writes a candidate generator only. It does not install or publish files.
"""
from pathlib import Path
import sys

NAMES=('index.html','firefox-licenses.html','emscripten-licenses.txt','wisp-license.txt',
       'adapter-license.txt','notice-manifest.json','firefox-2e1e835a.tar.zst',
       'firefox-wasm-bc69aaa5.tar.zst','firefox-wasm-local.patch','embed-host.cpp',
       'emscripten-6.0.1-patched-source.tar.zst','wisp-js-0.4.1-source.tar.zst',
       'codi-browser-source-59dfaf024.tar.zst','codi-browser-source-0fc6bf9a7.tar.zst','codi-browser-source-adece7482.tar.zst',
       'codi-relay-source-05e70e3b0.tar.zst')


def derive(source):
    old="('codi_browser_relay','codi_large_files','codi_login_filter')"
    new="('codi_browser_relay','codi_large_files','codi_login_filter','codi_browser_sources')"
    if source.count(old)!=2:raise ValueError('Expected exact Browser hosting flag anchors')
    source=source.replace(old,new)
    anchor='        *simplified_routes(s),\n'
    if source.count(anchor)!=1:raise ValueError('Expected exact Simplified route anchor')
    paths=' '.join('/'+name for name in NAMES)
    lines=["        *(['\\thandle /browser-sources {', '\\t\\tredir * /browser-sources/ 308', '\\t}',",
           "           '\\thandle_path /browser-sources/* {',",
           "           '\\t\\t@browser_source_file path / "+paths+"',",
           "           '\\t\\thandle @browser_source_file {',",
           "           '\\t\\t\\troot * /srv/codi-browser/source-staging/engine-6736dce5',",
           "           '\\t\\t\\tfile_server', '\\t\\t}',",
           "           '\\t\\thandle {', '\\t\\t\\trespond 404', '\\t\\t}', '\\t}'] if s.get('codi_browser_sources') else []),"]
    return source.replace(anchor,anchor+'\n'.join(lines)+'\n',1)


if __name__=='__main__':
    if len(sys.argv)!=3:raise SystemExit('Usage: prepare-browser-source-hosting.py INPUT OUTPUT')
    try:Path(sys.argv[2]).write_text(derive(Path(sys.argv[1]).read_text()))
    except (ValueError,OSError) as error:raise SystemExit(str(error))
