HARNESS = '<!doctype html><meta charset="utf-8"><link rel="stylesheet" href="__BUNDLE_CSS__"><div id="root"></div><script type="module">\nimport {mount} from \'./__BUNDLE_PATH__\';const store=new Map(),files={async read(p){if(!store.has(p))throw Error(\'File not found.\');return store.get(p)},async write(p,data,v){let result={data,version:String(Date.now())};store.set(p,result);return result}};files.subscribe=()=>()=>{};let abort=new AbortController();const host={w:{},signal:abort.signal,ui:{make(tag,cls,text){let el=document.createElement(tag);el.className=cls;if(text!==undefined)el.textContent=text;return el},textButton(text,cb){let b=document.createElement(\'button\');b.textContent=text;b.addEventListener(\'click\',cb);return b},appInput(label,value){let el=document.createElement(\'input\');el.setAttribute(\'aria-label\',label);el.value=value;return el}},storage:{signedInSubject(){return \'test\'},async mirrorFileContext(){return {files,valid(){return true},path(s){return s}}},async pickFile(){return \'/Circuit.logic.json\'}}};window.test={files,mount(){let m=mount(host);document.getElementById(\'root\').append(m.element);return m},store};window.test.app=window.test.mount();</script>'
#!/usr/bin/env python3
"""Create an isolated mock-host harness for the built Digital Logic app."""
import json
import os
from pathlib import Path
root=Path(os.environ.get('CODI_LOGIC_BUILD','.build/digital-logic-test'))
app=json.loads((root/'apps.json').read_text())['apps'][0]
assert app['id']=='digital-logic' and app['path'].startswith('assets/desktop/')
entry=app['path'].removeprefix('assets/desktop/')
html=HARNESS.replace('__BUNDLE_PATH__',entry).replace('__BUNDLE_CSS__',entry.removesuffix('index.mjs')+'index.css')
(root/'test.html').write_text(html)
