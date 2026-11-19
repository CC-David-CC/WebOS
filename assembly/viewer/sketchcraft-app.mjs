import {mountCraftAccount} from './craft-account-app.mjs';
import {createCraftRecovery} from './craft-account-recovery.mjs';

const project = {app:'sketchcraft', name:'SketchCraft', extension:'.sketchcraft'};
const recovery = createCraftRecovery(project);
const shape = (args, keys) => args !== null && typeof args === 'object' && !Array.isArray(args) &&
  Object.keys(args).length === keys.length && keys.every(key => Object.hasOwn(args, key));
const coordinate = value => Number.isFinite(value) && Math.abs(value) <= 1e6;
const point = value => Array.isArray(value) && value.length === 3 && value.every(coordinate);
const commands = Object.freeze({
  'document.inspect': args => shape(args, []),
  'edit.undo': args => shape(args, []),
  'model.rectangle': args => shape(args, ['from','to']) && point(args.from) && point(args.to),
  'model.pushpull': args => shape(args, ['face','distance']) && Number.isSafeInteger(args.face) &&
    args.face > 0 && args.face <= 0xffffffff && coordinate(args.distance) && args.distance !== 0,
});

export function mount(host) {
  return mountCraftAccount(host, {
    ...project, recovery, commands, reviewWindowClose:true, accountAutosave:false,
  });
}
