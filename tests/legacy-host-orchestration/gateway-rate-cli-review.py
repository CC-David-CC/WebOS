#!/usr/bin/env python3
"""Bounded loopback test of operator-configurable shared gateway request limit."""
import asyncio,hashlib,importlib.util,json,os,socket,subprocess,sys,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
os.chdir(ROOT)
spec=importlib.util.spec_from_file_location('gateway_checks',ROOT/'active-system/scripts/gateway-http-check.py');module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
async def main():
 fixture=module.HTTP('runTest');await fixture.asyncSetUp();process=None
 try:
  root=fixture.root/'operator';root.mkdir(mode=0o700);state=root/'state';data=root/'files';state.mkdir(mode=0o700);data.mkdir(mode=0o700)
  policy=root/'issuer-policy.json';raw=json.dumps(fixture.issuer.config()['identity']).encode();policy.write_bytes(raw);policy.chmod(0o600);digest=hashlib.sha256(raw).hexdigest()
  with socket.socket() as sock:sock.bind(('127.0.0.1',0));port=sock.getsockname()[1]
  common=['--state-root',str(state),'--data-root',str(data),'--issuer-policy',str(policy),'--issuer-policy-sha256',digest,'--port',str(port)]
  script=str(Path(os.environ.get('CODI_GATEWAY_RATE_ROOT',ROOT/'active-system'))/'scripts/serve-user-files.py')
  for bad in ['0','100001']:
   result=subprocess.run([sys.executable,'-I','-B',script,'initialize',*common,'--max-requests-per-minute',bad],capture_output=True,text=True,timeout=15)
   assert result.returncode!=0 and 'Bounded request limit required' in result.stderr
  initialized=subprocess.run([sys.executable,'-I','-B',script,'initialize',*common],capture_output=True,text=True,timeout=15)
  assert initialized.returncode==0,initialized.stderr
  fixture.gateway_url='http://127.0.0.1:'+str(port)
  trials=[(script,[],{403:257}),(script,['--max-requests-per-minute','256'],{403:256,429:1}),(script,['--max-requests-per-minute','2048'],{403:257})]
  if os.environ.get('CODI_GATEWAY_BASELINE_ROOT'):trials.append((str(Path(os.environ['CODI_GATEWAY_BASELINE_ROOT'])/'scripts/serve-user-files.py'),[],{403:256,429:1}))
  for trial_script,args,expected in trials:
   phase=time.monotonic()%60
   if phase>57:await asyncio.sleep(60-phase+.1)
   before=int(time.monotonic())//60
   process=subprocess.Popen([sys.executable,'-I','-B',trial_script,'serve',*common,*args],stdout=subprocess.DEVNULL,stderr=subprocess.PIPE,text=True)
   for _ in range(100):
    if process.poll() is not None:raise RuntimeError(process.stderr.read())
    try:
     reader,writer=await asyncio.open_connection('127.0.0.1',port);writer.close();await writer.wait_closed();break
    except OSError:await asyncio.sleep(.05)
   else:raise RuntimeError('Gateway did not start')
   statuses={}
   for _ in range(257):
    status,body,_=await fixture.post('/gateway/challenge',{'invalid':True},gateway=True);statuses[status]=statuses.get(status,0)+1
   assert before==int(time.monotonic())//60,'Test crossed the fixed window boundary'
   assert statuses==expected,(args,statuses)
   process.terminate();await asyncio.to_thread(process.wait,5);process=None
  print('PASS isolated executable default 2048, explicit 256/2048, bounds and restart'+(' and baseline executable rollback' if os.environ.get('CODI_GATEWAY_BASELINE_ROOT') else ''))
 finally:
  if process:
   process.terminate()
   try:await asyncio.to_thread(process.wait,5)
   except subprocess.TimeoutExpired:process.kill();await asyncio.to_thread(process.wait)
  await fixture.asyncTearDown()
asyncio.run(main())
