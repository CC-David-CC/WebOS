import {mountCraftAccount} from './craft-account-app.mjs';
import {createCraftRecovery} from './craft-account-recovery.mjs';

const project = {app:'materialcraft', name:'MaterialCraft', extension:'.mcraft'};
const recovery = createCraftRecovery(project);
const shape = (args, keys) => args !== null && typeof args === 'object' && !Array.isArray(args) &&
  Object.keys(args).length === keys.length && keys.every(key => Object.hasOwn(args, key));
const empty = args => shape(args, []);
const nodeId = value => Number.isSafeInteger(value) && value > 0;
const commands = Object.freeze({
  'document.inspect': empty,
  'edit.undo': empty,
  'graph.cook': empty,
  'graph.node.add': args => shape(args, ['def']) && ['uniform','levels','output'].includes(args.def),
  'graph.resource.add': args => shape(args, ['resource']) && typeof args.resource === 'string' &&
    args.resource.trim().length > 0 && new TextEncoder().encode(args.resource).length <= 128 &&
    !/\p{Cc}/u.test(args.resource),
  'graph.connect': args => shape(args, ['from','to']) && nodeId(args.from) && nodeId(args.to),
  'graph.node.move': args => shape(args, ['ids','to']) && Array.isArray(args.ids) &&
    args.ids.length === 1 && nodeId(args.ids[0]) && Array.isArray(args.to) && args.to.length === 2 &&
    args.to.every(value => Number.isFinite(value) && Math.abs(value) <= 1e6),
});

export function mount(host) {
  return mountCraftAccount(host, {
    ...project, recovery, commands, deviceImport:true, reviewWindowClose:true, accountAutosave:false,
  });
}
