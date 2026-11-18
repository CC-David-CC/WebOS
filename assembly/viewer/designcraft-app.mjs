import {mountCraftAccount} from './craft-account-app.mjs';
import {createCraftRecovery} from './craft-account-recovery.mjs';

const project = {app:'designcraft', name:'DesignCraft', extension:'.designcraft'};
const recovery = createCraftRecovery(project);
const object = args => args !== null && typeof args === 'object' && !Array.isArray(args);
const empty = args => object(args) && Object.keys(args).length === 0;
const textBytes = new TextEncoder();
const artworkExtensions = ['.png','.jpg','.jpeg','.webp','.svg','.tif','.tiff','.pdf','.eps','.psd'];

const commands = Object.freeze({
  'document.inspect': empty,
  'edit.undo': empty,
  'links.relink': args => object(args) && Object.keys(args).length === 1 && Number.isSafeInteger(args.asset) && args.asset > 0,
  'frame.create': args => object(args) && Object.keys(args).length === 2 &&
    Array.isArray(args.rect) && args.rect.length === 4 && args.rect.every(Number.isFinite) &&
    typeof args.text === 'string' && args.text.length > 0 && textBytes.encode(args.text).length <= 2048,
});

export function mount(host) {
  return mountCraftAccount(host, {...project, recovery, reviewWindowClose:true, commands, artworkExtensions});
}
