#!/usr/bin/env python3
"""Prepare isolated app host and MIT-licensed upstream example."""
import json,shutil,os
from pathlib import Path
HARNESS = '<!doctype html><link rel="stylesheet" href="./__BUNDLE_DIR__/index.css"><div id="root"></div><script type="module">import {mount} from \'./__BUNDLE_PATH__\';let signal=new AbortController();const store=new Map();const example=await (await fetch(\'/example.dez\')).arrayBuffer();store.set(\'/sample.dez\',{data:new Uint8Array(example),version:\'1\'});const files={async read(p){return store.get(p)},async write(p,data){let out={data,version:\'2\'};store.set(p,out);return out}};const host={w:{},signal:signal.signal,ui:{make(tag,cls,text){let e=document.createElement(tag);e.className=cls;if(text!==undefined)e.textContent=text;return e},textButton(text,cb){let b=document.createElement(\'button\');b.textContent=text;b.onclick=cb;return b},appInput(label,value){let e=document.createElement(\'input\');e.setAttribute(\'aria-label\',label);e.value=value;return e}},storage:{signedInSubject(){return \'test\'},async mirrorFileContext(){return {files,valid:()=>true,path:s=>s}},async pickFile(){return \'/sample.dez\'}}};window.test={store,app:mount(host)};document.querySelector(\'#root\').append(window.test.app.element);</script>'

root=Path(os.environ.get('CODI_TEST_BUNDLE','.build/electronics-design-source-test'))
app=json.loads((root/'apps.json').read_text())['apps'][0]
assert app['id']=='electronics-design' and app['path'].startswith('assets/desktop/')
entry=app['path'].removeprefix('assets/desktop/')
(root/'test.html').write_text(HARNESS.replace('__BUNDLE_PATH__',entry).replace('__BUNDLE_DIR__',entry.removesuffix('/index.mjs')))
shutil.copyfile('tests/fixtures/electronics-design/led-with-battery.dez',root/'example.dez')
