/** Parent-owned default routing; individual apps validate actual file contents. */
const spiceNetlist = /[.](?:cir|sp|spice)$/i;
export const isFpgaSource = path => /[.](?:v|cst|pcf)$/i.test(path);
/** Alternatives exposed by Files. The first choice is the default opener. */
export function accountFileOpenChoices(path) {
  if (/[.]pdf$/i.test(path)) return [{id:'pdfcraft',label:'PdfCraft'},{id:'pdf-viewer',label:'PDF Viewer (PDF.js)'}];
  if (spiceNetlist.test(path)) return [{id:'circuit-lab',label:'Circuit Lab'},{id:'text',label:'Text Editor'}];
  if (isFpgaSource(path)) return [{id:'text',label:'Text Editor'},{id:'softfpga',label:'Virtual FPGA Board'}];
  if (/[.]csv$/i.test(path)) return [
    {id:'text',label:'Text Editor'},{id:'spreadsheet',label:'Spreadsheet'},{id:'data-explorer',label:'Data Explorer'}
  ];
  return [];
}

export function accountFileApp(path, sourceApp, data) {
  if(sourceApp==='files'){
    if (spiceNetlist.test(path)) return 'circuit-lab';
    if (/[.]pico$/i.test(path)) return 'pico-simulator';
    if (/[.]esp32lab[.]json$/i.test(path)) return 'esp32sim';
    if (/[.]riscvlab[.]json$/i.test(path)) return 'riscv-rust';
    if (/[.]prowave$/i.test(path)) return 'pro-wave';
    if (/[.](?:gp|gpx|gp[345])$/i.test(path)) return 'oxiguitar';
    if (/[.]codisheet$/i.test(path)) return 'spreadsheet';
    if (/[.]codi-data[.]json$/i.test(path)) return 'data-explorer';
    if (/[.]codidoc$/i.test(path)) return 'document-editor';
    if (/[.]doc$/i.test(path) && data) {
      const bytes = data instanceof ArrayBuffer
        ? new Uint8Array(data,0,Math.min(data.byteLength,256))
        : new Uint8Array(data.buffer,data.byteOffset,Math.min(data.byteLength,256));
      const prefix = new TextDecoder().decode(bytes);
      if (/^\s*\{\s*"format"\s*:\s*"codi-document\/1"\s*,/.test(prefix)) return 'document-editor';
    }
  }
  if (/[.]hdl[.]json$/i.test(path)) return 'hdl-workbench';
  if (/[.]tdraw$/i.test(path)) return 'tracedraw';
  if (/[.]scriobh$/i.test(path)) return 'scriobh';
  if (/[.]subcraft$/i.test(path)) return 'subcraft';
  if (/[.]transitz?$/i.test(path)) return 'transit';
  if (/[.]mathcraft2$/i.test(path)) return 'mathcraft2';
  if (/[.]m$/i.test(path)) return 'matcraft';
  if (/[.]qproj$/i.test(path)) return 'cuepool';
  if (/[.]clothcraft[.]json$/i.test(path)) return 'clothcraft';
  if (/[.]pdn$/i.test(path)) return 'paint-rs';
  if (/[.]stitchfoundry$/i.test(path)) return 'embroidery-studio';
  if (/[.]replicad[.]json$/i.test(path)) return 'replicad';
  if (/[.]kiri$/i.test(path)) return 'kiri-moto';
  if (/[.]meshproj$/i.test(path)) return 'mesh-tool';
  if (/[.]hex$/i.test(path)) return 'arduino-simulator';
  if (/[.]logic[.]json$/i.test(path)) return 'digital-logic';
  if (/[.]circuit$/i.test(path)) return 'circuitjs';
  if (/[.]dez$/i.test(path)) return 'electronics-design';
  if (/[.]pcnd$/i.test(path)) return 'paintcraft';
  if (/[.]notecraft$/i.test(path)) return 'notecraft';
  const game = /[.](fraction-farm|market-math|math-path|pocket-conquest|rule-detective|tile-islands|word-weaver)[.]json$/i.exec(path);
  if (game) return game[1].toLowerCase();
  if (/[.](?:ipynb|(?:light|percent)[.]py)$/i.test(path)) return 'notebook';
  if (/[.]isuccess$/i.test(path)) return 'i-success';
  if (/[.]narration$/i.test(path)) return 'narrator';
  if (/[.]drakonpy$/i.test(path)) return 'drakon-python';
  if (/[.]drakonjs$/i.test(path)) return 'drakon-javascript';
  if (/[.]drakonsh$/i.test(path)) return 'drakon-bash';
  if (/[.]mathcraft$/i.test(path)) return 'mathcraft';
  if (/[.]calc[.]json$/i.test(path)) return 'calculator';
  if (['wordcraft','pdfcraft','gridcraft','deckcraft','photocraft','vectorcraft','figcraft','anicraft','lightcraft','designcraft','soundcraft','filmcraft','effectcraft','cadcraft','texturecraft','materialcraft','sketchcraft','solidcraft','pcbcraft','fieldcraft'].includes(sourceApp)) return sourceApp;
  if (/[.](docx|dotx|odt|rtf)$/i.test(path)) return 'wordcraft';
  if (/[.](png|jpe?g|webp)$/i.test(path)) return 'image-editor';
  if (/[.]svg$/i.test(path)) return 'svg-editor';
  if (/[.]excalidraw$/i.test(path)) return 'excalidraw';
  if (/[.]drawio$/i.test(path)) return 'diagrams-net';
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
  if (/[.](amss|wav|mp3|m4a|ogg|opus|webm|flac)$/i.test(path)) return 'audio-editor';
  return 'text';
}
