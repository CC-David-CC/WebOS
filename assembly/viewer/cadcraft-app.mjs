import {mountCraftAccount} from './craft-account-app.mjs';
import {createCraftRecovery} from './craft-account-recovery.mjs';

const drawing = {app:'cadcraft', name:'CADCraft', extension:'.dxf'};
const recovery = createCraftRecovery(drawing);
const shape = (args, keys) => args !== null && typeof args === 'object' && !Array.isArray(args) &&
  Object.keys(args).length === keys.length && keys.every(key => Object.hasOwn(args, key));
const point = value => Array.isArray(value) && value.length === 2 &&
  value.every(axis => Number.isFinite(axis) && Math.abs(axis) <= 1e9);
const commands = Object.freeze({
  'document.inspect': args => shape(args, []),
  'edit.undo': args => shape(args, []),
  line: args => shape(args, ['points']) && Array.isArray(args.points) &&
    args.points.length === 2 && args.points.every(point),
  circle: args => shape(args, ['center','radius']) && point(args.center) &&
    Number.isFinite(args.radius) && args.radius > 0 && args.radius <= 1e9,
  dimlinear: args => shape(args, ['p1','p2','at']) && [args.p1,args.p2,args.at].every(point),
});

export function mount(host) {
  return mountCraftAccount(host, {
    ...drawing, recovery, commands, reviewWindowClose:true, accountAutosave:false,
  });
}
