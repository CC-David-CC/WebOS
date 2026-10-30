#!/usr/bin/env python3
import asyncio,functools,http.server,importlib.util,json,threading,types,traceback
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];release=ROOT/'.build/releases/submission-fair-profile26-r1'
def mod(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
base=mod('package_fixture',ROOT/'scripts/composed-channel-peer-check.py');test=mod('ten_package',ROOT/'scripts/submission-fair-package-ten-check.py');server=None;thread=None;loop=None;lt=None;steward=None
try:
 server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(base.Handler,directory=str(release)));thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start();origin='http://127.0.0.1:'+str(server.server_port)
 m=types.ModuleType('steward_fixture');m.__file__=str(ROOT/'scripts/steward-network-check.py');exec((ROOT/'scripts/steward-network-check.py').read_text().split('async def main():',1)[0],m.__dict__)
 args,scope,port,root,seed=m.fixture();seed['stewards'][0]['limits']['lease_seconds']=120;args['seed']=m.jose.sign(seed,root,'codi-seed/1');args['admission_seconds']=300;args['origins'].append(origin);loop=asyncio.new_event_loop();lt=threading.Thread(target=loop.run_forever,daemon=True);lt.start();steward=m.StewardServer(**args);asyncio.run_coroutine_threadsafe(steward.start(port),loop).result(timeout=15)
 base.Handler.config=json.loads((release/'config.json').read_text());base.Handler.config['discovery']={'pin':{'realm':args['realm'],'rootKey':args['root_key'],'endpoints':[args['endpoint']],'allowLoopback':True},'seed':args['seed'],'descriptor':steward.descriptor(),'scope':scope}
 result=test.run(origin+'/',burst=True);out=ROOT/'.build/checks/submission-fair-package-ten-r1.json';assert not out.exists();out.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({'status':result['status'],'checks':result['checks'],'error':result.get('error')}));raise SystemExit(result['status']!='PASS')
finally:
 if steward and loop:
  try:asyncio.run_coroutine_threadsafe(steward.close(),loop).result(timeout=15)
  except Exception:traceback.print_exc()
 if loop:loop.call_soon_threadsafe(loop.stop)
 if lt:lt.join(timeout=10)
 if server:server.shutdown();server.server_close()
 if thread:thread.join(timeout=10)
