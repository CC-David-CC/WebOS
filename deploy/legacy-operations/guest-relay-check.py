#!/usr/bin/env python3
"""Packet policy and actual aiohttp/QEMU lifecycle checks; no external traffic."""
import asyncio,hashlib,importlib.util,json,socket,struct,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT))
spec=importlib.util.spec_from_file_location('guest_relay',ROOT/'guest-relay/server.py')
module=importlib.util.module_from_spec(spec);sys.modules[spec.name]=module;spec.loader.exec_module(module)
from aiohttp import ClientSession,CookieJar,WSMsgType,web
checks=[]
def check(name,value):
 assert value,name
 checks.append(name)
def packet(destination='1.1.1.1',protocol=1,payload=None,source='10.86.0.2',flags=0,options=b''):
 if payload is None:
  payload={1:b'\x08\0'+bytes(6),6:bytes(12)+b'\x50'+bytes(7),17:struct.pack('!HHHH',1234,53,8,0)}.get(protocol,bytes(8))
 header=struct.pack('!BBHHHBBH4s4s',0x45+len(options)//4,0,20+len(options)+len(payload),1,flags,64,protocol,0,socket.inet_aton(source),socket.inet_aton(destination))
 return bytes(12)+b'\x08\0'+header+options+payload
def rejects(name,action):
 try:action()
 except ValueError:check(name,True)
 else:check(name,False)
async def run():
 now=[0.0];limits=module.Limits(session_seconds=3,bytes_per_second=100,packets_per_second=2)
 budget=module.TrafficBudget(limits,lambda:now[0]);budget.charge(50);budget.charge(50)
 check('exact byte/packet budget accepted',budget.byte_count==100 and budget.packet_count==2)
 rejects('packet budget rejects zero-byte excess',lambda:budget.charge(0))
 budget=module.TrafficBudget(limits,lambda:now[0]);rejects('byte budget rejects excess',lambda:budget.charge(101))
 now[0]=1;budget.charge(100);check('one second window resets',budget.byte_count==100 and budget.packet_count==1)
 now[0]=3;rejects('exact lifetime boundary expires',lambda:budget.charge(0))
 now[0]=0;budget=module.TrafficBudget(module.Limits(session_bytes=100),lambda:now[0]);budget.charge(60);now[0]=2
 rejects('session byte cap survives rate window reset',lambda:budget.charge(41))
 shared=module.SharedByteBudget(100);shared.charge(60);shared.charge(40)
 check('exact shared byte cap exhausts service',shared.used==100 and shared.exhausted)
 rejects('shared cap refuses further bytes',lambda:shared.charge(1))
 shared=module.SharedByteBudget(100);rejects('single oversized charge exhausts service',lambda:shared.charge(101))
 check('failed shared charge never exceeds limit',shared.used==0 and shared.exhausted)
 for protocol in (1,6,17):check(f'public protocol {protocol}',module.permitted_frame(packet(protocol=protocol)))
 for port in (80,443,22,25,53,8000):
  payload=struct.pack('!HH',1234,port)+bytes(8)+b'\x50'+bytes(7)
  check(f'preview TCP port {port}',module.permitted_frame(packet(protocol=6,payload=payload),preview=True)==(port in (80,443)))
 check('preview arbitrary external UDP denied',not module.permitted_frame(packet(protocol=17),preview=True))
 check('preview public echo allowed',module.permitted_frame(packet(),preview=True))
 check('preview gateway DNS allowed',module.permitted_frame(packet('10.86.0.3',17),preview=True))
 for address in ('127.0.0.1','10.0.7.84','192.168.1.1','172.16.0.1','169.254.169.254','0.0.0.0','224.0.0.1','255.255.255.255','100.64.0.1','10.86.0.1'):
  check('deny destination '+address,not module.permitted_frame(packet(address)))
 check('DNS proxy UDP 53 allowed',module.permitted_frame(packet('10.86.0.3',17)))
 check('DNS proxy TCP denied',not module.permitted_frame(packet('10.86.0.3',6)))
 check('DNS other port denied',not module.permitted_frame(packet('10.86.0.3',17,struct.pack('!HHHH',1234,80,8,0))))
 for flags in (1,0x2000,0x8000):check(f'fragment/reserved {flags} denied',not module.permitted_frame(packet(flags=flags)))
 check('DF permitted',module.permitted_frame(packet(flags=0x4000)))
 check('source routing denied',not module.permitted_frame(packet(options=b'\x83\x04\x00\x00')))
 check('source spoof denied',not module.permitted_frame(packet(source='10.86.0.4')))
 for protocol,payload in ((1,b'\x03\0'+bytes(6)),(6,bytes(19)),(6,bytes(20)),(17,bytes(8)),(47,bytes(8))):
  check(f'malformed/unsupported transport {protocol}/{payload.hex()} denied',not module.permitted_frame(packet(protocol=protocol,payload=payload)))
 good=packet()
 check('every truncated IPv4 denied',all(not module.permitted_frame(good[:i]) for i in range(len(good))))
 check('oversized frame denied',not module.permitted_frame(good+bytes(1519)))
 arp=bytes(12)+b'\x08\x06'+b'\0\x01\x08\0\x06\x04\0\x01'+bytes(6)+socket.inet_aton('10.86.0.2')+bytes(6)+socket.inet_aton('10.86.0.1')
 check('gateway ARP permitted',module.permitted_frame(arp))
 check('other ARP target denied',not module.permitted_frame(arp[:-4]+socket.inet_aton('10.0.7.84')))
 check('short ARP denied',not module.permitted_frame(arp[:-1]))
 relay=module.Relay('http://127.0.0.1');app=web.Application();app.router.add_get('/guest-network',relay.relay);app.router.add_get('/{path:.*}',relay.assets)
 runner=web.AppRunner(app);await runner.setup();site=web.TCPSite(runner,'127.0.0.1',0);await site.start()
 base='http://127.0.0.1:'+str(site._server.sockets[0].getsockname()[1])
 sockets=[]
 try:
  async with ClientSession(cookie_jar=CookieJar(unsafe=True)) as client:
   async with client.get(base+'/guest-network',headers={'Origin':relay.origin}) as response:check('no cookie denied',response.status==403)
   async with client.get(base+'/') as response:check('index cookie issued',response.status==200 and 'codi_guest_relay' in response.cookies)
   async with client.get(base+'/guest-network',headers={'Origin':'https://other.invalid'}) as response:check('foreign origin denied',response.status==403)
   for path in ('guest-relay/server.py','scripts/guest-init.sh','.build/checks/guest-internet-result.json','.git/config','HANDOFF.md'):
    async with client.get(base+'/'+path) as response:check('private path denied '+path,response.status==404)
   async with client.get(base+'/config.json') as response:
    config=await response.json()
    check('same-origin relay config',config['guestNetwork']['relayPath']=='/guest-network')
    check('relay runtime revision pinned at load',config['guestNetwork']['relayRevision']==module.RELAY_REVISION==hashlib.sha256((ROOT/'guest-relay/server.py').read_bytes()).hexdigest())
    policy=config['guestNetwork']['previewPolicy'];check('bounded preview advertised',policy['tcpPorts']==[80,443] and policy['sessionBytes']==67108864 and policy['serviceBytes']==268435456 and policy['sessionSeconds']==1800 and policy['serviceCapReset']=='operator-restart')
   for i in range(4):sockets.append(await client.ws_connect(base+'/guest-network',origin=relay.origin))
   check('four real QEMU sessions active',relay.active==4)
   async def resolve_gateway(ws,mac):
    frame=bytes([255])*6+mac+arp[12:22]+mac+arp[28:]
    await ws.send_bytes(frame)
    message=await asyncio.wait_for(ws.receive(),2)
    check('isolated gateway answers '+mac.hex(),message.type==WSMsgType.BINARY and message.data[12:14]==b'\x08\x06' and message.data[20:22]==b'\0\x02' and message.data[32:38]==mac)
   await resolve_gateway(sockets[0],bytes.fromhex('022215000001'))
   try:
    await asyncio.wait_for(sockets[1].receive(),.1)
   except asyncio.TimeoutError:check('guest zero ARP reply not visible to guest one',True)
   else:check('guest zero ARP reply not visible to guest one',False)
   await resolve_gateway(sockets[1],bytes.fromhex('022215000002'))
   async with client.get(base+'/guest-network',headers={'Origin':relay.origin}) as response:check('fifth session rejected',response.status==503)
   for ws in sockets:await ws.close()
   for _ in range(100):
    if relay.active==0:break
    await asyncio.sleep(.05)
   check('all sessions cleaned after disconnect',relay.active==0)
   # Exercise production handler paths using short internal limits, not fake QEMU.
   async def closed_and_reaped(ws,label):
    message=await asyncio.wait_for(ws.receive(),3)
    check(label+' socket closed',message.type in (WSMsgType.CLOSE,WSMsgType.CLOSED,WSMsgType.ERROR))
    await ws.close()
    for _ in range(100):
     if relay.active==0:break
     await asyncio.sleep(.02)
    check(label+' session cleaned',relay.active==0)
   relay.limits=module.Limits(session_seconds=.05)
   ws=await client.ws_connect(base+'/guest-network',origin=relay.origin)
   await closed_and_reaped(ws,'idle expiry')
   relay.limits=module.Limits(packets_per_second=2)
   ws=await client.ws_connect(base+'/guest-network',origin=relay.origin)
   blocked=relay.blocked
   for _ in range(3):await ws.send_bytes(packet('10.0.7.84'))
   await closed_and_reaped(ws,'packet flood')
   check('blocked packets consume traffic quota',relay.blocked==blocked+2)
   relay.limits=module.Limits(bytes_per_second=50)
   ws=await client.ws_connect(base+'/guest-network',origin=relay.origin)
   await ws.send_bytes(packet()+bytes(20))
   await closed_and_reaped(ws,'byte flood')
   relay.limits=module.Limits()
   ws=await client.ws_connect(base+'/guest-network',origin=relay.origin)
   await ws.send_str('not Ethernet')
   await closed_and_reaped(ws,'text frame')
   ws=await client.ws_connect(base+'/guest-network',origin=relay.origin)
   await ws.send_bytes(bytes(1519))
   await closed_and_reaped(ws,'oversized frame')
   relay.limits=module.Limits(session_bytes=40)
   ws=await client.ws_connect(base+'/guest-network',origin=relay.origin);await ws.send_bytes(packet('10.0.7.84'))
   await closed_and_reaped(ws,'session data cap')
   relay.limits=module.Limits();relay.shared_budget=module.SharedByteBudget(85)
   ws=await client.ws_connect(base+'/guest-network',origin=relay.origin);await ws.send_bytes(packet('10.0.7.84'))
   for _ in range(100):
    if relay.shared_budget.used==42:break
    await asyncio.sleep(.01)
   check('first session charged shared allowance',relay.shared_budget.used==42)
   await ws.close()
   for _ in range(100):
    if relay.active==0:break
    await asyncio.sleep(.01)
   ws=await client.ws_connect(base+'/guest-network',origin=relay.origin);await ws.send_bytes(packet('10.0.7.84'));await ws.send_bytes(packet('10.0.7.84'))
   await closed_and_reaped(ws,'shared service cap')
   check('sequential sessions share a non-resetting cap',relay.shared_budget.used==84 and relay.shared_budget.exhausted)
   async with client.get(base+'/guest-network',headers={'Origin':relay.origin}) as response:check('exhausted service refuses new QEMU',response.status==503 and relay.active==0)
   relay.shared_budget=module.SharedByteBudget()
   relay.starts=[__import__('time').monotonic()]*20
   async with client.get(base+'/guest-network',headers={'Origin':relay.origin}) as response:check('start limit enforced',response.status==503)
 finally:
  for ws in sockets:await ws.close()
  await runner.cleanup()
asyncio.run(run())
receipt={'status':'PASS','checks':checks,'sha256':{n:hashlib.sha256((ROOT/n).read_bytes()).hexdigest() for n in ('guest-relay/server.py','scripts/guest-relay-check.py')}}
(ROOT/'.build/checks/guest-relay-result.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps(receipt,indent=2))
