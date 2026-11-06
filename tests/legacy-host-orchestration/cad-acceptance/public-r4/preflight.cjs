// Read-only public-code gate. No browser or account operation is available here.
const assert=require('node:assert/strict'),crypto=require('node:crypto');
const pins=Object.freeze({origin:'https://beta.ksu.codes/',source:'29fea20659f27f0cb212bf520b210f0311ad962f',artifact:'337b69de24aa84f726a5d3cedb8f16f7ade026baa206b4faa31281ff380d827e',bundle:'d90e75bbb67daa69ca1479ecb21165bfb0f0762dc87cf2caf7a5f2265db465ac',registry:'43a7b8cfd70ffbbaf34a5e83d785b1a0c5f61d9ba7c29a4e640f63e4d9520e41',core:'e5f603b609fe2b9948c4fa03181a706f4a9ee759',app:'d78d53333222222404fcd030d187b655a24132f750a429b0fa55cbd9b8c1b319'});
const assets=Object.freeze([['/app.js?simplified=1','e0915d882254bf03c78426eb96b2359f69994e528a80531eb595daa676f1f17f'],['/desktop-apps.js?simplified=1','966dc8f53c2968e6598cb804bfc947241dc01ea087627fa64e4d81124a006c99'],['/assets/desktop/command-registry.'+pins.registry+'.mjs',pins.registry]]);
function requiredPublicInputs(){
 assert.equal(process.env.CODI_TEST_URL,pins.origin);const cdp=new URL(process.env.CODI_TEST_CDP);assert.ok(['127.0.0.1','localhost','[::1]'].includes(cdp.hostname));assert.equal(cdp.protocol,'http:');
 assert.equal(process.env.CODI_SOURCE_PIN,pins.source);assert.equal(process.env.CODI_ARTIFACT_PIN,pins.artifact);
 assert.notEqual(process.env.NODE_TLS_REJECT_UNAUTHORIZED,'0','Ordinary trusted TLS is required');
}
async function assertPublicCandidate(){
 requiredPublicInputs();const rows=[];
 for(const [path,want] of assets){
  const r=await fetch(new URL(path,pins.origin),{redirect:'error'});assert.equal(r.status,200,'Candidate code status before browser/account creation: '+path);
  const hash=crypto.createHash('sha256');let bytes=0;for await(const chunk of r.body){bytes+=chunk.length;assert.ok(bytes<=2*1024**2);hash.update(chunk);}const actual=hash.digest('hex');
  if(actual!==want){const error=Error('R4 candidate must be active before browser connection or test-account registration: '+path);error.code='PUBLIC_CANDIDATE_NOT_ACTIVE';error.actualSHA256=actual;error.expectedSHA256=want;error.path=path;throw error;}
  rows.push({path,sha256:actual,bytes});
 }return rows;
}
let appProof=null;
async function verifyMountedCad(page){
 const src=await page.$eval('.jsketcher-frame',frame=>frame.src),url=new URL(src);
 assert.equal(url.origin,new URL(pins.origin).origin);assert.ok(url.pathname.includes('/apps/jsketcher/'+pins.bundle+'/node_modules/jsketcher-build/index-webos.html'));
 if(!appProof){
  const asset=new URL('static/index.bundle.js',url),r=await fetch(asset,{redirect:'error'});assert.equal(r.status,200);const hash=crypto.createHash('sha256');let bytes=0;
  for await(const part of r.body){bytes+=part.length;assert.ok(bytes<=64*1024**2);hash.update(part);}const actual=hash.digest('hex');assert.equal(actual,pins.app,'Exact mounted CAD runtime');
  appProof=Object.freeze({source:pins.core,path:asset.pathname,sha256:actual,bytes});
 }return {frameURL:src,...appProof};
}
async function launchPublicCad(page){
 await page.locator('.app-menu-button').click();
 for(const label of ['3D Printing','CAD Modeler (JSketcher inspired)'])await page.locator('.menu-pane button[aria-label='+JSON.stringify(label)+']').click();
}
module.exports={pins,assets,requiredPublicInputs,assertPublicCandidate,verifyMountedCad,launchPublicCad};
