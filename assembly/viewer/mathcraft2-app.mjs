import {mountBinaryStudio} from './binary-studio.mjs';

export function mount(host) {
  return mountBinaryStudio(host, {
    name:'MathCraft2',
    extension:'.mathcraft2',
    openExtensions:['.mathcraft2'],
  });
}
