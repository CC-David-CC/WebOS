#!/usr/bin/env python3
"""Check the server replay's write decision for publicly readable channels."""
import sys, unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from steward import official_chat_replay as replay
CHANNEL='A'*43
OTHER='B'*42+'A'
WIRE='a.b.signature'
GENESIS=replay.jose.digest(replay.jose.dumps([replay.CHANNEL_PROFILE,'signed-content','a','b']))

def policy(public_write):
 return {'profile':replay.CHANNEL_PROFILE,'type':'policy','channel':CHANNEL,'stream':'chat','validators':[CHANNEL],'publicWrite':public_write,'players':None,'publicRead':True}
def operation(actor):
 return {'kind':'chat','data':{'text':'test'},'actor':actor,'sequence':1,'previous':None,'permissionRevision':1,'operation':OTHER}
def append_result(public_write,actor):
 with patch.object(replay,'_proof',return_value=policy(public_write)),patch.object(replay,'inspect_certificate',return_value={'head':OTHER}),patch.object(replay,'inspect_author_record',return_value=operation(actor)),patch.object(replay,'apply_witness',return_value=OTHER):
  machine=replay.ExperimentalChatReplay(WIRE,channel=CHANNEL,genesis=GENESIS)
  records=[{'absence':{}}];head=machine.snapshot()['head'];block={'header':{'parent':head,'height':1,'operationsRoot':replay._digest(records),'count':1,'stateHash':'wrong'},'operations':records}
  try:machine.append([block])
  except ValueError as error:return str(error)
  raise AssertionError('Expected intentionally incorrect state hash to fail')
class ReadOnlyReplay(unittest.TestCase):
 def test_ungranted_reader_is_rejected(self):self.assertEqual(append_result(False,OTHER),'Author lacks write permission')
 def test_owner_passes_write_check(self):self.assertEqual(append_result(False,CHANNEL),'Block state differs')
 def test_public_writable_chat_retains_existing_behavior(self):self.assertEqual(append_result(True,OTHER),'Block state differs')
if __name__=='__main__':unittest.main()
