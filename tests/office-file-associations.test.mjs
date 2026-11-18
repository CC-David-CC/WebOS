import test from 'node:test';
import assert from 'node:assert/strict';
import {accountFileApp} from '../assembly/viewer/file-associations.mjs';

test('Files routes supported account formats and preserves Text/WordCraft defaults',()=>{
  for(const [app,extensions] of Object.entries({text:['txt','py'],wordcraft:['docx','dotx','odt','rtf'],pdfcraft:['pdf'],gridcraft:['xlsx'],deckcraft:['pptx','potx','ppsx','deckcraft'],photocraft:['pcraft']})) {
    for(const extension of extensions)assert.equal(accountFileApp('Documents/a.'+extension.toUpperCase(),'files'),app);
  }
  assert.equal(accountFileApp('Documents/name.xlsx.txt','files'),'text');
});
test('native Open remains in its owning app; filenames do not override an explicit native picker',()=>{
  for(const app of ['wordcraft','pdfcraft','gridcraft','deckcraft','photocraft'])assert.equal(accountFileApp('Documents/other.txt',app),app);
});
