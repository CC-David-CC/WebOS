// Disposable beta-origin browser integration; requires local generated-Caddy fixture.
import assert from 'node:assert/strict';import {createRequire} from 'node:module';import {randomBytes} from 'node:crypto';
const puppeteer=createRequire(process.env.PUPPETEER_CORE_PATH)('puppeteer-core');
const browser=await puppeteer.launch({executablePath:'/snap/bin/chromium',headless:true,args:['--no-sandbox','--disable-gpu','--no-proxy-server','--ignore-certificate-errors','--host-resolver-rules=MAP beta.ksu.codes:443 127.0.0.1:18444']});
const ctx=await browser.createBrowserContext(),page=await ctx.newPage(),username='route'+randomBytes(6).toString('hex'),password='temporary-password';
try{
 const pageResponse=await page.goto('https://beta.ksu.codes/',{waitUntil:'load'});assert.equal(pageResponse.status(),200);const csp=pageResponse.headers()['content-security-policy'];assert.match(csp,/beta\.ksu\.codes/);assert.doesNotMatch(csp,/wss:\/\/ksu\.codes/);
 const network=await page.goto('https://beta.ksu.codes/guest-network');assert.equal(network.status(),503);
 const cookieResponse=await page.goto('https://beta.ksu.codes/codi-guest-cookie');const cookie=cookieResponse.headers()['set-cookie'];assert.ok(cookie&&!/;\s*domain=/i.test(cookie)&&/;\s*secure/i.test(cookie)&&/httponly/i.test(cookie)&&/samesite=strict/i.test(cookie));
 await page.goto('https://beta.ksu.codes/');
 const run=async operation=>page.evaluate(async ({username,password,operation})=>{
  const {authenticatedRequest}=await import('/network/identity.mjs'),{makeKey}=await import('/network/crypto.mjs'),{UserFiles}=await import('/gateway/client.mjs');const cfg=await(await fetch('/config.json')).json();
  const key=await makeKey(),session={privateKey:key.privateKey,public:{sid:crypto.randomUUID(),key:key.publicKey},token:null};const result=await authenticatedRequest(cfg.identity,session,cfg.identity.apiBase+'/auth',{username,password,operation});session.public=result.identity;session.token=result.session_token;const files=new UserFiles(cfg,session);
  if(operation==='register'){
   const first=await files.write('route-test.txt',new TextEncoder().encode('initial'));await files.write('route-test.txt',new TextEncoder().encode('revised'),first.sha256);let stale=null;try{await files.write('route-test.txt',new TextEncoder().encode('stale'),first.sha256)}catch(e){stale=e.status}return {issuer:cfg.identity.issuer,guestNetwork:'guestNetwork' in cfg,stale,content:new TextDecoder().decode((await files.read('route-test.txt')).data)};
  }
  return {issuer:cfg.identity.issuer,content:new TextDecoder().decode((await files.read('route-test.txt')).data)};
 },{username,password,operation});
 const first=await run('register');assert.equal(first.issuer,'https://beta.ksu.codes');assert.equal(first.guestNetwork,false);assert.equal(first.stale,409);assert.equal(first.content,'revised');await page.reload();const reopened=await run('signin');assert.equal(reopened.issuer,'https://beta.ksu.codes');assert.equal(reopened.content,'revised');console.log(JSON.stringify({status:'PASS',first,reopened,cookieHostOnly:true,guestNetworkStatus:network.status(),tls:'disposable self-signed certificate, Chromium ignore-certificate-errors'}));
}finally{await ctx.close();await browser.close()}
