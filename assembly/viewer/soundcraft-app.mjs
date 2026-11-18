import {mountCraftAccount} from './craft-account-app.mjs';
import {createCraftRecovery} from './craft-account-recovery.mjs';

const project = {app:'soundcraft', name:'SoundCraft', extension:'.scraftz'};
const recovery = createCraftRecovery(project);
const object = args => args !== null && typeof args === 'object' && !Array.isArray(args);
const empty = args => object(args) && Object.keys(args).length === 0;
const text = new TextEncoder();

const commands = Object.freeze({
  'document.inspect': empty,
  'edit.undo': empty,
  'track.new': args => object(args) && Object.keys(args).length === 1 &&
    typeof args.name === 'string' && args.name.trim().length > 0 && text.encode(args.name).length <= 128,
});

export function mount(host) {
  return mountCraftAccount(host, {...project, recovery, reviewWindowClose:true, commands});
}
