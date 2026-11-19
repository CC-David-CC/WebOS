import test from 'node:test';
import assert from 'node:assert/strict';
import {craftProjectPath} from '../assembly/viewer/craft-account-storage.mjs';
import {accountFileApp} from '../assembly/viewer/file-associations.mjs';

test('Files routes supported account formats and preserves Text/WordCraft defaults',()=>{
  for(const [app,extensions] of Object.entries({text:['txt','py'],wordcraft:['docx','dotx','odt','rtf'],pdfcraft:['pdf'],gridcraft:['xlsx'],deckcraft:['pptx','potx','ppsx','deckcraft'],photocraft:['pcraft'],vectorcraft:['vectorcraft'],figcraft:['figcraft'],anicraft:['anicraft'],lightcraft:['lightcraft'],designcraft:['designcraft'],soundcraft:['scraftz'],filmcraft:['fcproj'],effectcraft:['ecproj'],cadcraft:['dxf'],texturecraft:['tcraft'],materialcraft:['mcraft'],sketchcraft:['sketchcraft'],solidcraft:['sc','solidcraft','solvecraft']})) {
    for(const extension of extensions)assert.equal(accountFileApp('Documents/a.'+extension.toUpperCase(),'files'),app);
  }
  assert.equal(accountFileApp('Documents/name.xlsx.txt','files'),'text');
});
test('native Open remains in its owning app',()=>{
  for(const app of ['wordcraft','pdfcraft','gridcraft','deckcraft','photocraft','vectorcraft','figcraft','anicraft','lightcraft','designcraft','soundcraft','filmcraft','effectcraft','cadcraft','texturecraft','materialcraft','sketchcraft','solidcraft'])assert.equal(accountFileApp('Documents/other.txt',app),app);
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
