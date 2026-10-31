self.window=self;self.__factories={};
const tools=[['cc1.js','createModule','cc1'],['cc1plus.js','createModule','cc1plus'],['lto1.js','createModule','lto1'],['avr-as.js','Module','avr-as'],['avr-ld.js','Module','avr-ld'],['ar.js','Module','ar'],['objcopy.js','Module','objcopy']];
for(const [file,name,key] of tools){importScripts('./dist-web/tools/'+file);const factory=self[name];self.__factories[key]=options=>factory({...options,locateFile:path=>new URL('./dist-web/tools/'+path,self.location.href).href});delete self[name]}
importScripts('./dist-web/recipe.js','./arduino-pipeline.js');
onmessage=async({data})=>{try{const result=await self.compileArduino({source:data.source,board:'uno',libraries:[]});postMessage({ok:result.ok,hex:result.hex,log:result.log})}catch(e){postMessage({ok:false,log:String(e.stack||e)})}};
