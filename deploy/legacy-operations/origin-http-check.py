#!/usr/bin/env python3
"""Real loopback saturation, idle timeout, and recovery of bounded WSGI."""
import hashlib,json,socket,sys,threading,time
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT))
from origin_service.http_server import BoundedServer
entered=threading.Event();release=threading.Event()
def app(env,start):
 if env['PATH_INFO']=='/hold':
  entered.set();release.wait(3)
 start('200 OK',[('Content-Length','2')]);return [b'ok']
def connect(port,path=None):
 s=socket.create_connection(('127.0.0.1',port),timeout=2)
 if path:s.sendall(('GET '+path+' HTTP/1.0\r\nHost: localhost\r\n\r\n').encode())
 return s
def response(s):
 chunks=[]
 while True:
  b=s.recv(4096)
  if not b:return b''.join(chunks)
  chunks.append(b)
with BoundedServer(('127.0.0.1',0),workers=2,timeout=.4) as server:
 server.set_app(app);port=server.server_port
 thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
 try:
  with connect(port,'/hold') as held:
   assert entered.wait(2)
   # A second request progresses while the first application is occupied.
   with connect(port,'/') as second:assert b'200 OK' in response(second)
   with connect(port) as idle:
    # Confirm both slots occupied rather than relying on a scheduling sleep.
    deadline=time.monotonic()+2
    while server.slots.acquire(blocking=False):
     server.slots.release()
     if time.monotonic()>deadline:raise AssertionError('idle request not admitted')
     time.sleep(.005)
    with connect(port,'/') as excess:assert b'503 Service Unavailable' in response(excess)
    # Idle header sender times out and releases its worker.
    assert idle.recv(1024)==b''
   release.set();assert b'200 OK' in response(held)
  with connect(port,'/') as recovered:assert b'200 OK' in response(recovered)
  malformed=[
   b'Host: localhost\r\nHost: other',
   b'Host: localhost\r\nContent-Length: 0\r\nContent-Length: 0',
   b'Host: localhost\r\nContent-Length: 0, 0',
   b'Host: localhost\r\nContent-Length: +0',
   b'Host: localhost\r\nContent-Length: -1',
   b'Host: localhost\r\nTransfer-Encoding: chunked',
   b'Host: localhost\r\nContent-Length: 0\r\nTransfer-Encoding: chunked',
   b'Host: localhost\r\nContent-Length: 65537',
   b'Host: localhost\r\nX-Test: first\r\n second',
  ]
  for headers in malformed:
   with connect(port) as bad:
    bad.sendall(b'POST / HTTP/1.0\r\n'+headers+b'\r\n\r\n')
    status=response(bad).split(b'\r\n',1)[0]
    assert b'400 ' in status or b'413 ' in status,(headers,status)
  with connect(port,'/') as recovered:assert b'200 OK' in response(recovered)
 finally:
  release.set();server.shutdown();thread.join(2)
result={'status':'PASS','scope':'Real loopback WSGI transport, not public deployment or full issuer load','concurrentProgress':True,'excessRejected503':True,'idleHeaderTimeout':True,'capacityRecovered':True,'ambiguousRequestsRejected':len(malformed),'sha256':{n:hashlib.sha256((ROOT/n).read_bytes()).hexdigest() for n in ['origin_service/http_server.py','scripts/serve-connected.py','scripts/origin-http-check.py']}}
p=ROOT/'.build/checks/origin-http-result.json';p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
