"""Owned separate coordinator + real Caddy front end for browser/load tests.

No production units, routes, keys, namespace changes or public listener. The
caller closes browser clients before closing this fixture and removing files.
"""
import importlib.util
import ast
import hashlib
import json
from pathlib import Path
import signal
import socket
import subprocess
import sys
import time
import urllib.request
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ec

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('coordinator_process_source',ROOT/'scripts/reader-coordinator-check.py');source=importlib.util.module_from_spec(spec);spec.loader.exec_module(source)
from reader_service.contract import issue
from room_service.contract import jose

def front_origin():
    with socket.socket() as s:s.bind(('127.0.0.1',0));return 'http://127.0.0.1:'+str(s.getsockname()[1])

class CoordinatorFixture:
    def __init__(self,fixture,caddy):
        self.f=fixture;self.folder=fixture.folder/'coordinator-fixture';self.folder.mkdir(mode=0o700);self.child=None;self.front=None;self.port=0;self.caddy=Path(caddy).resolve()
        self.key=ec.generate_private_key(ec.SECP256R1());self.public=jose.public_jwk(self.key);self.keyfile=self.folder/'key.pem'
        self.keyfile.write_bytes(self.key.private_bytes(serialization.Encoding.PEM,serialization.PrivateFormat.PKCS8,serialization.NoEncryption()));self.keyfile.chmod(0o600)
        self.delegation=issue(self.f.store.key,self.public,self.f.policy,self.f.base,int(time.time()));self.authority=self.folder/'delegation.jws';self.authority.write_text(self.delegation)
        try:
            self.start_coordinator()
            config=self.folder/'Caddyfile';prefix=self.f.base
            text='{\n admin off\n auto_https off\n}\n'+self.f.origin+' {\n bind 127.0.0.1\n'
            text+=' handle '+prefix+'/rooms/readers/* {\n reverse_proxy 127.0.0.1:'+str(self.port)+'\n }\n'
            for name in ['rooms','api']:
                text+=' handle '+prefix+'/'+name+'/* {\n reverse_proxy 127.0.0.1:'+str(self.f.server.server_port)+'\n }\n'
            text+=' handle'+(' '+prefix+'/*' if prefix else '')+' {\n'+(' uri strip_prefix '+prefix+'\n' if prefix else '')+' root * '+json.dumps(str(self.f.folder/'public'))+'\n file_server\n }\n'
            if prefix:text+=' handle { respond 404 }\n'
            text+='}\n';config.write_text(text)
            with (self.folder/'caddy.log').open('wb') as log:self.front=subprocess.Popen([str(self.caddy),'run','--config',str(config),'--adapter','caddyfile'],stdin=subprocess.DEVNULL,stdout=log,stderr=log)
            end=time.monotonic()+15
            while True:
                if self.front.poll() is not None:raise RuntimeError((self.folder/'caddy.log').read_text()[-3000:])
                try:
                    with urllib.request.urlopen(self.f.origin+self.f.base+'/rooms/readers/health',timeout=1) as r:assert json.load(r)['ready']
                    break
                except OSError:
                    if time.monotonic()>end:raise
                    time.sleep(.1)
        except BaseException:
            self.close();raise

    def start_coordinator(self):
        assert not self.child or self.child.poll() is not None
        # Fixed owned port across restarts; existing Caddy routes stay unchanged.
        code=source.CHILD.replace("ReaderHTTP(key,d['policy'],d['roomKey'],d['delegation'],", "ReaderHTTP(key,d['policy'],d['roomKey'],d['delegation'],base=d['base'],").replace("make_server('127.0.0.1',0,app", "make_server('127.0.0.1',d['port'],app")
        # Reuse the exact production server class without invoking root-policy
        # or LoadCredential startup in this unprivileged protocol fixture. The
        # earlier fixture's single-thread wsgiref front was a different queue/
        # concurrency boundary and must not stand in for production capacity.
        entry=ROOT/'scripts/serve-reader-coordinator.py';raw=entry.read_bytes()
        main=next(n for n in ast.parse(raw).body if isinstance(n,ast.FunctionDef) and n.name=='main')
        server=next(n for n in main.body if isinstance(n,ast.ClassDef) and n.name=='Server')
        self.http_server_sha256=hashlib.sha256(raw).hexdigest();self.http_transport='production-class-threaded16'
        code=code.replace('from wsgiref.simple_server import make_server,WSGIRequestHandler','from wsgiref.simple_server import make_server,WSGIRequestHandler,WSGIServer\nfrom socketserver import ThreadingMixIn\nimport threading')
        code=code.replace('class Quiet(WSGIRequestHandler):',ast.unparse(server)+'\nclass Quiet(WSGIRequestHandler):')
        code=code.replace('app,handler_class=Quiet)','app,server_class=Server,handler_class=Quiet)')
        # Production stderr is continuously consumed by journald. Do not let an
        # undrained test pipe turn worker diagnostics into a false load ceiling.
        self.logfile=self.folder/'coordinator.log'
        with self.logfile.open('ab') as errors:
            self.child=subprocess.Popen([sys.executable,'-I','-B','-c',code],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=errors,text=True)
        self.child.stdin.write(json.dumps({'source':str(ROOT),'key':str(self.keyfile),'policy':self.f.policy,'roomKey':self.f.store.public,'delegation':self.delegation,'authority':str(self.authority),'base':self.f.base,'port':self.port})+'\n');self.child.stdin.flush()
        line=self.child.stdout.readline()
        if not line:
            with self.logfile.open('rb') as errors:errors.seek(max(0,self.logfile.stat().st_size-4000));detail=errors.read().decode(errors='replace')
            raise RuntimeError(detail)
        self.ready=json.loads(line);self.port=self.ready['port'];assert self.ready['pid']==self.child.pid and not self.ready['roomStoreImported']

    def stop_coordinator(self):
        if self.child and self.child.poll() is None:self.child.terminate();self.child.wait(timeout=5)

    def close(self):
        if self.front and self.front.poll() is None:
            self.front.terminate()
            try:self.front.wait(timeout=12)
            except subprocess.TimeoutExpired:self.front.kill();self.front.wait(timeout=5)
        self.stop_coordinator()
