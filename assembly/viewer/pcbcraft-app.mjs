import {mountCraftAccount} from './craft-account-app.mjs';
import {createCraftRecovery} from './craft-account-recovery.mjs';

const project = {app:'pcbcraft', name:'PCBCraft', extension:'.pc'};
const recovery = createCraftRecovery(project);
const record = value => value !== null && typeof value === 'object' && !Array.isArray(value);
const shape = (args, keys) => record(args) && Object.keys(args).length === keys.length &&
  keys.every(key => Object.hasOwn(args, key));
const identifier = value => typeof value === 'string' && /^[A-Za-z0-9][A-Za-z0-9._:-]{0,63}$/.test(value);
const position = args => [args.x_nm, args.y_nm].every(value => Number.isSafeInteger(value) && Math.abs(value) <= 1e9);
const pins = mapping => record(mapping) && Object.keys(mapping).length > 0 && Object.keys(mapping).length <= 64 &&
  Object.entries(mapping).every(([pin, pad]) => identifier(pin) && identifier(pad));

const commands = Object.freeze({
  'document.inspect': args => shape(args, []),
  'edit.undo': args => shape(args, []),
  'project.rename': args => shape(args, ['name']) && typeof args.name === 'string' &&
    args.name.trim().length > 0 && new TextEncoder().encode(args.name).length <= 64 && !/[\x00-\x1f\x7f]/u.test(args.name),
  'schematic.place_symbol': args => shape(args, ['definition','x_nm','y_nm']) && identifier(args.definition) && position(args),
  'pcb.place_footprint': args => shape(args, ['symbol','definition','mapping','x_nm','y_nm']) &&
    identifier(args.symbol) && identifier(args.definition) && pins(args.mapping) && position(args),
});

export function mount(host) {
  return mountCraftAccount(host, {...project, recovery, commands, reviewWindowClose:true, accountAutosave:false});
}
