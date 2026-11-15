#!/usr/bin/env python3
"""Create a mock-host browser fixture for the built Pocket Golf app."""
import json
import os
from pathlib import Path

configured=Path(os.environ.get("CODI_POCKET_GOLF_MANIFEST",".build/pocket-golf"))
root=configured.parent if configured.name=="apps.json" else configured
app=json.loads((root/"apps.json").read_text())["apps"][0]
assert app["id"]=="pocket-golf" and app["path"].startswith("assets/desktop/")
entry=app["path"].removeprefix("assets/desktop/")
html=f"""<!doctype html>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<link rel="stylesheet" href="{entry.removesuffix("index.mjs")}index.css">
<div id="root"></div>
<script type="module">
import {{mount}} from './{entry}';
const store=new Map();
let revision=0;
const files={{
  async stat(path){{const file=store.get(path);if(!file)throw Error('File not found.');return {{version:file.version,status:file.status,bytes:file.data.byteLength}}}},
  async read(path){{const file=store.get(path);if(!file)throw Error('File not found.');return {{...file}}}},
  async write(path,data,expected){{const current=store.get(path)?.version??null;if(current!==expected)throw Error('File changed');const file={{data:data instanceof Uint8Array?data:new Uint8Array(data),version:String(++revision),status:'synced'}};store.set(path,file);return {{version:file.version,status:file.status}}}},
  subscribe(){{return()=>{{}}}},
}};
const context={{owner:'test',valid:()=>true,path:value=>value.startsWith('/')?value:'/'+value,name:value=>value.split('/').pop(),files}};
const make=(tag,className='',text='')=>{{const node=document.createElement(tag);node.className=className;if(text!=='')node.textContent=text;return node}};
const controller=new AbortController();
const host={{
  w:{{title:'Pocket Golf'}},
  signal:controller.signal,
  ui:{{
    make,
    textButton(label,action){{const node=make('button');node.type='button';node.textContent=label;node.setAttribute('aria-label',label);node.addEventListener('click',action);return node}},
    appInput(label,value=''){{const node=make('input');node.setAttribute('aria-label',label);node.value=value;return node}},
    async confirm(message){{return window.confirmAnswer!==false}},
  }},
  storage:{{
    signedInSubject:()=> 'test',
    mirrorFileContext:async()=>context,
    pickFile:async()=>globalThis.target,
    pickFolder:async()=>'/',
  }},
}};
window.fileStore=store;
window.target='/Pocket Golf.game.json';
window.confirmAnswer=true;
window.makeGolf=()=>{{
  const local=new AbortController();
  const app=mount({{...host,signal:local.signal}});
  document.getElementById('root').append(app.element);
  return {{app,controller:local}};
}};
window.test={{files,store,context,host,mount:window.makeGolf}};
window.test.instance=window.makeGolf();
</script>
"""
(root/"test.html").write_text(html)
print(root/"test.html")
