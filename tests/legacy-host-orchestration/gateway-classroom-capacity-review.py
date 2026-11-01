#!/usr/bin/env python3
"""Bounded 30-account signed loopback load; not a production capacity benchmark."""
import asyncio,importlib.util,time
from pathlib import Path
import os
os.chdir(Path(__file__).resolve().parents[1])
if os.environ.get('CODI_GATEWAY_RATE_ROOT'):
 import sys
 sys.path.insert(0,str(Path.cwd()/'active-system/codiserver-server-v0.3.0'))
 import codiauth.service
 sys.path.insert(0,os.environ['CODI_GATEWAY_RATE_ROOT'])
 import gateway_service.http  # Load the candidate gateway, not unrelated local WIP.
spec=importlib.util.spec_from_file_location('gateway_checks','active-system/scripts/gateway-http-check.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
async def main():
 t=m.HTTP('runTest');await t.asyncSetUp()
 try:
  started=time.monotonic();users=[]
  for i in range(30):users.append(await t.enter('class%02d'%i))
  print('registered',len(users),'elapsed',round(time.monotonic()-started,2),flush=True)
  async def trial(limit):
   await t.runner.cleanup();await t.start_gateway(max_requests_per_minute=limit)
   phase=time.monotonic()%60
   if phase>30:await asyncio.sleep(60-phase+.1)
   before=int(time.monotonic())//60;start=time.monotonic();times=[];failures=[];success=0
   async def userwork(i,session,key):
    nonlocal success
    for j in range(5):
     now=time.monotonic()
     try:
      status,body,headers=await t.rpc(session,key,'list','')
      if status!=200:raise RuntimeError('%s %s'%(status,body))
      success+=1;times.append(time.monotonic()-now)
     except Exception as e:failures.append((i,j,str(e)));break
   await asyncio.gather(*(userwork(i,*pair) for i,pair in enumerate(users)))
   elapsed=time.monotonic()-start;after=int(time.monotonic())//60
   print('limit',limit,'success',success,'failures',len(failures),'errors',failures[:3],'requests',t.gateway.requests,'same_window',before==after,'elapsed',round(elapsed,2),'p95_seconds',round(sorted(times)[int(len(times)*0.95)-1],3) if times else None,flush=True)
   return success,failures,before==after
  baseline=await trial(256);improved=await trial(2048)
  if not baseline[2] or not improved[2]:raise RuntimeError('A trial crossed a fixed-minute boundary; do not interpret it.')
  assert baseline[0]<150 and any('429' in str(e) for e in baseline[1]),baseline
  assert improved[0]==150 and not improved[1],improved
 finally:await t.asyncTearDown()
asyncio.run(main())
