import {mountBinaryStudio} from './binary-studio.mjs';

export function mount(host) {
  return mountBinaryStudio(host, {
    name:'Transit',
    extension:'.transitz',
    openExtensions:['.transitz','.transit'],
    imports:['.wav','.wave','.aiff','.aif','.flac','.mp3','.ogg','.m4a','.aac','.mp4','.caf','.mid','.midi','.smf'],
  });
}
