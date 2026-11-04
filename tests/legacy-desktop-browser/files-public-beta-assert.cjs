/* Read-only pin check before any public beta test mutates disposable data. */
const crypto=require('node:crypto');
module.exports=async function assertBeta(){
 const pins=[['/app.js?simplified=1','df957ec69e3930a741a1680c637c88e98a74bdaaa0dcd4abfc64f5ff264dc932'],['/desktop-apps.js?simplified=1','38f02da4e7df4430361296175225044b8a2f3b579ce0ef33a8acd7e56868ff84'],['/storage/browser/releases/0ea94092ebb6cd6120433c49cd4fe1284842e334b6313dc9945ed3d6cf87011a/mirror.mjs','67962be43d99bd0bb22229fc8f30c309d0637f9440e9903c2a070b6d618fa187']];
 for(const [path,pin] of pins){const r=await fetch('https://beta.ksu.codes'+path,{redirect:'error',signal:AbortSignal.timeout(12000)});if(!r.ok)throw Error('Beta candidate asset unavailable: '+path);const hash=crypto.createHash('sha256').update(Buffer.from(await r.arrayBuffer())).digest('hex');if(hash!==pin)throw Error('Beta candidate asset hash mismatch: '+path)}
 const r=await fetch('https://beta.ksu.codes/config.json',{redirect:'error',signal:AbortSignal.timeout(12000)});if(!r.ok)throw Error('Beta config unavailable');const c=await r.json();if(c.identity?.issuer!=='https://beta.ksu.codes'||c.fileStorage?.backend!=='opfs'||c.fileStorage?.databaseVersion!==2||c.fileStorage?.version!=='codi-browser-file-content/1')throw Error('Beta v2 identity/config not active');
};
