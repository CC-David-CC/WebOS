// Executes the genuine full production main module, not a geometry mock.
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const base=path.resolve(process.argv[2]),probe=path.resolve(process.argv[3]),pinPath=path.resolve(process.argv[4]),pins=JSON.parse(fs.readFileSync(pinPath));
const js=fs.readFileSync(path.join(base,'occ-portable.js')),wasm=fs.readFileSync(path.join(base,'main.wasm')),sha=b=>crypto.createHash('sha256').update(b).digest('hex');
if(sha(js)!==pins.jsSha256||sha(wasm)!==pins.wasmSha256)throw Error('Runtime bytes differ from pins');
const runtimePins={...pins,runnerSHA256:sha(fs.readFileSync(__filename)),probeSHA256:sha(fs.readFileSync(probe))};
const prefix='var Module={wasmBinary:require("node:fs").readFileSync(__dirname+"/main.wasm"),onRuntimeInitialized:function(){Module._InitCommands();runTest(runtimePins);}};\n';
new Function('require','__dirname','__filename','runtimePins',prefix+js.toString()+'\n'+fs.readFileSync(probe,'utf8'))(require,base,path.join(base,'occ-portable.js'),runtimePins);
