#!/usr/bin/env python3
"""Python-signed genesis is independently verified by Python and Web Crypto."""
import json,subprocess,sys
from pathlib import Path
from cryptography.hazmat.primitives.asymmetric import ec
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT),str(ROOT/'codiserver-server-v0.3.0')]
from codiauth import jose
from steward.official_recovery_genesis import verify_recovery_genesis
owner=ec.generate_private_key(ec.SECP256R1());key=jose.public_jwk(owner);recovery=jose.public_jwk(ec.generate_private_key(ec.SECP256R1()));channel=jose.digest(jose.dumps(['codi-device-channel-key/1',jose.thumbprint(key)]))
body={'profile':'codi-device-channel/1','type':'policy','channel':channel,'stream':'chat','validators':[channel],'publicWrite':True,'players':None,'publicRead':True,'recovery':{'profile':'codi-official-genesis-recovery/1','key':recovery}}
wire=jose.sign({'version':'codi-device-channel-key/1','channel':channel,'key':key,'purpose':'checkpoint','body':body},owner,'codi-device-channel-key-proof+jws');parts=wire.split('.');pin=jose.digest(jose.dumps(['codi-device-channel/1','signed-content',parts[0],parts[1]]));python=verify_recovery_genesis(wire,channel=channel,genesis_hash=pin)
source='''import {readDeviceChannelPolicy,initialDeviceChannelPosition} from './network/device-channel-state.mjs';let input='';for await(const s of process.stdin)input+=s;const x=JSON.parse(input),p=await readDeviceChannelPolicy(x.wire,{channel:x.channel,genesisHash:x.pin}),at=await initialDeviceChannelPosition(p);console.log(JSON.stringify({channel:p.channel,genesisHash:p.genesisHash,head:at.head,validators:p.validators,recoveryKey:p.recoveryKey}));'''
js=json.loads(subprocess.check_output([ROOT/'.build/tools/node-v24.22.1-linux-x64/bin/node','--input-type=module','-e',source],input=json.dumps({'wire':wire,'channel':channel,'pin':pin}),text=True,cwd=ROOT));assert js==python
print(json.dumps({'status':'PASS','scope':'Python-signed genesis verified independently in Python and Web Crypto'}))
