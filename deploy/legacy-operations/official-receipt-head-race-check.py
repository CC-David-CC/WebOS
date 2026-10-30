#!/usr/bin/env python3
"""Hold one server receipt while a newer verified message arrives."""
import asyncio,importlib.util,os,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];spec=importlib.util.spec_from_file_location('fixture',ROOT/'scripts/official-idle-receipt-check.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
def exercise(origin,app_url,css_url):
 sessions=[]
 try:
  alice=m.open_browser(origin,'register','racealice');sessions.append(alice)
  bob=m.open_browser(origin,'register','racebob');sessions.append(bob)
  m.command(alice,"""const f=window.fixture;f.originalFetch=window.fetch.bind(window);f.held=false;f.release=null;window.fetch=async(input,options)=>{const u=new URL(input instanceof Request?input.url:String(input),location.href);let receipt=false;try{receipt=!!JSON.parse(options?.body||'{}').receipt;}catch{}const response=await f.originalFetch(input,options);if(receipt&&u.pathname==='/official-ingest/use'&&!f.held){f.held=true;return await new Promise(resolve=>f.release=()=>resolve(response));}return response;};return true;""")
  m.command(bob,"await window.fixture.channel.queue('chat',{text:'First race message'});return true;");m.wait_message(alice,'First race message')
  m.command(alice,"const end=performance.now()+15000;while(performance.now()<end&&!window.fixture.release)await new Promise(r=>setTimeout(r,50));if(!window.fixture.release)throw Error('First receipt was not held');return true;")
  m.command(bob,"await window.fixture.channel.queue('chat',{text:'Second race message'});return true;");m.wait_message(alice,'Second race message')
  started=time.monotonic();m.command(alice,"window.fixture.release();return true;");m.wait_message(bob,'Second race message',True,timeout=12000);elapsed=round((time.monotonic()-started)*1000)
  assert elapsed<12000;print('PASS newer verified head triggers a fresh receipt after an older one completes:',elapsed,'ms',flush=True)
 finally:
  for sid in reversed(sessions):
   try:m.command(sid,"const f=window.fixture;f.release?.();f.view.close();f.owner.close();await f.owner.idle();f.pool.close();f.storage.close();f.life.abort();return true;")
   finally:m.driver.call('/session/'+sid,method='DELETE')
m.exercise=exercise
if __name__=='__main__':asyncio.run(m.main())
