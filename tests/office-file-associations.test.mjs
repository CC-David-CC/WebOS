import test from 'node:test';
import assert from 'node:assert/strict';
import {accountFileApp} from '../assembly/viewer/file-associations.mjs';

test('Files routes supported account formats and preserves Text/WordCraft defaults',()=>{
  for(const [app,extensions] of Object.entries({text:['txt','py'],wordcraft:['docx','dotx','odt','rtf'],pdfcraft:['pdf'],gridcraft:['xlsx'],deckcraft:['pptx','potx','ppsx','deckcraft'],photocraft:['pcraft'],vectorcraft:['vectorcraft'],figcraft:['figcraft'],anicraft:['anicraft'],soundcraft:['scraftz'],filmcraft:['fcproj'],effectcraft:['ecproj'],cadcraft:['dxf'],texturecraft:['tcraft']})) {
    for(const extension of extensions)assert.equal(accountFileApp('Documents/a.'+extension.toUpperCase(),'files'),app);
  }
  assert.equal(accountFileApp('Documents/name.xlsx.txt','files'),'text');
});
test('native Open remains in its owning app',()=>{
  for(const app of ['wordcraft','pdfcraft','gridcraft','deckcraft','photocraft','vectorcraft','figcraft','anicraft','soundcraft','filmcraft','effectcraft','cadcraft','texturecraft'])assert.equal(accountFileApp('Documents/other.txt',app),app);
});
