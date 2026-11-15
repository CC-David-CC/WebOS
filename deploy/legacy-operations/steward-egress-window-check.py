#!/usr/bin/env python3
"""Fair bounded introduction egress accounting without touching the live service."""
import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from steward.server import EgressWindow,StewardServer
class Checks(unittest.TestCase):
 def setUp(self):
  self.now=0;self.s=object.__new__(StewardServer);self.s.clock=lambda:self.now;self.s.starts=[];self.s.egress=EgressWindow(4096,16*1024*1024);self.s.socket_egress={};self.a=object();self.b=object()
 def test_one_socket_does_not_exhaust_other(self):
  for _ in range(128):self.s.quota('egress',100,self.a)
  with self.assertRaises(ValueError):self.s.quota('egress',100,self.a)
  self.s.quota('egress',100,self.b);self.assertEqual(129,len(self.s.egress.entries))
  self.now=60;self.s.quota('egress',100,self.a);self.assertEqual(1,len(self.s.egress.entries));self.assertEqual(100,self.s.egress.bytes)
 def test_bytes_and_global_bound_do_not_charge_refused_traffic(self):
  with self.assertRaises(ValueError):self.s.quota('egress',1024*1024+1,self.a)
  self.assertEqual(0,self.s.egress.bytes)
  self.s.egress=EgressWindow(1,200);self.s.quota('egress',150,self.a)
  with self.assertRaises(ValueError):self.s.quota('egress',20,self.b)
  self.assertEqual(0,len(self.s.socket_egress[self.b].entries));self.assertEqual(150,self.s.egress.bytes)
 def test_global_byte_bound(self):
  self.s.egress=EgressWindow(5,200);self.s.quota('egress',150,self.a)
  with self.assertRaises(ValueError):self.s.quota('egress',51,self.b)
  self.assertEqual(150,self.s.egress.bytes)
 def test_start_burst_is_bounded_and_expires(self):
  for _ in range(512):self.s.quota('start')
  with self.assertRaises(ValueError):self.s.quota('start')
  self.assertEqual(512,len(self.s.starts))
  self.now=60;self.s.quota('start');self.assertEqual(1,len(self.s.starts))
if __name__=='__main__':unittest.main(verbosity=2)
