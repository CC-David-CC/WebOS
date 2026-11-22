import test from 'node:test';
import assert from 'node:assert/strict';
import {craftProjectPath} from '../assembly/viewer/craft-account-storage.mjs';
import {accountFileApp} from '../assembly/viewer/file-associations.mjs';

test('Files routes supported account formats and preserves Text/WordCraft defaults',()=>{
  for(const [app,extensions] of Object.entries({text:['txt','py','png.txt','drawio.txt'],'image-editor':['png','jpg','jpeg','webp'],'svg-editor':['svg'],excalidraw:['excalidraw'],'diagrams-net':['drawio'],'audio-editor':['mp3','wav','amss','m4a','ogg','opus','webm','flac'],wordcraft:['docx','dotx','odt','rtf'],pdfcraft:['pdf'],gridcraft:['xlsx'],deckcraft:['pptx','potx','ppsx','deckcraft'],photocraft:['pcraft'],vectorcraft:['vectorcraft'],figcraft:['figcraft'],anicraft:['anicraft'],lightcraft:['lightcraft'],designcraft:['designcraft'],soundcraft:['scraftz'],filmcraft:['fcproj'],effectcraft:['ecproj'],cadcraft:['dxf'],texturecraft:['tcraft'],materialcraft:['mcraft'],sketchcraft:['sketchcraft'],solidcraft:['sc','solidcraft','solvecraft'],pcbcraft:['pc'],fieldcraft:['fieldcraft']})) {
    for(const extension of extensions)assert.equal(accountFileApp('Documents/a.'+extension.toUpperCase(),'files'),app);
  }
  assert.equal(accountFileApp('Documents/Marietta, early light.mp3.txt','files'),'text');
  assert.equal(accountFileApp('Documents/name.xlsx.txt','files'),'text');
  assert.equal(accountFileApp('Documents/Part.CAD','files'),'jsketcher');
  assert.equal(accountFileApp('Documents/Legacy.JSKETCHER.JSON','files'),'jsketcher');
  assert.equal(accountFileApp('Documents/Part.cad.txt','files'),'text');
});
test('native Open remains in its owning app',()=>{
  for(const app of ['wordcraft','pdfcraft','gridcraft','deckcraft','photocraft','vectorcraft','figcraft','anicraft','lightcraft','designcraft','soundcraft','filmcraft','effectcraft','cadcraft','texturecraft','materialcraft','sketchcraft','solidcraft','pcbcraft','fieldcraft'])assert.equal(accountFileApp('Documents/other.txt',app),app);
});
test('SolidCraft accepts native and legacy account design suffixes without permitting traversal', () => {
  const legacy=['.solidcraft','.solvecraft'];
  for (const name of ['Plate.sc','Original.SOLIDCRAFT','Old.solvecraft']) {
    const path='Documents/'+name;
    assert.equal(craftProjectPath(path,'.sc',legacy),path);
  }
  assert.throws(()=>craftProjectPath('../Plate.sc','.sc',legacy));
  assert.throws(()=>craftProjectPath('Documents/Plate.sc.txt','.sc',legacy));
  assert.throws(()=>craftProjectPath('Documents/Old.solidcraft','.sc'));
});

test('learning games reopen their own native snapshots',()=>{
  for (const id of ['fraction-farm','market-math','math-path','pocket-conquest','rule-detective','tile-islands','word-weaver']) {
    assert.equal(accountFileApp('Documents/My round.'+id.toUpperCase()+'.JSON', 'files'), id);
    assert.equal(accountFileApp('Documents/My round.'+id+'.json.txt', 'files'), 'text');
  }
  assert.equal(accountFileApp('Documents/other.json','files'), 'text');
});
