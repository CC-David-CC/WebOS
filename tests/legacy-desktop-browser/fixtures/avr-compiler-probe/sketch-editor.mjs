// Research-only integration. The compiler candidate is not approved for distribution.
export function mountSketch(host, acceptFirmware) {
  const {make,textButton,appInput}=host.ui;
  const owner=host.storage.signedInSubject();
  const root=make('section','arduino-sketch'),title=make('h3','','Arduino sketch'),editor=document.createElement('textarea');
  editor.setAttribute('aria-label','Arduino sketch');editor.spellcheck=false;editor.rows=12;
  editor.value='void setup() {\n  pinMode(13, OUTPUT);\n}\n\nvoid loop() {\n  digitalWrite(13, HIGH);\n  delay(500);\n  digitalWrite(13, LOW);\n  delay(500);\n}\n';
  const path=appInput('Sketch save path','/Blink.ino'),status=make('p','arduino-status'),log=document.createElement('pre'),bar=make('div','arduino-toolbar');
  log.setAttribute('aria-label','Build output');log.style.whiteSpace='pre-wrap';log.style.overflowWrap='anywhere';
  let worker=null,timer=null,disposed=false,revision=0,operation=0,savedPath=null,savedVersion=null;
  const valid=()=>!disposed&&!host.signal.aborted&&owner===host.storage.signedInSubject();
  const say=s=>{if(valid())status.textContent=s};
  const cancel=()=>{operation++;clearTimeout(timer);timer=null;worker?.terminate();worker=null};
  editor.addEventListener('input',()=>revision++);
  function build(){
    cancel();const source=editor.value,atRevision=revision,id=operation;
    if(new TextEncoder().encode(source).length>131072){say('Sketch is limited to 128 KiB.');return}
    log.textContent='';say('Building on this device…');
    try{worker=new Worker(new URL('./workers/compiler.mjs',import.meta.url));
      timer=setTimeout(()=>{if(id===operation){cancel();say('Build timed out. Try a smaller sketch.')}},120000);
      worker.onmessage=({data})=>{if(!valid()||id!==operation)return;cancel();log.textContent=String(data.log||'').slice(-65536);if(!data.ok){say('Build failed. Check the build output.');return}if(revision!==atRevision){say('The sketch changed during the build. Build again to run the latest version.');return}try{acceptFirmware(data.hex);say('Build complete. Running the simulated board.')}catch(e){say('Build produced invalid firmware: '+e.message)}};
      worker.onerror=()=>{if(valid()&&id===operation){cancel();say('The compiler could not start.')}};worker.postMessage({source});
    }catch(e){cancel();say('The compiler could not start: '+e.message)}
  }
  async function open(){const id=++operation;worker?.terminate();worker=null;clearTimeout(timer);try{const selected=await host.storage.pickFile({extensions:['.ino'],signal:host.signal});if(!selected||!valid()||id!==operation)return;const c=await host.storage.mirrorFileContext(),p=c.path(selected),f=await c.files.read(p);if(!valid()||!c.valid()||id!==operation)return;if(f.status==='conflict')throw Error('Resolve this file conflict in Files first.');if(f.data.byteLength>131072)throw Error('Sketch is limited to 128 KiB.');editor.value=new TextDecoder('utf-8',{fatal:true}).decode(f.data);revision++;savedPath=p;savedVersion=f.version;path.value=p;say('Sketch opened from My files.');}catch(e){say('Could not open sketch: '+e.message)}}
  async function save(){const source=editor.value,atRevision=revision;try{if(new TextEncoder().encode(source).length>131072)throw Error('Sketch is limited to 128 KiB.');const c=await host.storage.mirrorFileContext(),p=c.path(path.value);if(!/\.ino$/i.test(p))throw Error('Use an .ino filename.');let expected=null;try{const old=await c.files.read(p);if(old.status==='conflict')throw Error('Resolve this file conflict in Files first.');if(p===savedPath&&savedVersion){if(old.version!==savedVersion)throw Error('The saved sketch changed. Save a copy or reopen it.')}else if(!confirm('Replace '+p+'?'))return;expected=old.version}catch(e){if(e.message!=='File not found.')throw e;if(p===savedPath&&savedVersion)throw Error('The saved sketch was removed. Save a copy or reopen it.')}if(!valid()||!c.valid())return;const result=await c.files.write(p,source,expected);if(!valid()||!c.valid())return;savedPath=p;savedVersion=result.version;path.value=p;say(revision===atRevision?'Sketch saved on this device; syncing with the server.':'An earlier sketch was saved. Save again for your latest changes.')}catch(e){say('Could not save sketch: '+e.message)}}
  const stop=textButton('Cancel build',()=>{cancel();say('Build canceled.');});
  bar.append(textButton('Build and run',build),stop,textButton('Open sketch',open),textButton('Save sketch',save));
  root.append(title,make('p','arduino-note','Edit the sketch, then build and run it on the simulated Uno. This does not test physical hardware.'),editor,bar,path,status,log);
  return {element:root,dispose(){disposed=true;cancel()}};
}
