#!/usr/bin/env python3
"""Disposable loopback-only Gecko/Wisp fixture; NEVER use as a service.

The fixture deliberately uses fake account authentication and maps permitted
public DNS to a local HTTP test server. It is not production authorization.
"""
import asyncio,sys,time
from pathlib import Path
from types import SimpleNamespace
from aiohttp import web
root=Path(__file__).resolve().parents[1]/'apps/system/browser';sys.path.insert(0,str(root))
from relay.wisp import Relay
async def main():
 calls=[]
 async def serve(reader,writer):
  try:
   await reader.readuntil(b'\r\n\r\n');data=b'<!doctype html><title>Fixture</title><h1>RELAY TEST PAGE</h1><p>fixture reached through test relay</p>'
   writer.write(b'HTTP/1.1 200 OK\r\nContent-Type: text/html\r\nContent-Length: '+str(len(data)).encode()+b'\r\nConnection: close\r\n\r\n'+data);await writer.drain()
  finally:writer.close();await writer.wait_closed()
 echo=await asyncio.start_server(serve,'127.0.0.1',0);port=echo.sockets[0].getsockname()[1]
 async def auth(_):return SimpleNamespace(kind='registered',sub='user:fixture',deadline=time.time()+300)
 async def resolve(name,port):calls.append(name);return ['1.1.1.1']
 async def connect(addr,p):return await asyncio.open_connection('127.0.0.1',port)
 relay=Relay(policy_path=root/'relay/policy.json',origin='http://127.0.0.1:18088',authenticate=auth,source=lambda r:'127.0.0.1',resolver=resolve,connector=connect)
 @web.middleware
 async def headers(request,handler):
  response=await handler(request);response.headers.update({'Cross-Origin-Opener-Policy':'same-origin','Cross-Origin-Embedder-Policy':'require-corp','Cross-Origin-Resource-Policy':'same-origin','Content-Security-Policy':"default-src 'self'; script-src 'self' blob: 'wasm-unsafe-eval'; worker-src 'self' blob:; connect-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; object-src 'none'; frame-src 'none'; base-uri 'none'; form-action 'none'"});return response
 app=web.Application(middlewares=[headers]);app.router.add_get('/relay/',relay.handle)
 async def stats(_):return web.json_response({'resolved':calls})
 app.router.add_get('/test-calls',stats)
 async def demo(_):
  text=(root/'demo/main.mjs').read_text().replace('mount({ui:{make(tag,cls)',"mount({storage:{signedInSubject:()=>\"user:fixture\"},ui:{make(tag,cls)")
  return web.Response(text=text,content_type='text/javascript')
 app.router.add_get('/demo/main.mjs',demo)
 async def config(_):
  text=(root/'config.mjs').read_text().replace('wispURL: null','wispURL: "ws://127.0.0.1:18088/relay/"');return web.Response(text=text,content_type='text/javascript')
 app.router.add_get('/config.mjs',config);app.router.add_static('/',root,show_index=False)
 runner=web.AppRunner(app);await runner.setup();await web.TCPSite(runner,'127.0.0.1',18088).start();print('LOCAL TEST FIXTURE ONLY',flush=True)
 try:await asyncio.Event().wait()
 finally:await runner.cleanup();echo.close();await echo.wait_closed()
asyncio.run(main())
