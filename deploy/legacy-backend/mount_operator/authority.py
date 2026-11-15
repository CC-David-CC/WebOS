"""Prepare and apply mount-bound public authority changes without resetting floors.

These helpers do not export policy, stop/start services or change hosting. The
coordinator must journal prepared public plans, stop the affected services, apply
the authority first and run publisher updates as their existing owning users.
Old ledgers and keys are never recreated. A rollback is another forward revision.
"""
from contextlib import closing
from copy import deepcopy
import json
from urllib.parse import urlsplit

from origin_service.mount import validate_base_path
from steward.protocol import exact, jose, times
from steward.provision import verified_seed
from steward.root_authority import duration

VERSION = 'codi-mount-authority-plan/1'
PUBLISHER_VERSION = 'codi-mount-publisher-plan/2'


def plan_digest(plan):
    """Bind semantic public plan bytes independently of JSON insertion order."""
    return jose.digest(json.dumps(plan, sort_keys=True, separators=(',', ':'), ensure_ascii=True))


def provision(value):
    exact(value, 'root_key realm endpoint identity_policy origins seed')
    inspected = jose.inspect(value['seed'], 'codi-seed/1', 32768)[1]
    seed = verified_seed(value['seed'], value['root_key'], value['realm'], inspected['iat'])
    if len(seed['stewards']) != 1 or seed['stewards'][0]['endpoints'] != [value['endpoint']]:
        raise ValueError('One existing mount-bound steward is required')
    if not isinstance(value['origins'], list) or len(value['origins']) != 1:
        raise ValueError('One existing HTTPS origin is required')
    origin = value['origins'][0]
    parsed = urlsplit(origin)
    if parsed.scheme != 'https' or not parsed.hostname or parsed.username or parsed.password or parsed.path or parsed.query or parsed.fragment:
        raise ValueError('Exact existing HTTPS origin required')
    endpoint = urlsplit(value['endpoint'])
    if endpoint.scheme != 'wss' or endpoint.netloc != parsed.netloc or endpoint.query or endpoint.fragment or not endpoint.path.endswith('/rendezvous'):
        raise ValueError('Existing WSS endpoint must match the origin')
    base = validate_base_path(endpoint.path[:-len('/rendezvous')])
    policy = value['identity_policy']
    if not isinstance(policy, dict) or policy.get('mode') != 'server' or policy.get('authorityClass') != 'development' or policy.get('issuer') != origin or policy.get('apiBase') != base + '/api/v1' or not policy.get('authorityKeys'):
        raise ValueError('Existing development issuer policy must match the mount')
    return seed, base


def validate(plan):
    exact(plan, 'version before after')
    if plan['version'] != VERSION:
        raise ValueError('Unknown mount authority plan')
    before, after = plan['before'], plan['after']
    old, old_base = provision(before)
    new, new_base = provision(after)
    if any(before[k] != after[k] for k in ['root_key', 'realm', 'origins']):
        raise ValueError('Mount migration cannot replace root, realm or origin')
    if {k: v for k, v in before['identity_policy'].items() if k != 'apiBase'} != {k: v for k, v in after['identity_policy'].items() if k != 'apiBase'}:
        raise ValueError('Mount migration cannot replace issuer trust')
    stable = lambda grant: {k: v for k, v in grant.items() if k not in ('endpoints', 'exp')}
    if stable(old['stewards'][0]) != stable(new['stewards'][0]):
        raise ValueError('Mount migration cannot change service keys, scopes or quotas')
    if new['revision'] <= old['revision'] or new['iat'] < old['iat']:
        raise ValueError('Mount migration must advance the signed root revision')
    return old, new, old_base, new_base


def prepare(authority, base, *, seconds, minimum_revision):
    """Sign prospective public bytes. Caller journals them before apply()."""
    base = validate_base_path(base)
    seconds = duration(seconds)
    if type(minimum_revision) is not int or not 1 <= minimum_revision < 2**53 - 1:
        raise ValueError('Explicit bounded root floor required')
    with authority.operator(), closing(authority.connection()) as db:
        binding, revision, token, old = authority.row(db)
        before = {**binding['template'], 'seed': token}
        provision(before)
        now = int(authority.clock())
        if now < old['iat'] or minimum_revision < revision:
            raise ValueError('Clock or trusted root floor is behind current authority')
        next_revision = minimum_revision + 1
        if next_revision > 2**53 - 1:
            raise ValueError('Root revision exhausted')
        after = deepcopy(before)
        after['endpoint'] = before['origins'][0].replace('https:', 'wss:', 1) + base + '/rendezvous'
        after['identity_policy']['apiBase'] = base + '/api/v1'
        grant = {**binding['grant'], 'endpoints': [after['endpoint']], 'exp': now + seconds}
        seed = {**old, 'revision': next_revision, 'iat': now, 'exp': now + seconds, 'stewards': [grant]}
        after['seed'] = jose.sign(seed, authority.key, 'codi-seed/1')
        plan = {'version': VERSION, 'before': before, 'after': after}
        validate(plan)
        return plan


def apply(authority, plan):
    """Commit exactly the journaled plan; retries reuse its signed bytes."""
    _, new, _, _ = validate(plan)
    with authority.operator(), closing(authority.connection()) as db:
        db.execute('BEGIN IMMEDIATE')
        binding, revision, token, _ = authority.row(db)
        current = {**binding['template'], 'seed': token}
        if current == plan['after']:
            db.commit()
            return False
        if current != plan['before']:
            raise ValueError('Authority changed outside the prepared mount plan')
        if new['exp'] <= int(authority.clock()):
            raise ValueError('Prepared delegation expired; explicit new issuance is required')
        template = {k: v for k, v in plan['after'].items() if k != 'seed'}
        grant = {k: v for k, v in new['stewards'][0].items() if k != 'exp'}
        db.execute('UPDATE authority SET binding=?,revision=?,token=? WHERE id=1',
                   (jose.dumps({'template': template, 'grant': grant}), new['revision'], plan['after']['seed']))
        db.commit()
        return True


def publisher_binding(value, seed):
    return {'realm': value['realm'], 'root_key_id': jose.thumbprint(value['root_key']),
            'service_key_id': seed['stewards'][0]['key_id'], 'endpoint': value['endpoint']}


def publisher_row(publisher):
    with publisher.transaction() as db:
        row = db.execute('SELECT binding,seed_revision,seed_hash,revision,token,frozen FROM publisher WHERE id=1').fetchone()
        if row is None:
            raise ValueError('Missing publisher row; never initialize it implicitly')
        return list(row)


def validate_publisher_row(row, value, seed, allow_unbound):
    if not isinstance(row, list) or len(row) != 6:
        raise ValueError('Invalid publisher preimage')
    if row == ['UNBOUND', 0, '', 0, None, 0]:
        if not allow_unbound:
            raise ValueError('Online publisher must already have its durable binding')
        return
    if row[5] != 0 or row[0] != jose.dumps(publisher_binding(value, seed)) or row[1] != seed['revision'] or row[2] != jose.digest(jose.dumps(seed)):
        raise ValueError('Publisher is frozen or differs from the existing root policy')
    # The root-owned staging ledger can remain unused across several mount
    # transitions. It has a durable binding after the first move, but must not
    # invent a publication/counter merely to perform the next move or rollback.
    if allow_unbound and row[3:] == [0, None, 0]:
        return
    if type(row[3]) is not int or not 1 <= row[3] < 2**53 - 1 or row[4] is None:
        raise ValueError('Existing publisher revision/token is required')
    grant = seed['stewards'][0]
    descriptor = jose.verify(row[4], grant['public_key'], 'codi-steward/1', 8192)
    exact(descriptor, 'version realm key_id revision iat exp endpoint scopes limits')
    times(descriptor, descriptor['iat'], 300)
    limits = {'lease_seconds': grant['limits']['lease_seconds'],
              'sample_size': min(4, grant['limits']['sample_size']),
              'signal_bytes': min(32768, grant['limits']['signal_bytes'])}
    if descriptor['version'] != 'codi-steward/1' or descriptor['revision'] != row[3] or descriptor['realm'] != value['realm'] or descriptor['endpoint'] != value['endpoint'] or descriptor['key_id'] != grant['key_id'] or descriptor['exp'] > grant['exp'] or descriptor['scopes'] != grant['scopes'] or descriptor['limits'] != limits:
        raise ValueError('Existing signed publisher descriptor differs from its binding')


def publisher_plan(publisher, plan, *, allow_unbound=False):
    old, new, _, _ = validate(plan)
    if type(allow_unbound) is not bool:
        raise ValueError('Explicit unbound-ledger policy required')
    row = publisher_row(publisher)
    validate_publisher_row(row, plan['before'], old, allow_unbound)
    after = [jose.dumps(publisher_binding(plan['after'], new)), new['revision'], jose.digest(jose.dumps(new)), *row[3:]]
    return {'version': PUBLISHER_VERSION, 'authorityPlanSHA256': plan_digest(plan),
            'allowUnbound': allow_unbound, 'before': row, 'after': after}


def apply_publisher(publisher, plan, prepared):
    """Rebind a stopped publisher as its existing owner, retaining its counter/token."""
    exact(prepared, 'version authorityPlanSHA256 allowUnbound before after')
    validate(plan)
    if prepared['version'] != PUBLISHER_VERSION or prepared['authorityPlanSHA256'] != plan_digest(plan) or type(prepared['allowUnbound']) is not bool:
        raise ValueError('Publisher plan is not bound to this signed authority change')
    with publisher.transaction() as db:
        current = db.execute('SELECT binding,seed_revision,seed_hash,revision,token,frozen FROM publisher WHERE id=1').fetchone()
        if current is None:
            raise ValueError('Publisher state disappeared')
        current = list(current)
        # Recompute the expected row from the journaled preimage. Do not trust
        # arbitrary replacement counters/tokens supplied in a prepared object.
        old, new, _, _ = validate(plan)
        row = prepared['before']
        validate_publisher_row(row, plan['before'], old, prepared['allowUnbound'])
        expected = [jose.dumps(publisher_binding(plan['after'], new)), new['revision'], jose.digest(jose.dumps(new)), *row[3:]]
        if prepared['after'] != expected:
            raise ValueError('Publisher plan cannot replace token, counter or frozen state')
        if current == expected:
            return False
        if current != row:
            raise ValueError('Publisher advanced outside the stopped migration')
        db.execute('UPDATE publisher SET binding=?,seed_revision=?,seed_hash=? WHERE id=1', tuple(expected[:3]))
        return True
