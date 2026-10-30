import assert from 'node:assert/strict';
import {PublicListingCache} from '../assets/desktop/public-listing-cache.mjs';
const cache=new PublicListingCache({limit:2,seconds:120});let signatures=0;const make=async()=>`signed-${++signatures}`;const p={channel:'one',genesisHash:'g',label:'alpha',description:'',now:1000};
const a=await cache.listing(p,make);assert.equal(await cache.listing({...p,now:1008},make),a);assert.equal(signatures,1);
assert.notEqual(await cache.listing({...p,label:'renamed',now:1009},make),a);const b=await cache.listing({...p,label:'renamed',now:1010},make);assert.equal(b,'signed-2');
assert.equal(await cache.listing({...p,label:'renamed',now:1129},make),'signed-3');assert.equal(await cache.listing({...p,label:'renamed',now:1000},make),'signed-4');
await cache.listing({...p,channel:'two',now:1000},make);await cache.listing({...p,channel:'three',now:1000},make);assert.equal(await cache.listing({...p,now:1000},make),'signed-7');cache.clear();assert.equal(await cache.listing({...p,now:1000},make),'signed-8');
let finish;const waiting=cache.listing({...p,channel:'pending'},()=>new Promise(resolve=>finish=resolve));cache.clear();finish('pending-wire');await waiting;assert.equal(await cache.listing({...p,channel:'pending'},make),'signed-9');
console.log(JSON.stringify({status:'PASS',checks:['reuse unchanged listing','rename signs immediately','refresh before expiry','clock rollback invalidates','bounded eviction','clear on close']}));
