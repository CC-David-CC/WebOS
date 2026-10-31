#!/usr/bin/env python3
"""Add a narrow research service only to a disposable isolated preview."""
import shutil,sys
from pathlib import Path
project=Path(__file__).resolve().parents[3];public=Path(sys.argv[1]).resolve(strict=True)
if public.name!='public' or not public.parent.name.startswith('simplified-local-test-') or not public.is_relative_to(project/'active-system/.build'):raise SystemExit('Only an isolated local preview may be patched')
p=public/'desktop-apps.js';source=p.read_text();baseline=(project/'active-system/desktop-apps.js').read_text()
if source!=baseline:raise SystemExit('Unexpected preview host source')
needle='return {version:2,desktop,w,ui:'
service="""return {version:2,desktop,w,...(id==='arduino-simulator'?{researchAvr:async({toolchain,core,onProgress})=>{const session=currentSession,owner=signedInSubject(),vm=guestFiles.emulator;const valid=()=>currentSession===session&&signedInSubject()===owner&&guestFiles.emulator===vm&&guestFiles.ready&&guestState==='ready';if(!valid()||!terminalMuxReady)throw Error('Linux is still starting.');const mod=await import('./assets/desktop/v86-avr-research.mjs');if(!valid())throw Error('Linux guest or account changed.');return mod.createV86AvrCompiler({guest:guestFiles,terminalSession,sendTerminal,closeTerminal,sessionExists:id=>terminalSessions.has(id),valid,toolchain,core,onProgress});}}:{}),ui:"""
if source.count(needle)!=1:raise SystemExit('Unexpected host interface')
p.write_text(source.replace(needle,service,1));shutil.copyfile(Path(__file__).resolve().parent/'v86-guest-compiler.mjs',public/'assets/desktop/v86-avr-research.mjs');print('Patched isolated preview:',public)
