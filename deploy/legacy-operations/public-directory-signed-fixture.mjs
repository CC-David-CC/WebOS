/** Disposable public channel descriptors for directory checks; no private key leaves this process. */
import {makeKey,signJws,hash} from '../network/crypto.mjs';
import {deviceChannelId} from '../assets/desktop/channel-keys.mjs';
import {createDeviceChannelPolicy,readDeviceChannelPolicy} from '../network/device-channel-state.mjs';
import {createChannelListing} from '../network/channel-listing.mjs';
const now=Number(process.argv[2]),keysById=new Map(),keys={async sign(channel,purpose,body){const k=keysById.get(channel);return signJws({version:'codi-device-channel-key/1',channel,key:k.publicKey,purpose,body},k.privateKey,'codi-device-channel-key-proof+jws');}};
async function make(label,publicRead=true){const k=await makeKey(),channel=await deviceChannelId(k.publicKey);keysById.set(channel,k);const policyWire=await createDeviceChannelPolicy(keys,channel,{publicRead,publicWrite:publicRead,authorAuthorization:'actor-epoch/2'}),policy=await readDeviceChannelPolicy(policyWire,{channel}),config={channel,genesisHash:policy.genesisHash,policyWire};return {config,listing:await createChannelListing(keys,config,{label,now})};}
const a=await make('Alpha room'),b=await make('Beta room'),c=await make('Alpha second'),privateChannel=await make('Private room',false);const update=await createChannelListing(keys,a.config,{label:'Alpha updated',now:now+1}),conflict=await createChannelListing(keys,a.config,{label:'Conflicting name',now:now+1});console.log(JSON.stringify({scope:await hash('directory-test'),otherScope:await hash('other-directory'),a,b,c,privateChannel,update,conflict}));
