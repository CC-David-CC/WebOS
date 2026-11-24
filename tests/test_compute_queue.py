import concurrent.futures
import sys
from pathlib import Path
from tempfile import TemporaryDirectory
import threading
import time
import unittest

root=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(root/'scripts'))
from webos_compute.jobs import Jobs
from webos_storage.policy import Denied
from webos_storage.transfers import AllowanceExceeded


class QueueTest(unittest.TestCase):
    def test_concurrent_tabs_and_queued_accounts(self):
        finish=threading.Event()
        started=threading.Event()
        def render(data):
            started.set()
            self.assertTrue(finish.wait(5))
            return {'value':data}
        with TemporaryDirectory() as folder:
            jobs=Jobs(folder,render)
            try:
                def submit(_):
                    try:return jobs.submit('alice',1)['job']
                    except AllowanceExceeded:return None
                with concurrent.futures.ThreadPoolExecutor(max_workers=12) as pool:
                    accepted=list(filter(None,pool.map(submit,range(12))))
                self.assertEqual(len(accepted),1)
                self.assertTrue(started.wait(2))
                other=jobs.submit('bob',2)['job']
                with self.assertRaises(AllowanceExceeded):jobs.submit('bob',3)
                with self.assertRaises(Denied):jobs.status('alice',other)
                self.assertEqual(jobs.counts(),{'waiting':1,'running':1,'uncertain':0})
                finish.set()
                for _ in range(100):
                    if jobs.status('bob',other)['state']=='done':break
                    time.sleep(.02)
                self.assertEqual(jobs.status('bob',other)['value'],2)
                self.assertEqual(jobs.submit('alice',4)['state'],'queued')
            finally:
                finish.set(); jobs.close(); jobs.thread.join(5)
