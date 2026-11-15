const assert = require('node:assert/strict');
const crypto = require('node:crypto');
const puppeteer = require('puppeteer-core');
const origin = process.env.CODI_TEST_URL || 'http://127.0.0.1:19940/';
if (!/^http:\/\/127\.0\.0\.1:\d+\/$/.test(origin)) throw Error('loopback only');
(async () => {
  const browser = await puppeteer.connect({browserURL: process.env.CODI_TEST_CDP || 'http://127.0.0.1:19290'});
  const ctx = await browser.createBrowserContext(), a = await ctx.newPage();
  const suffix = crypto.randomBytes(5).toString('hex'), userA = 'flighta'+suffix, userB = 'flightb'+suffix;
  const pass = crypto.randomBytes(15).toString('hex'), body = 'owned signed account flight '+suffix;
  const expected = crypto.createHash('sha256').update(body).digest('hex');
  async function login(p,user,reg) {
    await p.goto(origin); await p.waitForSelector('.login-toggle'); if (reg) await p.click('.login-toggle');
    await p.type('[aria-label=Username]',user); await p.type('[aria-label=Password]',pass);
    if (reg) await p.type('[aria-label="Confirm password"]',pass);
    await p.click('.login-form button[type=submit]');
    await p.waitForFunction(name=>window.desktopLab?.session?.kind==='registered' && currentSession?.public?.name===name,{timeout:45000},user);
  }
  try {
    await login(a,userA,true);
    await a.evaluate(async () => {
      const files=(await mirrorFileContext()).files; await files.sync();
      await fetch('/gateway/__fixture_reset',{method:'POST'});
      const native=window.fetch; window.flight={received:0,aborted:0,settled:'pending'};
      window.fetch=async (input,opts={}) => {
        const response=await native(input,opts);
        if (!String(input).endsWith('/gateway/upload') || !response.ok) return response;
        window.flight.received++;
        return await new Promise((resolve,reject) => {
          window.releaseHeld=()=>resolve(response);
          const abort=()=>{window.flight.aborted++;reject(new DOMException('Cancelled','AbortError'))};
          if(opts.signal?.aborted) abort(); else opts.signal?.addEventListener('abort',abort,{once:true});
        });
      };
      window.addEventListener('beforeunload',e=>{e.preventDefault();e.returnValue='';});
    });
    const revision=await a.evaluate(async text=>{const f=(await mirrorFileContext()).files;const row=await f.write('/flight.txt',text);window.flightSync=f.sync().then(()=>window.flight.settled='success',e=>window.flight.settled=e.name);return row.version},body);
    await a.waitForFunction(()=>window.flight.received===1,{timeout:45000});
    const proof=await a.evaluate(async()=>({data:new TextDecoder().decode((await(await serverFileContext()).files.read('flight.txt')).data),counts:await(await fetch('/gateway/__fixture_counts')).json()}));
    assert.equal(proof.data,body);assert.deepEqual(proof.counts,{requests:1,commits:1});
    let dialog=false;a.once('dialog',async d=>{dialog=true;await d.dismiss()});
    await a.click('button[aria-label^="Session:"]');await a.waitForSelector('.status-popup[data-status-type="account"]');
    await a.evaluate(()=>[...document.querySelectorAll('.status-popup[data-status-type="account"] button')].find(x=>x.textContent==='Sign out').click());
    await a.waitForFunction(()=>window.flight.aborted===1,{timeout:45000});
    await a.waitForFunction(()=>window.flight.settled!=='pending',{timeout:45000});
    const b=await ctx.newPage();await login(b,userB,true);await a.evaluate(()=>window.releaseHeld());
    const old=await a.evaluate(()=>window.flight);assert(dialog,'beforeunload held old document');assert.notEqual(old.settled,'success');assert.equal(old.aborted,1);
    const bResult=await b.evaluate(async()=>{const f=(await mirrorFileContext()).files,r=(await serverFileContext()).files;return {local:await f.stat('/flight.txt').then(()=>true,()=>false),remote:await r.version('flight.txt').then(()=>200,e=>e.status)}});
    assert.deepEqual(bResult,{local:false,remote:404});
    const fresh=await ctx.newPage();await login(fresh,userA,false);
    const result=await fresh.evaluate(async()=>{const f=(await mirrorFileContext()).files;await f.sync();const local=await f.read('/flight.txt'),remote=await(await serverFileContext()).files.read('flight.txt');return {local:new TextDecoder().decode(local.data),remote:new TextDecoder().decode(remote.data),status:local.status,version:local.version,counts:await(await fetch('/gateway/__fixture_counts')).json()}});
    assert.equal(result.local,body);assert.equal(result.remote,body);assert.equal(result.status,'synced');assert.equal(result.version,revision);assert.deepEqual(result.counts,{requests:1,commits:1});
    const bOwn=await b.evaluate(async()=>{const f=(await mirrorFileContext()).files;await f.write('/b-own.txt','B own bytes');await f.sync();return new TextDecoder().decode((await(await serverFileContext()).files.read('b-own.txt')).data)});assert.equal(bOwn,'B own bytes');
    const aDenied=await fresh.evaluate(async()=>await(await serverFileContext()).files.version('b-own.txt').then(()=>200,e=>e.status));assert.equal(aDenied,404);
    console.log('PASS 830/dd8 actual sign-out, held committed response, account isolation, one-upload reconciliation',JSON.stringify({expected,revision,old,bResult,counts:result.counts}));
  } catch (e) { console.error('FAILED account-flight:',e.stack);throw e; }
  finally { await ctx.close();browser.disconnect(); }
})().catch(e=>{console.error(e.stack);process.exitCode=1});
