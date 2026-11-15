#!/usr/bin/env python3
"""Create disposable Arduino app sources for loopback v86 compiler research."""
import hashlib,json,os,shutil,sys
from pathlib import Path
original=Path(sys.argv[1]).resolve(strict=True);toolchain=Path(sys.argv[2]).resolve(strict=True);core=Path(sys.argv[3]).resolve(strict=True);dest=Path(sys.argv[4]).absolute()
if dest.exists() or dest.is_symlink():raise SystemExit('Destination must not exist')
for p,limit in ((toolchain,64*1024*1024),(core,4*1024*1024)):
 if p.is_symlink() or not p.is_file() or not 0<p.stat().st_size<=limit:raise SystemExit('Invalid input: '+str(p))
 print(p.name,hashlib.sha256(p.read_bytes()).hexdigest(),flush=True)
shutil.copytree(original,dest,ignore=shutil.ignore_patterns('node_modules','__pycache__'))
shutil.copytree(original/'node_modules',dest/'node_modules',copy_function=os.link)
here=Path(__file__).resolve().parent;shutil.copy2(here/'sketch-v86-editor.mjs',dest/'sketch-v86-editor.mjs')
index=dest/'index.mjs';source="import {mountSketch} from './sketch-v86-editor.mjs';\n"+index.read_text()
needle="  const note=make('p','arduino-note','Runs compiled ATmega328P firmware locally."
insert="  const sketch=mountSketch(host,hex=>{parseHex(hex);loadSerial++;firmwareSerial++;state.hex=hex;state.name='Built sketch';state.path=null;state.version=null;state.sourceKey=null;sourceButton.disabled=true;path.value='/Sketch.hex';run()});body.append(sketch.element);\n"
if source.count(needle)!=1:raise SystemExit('Unexpected Arduino source')
source=source.replace(needle,insert+needle).replace('Sketch compilation is not available here yet.','Sketch compilation is experimental.')
source=source.replace('dispose(){disposed=true;loadSerial++;stop();}','dispose(){sketch.dispose();disposed=true;loadSerial++;stop();}')
index.write_text(source)
with (dest/'style.css').open('a') as css:css.write('\n.arduino-sketch{display:flex;flex-direction:column;gap:8px}.arduino-sketch textarea{width:100%;min-height:200px;box-sizing:border-box;font:14px/1.5 monospace;resize:vertical}.arduino-sketch pre{max-height:180px;overflow:auto}\n')
(dest/'research').mkdir();shutil.copyfile(toolchain,dest/'research/toolchain.data');shutil.copyfile(core,dest/'research/core.data')
p=dest/'app.json';manifest=json.loads(p.read_text());manifest['assets']+=['research/toolchain.data','research/core.data'];p.write_text(json.dumps(manifest,indent=2)+'\n');print('Prepared isolated research app:',dest)
