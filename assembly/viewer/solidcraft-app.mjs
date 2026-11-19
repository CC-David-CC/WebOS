import {mountCraftAccount} from './craft-account-app.mjs';
import {createCraftRecovery} from './craft-account-recovery.mjs';

const design = {app:'solidcraft', name:'SolidCraft', extension:'.sc', legacyExtensions:['.solidcraft','.solvecraft']};
const recovery = createCraftRecovery(design);
const shape = (args, keys) => args !== null && typeof args === 'object' && !Array.isArray(args) &&
  Object.keys(args).length === keys.length && keys.every(key => Object.hasOwn(args, key));
const point = value => Array.isArray(value) && value.length === 2 &&
  value.every(axis => Number.isFinite(axis) && Math.abs(axis) <= 1e9);
const distance = value => Number.isFinite(value) && value > 0 && value <= 1e6;
const featureId = value => Number.isSafeInteger(value) && value > 0;
const empty = args => shape(args, []);
const commands = Object.freeze({
  'document.inspect': empty,
  'inspect.measure': empty,
  'edit.undo': empty,
  'sketch.create': args => shape(args, ['plane']) && ['XY','XZ','YZ'].includes(args.plane),
  'sketch.rectangle.two_point': args => shape(args, ['p0','p1']) && point(args.p0) && point(args.p1),
  'sketch.finish': empty,
  'solid.extrude': args => shape(args, ['distance']) && distance(args.distance),
  'timeline.redefine': args => shape(args, ['feature','command','params']) && featureId(args.feature) &&
    args.command === 'solid.extrude' && shape(args.params, ['sketch','profiles','distance','operation']) &&
    featureId(args.params.sketch) && args.params.profiles === 'all' && distance(args.params.distance) &&
    args.params.operation === 'new',
});

export function mount(host) {
  return mountCraftAccount(host, {
    ...design, recovery, commands, reviewWindowClose:true, accountAutosave:false,
  });
}
