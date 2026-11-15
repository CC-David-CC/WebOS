/** Accounting/typing tests only; no physical memory or network capacity claim. */
import assert from 'node:assert/strict';
import {ResourceBudget,sessionBudget,NETWORK_LIMITS} from '../network/resource-budget.mjs';
const checks=[];
const check=(name,fn)=>{fn();checks.push(name);};
check('same session shares one budget across callers',()=>{const s={};assert.equal(sessionBudget(s),sessionBudget(s));});
check('legacy default remains bounded and desktop may select128MiB',()=>{const b=new ResourceBudget();assert.equal(b.limits().metadataBytes,NETWORK_LIMITS.metadataBytes);b.setMetadataLimit(128*1048576);assert.equal(b.limits().metadataBytes,128*1048576);assert(Object.isFrozen(b.limits()));});
check('invalid numeric or typed allowances leave prior policy intact',()=>{
 const b=new ResourceBudget();b.setMetadataLimit(128*1048576);
 for(const n of [NaN,Infinity,-Infinity,-1,0,31*1048576,1025*1048576,128*1048576+.5,'134217728',null,undefined,true,1n]){assert.throws(()=>b.setMetadataLimit(n));assert.equal(b.limits().metadataBytes,128*1048576);}
});
check('multiple metadata consumers cannot bypass the configured total',()=>{
 const s={},a=sessionBudget(s),b=sessionBudget(s),left=a.metadata(16*1048576),right=b.metadata(16*1048576);
 assert.throws(()=>b.metadata(1),/metadataBytes/);a.setMetadataLimit(128*1048576);const extra=b.metadata(16*1048576);
 assert.throws(()=>b.setMetadataLimit(32*1048576),/metadataBytes/);assert.equal(a.limits().metadataBytes,128*1048576);
 extra();extra();right();left();a.setMetadataLimit(32*1048576);assert.equal(a.snapshot().metadataBytes,0);
});
check('resizing metadata leaves other queue peer and role limits unchanged',()=>{const b=new ResourceBudget();const before=b.limits();b.setMetadataLimit(256*1048576);for(const k of Object.keys(before))if(k!=='metadataBytes')assert.equal(b.limits()[k],before[k]);});
check('closing retains in-flight charge until its real release',()=>{const b=new ResourceBudget(),release=b.metadata(100);b.close();assert.equal(b.snapshot().metadataBytes,100);assert.throws(()=>b.setMetadataLimit(128*1048576),/closed/);assert.throws(()=>b.metadata(1),/closed/);release();release();assert.equal(b.snapshot().metadataBytes,0);});
console.log(JSON.stringify({status:'PASS',scope:'Synthetic shared accounting and validation, not physical memory/scale proof',checks},null,2));
