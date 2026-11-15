#!/usr/bin/env python3
"""Run an isolated desktop whose relay reaches only the loopback test fixture.

Never use this test-only DNS/connection override in a deployed relay.
"""
import asyncio,runpy,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'apps/system/browser'))
import relay.wisp
RealRelay=relay.wisp.Relay
class FixtureRelay(RealRelay):
    def __init__(self,**kwargs):
        async def resolve(name,port):
            if name!='download-fixture.test' or port!=80:raise ValueError('Fixture destination required')
            return ['1.1.1.1']
        async def connect(address,port):return await asyncio.open_connection('127.0.0.1',18777)
        kwargs.update(resolver=resolve,connector=connect)
        super().__init__(**kwargs)
relay.wisp.Relay=FixtureRelay
if '--isolated' not in sys.argv or '--browser-relay' not in sys.argv:
    raise SystemExit('Test fixture requires --isolated --browser-relay')
runpy.run_path(str(ROOT/'active-system/scripts/run-simplified-local.py'),run_name='__main__')
