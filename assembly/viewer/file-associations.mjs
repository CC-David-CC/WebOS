/** Parent-owned default routing; individual apps validate actual file contents. */
export function accountFileApp(path, sourceApp) {
  if (['wordcraft','pdfcraft','gridcraft','deckcraft','photocraft','vectorcraft','figcraft','anicraft','lightcraft','designcraft','soundcraft'].includes(sourceApp)) return sourceApp;
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
  return 'text';
}
