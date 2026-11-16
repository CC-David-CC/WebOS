/** Disposable signed-account fixture before/after a test-backend update. */
import {createAccountsClient} from '@webos/accounts';
import {UserFiles} from '@webos/storage';
import {readFile,writeFile} from 'node:fs/promises';
import {randomBytes,createHash} from 'node:crypto';
import assert from 'node:assert/strict';
const [mode,file]=process.argv.slice(2),origin=process.env.WEBOS_VIEWER_ORIGIN;
assert(['create','verify'].includes(mode)&&file&&origin);
globalThis.location=new URL(origin+'/');
assert.equal(location.protocol,'https:','Hosted preservation probe requires real HTTPS with normal TLS verification');
// This Node probe uses the browser client over actual HTTPS/Web Crypto. Node
// has no Window secure-context property; no server verification is bypassed.
globalThis.isSecureContext=true;
const nativeFetch=globalThis.fetch;
globalThis.fetch=(input,options={})=>{const url=new URL(input,location.href);assert.equal(url.origin,location.origin);const headers=new Headers(options.headers);if(options.method==='POST')headers.set('Origin',origin);return nativeFetch(url,{...options,headers});};
const fixture=mode==='create'?{username:'preserve'+randomBytes(5).toString('hex'),password:randomBytes(12).toString('hex'),path:'Documents/viewer-preservation.txt',text:'Account file retained across the viewer/backend update.\n'}:JSON.parse(await readFile(file,'utf8'));
if(mode==='create')await writeFile(file,JSON.stringify(fixture),{flag:'wx',mode:0o600});
const accounts=createAccountsClient();await accounts.authenticate({mode:mode==='create'?'register':'signin',username:fixture.username,password:fixture.password});
try{
 const files=new UserFiles(accounts.createFileAuthority(),{workerUrl:new URL('/gateway/hash/verify-worker.mjs',origin)});
 if(mode==='create')await files.request('create',{path:fixture.path,data:Buffer.from(fixture.text).toString('base64')});
 const stored=await files.read(fixture.path);assert.equal(Buffer.from(stored.data).toString('utf8'),fixture.text);
 assert.equal(stored.sha256,createHash('sha256').update(fixture.text).digest('hex'));
 console.log(JSON.stringify({status:'PASS',mode,accountFileBytesPreserved:true}));
}finally{await accounts.logout();}
