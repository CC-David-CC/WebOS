import asyncio,json
from pathlib import Path
from aiohttp import web, ClientSession
async def main():
 app=web.Application();app.router.add_get('/',lambda req:web.Response(text='ok'));runner=web.AppRunner(app);await runner.setup();await web.TCPSite(runner,'127.0.0.1',19688).start()
 src=(Path(__file__).resolve().parent.parent/'active-system/gateway_service/client.mjs').read_text();code=src[src.index('const DELTA_BLOCK='):src.index('export class UserFiles')]
 js='''(async()=>{const requireThat=(x,m)=>{if(!x)throw Error(m)};const MAX_FILE=128*1024*1024;'''+code+'''
 let count=0;const original=crypto.subtle.digest.bind(crypto.subtle);crypto.subtle.digest=(...args)=>{count++;return original(...args)};
 const data=new Uint8Array(1048576);for(let i=0;i<data.length;i++)data[i]=[101,98,101,100][i%4];
 const sig={version:'codi-file-delta/1',size:65536,block:65536,chunks:[[787416541,'f'.repeat(64)]]};
 const start=performance.now(),result=await makeFileDelta(data,sig);if(result!==null||count!==64)throw Error('bad collision limit '+count);return {hashes:count,ms:performance.now()-start,fallback:result===null};})()'''
 async with ClientSession() as s:
  async with s.put('http://127.0.0.1:19255/json/new?http://127.0.0.1:19688/') as r:t=await r.json()
  try:
   async with s.ws_connect(t['webSocketDebuggerUrl']) as w:
    await w.send_json({'id':1,'method':'Runtime.evaluate','params':{'expression':js,'awaitPromise':True,'returnByValue':True}})
    async for msg in w:
     v=json.loads(msg.data)
     if v.get('id')==1:
      if 'exceptionDetails' in v.get('result',{}):raise Exception(v)
      print('Chrome collision:',v['result']['result'].get('value'));break
  finally:
   async with s.get('http://127.0.0.1:19255/json/close/'+t['id']) as r:await r.read()
 await runner.cleanup()
asyncio.run(main())
