#!/usr/bin/env python3
"""Make an isolated research app source. Do not serve as a production release."""
import hashlib,json,shutil,sys
from pathlib import Path
original=Path(sys.argv[1]).resolve(strict=True);web=Path(sys.argv[2]).resolve(strict=True);dest=Path(sys.argv[3]).absolute()
if dest.exists():raise SystemExit('Destination must not exist')
expected={
 'compiler-inputs.data':'6db3cfdbd0aa59dcea91b2b6f59a09e53bb776c071b4d75022c34909c56663a3',
 'arduino-pipeline.js':'ea3814fbc050204c6eec9df9ce396268e010d9189bbab6ebc1bc64f74230de3a',
 'dist-web/recipe.js':'a61cd1e449db2603c94912b5a93354ee1587061a941a63418a8755c6d227ba4b',
 'dist-web/tools/cc1.js':'7056343b513a08383036f24343421dba164b9c3f276c6c756ab4e724793dffd0',
 'dist-web/tools/cc1.wasm':'6c0301f894c7c695a42a2619f745abcfcab6a19f8a4515472c92c8cb7317e3a8',
 'dist-web/tools/cc1plus.js':'2618df768c98cde7517f4f41dcaa9825180397a5c8616484653c1f1e697b1503',
 'dist-web/tools/cc1plus.wasm':'8f295e575a28c46666aa26bcee0d815def82c704880c1627ff3cbe7479d3ac0c',
 'dist-web/tools/avr-as.js':'4de0d8831bdbf6665198f06fdaaf4b36f4393aa14b9dc41feff7681d5954f502',
 'dist-web/tools/avr-ld.js':'924735b0b4283189ee282922c85a1d795308f5300a1450926bf7b27b81a0b797',
 'dist-web/tools/ar.js':'7b4e5270388539ed61b7eb3eb52becf1264f14aa90343b0d702baf201c1ece46',
 'dist-web/tools/objcopy.js':'bfcc621e33c4576635446bb426c232ae8fb2a3152f9269a594357d92221e5be5',
}
for name,digest in expected.items():
 path=web/name
 if path.is_symlink() or not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest()!=digest:raise SystemExit('Unexpected compiler input: '+str(path))
shutil.copytree(original,dest,ignore=shutil.ignore_patterns('node_modules','__pycache__'))
shutil.copytree(original/'node_modules',dest/'node_modules',copy_function=__import__('os').link)
root=Path(__file__).resolve().parent;shutil.copy2(root/'archive-worker.js',dest/'compiler-worker.js')
shutil.copy2(root/'sketch-editor.mjs',dest/'sketch-editor.mjs')
index=dest/'index.mjs';source=index.read_text()
source="import {mountSketch} from './sketch-editor.mjs';\n"+source
needle="  const note=make('p','arduino-note','Runs compiled ATmega328P firmware locally."
insert="  const sketch=mountSketch(host,hex=>{parseHex(hex);state.hex=hex;state.name='Built sketch';state.path=null;state.version=null;run()});body.append(sketch.element);\n"
if source.count(needle)!=1:raise SystemExit('Unexpected Arduino app source')
source=source.replace(needle,insert+needle).replace('Sketch compilation is not available here yet.','Sketch compilation is experimental.')
source=source.replace('dispose(){disposed=true;loadSerial++;stop();}','dispose(){sketch.dispose();disposed=true;loadSerial++;stop();}')
index.write_text(source)
with (dest/'style.css').open('a') as css:css.write('\n.arduino-sketch{display:flex;flex-direction:column;gap:8px}.arduino-sketch textarea{width:100%;min-height:200px;box-sizing:border-box;font:14px/1.5 monospace;resize:vertical}.arduino-sketch pre{max-height:180px;overflow:auto}\n')
files=list(expected)
for name in files:
 source=web/name
 if source.is_symlink() or not source.is_file():raise SystemExit('Missing or linked compiler input: '+str(source))
 out=dest/'workers'/name;out.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(source,out)
p=dest/'app.json';m=json.loads(p.read_text());m['workers']['compiler']='compiler-worker.js';m['assets']+=['workers/'+name for name in files];p.write_text(json.dumps(m,indent=2)+'\n');print('Prepared research-only app source:',dest)
