#!/usr/bin/env python3
"""Exercise Caddy's PROXY protocol source and trusted-header overwrite on loopback."""
import asyncio
import json
import os
from pathlib import Path
import pwd
import socket
import struct
import subprocess
import tempfile

async def main():
    with tempfile.TemporaryDirectory(prefix='codi-caddy-peer-') as folder:
        root=Path(folder);root.chmod(0o755);sockpath=root/'upstream.sock';seen=[]
        async def upstream(reader,writer):
            try:
                data=await asyncio.wait_for(reader.readuntil(b'\r\n\r\n'),5)
                peer=writer.get_extra_info('socket');_,uid,_=struct.unpack('3i',peer.getsockopt(socket.SOL_SOCKET,socket.SO_PEERCRED,12))
                values=[line.split(b':',1)[1].strip().decode() for line in data.split(b'\r\n') if line.lower().startswith(b'x-codi-client-ip:')]
                seen.append({'uid':uid,'addresses':values})
                body=json.dumps(seen[-1]).encode();writer.write(b'HTTP/1.1 200 OK\r\nContent-Type: application/json\r\nContent-Length: '+str(len(body)).encode()+b'\r\nConnection: close\r\n\r\n'+body);await writer.drain()
            finally:writer.close();await writer.wait_closed()
        server=await asyncio.start_unix_server(upstream,path=str(sockpath));os.chmod(sockpath,0o666)
        probe=socket.socket();probe.bind(('127.0.0.1',0));port=probe.getsockname()[1];probe.close()
        config=root/'Caddyfile';config.write_text('''{
 admin off
 auto_https off
 servers {
  listener_wrappers {
   proxy_protocol {
    allow 127.0.0.1/32
    fallback_policy reject
   }
  }
 }
}
http://127.0.0.1:%d {
 reverse_proxy unix//%s {
  header_up X-Codi-Client-IP {http.request.remote.host}
 }
}
'''%(port,str(sockpath).lstrip('/')));config.chmod(0o644)
        process=await asyncio.create_subprocess_exec('sudo','-n','runuser','-u','caddy','--','/usr/bin/caddy','run','--config',str(config),'--adapter','caddyfile',stdout=asyncio.subprocess.DEVNULL,stderr=asyncio.subprocess.PIPE)
        try:
            for version in (1,2):
                for _ in range(100):
                    try:reader,writer=await asyncio.open_connection('127.0.0.1',port);break
                    except OSError:
                        if process.returncode is not None:raise RuntimeError((await process.stderr.read()).decode())
                        await asyncio.sleep(.05)
                else:raise RuntimeError('Caddy fixture did not start')
                if version==1:prefix=('PROXY TCP4 198.51.100.8 127.0.0.1 34567 '+str(port)+'\r\n').encode()
                else:
                    prefix=b'\r\n\r\n\x00\r\nQUIT\n'+bytes([0x21,0x11])+struct.pack('!H',12)+socket.inet_aton('198.51.100.8')+socket.inet_aton('127.0.0.1')+struct.pack('!HH',34567,port)
                request=('GET / HTTP/1.1\r\nHost: 127.0.0.1:'+str(port)+'\r\nX-Codi-Client-IP: 203.0.113.99\r\nX-Codi-Client-IP: 203.0.113.100\r\nConnection: close\r\n\r\n').encode()
                writer.write(prefix+request);await writer.drain();reply=await asyncio.wait_for(reader.read(),10);writer.close();await writer.wait_closed()
                head,body=reply.split(b'\r\n\r\n',1);assert b' 200 ' in head,(head,body)
                result=json.loads(body);assert result=={'uid':pwd.getpwnam('caddy').pw_uid,'addresses':['198.51.100.8']},result
            print(json.dumps({'status':'PASS','scope':'Independent loopback Caddy fixture: PROXY v1/v2 source overrides duplicate spoofed headers; Unix peer UID checked','result':result}))

        finally:
            if process.returncode is None:process.terminate()
            try:await asyncio.wait_for(process.communicate(),10)
            except asyncio.TimeoutError:process.kill();await process.communicate()
            server.close();await server.wait_closed()

if __name__=='__main__':asyncio.run(main())
