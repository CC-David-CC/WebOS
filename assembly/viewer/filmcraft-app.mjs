import {mountCraftAccount} from './craft-account-app.mjs';
import {createCraftOriginalStore, craftOriginalScope} from './craft-account-originals.mjs';
import {createCraftRecovery} from './craft-account-recovery.mjs';

const project = {app:'filmcraft', name:'FilmCraft', extension:'.fcproj'};
const recovery = createCraftRecovery(project);
const object = value => value !== null && typeof value === 'object' && !Array.isArray(value);
const empty = args => object(args) && Object.keys(args).length === 0;
const utf8 = new TextEncoder();
const commands = Object.freeze({
  'document.inspect': empty,
  'edit.undo': empty,
  'file.newSequence': args => object(args) && Object.keys(args).length === 1 &&
    typeof args.name === 'string' && args.name.trim().length > 0 && utf8.encode(args.name).length <= 128,
});

export function mount(host) {
  return mountCraftAccount(host, {
    ...project, recovery, commands, reviewWindowClose:true,
    async setupOriginals({context,origin,valid,signal}) {
      const scope = await craftOriginalScope('filmcraft-account-media/1',origin,context.owner);
      const store = createCraftOriginalStore({name:project.name,directory:'Video/FilmCraft Originals',files:context.files,valid,signal});
      return {scope,store};
    }
  });
}
