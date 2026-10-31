// Local research worker: no user source executes as JavaScript.
self.window=self;self.__factories={};
const root=new URL('./dist-web/',self.location.href),archive=new URL('./compiler-inputs.data',self.location.href),realFetch=self.fetch.bind(self),maxBytes=64*1024*1024;
async function initialize(){
 const response=await realFetch(archive);if(!response.ok||!response.body)throw Error('Compiler inputs unavailable.');
 const stream=response.body.pipeThrough(new DecompressionStream('gzip')),reader=stream.getReader(),chunks=[];let length=0;
 try{for(;;){const {done,value}=await reader.read();if(done)break;if((length+=value.byteLength)>maxBytes)throw Error('Compiler inputs exceed the limit.');chunks.push(value);}}finally{reader.releaseLock();}
 const bytes=new Uint8Array(length);let pos=0;for(const chunk of chunks){bytes.set(chunk,pos);pos+=chunk.length;}
 if(length<12||new TextDecoder().decode(bytes.subarray(0,8))!=='CAVRIN01')throw Error('Invalid compiler inputs.');
 const head=new DataView(bytes.buffer).getUint32(8,true);if(head>262144||head+12>length)throw Error('Invalid compiler input index.');
 const entries=JSON.parse(new TextDecoder('utf-8',{fatal:true}).decode(bytes.subarray(12,12+head)));if(!Array.isArray(entries)||entries.length>1024)throw Error('Invalid compiler input index.');
 const contents=new Map(),dataStart=12+head;let end=0;
 for(const x of entries){if(!x||typeof x.name!=='string'||!x.name||x.name.startsWith('/')||x.name.split('/').some(p=>!p||p==='.'||p==='..')||contents.has(x.name)||!Number.isSafeInteger(x.offset)||!Number.isSafeInteger(x.size)||x.offset!==end||x.size<0||dataStart+x.offset+x.size>length)throw Error('Invalid compiler input entry.');end+=x.size;contents.set(x.name,bytes.subarray(dataStart+x.offset,dataStart+end));}
 if(dataStart+end!==length)throw Error('Invalid compiler input length.');
 self.fetch=async(input,options)=>{const url=new URL(typeof input==='string'||input instanceof URL?input:input.url,self.location.href);if(url.origin!==root.origin||!url.pathname.startsWith(root.pathname))throw Error('External compiler requests are disabled.');const name=decodeURIComponent(url.pathname.slice(root.pathname.length));if(contents.has(name))return new Response(contents.get(name));if(/^tools\/(?:cc1|cc1plus)\.wasm$/.test(name))return realFetch(url,options);throw Error('Unexpected compiler asset: '+name);};
 const tools=[['cc1.js','createModule','cc1'],['cc1plus.js','createModule','cc1plus'],['avr-as.js','Module','avr-as'],['avr-ld.js','Module','avr-ld'],['ar.js','Module','ar'],['objcopy.js','Module','objcopy']];
 for(const [file,name,key] of tools){importScripts(new URL('tools/'+file,root).href);const factory=self[name];if(typeof factory!=='function')throw Error('Compiler tool could not load.');self.__factories[key]=options=>factory({...options,locateFile:path=>new URL('tools/'+path,root).href});delete self[name];}
 importScripts(new URL('recipe.js',root).href,new URL('../arduino-pipeline.js',root).href);
}
let started=false;
onmessage=async({data})=>{if(started)return;started=true;try{if(typeof data?.source!=='string'||new TextEncoder().encode(data.source).length>131072)throw Error('Sketch is limited to 128 KiB.');await initialize();const result=await self.compileArduino({source:data.source,board:'uno',libraries:[]});postMessage({ok:result.ok,hex:result.hex,log:result.log})}catch(e){postMessage({ok:false,log:String(e?.message||e)})}};
