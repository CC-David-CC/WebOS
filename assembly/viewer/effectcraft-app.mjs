import {mountCraftAccount} from './craft-account-app.mjs';
import {createCraftOriginalStore, craftOriginalScope} from './craft-account-originals.mjs';
import {createCraftRecovery} from './craft-account-recovery.mjs';

const project = {app:'effectcraft', name:'EffectCraft', extension:'.ecproj'};
const recovery = createCraftRecovery(project);
const object = value => value !== null && typeof value === 'object' && !Array.isArray(value);
const empty = args => object(args) && Object.keys(args).length === 0;
const dimension = value => Number.isInteger(value) && value >= 1 && value <= 8192;
const utf8 = new TextEncoder();

const commands = Object.freeze({
  'document.inspect': empty,
  'edit.undo': empty,
  'comp.new': args => object(args) && Object.keys(args).length === 3 &&
    typeof args.name === 'string' && args.name.trim().length > 0 && utf8.encode(args.name).length <= 128 &&
    dimension(args.width) && dimension(args.height),
});

export function mount(host) {
  return mountCraftAccount(host, {
    ...project, recovery, commands, reviewWindowClose:true,
    async setupOriginals({context,origin,valid,signal}) {
      const scope = await craftOriginalScope('effectcraft-account-media/1',origin,context.owner);
      const store = createCraftOriginalStore({
        name:project.name,directory:'Video/EffectCraft Originals',files:context.files,valid,signal,
      });
      return {scope,store};
    },
  });
}
