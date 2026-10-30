#!/usr/bin/env python3
"""Export exact public speech code/runtime/model assets; never recordings/state."""
import argparse,hashlib,json,shutil,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
MODEL='models/onnx-community/whisper-tiny.en/'
FILES={'client.mjs','worker.mjs','provenance.json','LICENSE-transformers','LICENSE-onnxruntime','LICENSE-whisper',
 'vendor/transformers.min.js','vendor/ort-wasm-simd-threaded.jsep.mjs','vendor/ort-wasm-simd-threaded.jsep.wasm',
 *[MODEL+name for name in ['config.json','generation_config.json','preprocessor_config.json','tokenizer.json','tokenizer_config.json','special_tokens_map.json','added_tokens.json','normalizer.json','merges.txt','vocab.json','README.md','onnx/encoder_model_quantized.onnx','onnx/decoder_model_merged_quantized.onnx']]}
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def verify(folder):
 folder=Path(folder);manifest=folder/'speech.json';assert not folder.is_symlink() and not manifest.is_symlink()
 value=json.loads(manifest.read_text());assert set(value)=={'version','files'} and value['version']=='codi-speech-assets/1' and set(value['files'])==FILES
 found=set()
 for file in folder.rglob('*'):
  assert not file.is_symlink()
  if file.is_dir():continue
  assert file.is_file() and file.stat().st_nlink==1;name=str(file.relative_to(folder))
  if name=='speech.json':continue
  assert name in FILES and value['files'][name]=={'bytes':file.stat().st_size,'sha256':digest(file)};found.add(name)
 assert found==FILES
 provenance=json.loads((folder/'provenance.json').read_text());assert provenance['modelRevision']=='2575352d61be1bf7225cf8f8b268a4678025fc58' and provenance['transformersVersion']=='3.8.1'
 for name,record in provenance['modelFiles'].items():assert value['files'][MODEL+name]==record
 return {'directory':str(folder),'manifestSHA256':digest(manifest),'files':value['files']}
def export(target):
 target=Path(target).absolute();assert not target.exists() and not target.is_symlink();target.parent.mkdir(parents=True,exist_ok=True)
 stage=Path(tempfile.mkdtemp(prefix='.speech-export-',dir=target.parent))
 try:
  for name in sorted(FILES):
   source=ROOT/'assets/speech'/name;assert source.is_file() and not source.is_symlink() and all(not p.is_symlink() for p in source.parents if p.is_relative_to(ROOT))
   dest=stage/name;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(source,dest);dest.chmod(0o644)
  manifest={'version':'codi-speech-assets/1','files':{name:{'bytes':(stage/name).stat().st_size,'sha256':digest(stage/name)} for name in sorted(FILES)}}
  (stage/'speech.json').write_text(json.dumps(manifest,indent=2)+'\n')
  for file in [stage,*stage.rglob('*')]:file.chmod(0o755 if file.is_dir() else 0o644)
  verify(stage);stage.rename(target)
 finally:
  if stage.exists():shutil.rmtree(stage)
 return verify(target)
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);g=p.add_mutually_exclusive_group(required=True);g.add_argument('--output',type=Path);g.add_argument('--verify',type=Path);a=p.parse_args();print(json.dumps(verify(a.verify) if a.verify else export(a.output),indent=2))
