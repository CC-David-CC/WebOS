// Read actual authenticated served bytes in a fresh owned browser context.
import assert from 'node:assert/strict';
import fs from 'node:fs';
import {harness,launch,frame} from './helpers.mjs';
const worker=process.env.CODI_TEST_WORKER_PATH;
assert.match(worker||'',/^static\/sketch-solver\.[a-f0-9]+\.js$/);
const h=await harness();
try{
 const p=await h.login(true);await launch(p);const f=await frame(p);
 const result=await f.evaluate(async paths=>{
  const pins={};for(const path of paths){const response=await fetch(new URL(path,location.href),{redirect:'error'});if(!response.ok)throw Error('Pin fetch failed: '+response.status);pins[path]=[...new Uint8Array(await crypto.subtle.digest('SHA-256',await response.arrayBuffer()))].map(n=>n.toString(16).padStart(2,'0')).join('');}
  return {url:location.href,pins};
 },['static/index.bundle.js',worker,'static/project-validator.4139afa9eed975359c26.js']);
 if(process.env.CODI_EXPECT_APP_SHA)assert.equal(result.pins['static/index.bundle.js'],process.env.CODI_EXPECT_APP_SHA);
 if(process.env.CODI_PIN_RECEIPT)fs.writeFileSync(process.env.CODI_PIN_RECEIPT,JSON.stringify(result,null,2)+'\n');
 console.log('PASS authenticated actual runtime pins',JSON.stringify(result));
}finally{await h.close();}
