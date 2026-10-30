#!/usr/bin/env python3
"""Loopback static desktop server with an explicit public asset allowlist."""
import argparse
from http.server import SimpleHTTPRequestHandler,ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote,urlsplit
ROOT=Path(__file__).resolve().parent
PUBLIC={'index.html','style.css','app.js','reference.js','terminal.js','desktop-apps.js','config.json'}
STORAGE={'storage/browser/mirror.mjs'}
NETWORK={'crypto.mjs','identity.mjs','strict-json.mjs'}
RUNTIME={'libv86.js','v86.wasm','seabios.bin','vgabios.bin','vmlinuz','initramfs.cpio.gz'}
class PublicHandler(SimpleHTTPRequestHandler):
    def __init__(self,*args,**kwargs):super().__init__(*args,directory=str(ROOT),**kwargs)
    def end_headers(self):
        if urlsplit(self.path).path=='/assets/desktop/offline-worker.js':self.send_header('Service-Worker-Allowed','/')
        super().end_headers()
    def send_head(self):
        try:
            path=unquote(urlsplit(self.path).path,errors='strict');relative=path.lstrip('/') or 'index.html';parts=relative.split('/')
            if any(p in ('.','..','') for p in parts) or '\\' in path or '\x00' in path:raise ValueError()
            allowed=relative in PUBLIC or relative in STORAGE or len(parts)>1 and parts[0]=='assets' or len(parts)==2 and parts[0]=='network' and parts[1] in NETWORK or len(parts)==3 and parts[:2]==['.build','v86'] and parts[2] in RUNTIME
            if not allowed:raise ValueError()
            target=ROOT
            for part in parts:
                target=target/part
                if target.is_symlink():raise ValueError()
            if not target.is_file() or not target.resolve().is_relative_to(ROOT):raise ValueError()
        except (ValueError,UnicodeError):
            self.send_error(404,'Not found');return None
        return super().send_head()

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--port',type=int,default=8097);args=p.parse_args()
    with ThreadingHTTPServer(('127.0.0.1',args.port),PublicHandler) as server:
        print('CodiServer desktop lab: http://127.0.0.1:'+str(args.port),flush=True)
        try:server.serve_forever()
        except KeyboardInterrupt:pass
if __name__=='__main__':main()
