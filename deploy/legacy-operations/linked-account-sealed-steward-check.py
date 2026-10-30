#!/usr/bin/env python3
"""Exercise the sealed candidate steward with registered account WebRTC fixtures."""
import asyncio,importlib.util,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('linked_fixture',ROOT/'scripts/linked-account-discovery-diagnostic-check.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
old=m.rendezvous.Fixture.start_broker
async def start_exact(self):
 original=str(ROOT/'scripts/serve-steward.py');candidate=str(ROOT/'.build/releases/steward-account-features-r1/scripts/serve-steward.py');assert self.command.count(original)==1;self.command[self.command.index(original)]=candidate
 return await old(self)
m.rendezvous.Fixture.start_broker=start_exact
asyncio.run(m.run(ROOT/'.build/checks/linked-account-sealed-steward-r1-result.json',ROOT/'.build/qa/member-account-inline-r1',ROOT/'.build/shared-services/account-rendezvous-r3'))
