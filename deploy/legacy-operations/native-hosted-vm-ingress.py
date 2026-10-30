#!/usr/bin/env python3
"""Private VM-only HTTPS ingress and controlled fake Internet destinations."""
import argparse
import asyncio
import hashlib
import json
import mimetypes
import re
from pathlib import Path
import socket
import ssl
import struct
from aiohttp import ClientSession,ClientTimeout,WSMsgType,WSServerHandshakeError,web

class DNS(asyncio.DatagramProtocol):
    def connection_made(self,transport):self.transport=transport
    def datagram_received(self,data,peer):
        try:
            if len(data)<12 or data[4:6]!=b'\0\1':return
            at=12
            while data[at]:at+=1+data[at]
            end=at+5
            if end>len(data):return
            question=data[12:end];answer=b'\xc0\x0c\0\1\0\1'+struct.pack('!IH',30,4)+socket.inet_aton('1.1.1.2')
            self.transport.sendto(data[:2]+b'\x81\x80\0\1\0\1\0\0\0\0'+question+answer,peer)
        except (IndexError,ValueError):return

async def main(args):
    legacy=None;legacy_public=None
    if args.legacy_release:
        legacy=Path(args.legacy_release)
        raw=(legacy/'connected-release.json').read_bytes()
        if hashlib.sha256(raw).hexdigest()!='abb67a1f7a2e718c006cf0784dd216cceebb49982d4a8c03f14b7e21bfff2abf':raise ValueError('Exact original R16 release required')
        legacy_public=json.loads((legacy/'release.json').read_text())['files']
    context=ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER);context.load_cert_chain(args.certificate,args.key)
    sessions=[];runners=[];counters={}
    async def public(request):
        ip=request.transport.get_extra_info('sockname')[0];counters[ip]=counters.get(ip,0)+1
        return web.Response(text='CODI_CONTROLLED_PUBLIC_'+ip+'\n')
    app=web.Application();app.router.add_get('/{path:.*}',public);runner=web.AppRunner(app,access_log=None);await runner.setup();runners.append(runner)
    await web.TCPSite(runner,'0.0.0.0',80).start();await web.TCPSite(runner,'0.0.0.0',443,ssl_context=context).start()
    transport,_=await asyncio.get_running_loop().create_datagram_endpoint(DNS,local_addr=('1.1.1.3',53))
    outgoing=ClientSession(timeout=ClientTimeout(total=60),trust_env=False,auto_decompress=False);sessions.append(outgoing)
    async def proxy(request):
        if request.path=='/fixture-health':return web.json_response({'status':'ok','publicRequests':counters})
        base=args.base_path
        if args.native_config:
            # Owned private fixture only: follow the actual managed mount, so
            # root tests exercise root APIs rather than a hidden-path rewrite.
            try:
                base=json.loads(Path(args.native_config).read_text())['basePath']
                if not isinstance(base,str) or len(base)>128 or base and not re.fullmatch(r'(?:/[A-Za-z0-9_-]+)+',base):raise ValueError('Invalid fixture mount')
            except (OSError,ValueError,KeyError):raise web.HTTPServiceUnavailable()
        if not request.path.startswith(base+'/'):raise web.HTTPNotFound()
        path=request.path[len(base):]
        if path.startswith('/rooms/') and args.room_port is not None:
            if args.native_config is None or not json.loads(Path(args.native_config).read_text()).get('hostedRooms'):raise web.HTTPNotFound()
            port=args.room_port
        else:port=8118 if path.startswith('/api/') or path in ('/discovery.json','/.well-known/codi-issuer.json') else 8119 if path.startswith('/rendezvous') else 8140 if path.startswith('/gateway/') else 8132
        build=request.cookies.get('codi_fixture_build','modern')
        if path=='/':build=request.query.get('build',build)
        name=path.lstrip('/') or 'index.html'
        if legacy is not None and build=='legacy' and name!='config.json' and name in legacy_public:
            target=legacy/name;record=legacy_public[name]
            if target.is_symlink() or record!={'bytes':target.stat().st_size,'sha256':hashlib.sha256(target.read_bytes()).hexdigest()}:raise web.HTTPInternalServerError()
            # The real index backend must still issue/renew its protected guest
            # cookie. Only its already-public response body is replaced below.
            if path!='/':
                typ='text/javascript' if name.endswith('.mjs') else mimetypes.guess_type(name)[0] or 'application/octet-stream'
                response=web.Response(body=target.read_bytes(),content_type=typ,headers={'Cache-Control':'no-store','Cross-Origin-Opener-Policy':'same-origin','Cross-Origin-Embedder-Policy':'require-corp'})
                if name=='assets/desktop/offline-worker.js':response.headers['Service-Worker-Allowed']=base+'/'
                return response
        target='http://127.0.0.1:'+str(port)+(request.path if port==8119 else path)+('?' + request.query_string if request.query_string else '')
        headers={k:v for k,v in request.headers.items() if k.lower() not in {'connection','upgrade','transfer-encoding','content-length'}}
        if request.headers.get('Upgrade','').lower()=='websocket':
            browser=web.WebSocketResponse(max_msg_size=1048576,compress=False,heartbeat=30)
            try:upstream=await outgoing.ws_connect(target,headers=headers,max_msg_size=1048576,compress=0)
            except WSServerHandshakeError as error:return web.Response(status=error.status)
            async with upstream:
                await browser.prepare(request)
                async def pump(source,destination):
                    async for message in source:
                        if message.type==WSMsgType.TEXT:await destination.send_str(message.data)
                        elif message.type==WSMsgType.BINARY:await destination.send_bytes(message.data)
                        else:break
                tasks=[asyncio.create_task(pump(browser,upstream)),asyncio.create_task(pump(upstream,browser))]
                try:await asyncio.wait(tasks,return_when=asyncio.FIRST_COMPLETED)
                finally:
                    for task in tasks:task.cancel()
                    await asyncio.gather(*tasks,return_exceptions=True);await browser.close()
            return browser
        async with outgoing.request(request.method,target,headers=headers,data=await request.read(),allow_redirects=False) as upstream:
            response=web.Response(body=await upstream.read(),status=upstream.status,headers={k:v for k,v in upstream.headers.items() if k.lower() not in {'connection','transfer-encoding','content-length'}})
            if path=='/' and legacy is not None:
                if build=='legacy':response.body=(legacy/'index.html').read_bytes()
                response.set_cookie('codi_fixture_build',build,path=base+'/',samesite='Strict')
            response.headers['Cross-Origin-Opener-Policy']='same-origin';response.headers['Cross-Origin-Embedder-Policy']='require-corp';return response
    ingress=web.Application(client_max_size=12*1024*1024);ingress.router.add_route('*','/{path:.*}',proxy);runner=web.AppRunner(ingress,access_log=None);await runner.setup();runners.append(runner);await web.TCPSite(runner,'0.0.0.0',8443,ssl_context=context).start()
    print(json.dumps({'status':'ready','sourceSHA256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'controlledPublicIPv4':['1.1.1.1','1.1.1.2','1.1.1.3']}),flush=True)
    try:await asyncio.Event().wait()
    finally:
        transport.close()
        for runner in reversed(runners):await runner.cleanup()
        for session in sessions:await session.close()
if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--certificate',required=True);parser.add_argument('--key',required=True);parser.add_argument('--legacy-release',help='Owned fixture only: retain original R16 public assets per throwaway-browser cookie');parser.add_argument('--base-path',default='/hidden');parser.add_argument('--native-config',type=Path,help='Owned fixture only: read current mount from protected native configuration');parser.add_argument('--room-port',type=int,choices=range(1024,65536),help='Owned private fixture only: fixed room proxy; requires enabled native metadata');asyncio.run(main(parser.parse_args()))
