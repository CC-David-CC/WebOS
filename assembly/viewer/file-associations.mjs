/** Parent-owned default routing; individual apps validate actual file contents. */
export function accountFileApp(path, sourceApp) {
  if (/[.]narration$/i.test(path)) return 'narrator';
  if (/[.]drakonpy$/i.test(path)) return 'drakon-python';
  if (/[.]drakonjs$/i.test(path)) return 'drakon-javascript';
  if (/[.]drakonsh$/i.test(path)) return 'drakon-bash';
  if (/[.]mathcraft$/i.test(path)) return 'mathcraft';
  if (['wordcraft','pdfcraft','gridcraft','deckcraft','photocraft','vectorcraft','figcraft','anicraft','lightcraft','designcraft','soundcraft','filmcraft','effectcraft','cadcraft','texturecraft','materialcraft','sketchcraft','solidcraft','pcbcraft','fieldcraft'].includes(sourceApp)) return sourceApp;
  if (/[.](docx|dotx|odt|rtf)$/i.test(path)) return 'wordcraft';
  if (/[.]pdf$/i.test(path)) return 'pdfcraft';
  if (/[.]xlsx$/i.test(path)) return 'gridcraft';
  if (/[.](pptx|potx|ppsx|deckcraft)$/i.test(path)) return 'deckcraft';
  if (/[.]pcraft$/i.test(path)) return 'photocraft';
  if (/[.]vectorcraft$/i.test(path)) return 'vectorcraft';
  if (/[.]figcraft$/i.test(path)) return 'figcraft';
  if (/[.]anicraft$/i.test(path)) return 'anicraft';
  if (/[.]lightcraft$/i.test(path)) return 'lightcraft';
  if (/[.]designcraft$/i.test(path)) return 'designcraft';
  if (/[.]scraftz$/i.test(path)) return 'soundcraft';
  if (/[.]fcproj$/i.test(path)) return 'filmcraft';
  if (/[.]ecproj$/i.test(path)) return 'effectcraft';
  if (/[.]dxf$/i.test(path)) return 'cadcraft';
  if (/[.]tcraft$/i.test(path)) return 'texturecraft';
  if (/[.]mcraft$/i.test(path)) return 'materialcraft';
  if (/[.](sc|solidcraft|solvecraft)$/i.test(path)) return 'solidcraft';
  if (/[.]sketchcraft$/i.test(path)) return 'sketchcraft';
  if (/[.]pc$/i.test(path)) return 'pcbcraft';
  if (/[.]fieldcraft$/i.test(path)) return 'fieldcraft';
  if (/[.](cad|jsketcher[.]json)$/i.test(path)) return 'jsketcher';
  return 'text';
}
