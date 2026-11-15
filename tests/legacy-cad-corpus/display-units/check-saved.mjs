// Independent recorded evidence/native intent checks. No fresh native run.
import assert from 'node:assert/strict';import fs from 'node:fs';import path from 'node:path';
import {canonical,sha,savedModel,geometry,noWorkerDispatch,sameModel} from './oracle.mjs';
const out=process.argv[2];assert(out);const r=JSON.parse(fs.readFileSync(path.join(out,'receipt.json')));assert.equal(r.status,'PASS');
const mmBytes=fs.readFileSync(path.join(out,'default-mm.jsketcher.json')),inchBytes=fs.readFileSync(path.join(out,'saved-inch.jsketcher.json')),mm=JSON.parse(mmBytes),inch=JSON.parse(inchBytes);
savedModel(mm,r.binding,25.4,'millimeter');savedModel(inch,r.binding,25.4,'inch');assert.equal(canonical(mm.project),canonical(inch.project));
for(const [name,bytes] of [['default-mm',mmBytes],['saved-inch',inchBytes]])assert.equal(r.rows.find(x=>x.label===name+' normal native Save and server sync').sha256,sha(bytes));
const flip=r.rows.find(x=>x.label.startsWith('Normal public inch setter'));sameModel(flip.before,flip.after);noWorkerDispatch(flip.before,flip.after);geometry(flip.before.solids,25.4);geometry(flip.after.solids,25.4);
const travel=r.rows.find(x=>x.label.startsWith('Ordinary focused'));geometry(travel.undone.solids,12.7);geometry(travel.redone.solids,25.4);assert.equal(travel.undone.units.lengthUnit,'inch');assert.equal(travel.redone.units.lengthUnit,'inch');
const reopened=r.rows.find(x=>x.label.startsWith('Fresh signed')).reopened;geometry(reopened.solids,25.4);assert.equal(reopened.units.lengthUnit,'inch');assert.equal(reopened.journal.canUndo,false);assert.equal(reopened.journal.canRedo,false);
console.log(JSON.stringify({status:'PASS',scope:'Saved native intent and recorded geometry/Worker observations',defaultSha256:sha(mmBytes),inchSha256:sha(inchBytes),canonicalProjectIdentical:true,units:'canonical millimeter/radian; presentation inch',rows:r.rows.length,surfaces:r.surfaces},null,2));
