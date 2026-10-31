// Research-only v86 sketch integration. Not part of the shipped desktop.
export function mountSketch(host, acceptFirmware) {
  const {make,textButton,appInput}=host.ui;
  const owner=host.storage.signedInSubject();
  const root=make('section','arduino-sketch'),title=make('h3','','Arduino sketch'),editor=document.createElement('textarea');
  editor.setAttribute('aria-label','Arduino sketch');editor.spellcheck=false;editor.rows=12;
  const example='void setup() {\n  pinMode(13, OUTPUT);\n}\n\nvoid loop() {\n  digitalWrite(13, HIGH);\n  delay(500);\n  digitalWrite(13, LOW);\n  delay(500);\n}\n';
  const state=host.w.arduinoSketch??={source:example,baseline:example,path:null,version:null,dirty:false};editor.value=state.source;
  const path=appInput('Sketch save path',state.path||'/Blink.ino'),status=make('p','arduino-status'),warning=make('p','arduino-note'),log=document.createElement('pre'),bar=make('div','arduino-toolbar');warning.hidden=true;warning.setAttribute('role','status');
  log.setAttribute('aria-label','Build output');log.style.whiteSpace='pre-wrap';log.style.overflowWrap='anywhere';
  let compiler=null,installed=false,controller=null,active=false,disposed=false,revision=0,operation=0,saving=false,documentId=0,unwatch=()=>{},watchSerial=0,checkSerial=0;
  const valid=()=>!disposed&&!host.signal.aborted&&owner===host.storage.signedInSubject();
  const say=s=>{if(valid())status.textContent=s};
  function watch(c,p){unwatch();const serial=++watchSerial;warning.hidden=true;warning.textContent='';const check=async()=>{const version=state.version,id=++checkSerial;if(!valid()||!c.valid()||!version||state.path!==p)return;let message='';try{const f=await c.files.stat(p);if(f.status==='conflict')message='This sketch has conflicting copies. Resolve them in Files; the current sketch remains open.';else if(f.version!==version)message='The saved sketch changed. Save a copy or reopen it; the current sketch remains open.';}catch{message='The saved sketch is unavailable. The current sketch remains open.';}if(valid()&&c.valid()&&serial===watchSerial&&id===checkSerial&&state.path===p&&state.version===version){warning.textContent=message;warning.hidden=!message;}};unwatch=c.files.subscribe(check);queueMicrotask(check);}
  const cancel=()=>{operation++;controller?.abort();};
  editor.addEventListener('input',()=>{revision++;state.source=editor.value;state.dirty=state.source!==state.baseline});
  async function build(){
    if(active||!valid())return;const source=editor.value,atRevision=revision,id=++operation;
    if(new TextEncoder().encode(source).length>131072){say('Sketch is limited to 128 KiB.');return}
    active=true;controller=new AbortController();const signal=controller.signal;log.textContent='';say('Preparing the Linux compiler on this device…');
    try{
      if(!compiler){
        compiler=await host.researchAvr({toolchainURL:new URL('./research/toolchain.data',import.meta.url).href,coreURL:new URL('./research/core.data',import.meta.url).href,onProgress:text=>{if(valid()&&id===operation)say(text)}});await compiler.install(signal);installed=true;
      }
      if(!valid()||id!==operation)return;say('Building in temporary Linux…');
      const result=await compiler.build('#include <Arduino.h>\n#line 1 "sketch.ino"\n'+source,{signal});if(!valid()||id!==operation)return;
      log.textContent=String(result.diagnostics||'').slice(-65536);if(!result.ok){say('Build failed. Check the build output.');return}
      if(revision!==atRevision){say('The sketch changed during the build. Build again to run the latest version.');return}
      acceptFirmware(new TextDecoder('utf-8',{fatal:true}).decode(result.hex));say('Build complete. Running the simulated board.');
    }catch(e){if(valid()&&id===operation)say(e.name==='AbortError'?'Build canceled.':'Could not build sketch: '+e.message);if(compiler&&!installed){await compiler.close().catch(()=>{});compiler=null;}}
    finally{controller=null;active=false;if(valid()&&status.textContent==='Canceling build…')say('Build canceled.');}
  }
  async function open(){
    if(state.dirty&&!confirm('Discard unsaved sketch changes?'))return;
    cancel();const id=operation,atRevision=revision;
    try{const selected=await host.storage.pickFile({extensions:['.ino'],signal:host.signal});if(!selected||!valid()||id!==operation)return;
      const c=await host.storage.mirrorFileContext(),p=c.path(selected),f=await c.files.read(p);if(!valid()||!c.valid()||id!==operation)return;
      if(revision!==atRevision){say('Sketch changed while opening. Open again to replace it.');return}
      if(f.status==='conflict')throw Error('Resolve this file conflict in Files first.');if(f.data.byteLength>131072)throw Error('Sketch is limited to 128 KiB.');
      editor.value=new TextDecoder('utf-8',{fatal:true}).decode(f.data);revision++;documentId++;state.source=state.baseline=editor.value;state.dirty=false;state.path=p;state.version=f.version;path.value=p;watch(c,p);say('Sketch opened from My files.');
    }catch(e){say('Could not open sketch: '+e.message)}
  }
  async function save(){
    if(saving)return;saving=true;const source=editor.value,atRevision=revision,requestedPath=path.value,priorPath=state.path,priorVersion=state.version,doc=documentId;
    try{if(new TextEncoder().encode(source).length>131072)throw Error('Sketch is limited to 128 KiB.');const c=await host.storage.mirrorFileContext(),p=c.path(requestedPath);if(!/\.ino$/i.test(p))throw Error('Use an .ino filename.');let expected=null;
      try{const old=await c.files.stat(p);if(old.status==='conflict')throw Error('Resolve the file conflict in Files first.');if(p===priorPath&&priorVersion){if(old.version!==priorVersion)throw Error('The saved sketch changed. Save a copy or reopen it.')}else if(!confirm('Replace '+p+'?'))return;expected=old.version}
      catch(e){if(e.message!=='File not found.')throw e;if(p===priorPath&&priorVersion)throw Error('The saved sketch was removed. Save a copy or reopen it.')}
      if(!valid()||!c.valid())return;const result=await c.files.write(p,source,expected);if(!valid()||!c.valid())return;
      if(doc!==documentId){say(result.status==='conflict'?'Previous sketch saved locally with a conflict. Resolve it in Files: '+p:'Previous sketch saved to '+p+'; the current sketch is separate.');return;}
      state.path=p;state.version=result.version;state.baseline=source;state.dirty=state.source!==source||result.status==='conflict';if(path.value===requestedPath)path.value=p;watch(c,p);say(result.status==='conflict'?'Sketch saved locally with a conflict. Resolve the copies in Files: '+p:revision===atRevision?'Sketch saved on this device to '+p+'; syncing with the server.':'An earlier sketch was saved to '+p+'. Save again for your latest changes.');
    }catch(e){say('Could not save sketch: '+e.message)}finally{saving=false}
  }
  const stop=textButton('Cancel build',()=>{cancel();say('Canceling build…');});
  bar.append(textButton('Build and run',build),stop,textButton('Open sketch',open),textButton('Save sketch',save));
  root.append(title,make('p','arduino-note','Experimental: build simple Uno sketches in temporary browser Linux. Digital pins and delay are supported; serial and additional libraries are not yet supported. This does not test physical hardware.'),warning,editor,bar,path,status,log);
  return {element:root,dispose(){disposed=true;watchSerial++;unwatch();cancel();compiler?.close().catch(()=>{})}};
}
