/* Generated public-asset cache. Auth, status and user files always use network. */
const RELEASE=__PUBLIC_CACHE_MANIFEST__;
const SCOPE=new URL(self.registration.scope),CACHE='codi-public-v1|'+SCOPE.pathname+'|'+RELEASE.id;
const CORE=['index.html','app.js','style.css','reference.js','terminal.js','desktop-apps.js','networking.js','assets/desktop/apps.mjs','assets/desktop/apps.json','assets/desktop/lifecycle.mjs','assets/desktop/device-cache.mjs'];
function asset(request){
  const url=new URL(request.url);if(url.origin!==SCOPE.origin||!url.pathname.startsWith(SCOPE.pathname))return null;
  const path=url.pathname.slice(SCOPE.pathname.length);
  if(url.search&&!(path==='network/identity.mjs'&&url.search==='?originProfile=codi-session-ice-1'))return null;
  if(!path)return request.mode==='navigate'?'index.html':null; // Transport-cookie renewal must reach the server.
  return Object.hasOwn(RELEASE.files,path)?path:null;
}
async function verified(response,path){
  if(!response.ok||response.status!==200||response.redirected)throw Error('Public asset unavailable');
  const expected=RELEASE.files[path],bytes=await response.arrayBuffer();
  if(bytes.byteLength!==expected.bytes)throw Error('Public asset size changed');
  const hash=[...new Uint8Array(await crypto.subtle.digest('SHA-256',bytes))].map(b=>b.toString(16).padStart(2,'0')).join('');
  if(hash!==expected.sha256)throw Error('Public asset hash changed');
  const headers=new Headers(response.headers);for(const name of ['set-cookie','content-encoding','content-length'])headers.delete(name);
  return new Response(bytes,{status:200,headers});
}
async function fromNetwork(path,cache){
  const response=await fetch(new URL(path,SCOPE),{credentials:'same-origin',redirect:'error',cache:'no-store'}),clean=await verified(response,path);
  try{await cache.put(new URL(path,SCOPE),clean.clone());}catch(error){if(error.name!=='QuotaExceededError')throw error;}
  return clean;
}
async function cached(path){
  const cache=await caches.open(CACHE),url=new URL(path,SCOPE),saved=await cache.match(url);
  if(saved){try{return await verified(saved,path);}catch{await cache.delete(url);}}
  return fromNetwork(path,cache);
}
async function rootEntry(request,path){
  // The domain root may become the blog again after rollback. Online entry
  // documents come from the authoritative server; only this exact desktop
  // release is cached. An offline reload still gets the verified recovery UI.
  let response;
  try{response=await fetch(request.url,{credentials:'same-origin',redirect:'follow',cache:'no-store'});}
  catch{return cached(path);}
  if(response.status>=500){try{return await cached(path);}catch{return response;}}
  let clean;
  try{clean=await verified(response.clone(),path);}catch{return response;}
  try{await (await caches.open(CACHE)).put(new URL(path,SCOPE),clean.clone());}catch{}
  return clean;
}
self.addEventListener('install',event=>event.waitUntil((async()=>{
  const cache=await caches.open(CACHE);
  // App modules, Linux binaries and speech models load only when requested.
  for(const path of CORE)await fromNetwork(path,cache);
})()));
self.addEventListener('activate',event=>event.waitUntil(self.clients.claim()));
self.addEventListener('fetch',event=>{
  if(!['GET','HEAD'].includes(event.request.method))return;
  const path=asset(event.request);if(!path)return;
  event.respondWith((async()=>{
    const response=SCOPE.pathname==='/'&&event.request.mode==='navigate'&&path==='index.html'?await rootEntry(event.request,path):await cached(path);
    return event.request.method==='HEAD'?new Response(null,{status:response.status,headers:response.headers}):response;
  })());
});
self.addEventListener('message',event=>{
  if(event.data?.type!=='cache-loaded'||!event.ports[0])return;
  event.waitUntil((async()=>{
    try{
      const urls=event.data.urls;if(!Array.isArray(urls)||urls.length>1024)throw Error('Bounded asset references required');
      const paths=new Set();for(const url of urls){if(typeof url!=='string')throw Error('Invalid asset reference');const path=asset(new Request(url));if(path)paths.add(path);}
      for(const path of paths)await cached(path);
      const cache=await caches.open(CACHE),keys=await cache.keys();let bytes=0;for(const key of keys){const path=asset(new Request(key.url));bytes+=RELEASE.files[path]?.bytes||0;}
      event.ports[0].postMessage({ok:true,items:keys.length,bytes,release:RELEASE.id});
    }catch(error){event.ports[0].postMessage({ok:false,error:error.name+': '+error.message});}
  })());
});
