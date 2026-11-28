import assert from 'node:assert/strict';
import test from 'node:test';
import {suggestedProjectName} from '../assembly/viewer/binary-studio.mjs';

test('Save and Save Copy preserve the complete project suffix and the drawing format', () => {
  const garment = ['Editor', '.model.json', ['.model.json']];
  const drawing = ['DiaCraft', '.diacraft', ['.diacraft', '.vsdx', '.odg']];
  assert.equal(suggestedProjectName('Folder/Blue.model.json', ...garment, true), 'Blue copy.model.json');
  assert.equal(suggestedProjectName('Folder/Blue.model.json', ...garment, false), 'Blue.model.json');
  assert.equal(suggestedProjectName('Two.v2.ODG', ...drawing, true), 'Two.v2 copy.ODG');
  assert.equal(suggestedProjectName('Sketch.vsdx', ...drawing, false), 'Sketch.vsdx');
  assert.equal(suggestedProjectName('Imported.xml', ...drawing, false), 'Imported.diacraft');
  assert.equal(suggestedProjectName(null, ...drawing, false), 'DiaCraft.diacraft');
});
