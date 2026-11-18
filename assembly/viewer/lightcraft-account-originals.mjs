import {createCraftOriginalStore, craftOriginalScope} from './craft-account-originals.mjs';

export function lightCraftAccountScope(origin, owner) {
  return craftOriginalScope('lightcraft-account-cache/1',origin,owner);
}

export function createLightCraftOriginalStore(options) {
  return createCraftOriginalStore({...options,name:'LightCraft',directory:'Pictures/LightCraft Originals'});
}
