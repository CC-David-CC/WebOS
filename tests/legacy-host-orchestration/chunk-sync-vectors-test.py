import hashlib,importlib.util,json,sys,tempfile,unittest
from pathlib import Path
root=Path(__file__).resolve().parents[1];sys.path.insert(0,str(root/'active-system'))
from gateway_service.chunk_sync import manifest
class Vectors(unittest.TestCase):
 def test_frozen_vectors(self):
  for v in json.loads((root/'tests/fixtures/chunk-sync/v1.json').read_text())['vectors']:
   n=v['length'];data=b''.join(hashlib.sha256(i.to_bytes(4,'big')).digest() for i in range((n+31)//32))[:n]
   with tempfile.TemporaryFile() as f:
    f.write(data);f.flush();self.assertEqual(manifest(f.fileno(),n,hashlib.sha256(data).hexdigest()),v['manifest'])
if __name__=='__main__':unittest.main()
