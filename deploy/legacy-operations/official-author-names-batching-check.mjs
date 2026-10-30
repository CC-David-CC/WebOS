import assert from 'node:assert/strict';
import {officialAuthorNames} from '../served_apps_public/shared/official-author-names.mjs';

globalThis.location=new URL('https://example.test/');
const actors=Array.from({length:64},(_,n)=>String(n).padStart(43,'A'));
let active=0,peak=0,calls=0;const sizes=[];
globalThis.fetch=async input=>{
 active++;peak=Math.max(peak,active);calls++;
 const batch=new URL(input,location.href).searchParams.get('authors').split(',');sizes.push(batch.length);
 await new Promise(resolve=>setTimeout(resolve,5));active--;
 return new Response(JSON.stringify({version:'codi-official-author-names/1',authors:{[batch[0]]:'alice'}}),{status:200});
};
const controller=new AbortController(),host={signal:controller.signal,network:{config:{identity:{mode:'server',issuer:location.origin,apiBase:'/api/v1'}}}},channel='B'.repeat(43);
let resolver;resolver=officialAuthorNames(host,()=>resolver.resolve(channel,actors));resolver.resolve(channel,actors);
const deadline=Date.now()+2000;while((calls<2||active)&&Date.now()<deadline)await new Promise(resolve=>setTimeout(resolve,5));
assert.equal(calls,2);assert.equal(peak,1);assert.deepEqual(sizes,[32,32]);assert.equal(resolver.get(channel,actors[0]),'alice');assert.equal(resolver.get(channel,actors[32]),'alice');
resolver.resolve(channel,actors);await new Promise(resolve=>setTimeout(resolve,20));assert.equal(calls,2,'missing names should be cached temporarily');resolver.close();controller.abort();
console.log('PASS 64 names use two sequential bounded requests, with temporary negative caching');
