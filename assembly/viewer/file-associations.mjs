/** Parent-owned default routing; individual apps validate actual file contents. */
export function accountFileApp(path, sourceApp) {
  if (['wordcraft','pdfcraft','gridcraft','deckcraft','photocraft','vectorcraft','figcraft'].includes(sourceApp)) return sourceApp;
  if (/[.](docx|dotx|odt|rtf)$/i.test(path)) return 'wordcraft';
  if (/[.]pdf$/i.test(path)) return 'pdfcraft';
  if (/[.]xlsx$/i.test(path)) return 'gridcraft';
  if (/[.](pptx|potx|ppsx|deckcraft)$/i.test(path)) return 'deckcraft';
  if (/[.]pcraft$/i.test(path)) return 'photocraft';
  if (/[.]vectorcraft$/i.test(path)) return 'vectorcraft';
  if (/[.]figcraft$/i.test(path)) return 'figcraft';
  return 'text';
}
