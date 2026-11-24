import {mountBinaryStudio} from './binary-studio.mjs';

export function mount(host) {
  return mountBinaryStudio(host, {
    name:'TraceDraw', extension:'.tdraw', openExtensions:['.tdraw'], multipleProjects:true,
  });
}
