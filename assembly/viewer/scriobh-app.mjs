import {mountBinaryStudio} from './binary-studio.mjs';

export function mount(host) {
  return mountBinaryStudio(host, {
    name:'Scríobh',
    extension:'.scriobh',
    openExtensions:['.scriobh'],
  });
}
