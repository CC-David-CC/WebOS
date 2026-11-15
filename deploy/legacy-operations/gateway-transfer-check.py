#!/usr/bin/env python3
"""Durable shared/account allowances across crashes and aggregate pacing tests."""
import asyncio
from dataclasses import replace
import hashlib
import json
import os
from pathlib import Path
import sys
import tempfile
import time
import unittest

ROOT=Path(__file__).resolve().parent.parent;sys.path.insert(0,str(ROOT))
from gateway_service.policy import Principal
from gateway_service.user_store import UserStore
from gateway_service.transfers import initialize_transfers,Quotas,Pacer,AllowanceExceeded

class Durable(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup);self.root=Path(self.temp.name);self.t=2000000000
        for name in ['state','files']:(self.root/name).mkdir(mode=0o700)
        self.store=UserStore(self.root/'state',self.root/'files',clock=lambda:self.t);initialize_transfers(self.store)
        self.a=Principal('user:11111111-1111-4111-8111-111111111111','a','registered',{},self.t+120)
        self.b=replace(self.a,sub='user:22222222-2222-4222-8222-222222222222',sid='b')
        self.store.ensure_user(self.a);self.store.ensure_user(self.b)
    def quota(self,**kwargs):return Quotas(self.store,daily_bytes=100,shared_daily_bytes=150,bytes_per_use=80,**kwargs)
    def test_default_daily_allowances(self):
        q=Quotas(self.store)
        self.assertEqual(q.daily,50*1024**3)
        self.assertEqual(q.shared,200*1024**3)
        self.assertEqual(q.per_use,192*1024**2)
    def test_new_session_does_not_reset_account_allowance(self):
        q=self.quota();first=q.begin(self.a,60);q.finish(first)
        with self.assertRaises(AllowanceExceeded):self.quota().begin(replace(self.a,sid='new-device'),50)
    def test_global_limit_is_atomic_when_account_has_room(self):
        q=Quotas(self.store,daily_bytes=100,shared_daily_bytes=150,bytes_per_use=100);q.finish(q.begin(self.a,70));transfer=q.begin(self.b,70)
        with self.assertRaises(AllowanceExceeded):q.extend(transfer,20)
        with self.store.db() as db:
            self.assertEqual(db.execute('SELECT bytes FROM gateway_usage WHERE subject=?',(self.b.sub,)).fetchone()[0],70)
            self.assertEqual(db.execute("SELECT bytes FROM gateway_usage WHERE subject='*'").fetchone()[0],140)
    def test_process_death_does_not_free_reserved_bytes_or_active_slot(self):
        child=os.fork()
        if child==0:
            try:self.quota(concurrent_uses=1).begin(self.a,60)
            except BaseException:os._exit(74)
            os._exit(73)
        _,status=os.waitpid(child,0);self.assertEqual(os.waitstatus_to_exitcode(status),73)
        with self.assertRaises(AllowanceExceeded):self.quota(concurrent_uses=1).begin(self.a,10)
        self.t+=121;fresh=replace(self.a,deadline=self.t+120);q=self.quota(concurrent_uses=1);q.finish(q.begin(fresh,10))
        with self.assertRaises(AllowanceExceeded):q.begin(fresh,31)
    def test_day_boundary_counts_the_started_operation_consistently(self):
        self.t=(self.t//86400+1)*86400-1;principal=replace(self.a,deadline=self.t+120);day=self.t//86400
        q=self.quota();use=q.begin(principal,30);self.t+=2;q.extend(use,10);q.finish(use);q.finish(q.begin(principal,20))
        with self.store.db() as db:self.assertEqual(db.execute('SELECT day,bytes FROM gateway_usage WHERE subject=? ORDER BY day',(principal.sub,)).fetchall(),[(day,40),(day+1,20)])
    def test_shared_concurrency_persists_across_quota_instances(self):
        q=self.quota(concurrent_uses=1,shared_concurrent_uses=1);use=q.begin(self.a,10)
        with self.assertRaises(AllowanceExceeded):self.quota(concurrent_uses=1,shared_concurrent_uses=1).begin(self.b,10)
        q.finish(use);self.quota(concurrent_uses=1,shared_concurrent_uses=1).finish(self.quota(concurrent_uses=1,shared_concurrent_uses=1).begin(self.b,10))

class Pacing(unittest.IsolatedAsyncioTestCase):
    async def test_same_account_parallel_requests_share_one_rate(self):
        pacer=Pacer(per_second=5000,shared_per_second=20000,burst=1000);start=time.monotonic()
        async def transfer():
            for _ in range(5):await pacer.wait('same-account',1000,start+5)
        await asyncio.gather(transfer(),transfer());self.assertGreaterEqual(time.monotonic()-start,1.7)
    async def test_different_accounts_share_global_rate(self):
        pacer=Pacer(per_second=20000,shared_per_second=5000,burst=1000);start=time.monotonic()
        async def transfer(subject):
            for _ in range(5):await pacer.wait(subject,1000,start+5)
        await asyncio.gather(transfer('a'),transfer('b'));self.assertGreaterEqual(time.monotonic()-start,1.7)
    async def test_deadline_refuses_infinite_pacing_wait(self):
        pacer=Pacer(per_second=1,shared_per_second=1,burst=1);await pacer.wait('a',1,time.monotonic()+1)
        with self.assertRaises(TimeoutError):await pacer.wait('a',1,time.monotonic()+.01)

if __name__=='__main__':
    suite=unittest.TestSuite([unittest.defaultTestLoader.loadTestsFromTestCase(case) for case in [Durable,Pacing]])
    result=unittest.TextTestRunner(verbosity=2).run(suite)
    report={'status':'PASS' if result.wasSuccessful() else 'FAIL','tests':result.testsRun,'failures':len(result.failures),'errors':len(result.errors),
            'scope':'Real SQLite/disk and fork crash, UTC rollover, aggregate account/global wall-clock pacing; deployment/HTTP checked separately',
            'sha256':{name:hashlib.sha256((ROOT/name).read_bytes()).hexdigest() for name in ['gateway_service/transfers.py','gateway_service/user_store.py','scripts/gateway-transfer-check.py']}}
    output=ROOT/'.build/checks/gateway-transfer-result.json'
    if output.exists() and json.loads(output.read_text()).get('status')=='FAIL':output.rename(output.with_name('gateway-transfer-before-'+str(time.time_ns())+'.json'))
    output.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2));raise SystemExit(0 if result.wasSuccessful() else 1)
