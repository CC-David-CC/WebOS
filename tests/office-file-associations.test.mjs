import test from 'node:test';
import assert from 'node:assert/strict';
import {craftProjectPath} from '../assembly/viewer/craft-account-storage.mjs';
import {accountFileApp,accountFileOpenChoices} from '../assembly/viewer/file-associations.mjs';

test('Files routes supported account formats and preserves Text/WordCraft defaults',()=>{
  for(const [app,extensions] of Object.entries({text:['txt','py'],wordcraft:['docx','dotx','odt','rtf'],pdfcraft:['pdf'],gridcraft:['xlsx'],deckcraft:['pptx','potx','ppsx','deckcraft'],photocraft:['pcraft'],vectorcraft:['vectorcraft'],figcraft:['figcraft'],anicraft:['anicraft'],lightcraft:['lightcraft'],designcraft:['designcraft'],soundcraft:['scraftz'],filmcraft:['fcproj'],effectcraft:['ecproj'],cadcraft:['dxf'],texturecraft:['tcraft'],materialcraft:['mcraft'],sketchcraft:['sketchcraft'],solidcraft:['sc','solidcraft','solvecraft'],pcbcraft:['pc'],fieldcraft:['fieldcraft']})) {
    for(const extension of extensions)assert.equal(accountFileApp('Documents/a.'+extension.toUpperCase(),'files'),app);
  }
  assert.equal(accountFileApp('Documents/name.xlsx.txt','files'),'text');
  assert.equal(accountFileApp('Documents/Take.PROWAVE','files'),'pro-wave');
  assert.equal(accountFileApp('Documents/Take.prowave.txt','files'),'text');
  for (const extension of ['GP','GPX','GP5','GP4','GP3']) {
    assert.equal(accountFileApp('Documents/Score.'+extension,'files'),'oxiguitar');
  }
  assert.equal(accountFileApp('Documents/Score.gp.txt','files'),'text');
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


test('Files opens the restored native Office formats using the legacy document marker',()=>{
  const document=new TextEncoder().encode('{"format":"codi-document/1","document":{"type":"doc"}}');
  assert.equal(accountFileApp('Project.CODISHEET','files'),'spreadsheet');
  assert.equal(accountFileApp('Analysis.CODI-DATA.JSON','files'),'data-explorer');
  assert.equal(accountFileApp('Report.codidoc','files'),'document-editor');
  assert.equal(accountFileApp('Report.DOC','files',document),'document-editor');
  assert.equal(accountFileApp('Report.doc','files',document.buffer),'document-editor');
  assert.equal(accountFileApp('Legacy Word.doc','files',new Uint8Array([208,207,17,224])),'text');
  assert.equal(accountFileApp('Report.doc','files',new TextEncoder().encode('example codi-document/1')),'text');
  assert.equal(accountFileApp('Report.doc.txt','files',document),'text');
  assert.equal(accountFileApp('table.csv','files'),'text');
  assert.equal(accountFileApp('Report.doc','wordcraft',document),'wordcraft');
});


test('Open With menus retain the PDF and CSV defaults and offer their alternate viewers',()=>{
  for (const path of ['Documents/book.PDF','Documents/grid.CSV']) {
    assert.equal(accountFileOpenChoices(path)[0].id,accountFileApp(path,'files'));
  }
  assert.deepEqual(accountFileOpenChoices('book.pdf').map(app=>app.id),['pdfcraft','pdf-viewer']);
  assert.deepEqual(accountFileOpenChoices('table.csv').map(app=>app.id),['text','spreadsheet','data-explorer']);
  assert.deepEqual(accountFileOpenChoices('book.pdf.txt'),[]);
});

test('Files opens SPICE netlists in Circuit Lab with Text Editor available',()=>{
  for(const extension of ['cir','sp','SPICE']){
    const path='Documents/divider.'+extension;
    assert.equal(accountFileApp(path,'files'),'circuit-lab');
    assert.deepEqual(accountFileOpenChoices(path).map(choice=>choice.id),['circuit-lab','text']);
  }
  assert.equal(accountFileApp('Documents/divider.cir.txt','files'),'text');
  assert.deepEqual(accountFileOpenChoices('Documents/divider.txt'),[]);
  assert.equal(accountFileApp('Documents/divider.circuit','files'),'circuitjs');
});

test('Files routes a Pico project to Pico Simulator',()=>{
  assert.equal(accountFileApp('Documents/Blink.PICO','files'),'pico-simulator');
  assert.equal(accountFileApp('Documents/Blink.pico.txt','files'),'text');
});

test('Files routes ESP32 and RISC-V lab projects without changing generic Python or JSON',()=>{
  assert.equal(accountFileApp('Documents/Blink.ESP32LAB.JSON','files'),'esp32sim');
  assert.equal(accountFileApp('Documents/Boot.riscvlab.json','files'),'riscv-rust');
  assert.equal(accountFileApp('Documents/Blink.py','files'),'text');
  assert.equal(accountFileApp('Documents/Boot.json','files'),'text');
});
test('Virtual FPGA Board is an alternate opener for supported source and pin files',()=>{
  for(const extension of ['v','cst','PCF']){
    const path='Documents/Board.'+extension;
    assert.equal(accountFileApp(path,'files'),'text');
    assert.deepEqual(accountFileOpenChoices(path).map(choice=>choice.id),['text','softfpga']);
  }
  assert.deepEqual(accountFileOpenChoices('Documents/Board.v.txt'),[]);
});
