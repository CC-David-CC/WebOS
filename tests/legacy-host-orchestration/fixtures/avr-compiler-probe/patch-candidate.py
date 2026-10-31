#!/usr/bin/env python3
"""Patch only the pinned avr-v1.0.0 research bundle; never use on unreviewed files."""
import hashlib
from pathlib import Path
import sys
root=Path(sys.argv[1]);pipeline=root/'arduino-pipeline.js';recipe=root/'dist-web/recipe.js'
expected={pipeline:'71f7e36823b8db6c6cb4c47ce0aa16cea40c57cb7fb809f45d8f9ff6ce3acd3a',recipe:'bddb4b5243339e33f1b3dc3186cded86b973a31551b50ea58ed32401a8d06108'}
for path,digest in expected.items():
 if hashlib.sha256(path.read_bytes()).hexdigest()!=digest:raise SystemExit('Unexpected candidate input: '+str(path))
def replace_once(text,old,new):
 if text.count(old)!=1:raise SystemExit('Candidate patch anchor changed')
 return text.replace(old,new)
s=pipeline.read_text();s=replace_once(s,"const want = (rel) => /\\.(h|hpp|inc|c|cpp|cc|cxx|S)$/.test(rel);","const want = (rel) => /\\.(h|hpp|inc|c|cpp|cc|cxx|S)$/.test(rel) || rel.endsWith('/new');")
s=replace_once(s,"    if (exitCode !== 0 || outputs.some((o) => !out.has(o)))", "    if (lines.some(line => /(?:^|:\\d+(?::\\d+)?:\\s*)(?:fatal )?error:|^(?:cc1plus?|as|ld):\\s*(?:fatal )?error:|internal compiler error:/i.test(line))) throw new Error(`[${label}]\\n${lines.join('\\n')}`);\n    if (exitCode !== 0 || outputs.some((o) => !out.has(o)))")
s=replace_once(s,"      sketchBase.set(sketchVfs, enc(R.preprocessIno(req.source)));", "      sketchBase.set('/sketch/input.ino', enc(req.source));\n      sketchBase.set(sketchVfs, enc(R.preprocessIno(req.source)));")
t=recipe.read_text();t=replace_once(t,"return header + '#line 1\\n' + code;", "return header + '#line 1 \\\"/sketch/input.ino\\\"\\n' + code;")
t=replace_once(t,"return header + before + protoBlock + `#line ${lineNo}\\n` + after;", "return header + '#line 1 \\\"/sketch/input.ino\\\"\\n' + before + protoBlock + `#line ${lineNo} \\\"/sketch/input.ino\\\"\\n` + after;")
pipeline.write_text(s);recipe.write_text(t);print('Patched pinned research compiler assets')
