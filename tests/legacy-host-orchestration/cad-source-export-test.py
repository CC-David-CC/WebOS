#!/usr/bin/env python3
import hashlib,importlib.util,json,pathlib,tempfile
P=pathlib.Path;p=P(__file__).resolve().parents[1]/'apps/system/jsketcher/export-source-registry.py';spec=importlib.util.spec_from_file_location('source_export',p);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
with tempfile.TemporaryDirectory() as t:
 root=P(t);source=root/'prepared';source.mkdir();static=source/'static';static.mkdir();m.FORK='f'*40;m.ENGINE='e'*40;m.JS='a'*64;payload=b'wasm sample';m.WASM=hashlib.sha256(payload).hexdigest();(static/(m.WASM[:20]+'.wasm')).write_bytes(payload)
 (source/'BUILD-RECEIPT.json').write_text(json.dumps({'forkCommit':m.FORK,'workerInterpreterCommit':m.ENGINE,'workerOcctInputs':{'main.js':m.JS,'main.wasm':m.WASM}}));(source/'notice.txt').write_text('terms');(source/'source.zip').write_bytes(b'source');(source/'SOURCE-INDEX.html').write_text('<a href="BUILD-RECEIPT.json">build</a><a href="notice.txt">notice</a><a href="source.zip">source</a>')
 out=root/'private';m.run(source,out);manifest=json.loads((out/'manifest.json').read_bytes());assert set(manifest['files'])=={'SOURCE-INDEX.html','BUILD-RECEIPT.json','notice.txt','source.zip'}
 try:m.run(source,out)
 except ValueError:pass
 else:raise AssertionError('existing destination accepted')
 (source/'SOURCE-INDEX.html').write_text('<a href="https://bad.test/">bad</a>')
 try:m.run(source,root/'bad')
 except ValueError:pass
 else:raise AssertionError('unsafe/incomplete source index accepted')
 assert not (root/'bad').exists()
 print('PASS exact private source inventory and refusal of incomplete/unsafe index and existing output')
