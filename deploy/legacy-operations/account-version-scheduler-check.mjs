/** Exercise the real session scheduler with a deterministic clock and network. */
import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import vm from 'node:vm';
const source=await readFile(new URL('../desktop-apps.js',import.meta.url),'utf8');
const start=source.indexOf('let accountLinksRecord;'),end=source.indexOf('async function accountLinkContext',start);
assert(start>=0&&end>start);
const timers=new Map();let sequence=0,clock=0,changed=0,failed=0,applied=0,allowed=true,status='ready';
const document={hidden:false},session={},context={session,valid:()=>true};
const desktopNetwork={appContext:()=>({accountDiscoveryStatus:()=>({status})}),accountLinksRefreshAllowed:()=>allowed,
  accountLinksStale:()=>{changed++;return true;},accountLinksRefreshFailed:()=>{failed++;},accountLinksChanged:()=>{applied++;}};
const sandbox={document,desktopNetwork,performance:{now:()=>clock},setTimeout:(f,ms)=>{const id=++sequence;timers.set(id,{f,ms});return id;},clearTimeout:id=>timers.delete(id),console};
vm.createContext(sandbox);vm.runInContext(source.slice(start,end)+'\nglobalThis.hooks={set:r=>accountLinksRecord=r,schedule:scheduleAccountVersion,probe:probeAccountVersion,retire:retireAccountLinks};',sandbox);
let mode='unchanged',checks=0,release;
const links={checkVersion:async()=>{checks++;if(mode==='error')throw Error('offline');if(mode==='held')return await new Promise(r=>release=r);return mode==='changed';},waitIdle:async()=>{},load:async()=>({}),close:()=>{}};
const record={session,task:Promise.resolve(links),versionTimer:null,versionTask:null,versionUncertain:false,refreshTimer:null,refreshTask:null,nextRefreshAt:0,changes:0};
sandbox.hooks.set(record);sandbox.hooks.schedule(record,context);
const flush=async()=>{for(let i=0;i<100;i++)await Promise.resolve();};
async function tick(){assert.equal(timers.size,1);const [id,t]=[...timers][0];assert.equal(t.ms,300000);timers.delete(id);clock+=t.ms;t.f();await flush();}
document.hidden=true;await tick();assert.equal(checks,0);
document.hidden=false;status='paused';await tick();assert.equal(checks,0);
status='ready';await tick();assert.equal(checks,1);assert.equal(changed,0);
mode='changed';await tick();assert.equal(changed,1);assert.equal(applied,1);
mode='error';await tick();assert.equal(failed,1);assert.equal(record.versionUncertain,true);
mode='unchanged';await tick();assert.equal(changed,2);assert.equal(applied,2);assert.equal(record.versionUncertain,false);
allowed=false;await tick();assert.equal(checks,4);allowed=true;
mode='held';await tick();assert.equal(checks,5);assert.equal(timers.size,0);sandbox.hooks.retire();release(true);await flush();assert.equal(changed,2);assert.equal(timers.size,0);
let probes=0,probeMode='error',releaseProbe;
context.files={supportsVersion:async()=>{probes++;if(probeMode==='error')throw Error('offline');if(probeMode==='held')return await new Promise(r=>releaseProbe=r);return probeMode==='supported';}};
const fresh=()=>({session,task:Promise.resolve(links),versionTimer:null,versionTask:null,versionUncertain:false,refreshTimer:null,refreshTask:null,nextRefreshAt:0,changes:0});
let p=fresh();sandbox.hooks.set(p);sandbox.hooks.probe(p,context);await flush();assert.equal(probes,1);assert.equal(timers.size,1);
document.hidden=true;await tick();assert.equal(probes,1);document.hidden=false;
probeMode='supported';await tick();assert.equal(probes,2);assert.equal(timers.size,1);sandbox.hooks.retire();assert.equal(timers.size,0);
p=fresh();sandbox.hooks.set(p);probeMode='unsupported';sandbox.hooks.probe(p,context);await flush();assert.equal(probes,3);assert.equal(timers.size,0);sandbox.hooks.retire();
p=fresh();sandbox.hooks.set(p);probeMode='held';sandbox.hooks.probe(p,context);await flush();assert.equal(probes,4);sandbox.hooks.retire();releaseProbe(true);await flush();assert.equal(timers.size,0);
console.log('Account version scheduler visibility, pacing, failure, recovery and cleanup passed');
