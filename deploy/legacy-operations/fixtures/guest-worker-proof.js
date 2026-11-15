// Test-only feasibility probe, not a desktop integration or security boundary.
importScripts('/.build/v86/libv86.js');
let vm;
const reply=(id,ok,value)=>postMessage({type:'reply',id,ok,value});
onmessage=async({data})=>{
 try{
  if(data.type==='start'){
   const image=await (await fetch('/assets/terminal/v2/image.json')).json();
   vm=new V86({wasm_path:'/.build/v86/v86.wasm',memory_size:256*1024*1024,bios:{url:'/.build/v86/seabios.bin'},vga_bios:{url:'/.build/v86/vgabios.bin'},bzimage:{url:'/.build/v86/vmlinuz'},initrd:{url:'/'+image.path},filesystem:{},cmdline:'console=ttyS0,115200n8 rdinit=/init panic=-1 quiet loglevel=0',autostart:true,disable_keyboard:true,disable_mouse:true,disable_speaker:true});
   let buffer='',scheduled=false;
   vm.add_listener('serial0-output-byte',byte=>{buffer+=String.fromCharCode(byte);if(!scheduled){scheduled=true;setTimeout(()=>{postMessage({type:'serial',text:buffer});buffer='';scheduled=false;},5);}});
   vm.add_listener('download-error',e=>postMessage({type:'fatal',message:'Download failed: '+e.file_name}));
   vm.add_listener('emulator-ready',()=>{const root=vm.fs9p.GetInode(0);root.uid=1000;root.gid=1000;root.mode=0o40777;postMessage({type:'ready'});});
  }else if(data.type==='serial')vm.serial0_send(data.text);
  else if(data.type==='write'){await vm.create_file(data.path,new TextEncoder().encode(data.text));reply(data.id,true,null);}
  else if(data.type==='read')reply(data.id,true,new TextDecoder().decode(await vm.read_file(data.path)));
  else if(data.type==='stop'){await vm.destroy();reply(data.id,true,null);close();}
 }catch(e){if(data.id!==undefined)reply(data.id,false,String(e));else postMessage({type:'fatal',message:String(e)});}
};
