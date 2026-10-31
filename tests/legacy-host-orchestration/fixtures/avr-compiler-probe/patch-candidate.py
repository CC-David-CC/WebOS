#!/usr/bin/env python3
"""Patch only the pinned avr-v1.0.0 research bundle; never use on unreviewed files."""
import hashlib
from pathlib import Path
import sys
root=Path(sys.argv[1]);pipeline=root/'arduino-pipeline.js';recipe=root/'dist-web/recipe.js'
expected={pipeline:'71f7e36823b8db6c6cb4c47ce0aa16cea40c57cb7fb809f45d8f9ff6ce3acd3a',recipe:'bddb4b5243339e33f1b3dc3186cded86b973a31551b50ea58ed32401a8d06108'}
tools={'avr-as.js':'25146c0d9cb5fa573ebf795f256dc8c4b94fc7bbb682716a21e92c7846d2ea48','avr-ld.js':'02762748f79a094f2780dd5bfe6a769a20a31c757ffa5b0c6aafbbbc98aa878c','ar.js':'68183fc5c15f03fbdd3530cc033e35c222370af248e1ded078ce9535e7ae31fd','objcopy.js':'10b9cba0cd0e62a6c62b5250a28e46e9ebafda74cd2096f2613bf7fb4c07f456'}
expected.update({root/'dist-web/tools'/name:digest for name,digest in tools.items()})
for path,digest in expected.items():
 if hashlib.sha256(path.read_bytes()).hexdigest()!=digest:raise SystemExit('Unexpected candidate input: '+str(path))
def replace_once(text,old,new):
 if text.count(old)!=1:raise SystemExit('Candidate patch anchor changed')
 return text.replace(old,new)
s=pipeline.read_text();s=replace_once(s,"const want = (rel) => /\\.(h|hpp|inc|c|cpp|cc|cxx|S)$/.test(rel);","const want = (rel) => /\\.(h|hpp|inc|c|cpp|cc|cxx|S)$/.test(rel) || rel.endsWith('/new');")
start=s.index("  async function runTool(factory, label, argv, inputs, outputs) {");end=s.index("\n  // Build the MEMFS base map",start)
runner=r'''  async function runTool(factory, label, argv, inputs, outputs) {
    const lines=[],out=new Map();
    const mod=await factory({noInitialRun:true,print:s=>lines.push(s),printErr:s=>lines.push(s)});
    for(const [p,b] of inputs){const i=p.lastIndexOf('/');if(i>0)mod.FS.mkdirTree(p.slice(0,i));mod.FS.writeFile(p,b);}
    for(const p of outputs){const i=p.lastIndexOf('/');if(i>0)mod.FS.mkdirTree(p.slice(0,i));}
    let exitCode;
    try{exitCode=mod.callMain([...argv]);}catch(error){throw new Error(`[${label}] failed: ${String(error?.message||error)}\n${lines.join('\n')}`);}
    if(!Number.isInteger(exitCode)||exitCode!==0)throw new Error(`[${label}] exit ${exitCode}\n${lines.join('\n')}`);
    for(const p of outputs){try{out.set(p,mod.FS.readFile(p));}catch(error){throw new Error(`[${label}] did not produce ${p}: ${String(error?.message||error)}\n${lines.join('\n')}`);}}
    return out;
  }
'''
s=s[:start]+runner+s[end:]

s=replace_once(s,"      sketchBase.set(sketchVfs, enc(R.preprocessIno(req.source)));", "      sketchBase.set('/sketch/input.ino', enc(req.source));\n      sketchBase.set(sketchVfs, enc(R.preprocessIno(req.source)));")
t=recipe.read_text();t=replace_once(t,"return header + '#line 1\\n' + code;", "return header + '#line 1 \\\"/sketch/input.ino\\\"\\n' + code;")
t=replace_once(t,"return header + before + protoBlock + `#line ${lineNo}\\n` + after;", "return header + '#line 1 \\\"/sketch/input.ino\\\"\\n' + before + protoBlock + `#line ${lineNo} \\\"/sketch/input.ino\\\"\\n` + after;")
patched_tools={}
for name in tools:
 path=root/'dist-web/tools'/name;source=path.read_text()
 if 'Module[\"callMain\"]=callMain;' in source:raise SystemExit('Unexpected existing callMain export: '+name)
 patched_tools[path]=replace_once(source,'Module[\"FS\"]=FS;','Module[\"callMain\"]=callMain;Module[\"FS\"]=FS;')
pipeline.write_text(s);recipe.write_text(t)
for path,source in patched_tools.items():path.write_text(source)
print('Patched pinned research compiler assets')
