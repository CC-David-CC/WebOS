import {mountCraftAccount} from './craft-account-app.mjs';
import {createCraftRecovery} from './craft-account-recovery.mjs';
import {createLightCraftOriginalStore, lightCraftAccountScope} from './lightcraft-account-originals.mjs';

const project = {app:'lightcraft', name:'LightCraft', extension:'.lightcraft'};
export const lightRecovery = createCraftRecovery(project);

const commands = Object.freeze({
  'document.inspect': args => args && !Array.isArray(args) && typeof args === 'object' && !Object.keys(args).length,
  'photo.rate': args => args && Object.keys(args).length === 2 &&
    Array.isArray(args.ids) && args.ids.length === 1 && Number.isSafeInteger(args.ids[0]) && args.ids[0] > 0 &&
    Number.isInteger(args.rating) && args.rating >= 0 && args.rating <= 5,
});

export function mount(host) {
  return mountCraftAccount(host, {
    ...project, recovery:lightRecovery, reviewWindowClose:true, commands,
    async setupOriginals({context, origin, valid, signal}) {
      const scope = await lightCraftAccountScope(origin, context.owner);
      return {scope, store:createLightCraftOriginalStore({files:context.files,valid,signal})};
    },
  });
}
