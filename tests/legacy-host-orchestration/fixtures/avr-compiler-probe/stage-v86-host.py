#!/usr/bin/env python3
"""Add a narrow shared research service only to an isolated preview."""
import shutil,sys
from pathlib import Path
project=Path(__file__).resolve().parents[3];public=Path(sys.argv[1]).resolve(strict=True)
if public.name!='public' or not public.parent.name.startswith('simplified-local-test-') or not public.is_relative_to(project/'active-system/.build'):raise SystemExit('Only an isolated local preview may be patched')
p=public/'desktop-apps.js';source=p.read_text();baseline=(project/'active-system/desktop-apps.js').read_text()
if source!=baseline:raise SystemExit('Unexpected preview host source')
service=r'''
let researchAvrRecord=null;
async function getResearchAvr({toolchainURL,coreURL,onProgress}){
 const session=currentSession,owner=signedInSubject(),vm=guestFiles.emulator;
 const valid=()=>currentSession===session&&signedInSubject()===owner&&guestFiles.emulator===vm&&guestFiles.ready&&guestState==='ready';
 if(!valid()||!terminalMuxReady)throw Error('Linux is still starting.');
 const tools=new URL(toolchainURL,location.href),core=new URL(coreURL,location.href);
 if(tools.origin!==location.origin||core.origin!==location.origin||!/^\/assets\/desktop\/apps\/arduino-simulator\/[0-9a-f]{64}\/research\/toolchain\.data$/.test(tools.pathname)||core.pathname!==tools.pathname.replace('toolchain.data','core.data')||tools.search||tools.hash||core.search||core.hash)throw Error('Invalid compiler assets.');
 if(researchAvrRecord&&(!researchAvrRecord.valid()||researchAvrRecord.manager.isClosing())){await researchAvrRecord.manager.shutdown();researchAvrRecord=null;}
 const [adapter,shared]=await Promise.all([import('./assets/desktop/v86-avr-research.mjs'),import('./assets/desktop/v86-avr-shared-research.mjs')]);if(!valid())throw Error('Linux guest or account changed.');
 if(researchAvrRecord&&researchAvrRecord.key!==tools.href)throw Error('Another compiler version is active.');
 if(!researchAvrRecord){
  let record;const loadAssets=async signal=>{async function load(url,max){const response=await fetch(url,{signal});if(!response.ok)throw Error('Compiler assets could not be loaded.');const declared=Number(response.headers.get('content-length'));if(Number.isFinite(declared)&&declared>max)throw Error('Compiler asset is too large.');const bytes=new Uint8Array(await response.arrayBuffer());if(!bytes.length||bytes.length>max)throw Error('Compiler asset is too large.');return bytes;}const [toolchain,coreBytes]=await Promise.all([load(tools.href,64*1024*1024),load(core.href,4*1024*1024)]);return {toolchain,core:coreBytes};};
  const manager=shared.createSharedV86Compiler({valid,loadAssets,create:async({toolchain,core,onProgress})=>adapter.createV86AvrCompiler({guest:guestFiles,terminalSession,sendTerminal,closeTerminal,sessionExists:id=>terminalSessions.has(id),valid,toolchain,core,onProgress}),onIdle:()=>{if(researchAvrRecord===record)researchAvrRecord=null;}});record={valid,key:tools.href,manager};researchAvrRecord=record;
 }
 return researchAvrRecord.manager.acquire(onProgress);
}
'''
needle='function publicAppHost(desktop,w,id){return {version:2,desktop,w,ui:'
replacement=service+"function publicAppHost(desktop,w,id){return {version:2,desktop,w,...(id==='arduino-simulator'?{researchAvr:getResearchAvr}:{}),ui:"
if source.count(needle)!=1:raise SystemExit('Unexpected host interface')
p.write_text(source.replace(needle,replacement,1));here=Path(__file__).resolve().parent
for source_name,target_name in [('v86-guest-compiler.mjs','v86-avr-research.mjs'),('shared-v86-compiler.mjs','v86-avr-shared-research.mjs')]:shutil.copyfile(here/source_name,public/'assets/desktop'/target_name)
print('Patched isolated preview:',public)
