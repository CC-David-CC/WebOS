#!/usr/bin/env python3
"""Loopback-only bounded streaming fault proxy for disposable gateway fixtures."""
import asyncio, json, os, sys
if len(sys.argv)!=3: raise SystemExit('usage: proxy-port gateway-port')
port,upstream=map(int,sys.argv[1:]); assert 1024<=port<=65535 and 1024<=upstream<=65535
state={'armed':None,'cuts':0,'requestBytes':0,'responseBytes':0,'requests':0,'upstreamStatus':None,'uploads':0,'upload2xx':0}
async def conn(reader,writer):
 up=None
 try:
  header=await asyncio.wait_for(reader.readuntil(b'\r\n\r\n'),10)
  if len(header)>32768: raise ValueError('header limit')
  lines=header[:-4].split(b'\r\n'); method,path,_=lines[0].split(b' ',2);path=path.decode('ascii'); fields={}
  for line in lines[1:]:
   k,v=line.split(b':',1); k=k.lower();
   if k in fields: raise ValueError('duplicate header')
   fields[k]=v.strip()
  if b'transfer-encoding' in fields:raise ValueError('chunked request unsupported')
  length=int(fields.get(b'content-length',b'0'))
  if length<0 or length>140*1024*1024:raise ValueError('request size')
  if path.startswith('/__fault/'):
   cmd=path.rsplit('/',1)[-1]
   if cmd!='status':
    if cmd not in ('upload-in','upload-reply','read-binary','chunk-read-batch-v1'):raise ValueError('unknown fault')
    state.update(armed=cmd,cuts=0,requestBytes=0,responseBytes=0,requests=0,upstreamStatus=None)
   data=json.dumps(state).encode();writer.write(b'HTTP/1.1 200 OK\r\nContent-Type: application/json\r\nContent-Length: '+str(len(data)).encode()+b'\r\nConnection: close\r\n\r\n'+data);await writer.drain();return
  body=b'';operation=None
  if path=='/gateway/use':
   if length>65536:raise ValueError('operation metadata limit')
   body=await reader.readexactly(length);operation=json.loads(body).get('operation')
  selected=(path=='/gateway/upload' and state['armed'] in ('upload-in','upload-reply')) or (path=='/gateway/use' and operation==state['armed'])
  if path=='/gateway/upload':state['uploads']+=1
  if selected:state['requests']+=1
  ur,up=await asyncio.open_connection('127.0.0.1',upstream)
  out=b'\r\n'.join(line for line in lines if not line.lower().startswith(b'connection:'))+b'\r\nConnection: close\r\n\r\n';up.write(out+body);await up.drain();remaining=length-len(body)
  while remaining:
   data=await reader.read(min(65536,remaining))
   if not data:raise EOFError('truncated request')
   if selected:state['requestBytes']+=len(data)
   up.write(data);await up.drain();remaining-=len(data)
   if selected and state['armed']=='upload-in' and state['requestBytes']>=65536:
    state.update(armed=None,cuts=state['cuts']+1);writer.transport.abort();return
  response=await ur.readuntil(b'\r\n\r\n');status=int(response.split(b' ',2)[1]);
  if path=='/gateway/upload' and 200<=status<300:state['upload2xx']+=1
  if selected:state['upstreamStatus']=status
  if selected and state['armed']=='upload-reply':
   # Upstream produced its HTTP result after handling the full mutation. Drop it.
   state.update(armed=None,cuts=state['cuts']+1);writer.transport.abort();return
  writer.write(response);await writer.drain()
  while True:
   data=await ur.read(65536)
   if not data:break
   writer.write(data);await writer.drain()
   if selected:
    state['responseBytes']+=len(data)
    if state['responseBytes']>=65536:
     state.update(armed=None,cuts=state['cuts']+1);writer.transport.abort();return
 except (ConnectionError,asyncio.IncompleteReadError,asyncio.LimitOverrunError,EOFError,ValueError,KeyError,asyncio.TimeoutError) as e:
  print('proxy connection ended',type(e).__name__,flush=True)
 finally:
  if up:up.close()
  writer.close()
async def main():
 server=await asyncio.start_server(conn,'127.0.0.1',port,limit=65536);print('fault proxy ready',port,'upstream',upstream,flush=True)
 async with server:await server.serve_forever()
try:asyncio.run(main())
except KeyboardInterrupt:pass
