// Isolated research adapter. This is not part of the shipped desktop.
// All guest commands are fixed here; sketch contents are written as data.
export function createV86AvrCompiler({guest,terminalSession,sendTerminal,closeTerminal,sessionExists=()=>false,valid,toolchain,core,onProgress=()=>{}}){
 if(!guest||typeof valid!=='function'||!(toolchain instanceof Uint8Array)||!toolchain.length||toolchain.length>64*1024*1024||!(core instanceof Uint8Array)||!core.length||core.length>4*1024*1024)throw Error('Invalid compiler environment.');
 const nonce=crypto.randomUUID().replaceAll('-',''),root='/codi-avr-'+nonce,absolute='/home/guest'+root,encoder=new TextEncoder();let closed=false,installed=false,installing=null,setupController=null;const jobs=new Set();
 const check=signal=>{if(closed||!valid())throw Error('Linux guest or account changed.');if(signal?.aborted)throw new DOMException('Build cancelled.','AbortError');};
 async function removeTree(path){let children;try{children=await guest.list(path)}catch(e){if(String(e.message).startsWith('File or folder not found:'))return;throw e}for(const item of children){if(item.dir)await removeTree(item.path);else await guest.request('remove',item.path)}await guest.request('remove',path);}
 async function task(dir,script,signal,timeout){
  check(signal);const scriptPath=dir+'/task.sh',statusPath=dir+'/status',absoluteScript='/home/guest'+scriptPath;await guest.write(scriptPath,encoder.encode(script));check(signal);
  let id;do{id=1000000000+crypto.getRandomValues(new Uint32Array(1))[0]%1000000000}while(sessionExists(id));
  const session=terminalSession(id),deadline=Date.now()+timeout;let stopped=false;
  const stop=()=>{if(!stopped){stopped=true;closeTerminal(id)}};signal?.addEventListener('abort',stop,{once:true});if(signal?.aborted)stop();
  try{
   sendTerminal(id,'exec /bin/sh '+absoluteScript+'\n');
   for(;;){check(signal);try{const bytes=await guest.read(statusPath),text=new TextDecoder().decode(bytes);if(!/^[01]$/.test(text))throw Error('Invalid guest result.');return text==='0';}catch(e){if(!String(e.message).startsWith('File or folder not found:'))throw e;}if(session.exited)throw Error('The Linux build process exited without a result.');if(Date.now()>deadline)throw Error('Linux build timed out.');await new Promise(resolve=>setTimeout(resolve,200));}
  }finally{signal?.removeEventListener('abort',stop);stop();}
 }
 async function setup(signal){
  check(signal);await guest.mkdir(root);await guest.mkdir(root+'/tools');await guest.mkdir(root+'/core');await guest.mkdir(root+'/install');check(signal);
  onProgress('Copying compiler to temporary Linux…');await guest.write(root+'/install/tools.tar.gz',toolchain);check(signal);await guest.write(root+'/install/core.tar.gz',core);check(signal);onProgress('Preparing compiler in temporary Linux…');
  const script=`if tar -xzf ${absolute}/install/tools.tar.gz -C ${absolute}/tools && tar -xzf ${absolute}/install/core.tar.gz -C ${absolute}/core; then result=0; else result=1; fi\nprintf %s "$result" > ${absolute}/install/status.tmp\nmv ${absolute}/install/status.tmp ${absolute}/install/status\n`;
  if(!await task(root+'/install',script,signal,180000))throw Error('Could not prepare the Linux compiler.');await removeTree(root+'/install');installed=true;onProgress('Compiler ready.');
 }
 async function install(signal){if(installed){check(signal);return}if(installing)throw Error('Compiler installation is already in progress.');check(signal);setupController=new AbortController();const forward=()=>setupController?.abort();signal?.addEventListener('abort',forward,{once:true});if(signal?.aborted)forward();installing=setup(setupController.signal);try{await installing}catch(error){if(valid())await removeTree(root).catch(()=>{});throw error}finally{signal?.removeEventListener('abort',forward);installing=null;setupController=null}}
 async function build(source,{signal}={}){
  if(typeof source!=='string'||encoder.encode(source).length>128*1024)throw Error('Sketches are limited to 128 KiB.');check(signal);if(!installed)throw Error('Prepare the compiler first.');if(jobs.size>=2)throw Error('At most two builds can run at once.');
  const controller=new AbortController(),forward=()=>controller.abort();signal?.addEventListener('abort',forward,{once:true});if(signal?.aborted)forward();const job=root+'/job-'+crypto.randomUUID().replaceAll('-',''),a='/home/guest'+job;let finish;const tracked={controller,done:new Promise(resolve=>finish=resolve)};jobs.add(tracked);
  try{
   check(controller.signal);await guest.mkdir(job);await guest.write(job+'/sketch.cpp',encoder.encode(source));check(controller.signal);onProgress('Building in temporary Linux…');
   const script=`cd ${a} || exit 1\nPATH=${absolute}/tools/usr/bin:/bin:/usr/bin; LD_LIBRARY_PATH=${absolute}/tools/libs; export PATH LD_LIBRARY_PATH\nCFLAGS='-mmcu=atmega328p -DF_CPU=16000000L -DARDUINO=10819 -DARDUINO_AVR_UNO -DARDUINO_ARCH_AVR -Os -ffunction-sections -fdata-sections -I${absolute}/core/cores/arduino -I${absolute}/core/variants/standard'\nif (avr-gcc $CFLAGS -c ${absolute}/core/cores/arduino/wiring.c -o wiring.o && avr-gcc $CFLAGS -c ${absolute}/core/cores/arduino/wiring_digital.c -o digital.o && avr-g++ $CFLAGS -fno-exceptions -c ${absolute}/core/cores/arduino/main.cpp -o main.o && avr-g++ $CFLAGS -fno-exceptions -c sketch.cpp -o sketch.o && avr-g++ -mmcu=atmega328p -Wl,--gc-sections -o sketch.elf wiring.o digital.o main.o sketch.o && avr-objcopy -O ihex -R .eeprom sketch.elf sketch.hex) > diagnostics.txt 2>&1; then result=0; else result=1; fi\nprintf %s "$result" > status.tmp\nmv status.tmp status\n`;
   const success=await task(job,script,controller.signal,120000);check(controller.signal);const info=await guest.stat(job+'/diagnostics.txt'),diagnostics=info.size>65536?'Compiler output exceeded 64 KiB.':info.size===0?'':new TextDecoder().decode(await guest.read(job+'/diagnostics.txt'));if(!success)return {ok:false,diagnostics};const file=await guest.stat(job+'/sketch.hex');if(!file.size||file.size>262144)throw Error('Compiler returned invalid firmware size.');const hex=await guest.read(job+'/sketch.hex');check(controller.signal);return {ok:true,hex,diagnostics};
  }finally{signal?.removeEventListener('abort',forward);if(valid())await removeTree(job).catch(()=>{});jobs.delete(tracked);finish();}
 }
 async function close(){if(closed)return;closed=true;setupController?.abort();for(const job of jobs)job.controller.abort();if(installing)await installing.catch(()=>{});await Promise.all([...jobs].map(job=>job.done));if(valid())await removeTree(root).catch(()=>{});}
 return {install,build,close};
}
