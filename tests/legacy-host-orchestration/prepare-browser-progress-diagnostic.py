#!/usr/bin/env python3
"""Prepare an isolated diagnostic app; never alter the shipped Browser files."""
from pathlib import Path
import argparse,os,shutil
ROOT=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('--engine',required=True,type=Path);p.add_argument('--out',required=True,type=Path);a=p.parse_args()
src=ROOT/'apps/system/browser';out=a.out.absolute();engine=a.engine.resolve()
if out.exists() or out.is_symlink():raise SystemExit('Output must not exist')
shutil.copytree(src,out,copy_function=os.link)
for name in ('gecko.js','gecko.wasm','gecko.data','manifest.json'):
 srcfile=engine/name
 if not srcfile.is_file() or srcfile.is_symlink():raise SystemExit('Missing or unsafe engine artifact '+str(srcfile))
 temp=out/'engine'/('.diagnostic-'+name);shutil.copyfile(srcfile,temp);os.replace(temp,out/'engine'/name)
p=out/'src/engine-worker.js';s=p.read_text();needle="  event('navigation',{url:s.url.slice(0,16384),canGoBack:s.canGoBack,canGoForward:s.canGoForward});"
if s.count(needle)!=1:raise SystemExit('Worker navigation anchor changed')
s=s.replace(needle,needle+"\n  const {url,...diagnostic}=s;event('log',{message:'PROGRESS '+JSON.stringify(diagnostic),error:false});")
needle='  ready=true;scheduleTick();'
if s.count(needle)!=1:raise SystemExit('Worker startup anchor changed')
s=s.replace(needle,"  await mailbox.command({op:10,evType:0},width,height,abort.signal);\n"+needle)
temp=p.with_suffix('.diagnostic');temp.write_text(s);os.replace(temp,p)
print('Diagnostic app prepared at',out,'— use loopback fixture only')
