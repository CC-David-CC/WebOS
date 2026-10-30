#!/usr/bin/env python3
"""Bind the supplied acceptance obligations to current evidence without passing gates by inference."""
import hashlib
import json
import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ACTIVE = ROOT / 'active-system'
CHECKS = ACTIVE / '.build/checks'


def record(path):
    data = (ROOT / path).read_bytes()
    return {'path': path, 'sha256': hashlib.sha256(data).hexdigest(), 'bytes': len(data)}


def main():
    paths = [
        'AGENTS.md', 'ROADMAP.md', 'served_apps_public/CONTRIBUTING.md',
        'codiserver-browser-v86-auth-handoff-v0.1.0/contracts/acceptance.json',
        'codiserver-web-v0.2.0/contracts/acceptance.json',
        'codiserver-web-v0.3.0/contracts/acceptance.json',
        'codiserver-server-v0.3.0/contracts/acceptance.json',
        'codiserver-web-v0.3.0/README.md',
        'codiserver-web-v0.3.0/docs/02_BUILD_TEST_LADDER.md',
        'codiserver-web-v0.3.0/docs/08_P2P_V03_DECISIONS.md',
        'codiserver-web-v0.3.0/evidence/STATUS.md',
        'codiserver-server-v0.3.0/docs/01_SERVICE_PLAN.md',
        'evidence/M00-dependency-review.md', 'evidence/network-candidates.json',
        'active-system/network/routed-rooms.mjs',
        'active-system/network/routed-room-grant.mjs',
        'active-system/network/resource-budget.mjs',
        'active-system/network/replay.mjs',
        'active-system/evidence/root-cutover-live.md',
        'active-system/evidence/mesh-pool.md',
        'active-system/evidence/mesh-host.md',
        'active-system/evidence/mesh-native.md',
        'active-system/evidence/mesh-neighbors.md',
        'active-system/network/mesh-introductions.mjs',
        'active-system/network/mesh-lease-control.mjs',
        'active-system/network/MESH-PUBLIC-PROFILE.md',
        'active-system/scripts/mesh-lease-browser-check.py',
        'active-system/scripts/mesh-lease-page.mjs',
        'active-system/scripts/mesh-lease-rtc-check.py',
        'active-system/scripts/mesh-lease-rtc-page.mjs',
        'active-system/scripts/mesh-lease-route-check.py',
        'active-system/scripts/mesh-source-protocol-check.py',
        'active-system/scripts/mesh-lease-final-health.py',
        'active-system/scripts/mesh-lease-milestone.py',
        'active-system/network/hosted-room-authority.mjs',
        'active-system/room_service/__init__.py',
        'active-system/room_service/contract.py',
        'active-system/room_service/access.py',
        'active-system/room_service/store.py',
        'active-system/room_service/http.py',
        'active-system/origin_service/room_authority.py',
        'active-system/scripts/hosted-room-check.py',
        'active-system/scripts/hosted-room-browser-check.py',
        'active-system/scripts/hosted-room-page.mjs',
        'active-system/scripts/hosted-room-milestone.py',
        'active-system/room_service/operator.py',
        'active-system/origin_service/room_management.py',
        'active-system/scripts/serve-hosted-rooms.py',
        'active-system/scripts/manage-hosted-rooms.py',
        'active-system/scripts/build-hosted-native.py',
        'active-system/scripts/hosted-binding-vm-check.py',
        'active-system/scripts/hosted-native-browser-check.py',
        'active-system/scripts/hosted-native-final-health.py',
        'active-system/scripts/hosted-snapshot-check.py',
        'active-system/scripts/hosted-snapshot-page.mjs',
        'active-system/scripts/hosted-snapshot-milestone.py',
        'active-system/evidence/hosted-checkpoints.md',
        'active-system/scripts/room-code-upgrade-vm-check.py',
        'active-system/scripts/checkpoint-native-milestone.py',
        'active-system/evidence/room-code-upgrade.md',
        'active-system/network/hosted-room-store.mjs',
        'active-system/network/hosted-room-client.mjs',
        'active-system/scripts/hosted-client-check.py',
        'active-system/scripts/hosted-client-page.mjs',
        'active-system/scripts/hosted-client-milestone.py',
        'active-system/scripts/build-hosted-client-native.py',
        'active-system/scripts/hosted-client-native-check.py',
        'active-system/evidence/hosted-client.md',
        'served_apps_public/rooms/hosted-view.mjs',
        'active-system/evidence/compact-replay.md',
        'active-system/scripts/mesh-neighbors-browser-check.py',
        'active-system/scripts/build-mesh-native.py',
        'active-system/scripts/build-native-app-update.py',
        'active-system/scripts/native-rollout.py',
        'active-system/.build/releases/connected-mesh-native-r1/connected-release.json',
        'active-system/app.js',
        'active-system/networking.js',
        'served_apps_public/rooms/index.mjs',
        'served_apps_public/rooms/mesh-view.mjs',
        'served_apps_public/rooms/mesh-view.css',
        'active-system/network/mesh-groups.mjs',
        'active-system/network/mesh-membership.mjs',
        'active-system/network/gossip-pool-transport.mjs',
        'active-system/network/gossip-bounds.mjs',
        'active-system/network/gossip-vendor.mjs',
        'active-system/network/peer.mjs',
        'active-system/network/peer-pool.mjs',
        'active-system/tools/network-builder/package.json',
        'active-system/tools/network-builder/package-lock.json',
        'active-system/tools/network-builder/build-vendor.mjs',
        'active-system/assets/vendor/gossip/manifest.json',
    ]
    paths += ['codiserver-web-v0.3.0/shared/' + n for n in (
        'PROTOCOL.md', 'MESH_ARCHITECTURE.md', 'MESH_BROWSER.md', 'MESH_WIRE.md',
        'MESH_SUPPORT_SERVICES.md', 'MESH_SCALE.md', 'mesh-policy.json')]
    sources = [record(p) for p in paths]
    registries = [json.loads((ROOT / p).read_text()) for p in paths if p.endswith('acceptance.json')]
    original, previous, current, server = registries
    assert current == server
    assert {c['id'] for c in previous['cases']} <= {c['id'] for c in current['cases']}
    assert all(next(n for n in current['cases'] if n['id'] == c['id'])['requirement'] == c['requirement']
               for c in previous['cases'])
    ladder = (ROOT / 'codiserver-web-v0.3.0/docs/02_BUILD_TEST_LADDER.md').read_text()
    oracles = dict(re.findall(r'\*\*([A-Z0-9]+-\d+):\*\* ([^\n]+)', ladder))
    # These are pointers to inspected witnesses, NOT automatic gate passes.
    candidates = {
        'G00': ['root-live-health', 'root-live-source-sync'],
        'W01': ['root-public-account', 'root-public-cache'],
        'W02': ['root-wan-group', 'root-wan-history', 'root-wan-scope'],
        'W03': ['root-public-terminal', 'root-public-lifecycle', 'mesh-native-vm-terminal', 'mesh-native-vm-lifecycle'],
        'W04': ['root-public-terminal', 'root-public-account', 'mesh-native-vm-accounts'],
        'W05': ['root-public-lifecycle', 'root-public-cache'],
        'S00': ['root-live-health'], 'S01': ['root-live-health', 'root-public-account'],
        'S02': ['root-public-documents', 'root-live-health'],
        'I01': ['root-wan-group', 'root-public-account'],
        'S03': ['root-live-health', 'site-cutover-production-apply'],
        'S04': ['root-live-health', 'site-cutover-production-apply'],
        'P01': ['root-wan-group', 'root-wan-history', 'root-wan-scope'],
        'H01': ['root-public-documents', 'root-public-account'],
        'H02': ['root-public-documents'],
        'M00': ['root-live-health', 'root-wan-scope', 'mesh-pool-acceptance', 'gossip-vendor-rebuild'],
        'M01': ['root-public-lifecycle', 'mesh-host-desktop', 'mesh-native-vm-lifecycle', 'mesh-neighbors-desktop'],
        'M02': ['root-wan-group', 'root-wan-history', 'root-public-lifecycle', 'mesh-pool-acceptance', 'mesh-pool-final-protocol', 'mesh-host-protocol', 'mesh-host-desktop', 'mesh-native-release', 'mesh-native-vm-rollout', 'mesh-native-vm-custody'],
        'M03': ['root-wan-group', 'root-wan-history', 'root-wan-scope', 'mesh-pool-acceptance', 'mesh-host-pool', 'mesh-host-desktop', 'mesh-native-vm-mesh-after-rollout', 'mesh-neighbors-browser', 'mesh-neighbors-legacy-regression'],
        'M04': ['root-wan-group'], 'M05': [],
        'M06': ['root-public-cache'], 'M07': [],
        'M08': ['root-wan-scope'], 'M09': ['root-wan-group', 'root-wan-history', 'mesh-pool-acceptance'],
        'M10': ['mesh-pool-acceptance'], 'M11': ['root-live-health', 'site-cutover-production-apply'],
    }
    # New witnesses retain partial status: online-controller lease maintenance
    # and bounded alternate RTC routes do not prove durable games or 8k gossip.
    candidates['M01'] += ['mesh-lease-route-desktop']
    candidates['M02'] += ['mesh-lease-route-protocol', 'mesh-lease-route-regression']
    candidates['M03'] += ['mesh-lease-route-regression', 'mesh-lease-alternate-routes-r2',
                           'mesh-lease-route-v3-neighbors', 'mesh-lease-route-v3-legacy']
    candidates['M09'] += ['mesh-lease-route-regression', 'mesh-lease-alternate-routes-r2']
    # Hosted APIs now have private installed-service acceptance. This is still
    # separate from Rooms UI/P2P, private message crypto or replica agreement.
    candidates['M03'] += ['hosted-room-core-final', 'hosted-room-browser-final']
    candidates['M02'] += ['hosted-native-release-r2', 'hosted-native-vm-upgrade',
                           'hosted-native-vm-binding-recovery-r1']
    candidates['M02'] += ['hosted-room-code-vm-r1', 'checkpoint-native-release-r1',
                           'checkpoint-native-vm-upgrade-r1']
    candidates['M03'] += ['hosted-native-browser-r1', 'hosted-native-source-core-r1']
    candidates['M03'] += ['hosted-snapshot-r2', 'hosted-snapshot-core-regression-r1',
                           'hosted-snapshot-browser-regression-r1']
    candidates['M03'] += ['hosted-native-browser-checkpoint-r1', 'checkpoint-native-vm-mesh-r1']
    candidates['M01'] += ['hosted-client-source-r4']
    candidates['M02'] += ['hosted-client-native-release-r2']
    candidates['M03'] += ['hosted-client-source-r4', 'hosted-client-core-regression-r1',
                           'hosted-client-proof-regression-r1']
    candidates['M11'] += ['hosted-room-operator-vm', 'hosted-native-vm-binding-recovery-r1']
    candidates['M11'] += ['hosted-room-code-vm-r1']
    # A precise witnessed behavior, not merely a PASS filename or an inherited model.
    direct = {
        'W03-03': ('root-public-terminal', 'two real PTYs preserve independent shell environments'),
        'M03-02': ('root-wan-group', 'alternate valid signature cannot bypass replay floor'),
        'M03-03': ('root-wan-history', 'recovered message fills the gap without a new live delivery'),
    }
    additional = {'W03-03': [
        ('root-public-terminal', 'Close disposes xterm view and only its logical PTY'),
        ('root-public-lifecycle', 'same Linux and shared filesystem survive 182 application opens/closes')]}
    overrides = {
        'G00-02': 'Backend-free configuration belongs to desktop-lab and /desktop/. Connected active-system intentionally uses its declared services.',
        'W01-01': 'Static-only ANON remains a lab/prototype requirement. Active ANON is explicitly server-certified; no anonymous private folder or Linux Internet.',
        'W01-03': 'Local/unvalidated identity labeling remains required in the lab. The active site now has real optional registration/sign-in.',
        'W01-04': 'Anonymous identity and private work stay ephemeral; user-approved verified public caching is explicitly allowed.',
        'W03-01': 'Preserve sizing/compare controls in desktop-lab and /desktop/ only. Active-system must not regain proportion controls.',
        'W03-03': 'User superseded the single serial stream with independent PTYs in one v86 guest. Closing a window closes its shell, not Linux.',
        'W05-01': 'Backend-free extraction is the separate lab. Connected production ANON requires its real issuer and must not silently downgrade.',
        'S01-08': 'User authorized separate file/document-operation, signaling and guest services. They must not become identity-endpoint chat/compute relays.',
        'H01-01': 'Private home authority is now provisioned per immutable account ID, not only an owner. Username/root text grants no privilege.',
        'H01-05': 'Registered users can read only their own authorized UUID homes; no grant to other homes is inferred.',
        'M00-03': 'Production /2 and candidate /3 are distinct negotiated modes. Candidate maintained GossipSub is not a silent reinterpretation of the old max-hops2 star contract.',
        'M00-05': 'User approved build dependencies; visitors install/build nothing. Pinned maintained GossipSub runs in the /3 loopback candidate over the existing pool, with a pinned one-line bounded-source adapter patch. Private MLS remains an unevaluated runtime gate; this is not production/security completion.',
        'M05-01': 'Required feature gate for private multi-hop content. Private mode remains OFF; public routing must not claim end-to-end relay secrecy.',
        'M10-02': 'Supplied 1k/10k/100k simulations remain separate from the requested actual staged8k identity/signature/transport test.',
        'M10-04': '10^10 is an analytical envelope, not a requested live deployment or substitute for8k transport evidence.',
        'M09-01': 'Root /2 has separate-network TURN/TLS443 evidence. Candidate /3 currently has loopback host-candidate RTC evidence only; it still needs its own public/WAN acceptance.',
        'M10-01': 'Candidate /3 has four actual networking browsers, solo/ring/path/partition/rejoin and two shared rooms. This is not the required2/8/32 ladder or8k transport evidence.',
    }
    # No runtime for these obligations is present in the inspected active tree.
    absent = {'M05-01', 'M05-02', 'M05-03', 'M05-04', 'M05-05',
              'M06-05', 'M07-01', 'M07-02', 'M07-03', 'M07-04', 'M07-05',
              'M08-05', 'M10-01', 'M10-02', 'M10-03', 'M10-04', 'M10-06'}
    rows, receipts = [], {}
    for c in current['cases']:
        witnesses = []
        for n in candidates[c['gate']]:
            p = CHECKS / (n + '-result.json')
            if p.exists():
                rel = str(p.relative_to(ROOT))
                if rel not in receipts:
                    value = json.loads(p.read_text())
                    receipts[rel] = {**record(rel), 'reportedStatus': value.get('status'),
                                     'scope': 'Candidate witness; examine exact assertions before relying on it.'}
                witnesses.append(rel)
        row = {'id': c['id'], 'gate': c['gate'], 'requirement': c['requirement'],
               'status': 'required' if c['id'] in absent else 'partial',
               'acceptance': oracles.get(c['id'], c['pass_rule']),
               'candidateEvidence': witnesses,
               'remaining': 'Match all positive AND negative oracles to actual current tests; do not infer a complete gate from these pointers.'}
        if c['id'] in direct:
            proofs = [direct[c['id']], *additional.get(c['id'], [])]
            assertions = []
            for n, text in proofs:
                p = CHECKS / (n + '-result.json')
                value = json.loads(p.read_text())
                matches = [x for x in value.get('checks', []) if text in str(x)]
                assert value['status'] == 'PASS' and matches, (c['id'], n, text)
                assertions.append({'receipt': str(p.relative_to(ROOT)), 'assertions': matches})
            row.update(status='completed', directEvidence=assertions,
                       remaining='Preserve the witnessed current public-profile behavior; this does not pass its surrounding gate.')
        if c['id'] in overrides:
            row['scopeResolution'] = overrides[c['id']]
        rows.append(row)
    result = {
        'version': 'codi-goal-reference-audit/1', 'wholeGoalComplete': False,
        'auditComplete': False,
        'scope': 'Every combined v0.3 case catalogued; v0.2 requirements preserved verbatim. v0.1 uses DIFFERENT and sometimes colliding IDs and is separately namespaced. Direct matching remains incomplete; partial means NOT passed.',
        'sources': sources, 'receipts': list(receipts.values()),
        'counts': dict(Counter(r['status'] for r in rows)),
        'gates': [{**g, 'status': 'partial', 'completeGateClaimed': False} for g in current['gates']],
        'cases': rows,
        'legacyV01Cases': [{**c, 'id': 'v0.1:' + c['id'], 'originalId': c['id'],
                           'status': 'partial',
                           'scopeResolution': ('Local encrypted-account flow was superseded by the user-authorized authoritative SQLite login service; do not reintroduce a parallel local login.'
                                               if c['gate'] == 'G04' else
                                               'Review against later boundary decisions: backend-free lab stays separate; connected active-system has real accounts and independent terminal PTYs.'),
                           'evidence': []} for c in original['cases']],
        'explicitDeferrals': [
            {'status': 'explicitly_deferred', 'requirement': 'Marketplace/payment applications', 'reason': 'User says these are not prerequisites.'},
            {'status': 'explicitly_deferred', 'requirement': 'Graphical game UI', 'reason': 'User chose text moves plus separate chat first.'},
            {'status': 'explicitly_deferred', 'requirement': 'Native ISO/Surface work', 'reason': 'Separate project, outside this browser upgrade.'}],
        'remainingAudit': ['Bind inherited ticket-level commands/negative oracles to original actual receipts.',
                           'Review additional CONTRIBUTING future-app ideas without treating them as current prerequisites.',
                           'Keep live-root evidence separate from reference package model evidence.'],
    }
    out = ACTIVE / 'requirement-audit.json'
    out.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({'output': str(out.relative_to(ROOT)), 'cases': len(rows), 'gates': len(current['gates']),
                      'counts': result['counts'], 'auditComplete': False}))


if __name__ == '__main__':
    main()
