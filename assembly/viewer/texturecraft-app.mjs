import {mountCraftAccount} from './craft-account-app.mjs';
import {createCraftRecovery} from './craft-account-recovery.mjs';

const project = {app:'texturecraft', name:'TextureCraft', extension:'.tcraft'};
const recovery = createCraftRecovery(project);
const shape = (args, keys) => args !== null && typeof args === 'object' && !Array.isArray(args) &&
  Object.keys(args).length === keys.length && keys.every(key => Object.hasOwn(args, key));
const empty = args => shape(args, []);
const namedLayer = args => shape(args, ['name']) && typeof args.name === 'string' &&
  args.name.trim().length > 0 && new TextEncoder().encode(args.name).length <= 128 &&
  !/[\u0000-\u001f\u007f-\u009f]/u.test(args.name);
const uv = point => Array.isArray(point) && point.length === 2 &&
  point.every(value => Number.isFinite(value) && value >= 0 && value <= 1);
const commands = Object.freeze({
  'document.inspect': empty,
  'edit.undo': empty,
  'layer.add.paint': namedLayer,
  'layer.rename': namedLayer,
  'tool.strokeUv': args => shape(args, ['points']) && Array.isArray(args.points) &&
    args.points.length > 0 && args.points.length <= 128 &&
    args.points.every(uv) && JSON.stringify(args).length <= 4096,
});

export function mount(host) {
  return mountCraftAccount(host, {
    ...project, recovery, commands, deviceImport:true, reviewWindowClose:true, accountAutosave:false,
  });
}
