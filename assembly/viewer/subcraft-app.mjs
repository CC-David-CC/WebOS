import {mountBinaryStudio} from './binary-studio.mjs';

export function mount(host) {
  return mountBinaryStudio(host, {
    name:'SubCraft',
    extension:'.subcraft',
    openExtensions:['.subcraft'],
  });
}
