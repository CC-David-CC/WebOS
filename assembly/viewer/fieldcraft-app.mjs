import {mountCraftAccount} from './craft-account-app.mjs';
import {createCraftRecovery} from './craft-account-recovery.mjs';

const project = {app:'fieldcraft', name:'FieldCraft', extension:'.fieldcraft'};
const recovery = createCraftRecovery(project);
const shape = (args, keys) => args !== null && typeof args === 'object' && !Array.isArray(args) &&
  Object.keys(args).length === keys.length && keys.every(key => Object.hasOwn(args, key));
const commands = Object.freeze({
  'document.inspect': args => shape(args, []),
  'edit.undo': args => shape(args, []),
  'solve.static': args => shape(args, []),
  'mesh.node.add': args => shape(args, ['label','xyz']) && Number.isSafeInteger(args.label) &&
    args.label > 0 && args.label <= 0xffffffff && Array.isArray(args.xyz) && args.xyz.length === 3 &&
    args.xyz.every(n => Number.isFinite(n) && Math.abs(n) <= 1e9),
});

export function mount(host) {
  return mountCraftAccount(host, {...project, recovery, commands, reviewWindowClose:true, accountAutosave:false});
}
