import {mountCraftAccount} from './craft-account-app.mjs';
import {createCraftRecovery} from './craft-account-recovery.mjs';

const project = {app:'photocraft', name:'PhotoCraft', extension:'.pcraft'};
export const photoRecovery = createCraftRecovery(project);

export function mount(host) {
  return mountCraftAccount(host, {...project,recovery:photoRecovery,deviceImport:true});
}
