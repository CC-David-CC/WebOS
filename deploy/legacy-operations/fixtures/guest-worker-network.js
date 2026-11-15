// Test-only network bridge for the real local relay fixture.
const base=new URL('.',self.location.href);
importScripts(new URL('.build/v86/libv86.js',base));
postMessage({type:'trace',message:'worker-loaded'});
let vm;
onmessage=async({data})=>{
 try{
  if(data.type==='start'){
   postMessage({type:'trace',message:'starting'});const url=name=>new URL(name,base).href,image=await (await fetch(url('assets/terminal/v2/image.json'))).json();postMessage({type:'trace',message:'image-loaded'});
   vm=new V86({wasm_path:url('.build/v86/v86.wasm'),memory_size:256*1024*1024,bios:{url:url('.build/v86/seabios.bin')},vga_bios:{url:url('.build/v86/vgabios.bin')},bzimage:{url:url('.build/v86/vmlinuz')},initrd:{url:url(image.path)},net_device:{type:'virtio'},filesystem:{},cmdline:'console=ttyS0,115200n8 rdinit=/init panic=-1 quiet loglevel=0 guest_net=1',autostart:true,disable_keyboard:true,disable_mouse:true,disable_speaker:true});
   postMessage({type:'trace',message:'vm-created'});vm.bus.register('net0-send',frame=>{if(frame instanceof Uint8Array&&frame.length>=14&&frame.length<=1518)postMessage({type:'frame',frame});},null);
   let buffer='',scheduled=false;vm.add_listener('serial0-output-byte',byte=>{buffer+=String.fromCharCode(byte);if(!scheduled){scheduled=true;setTimeout(()=>{postMessage({type:'serial',text:buffer});buffer='';scheduled=false;},5);}});
   vm.add_listener('download-error',e=>postMessage({type:'fatal',message:'Download failed: '+e.file_name}));
   vm.add_listener('emulator-ready',()=>{const root=vm.fs9p.GetInode(0);root.uid=1000;root.gid=1000;root.mode=0o40777;postMessage({type:'ready'});});
  }else if(data.type==='serial')vm.serial0_send(data.text);
  else if(data.type==='frame'){const frame=data.frame;if(frame instanceof Uint8Array&&frame.length>=14&&frame.length<=1518)vm.bus.send('net0-receive',frame);}
  else if(data.type==='read')postMessage({type:'reply',id:data.id,value:new TextDecoder().decode(await vm.read_file(data.path))});
  else if(data.type==='stop'){await vm.destroy();postMessage({type:'reply',id:data.id,value:true});close();}
 }catch(e){postMessage({type:'fatal',message:String(e)});}
};
