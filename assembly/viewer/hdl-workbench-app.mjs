import {mountBinaryStudio} from './binary-studio.mjs';

export function mount(host) {
  return mountBinaryStudio(host, {
    name:'HDL Workbench', extension:'.hdl.json', openExtensions:['.hdl.json'],
    fileExport:{
      label:'Save for Digital Logic', title:'Save Digital Logic circuit',
      extension:'.logic.json', mime:'application/json', take:'take_file_export',
    },
  });
}
