import hashlib,importlib.util,json,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('final_maps',ROOT/'apps/system/browser/tools/join_gecko_final_maps.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
class FinalMapJoin(unittest.TestCase):
 def test_direct_ambiguous_and_unmatched_symbols(self):
  with tempfile.TemporaryDirectory() as t:
   p=Path(t);wasm=p/'wasm';final=p/'final';intermediate=p/'intermediate';inv=p/'inv'
   wasm.write_bytes(b'fixture');final.write_bytes(b'  /tmp/libxul.o:(foo)\n  /tmp/libxul.o:(bar)\n  /tmp/libxul.o:(unknown)\n')
   intermediate.write_bytes(b'  libgkrust.a(crate-0123456789abcdef.x.o):(foo)\n  libgkrust.a(crate-0123456789abcdef.x.o):(bar)\n  obj.o:(bar)\n')
   inv.write_text(json.dumps({'version':'codi-gecko-rust-archive-inputs/1','crateBuilds':[{'crate':'crate','buildHash':'0123456789abcdef','package':'example'}],'otherMembers':[]}))
   keys=('WASM_SHA','FINAL_SHA','INTERMEDIATE_SHA','INVENTORY_SHA');old=[getattr(m,k) for k in keys]
   for key,path in zip(keys,(wasm,final,intermediate,inv)):setattr(m,key,hashlib.sha256(path.read_bytes()).hexdigest())
   try:
    result=m.join(wasm,final,intermediate,inv);self.assertEqual(result['matchedSymbols'],2);self.assertEqual(result['unmatchedFinalSymbols'],1);self.assertEqual(result['ambiguousSymbols'],1);self.assertEqual(result['uniquePackageSymbols'],{'example':1});self.assertEqual(result['ambiguousPackageSymbols'],{'example':1})
    final.write_bytes(final.read_bytes()+b'changed')
    with self.assertRaisesRegex(ValueError,'link map hash'):m.join(wasm,final,intermediate,inv)
   finally:
    for key,value in zip(keys,old):setattr(m,key,value)
if __name__=='__main__':unittest.main()
