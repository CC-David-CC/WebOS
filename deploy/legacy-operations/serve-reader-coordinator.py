#!/usr/bin/env python3
"""Unprivileged discovery-only worker; key arrives through systemd credentials."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import signal
import stat
import sys
import threading
from socketserver import ThreadingMixIn
from wsgiref.simple_server import make_server,WSGIServer,WSGIRequestHandler
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ec

ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from room_service.contract import exact,require,public_key
from reader_service.http import ReaderHTTP
from reader_service.contract import paths
from reader_service.delegation import public_file as protected_public, credential as load_credential, policy_file

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--policy-directory',type=Path,required=True);p.add_argument('--policy-sha256',required=True);p.add_argument('--port',type=int,default=8143);a=p.parse_args()
    if os.geteuid()==0:p.error('Coordinator must run as its isolated unprivileged service account')
    require(1024<=a.port<=65535,'Unprivileged loopback port required');policy=policy_file(a.policy_directory,a.policy_sha256)
    key=load_credential('reader-key');from room_service.contract import jose
    require(jose.public_jwk(key)==policy['coordinatorKey'],'Signing key differs from discovery delegation policy')
    delegation=lambda:protected_public(a.policy_directory/'delegation.jws',4096).decode('ascii')
    app=ReaderHTTP(key,policy['identity'],policy['roomControllerKey'],delegation(),base=policy['basePath'],delegation_provider=delegation)
    class Server(ThreadingMixIn,WSGIServer):
        daemon_threads=True;request_queue_size=16
        def __init__(self,*args,**kwargs):self.slots=threading.BoundedSemaphore(16);super().__init__(*args,**kwargs)
        def process_request(self,request,address):
            request.settimeout(15)
            if not self.slots.acquire(blocking=False):
                # Explicit short backpressure instead of a silent socket reset.
                body=b'{"error":"Coordinator busy"}'
                try:request.sendall(b'HTTP/1.1 503 Service Unavailable\r\nConnection: close\r\nContent-Type: application/json\r\nRetry-After: 1\r\nContent-Length: '+str(len(body)).encode()+b'\r\n\r\n'+body)
                except OSError:pass
                self.shutdown_request(request);return
            try:super().process_request(request,address)
            except BaseException:self.slots.release();raise
        def process_request_thread(self,*args):
            try:super().process_request_thread(*args)
            finally:self.slots.release()
    class Quiet(WSGIRequestHandler):
        def log_message(self,*_):pass
    def stop(*_):raise KeyboardInterrupt
    signal.signal(signal.SIGTERM,stop)
    with make_server('127.0.0.1',a.port,app,server_class=Server,handler_class=Quiet) as server:
        try:server.serve_forever()
        except KeyboardInterrupt:pass

if __name__=='__main__':main()
