"""Conservative next step for a bounded expired-root recovery.

This classifier performs no I/O or signing. Callers must independently verify
the signatures, protected-file custody, binding/key equality, ledger integrity,
current locks and service identity before providing these observations.
"""
import re
import hashlib
from steward.protocol import jose
from steward.provision import verified_seed

_DIGEST=re.compile(r'[0-9a-f]{64}\Z')
def _digest(value):return hashlib.sha256(value.encode('utf-8')).hexdigest()
def _verified(value,key,realm):
    if not isinstance(value,dict) or 'seed' not in value:raise ValueError('Provision record required')
    raw=value['seed'];claim=jose.inspect(raw,'codi-seed/1',32768)[1]
    if type(claim.get('iat')) is not int:raise ValueError('Signed seed issue time required')
    claim=verified_seed(raw,key,realm,claim['iat'])
    binding={k:v for k,v in value.items() if k!='seed'}
    if binding.get('root_key')!=key or binding.get('realm')!=realm:raise ValueError('Provision root or realm changed')
    grants=[{k:v for k,v in grant.items() if k!='exp'} for grant in claim['stewards']]
    return claim,_digest(raw),_digest(jose.dumps(binding)),_digest(jose.dumps(grants))

def make_checkpoint(provision):
    """Record public, verified baseline fingerprints before reserving an epoch."""
    key=provision['root_key'];realm=provision['realm'];claim,seed,binding,grant=_verified(provision,key,realm)
    return {'version':'codi-expired-root-checkpoint/1','baseRevision':claim['revision'],'seedHash':seed,'payloadHash':jose.digest(jose.dumps(claim)),'bindingHash':binding,'grantHash':grant,'rootKeyId':jose.thumbprint(key),'realm':realm}

def inspect_signed_exports(root,staged,live,checkpoint,*,fence_revision,now,steward_running,ledger_verified):
    """Validate signed, possibly partial exports against a prior trusted checkpoint.

    The caller is responsible for protected custody of the checkpoint and files,
    validating the independent fence binding and publisher ledger, and locking.
    """
    if not isinstance(checkpoint,dict) or set(checkpoint)!={'version','baseRevision','seedHash','payloadHash','bindingHash','grantHash','rootKeyId','realm'} or checkpoint['version']!='codi-expired-root-checkpoint/1':raise ValueError('Exact trusted checkpoint required')
    if type(now) is not int or now<1:raise ValueError('Current time required')
    key=root.get('root_key');realm=checkpoint['realm']
    if jose.thumbprint(key)!=checkpoint['rootKeyId']:raise ValueError('Root key changed since checkpoint')
    values=[_verified(item,key,realm) for item in [root,staged,live]]
    if any(binding!=checkpoint['bindingHash'] or grant!=checkpoint['grantHash'] for _,_,binding,grant in values):raise ValueError('Signed authority binding changed since checkpoint')
    if any(claim['iat']>now for claim,_,_,_ in values):raise ValueError('Authority issue time is ahead of the recovery clock')
    base=checkpoint['baseRevision']
    return next_step(base_revision=base,target_revision=base+1,root_revision=values[0][0]['revision'],fence_revision=fence_revision,staged_revision=values[1][0]['revision'],live_revision=values[2][0]['revision'],base_hash=checkpoint['seedHash'],root_hash=values[0][1],staged_hash=values[1][1],live_hash=values[2][1],root_expired=now>=values[0][0]['exp'],steward_running=steward_running,bindings_verified=True,ledger_verified=ledger_verified)

def verify_publisher(row,root,live,checkpoint,*,minimum_revision):
    """Validate an existing publisher row across a one-epoch partial export.

    The caller must use a protected read-only database snapshot, verify its
    integrity and hold the managed lock. This function never changes the row.
    """
    if not isinstance(row,(tuple,list)) or len(row)!=6:raise ValueError('Exact publisher row required')
    binding,seed_revision,seed_hash,revision,token,frozen=row
    base=checkpoint['baseRevision'];key=root['root_key'];realm=checkpoint['realm']
    seed,_,binding_hash,grant_hash=_verified(root,key,realm);live_seed,_,live_binding,live_grant=_verified(live,key,realm)
    if jose.thumbprint(key)!=checkpoint['rootKeyId'] or binding_hash!=checkpoint['bindingHash'] or live_binding!=binding_hash or grant_hash!=checkpoint['grantHash'] or live_grant!=grant_hash:raise ValueError('Publisher authority binding changed')
    if type(minimum_revision) is not int or minimum_revision<1 or type(revision) is not int or not minimum_revision<=revision<2**53 or type(seed_revision) is not int or seed_revision not in (base,base+1) or seed_revision>seed['revision'] or seed_revision>live_seed['revision'] or type(frozen) is not int or frozen!=0:raise ValueError('Publisher revision or frozen state invalid')
    expected_hash=checkpoint['payloadHash'] if seed_revision==base else jose.digest(jose.dumps(seed))
    if seed_hash!=expected_hash:raise ValueError('Publisher signed seed fingerprint differs')
    if len(seed['stewards'])!=1 or root['endpoint'] not in seed['stewards'][0]['endpoints']:raise ValueError('Exactly one pinned steward grant required')
    grant=seed['stewards'][0];expected_binding={'realm':realm,'root_key_id':checkpoint['rootKeyId'],'service_key_id':grant['key_id'],'endpoint':root['endpoint']}
    if jose.loads(binding)!=expected_binding:raise ValueError('Publisher service binding differs')
    descriptor=jose.verify(token,grant['public_key'],'codi-steward/1',8192)
    required={'version','realm','key_id','endpoint','scopes','limits','iat','exp','revision'}
    limits={'lease_seconds':grant['limits']['lease_seconds'],'sample_size':min(4,grant['limits']['sample_size']),'signal_bytes':min(32768,grant['limits']['signal_bytes'])}
    if set(descriptor)!=required or descriptor['version']!='codi-steward/1' or descriptor['realm']!=realm or descriptor['key_id']!=grant['key_id'] or descriptor['endpoint']!=root['endpoint'] or descriptor['scopes']!=grant['scopes'] or descriptor['limits']!=limits or descriptor['revision']!=revision or type(descriptor['iat']) is not int or type(descriptor['exp']) is not int or not 0<descriptor['exp']-descriptor['iat']<=300:raise ValueError('Publisher descriptor differs from its signed binding')
    return {'seedRevision':seed_revision,'publisherRevision':revision}

def next_step(*,base_revision,target_revision,root_revision,fence_revision,
              staged_revision,live_revision,base_hash,root_hash,staged_hash,live_hash,
              root_expired,steward_running,bindings_verified,ledger_verified):
    revisions=[base_revision,target_revision,root_revision,fence_revision,staged_revision,live_revision]
    if any(type(v) is not int or not 1<=v<2**53-1 for v in revisions):raise ValueError('Invalid authority revision')
    if target_revision!=base_revision+1:raise ValueError('Exactly one root revision must be authorized')
    if any(not isinstance(v,str) or not _DIGEST.fullmatch(v) for v in [base_hash,root_hash,staged_hash,live_hash]):raise ValueError('Exact signed seed hashes required')
    if any(type(v) is not bool for v in [root_expired,steward_running,bindings_verified,ledger_verified]):raise ValueError('Exact verification flags required')
    if not bindings_verified or not ledger_verified:raise ValueError('Authority bindings and publisher ledger must be verified')
    if root_revision not in (base_revision,target_revision) or fence_revision not in (root_revision,root_revision+1) or fence_revision>target_revision:
        raise ValueError('Authority or independent floor is outside the approved recovery')
    if not (base_revision<=live_revision<=staged_revision<=root_revision):raise ValueError('Signed export state is inconsistent')
    if any(revision==base_revision and digest!=base_hash for revision,digest in [(root_revision,root_hash),(staged_revision,staged_hash),(live_revision,live_hash)]):raise ValueError('The original signed seed differs from the recorded checkpoint')
    if staged_revision==root_revision and staged_hash!=root_hash or live_revision==root_revision and live_hash!=root_hash or staged_revision==live_revision and staged_hash!=live_hash:
        raise ValueError('Signed seed fork or changed export bytes')
    if root_revision==base_revision:
        if not root_expired or steward_running:raise ValueError('Expired, stopped steward required for renewal')
        return 'renew-once'
    if fence_revision!=target_revision or root_expired:raise ValueError('The committed recovery seed is unavailable or expired')
    if staged_revision!=root_revision or live_revision!=root_revision:
        if steward_running:raise ValueError('Stop the steward before repairing a partial export')
        return 'export-committed'
    return 'verify-running' if steward_running else 'start-steward'
