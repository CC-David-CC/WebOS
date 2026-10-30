# Original signed chat proposal recovery —2026-10-25

Externally reachable development, not a public launch. Root desktop,/blog/,
backend-free /desktop/ and other hosted sites remain intact.

Current native25/b97dce3bb9956d5ed352f238b84d8f0797e18650f315a687f69d4e7eb3718b8d,
worker081bd143a37d486d1984d92389c0b1eb649563d052e3e793bdbd21de7542acdf;
operator53aa9930 unchanged. Sourcee3f3127fd9205c527ec4c6c39c1101460751d845,
reader-recovery-producer-r1:468declared files/source-proof
853b999c51aa445fbcb60a1d11e129a5baf584fc1bb9f13a2a50c3c757bb218c.
SDK298files/40modules/57native/all7app bundles unchanged; SDK update only enables
proposalRecovery:true in desktop construction. Worker graph2/schema1 changes
only contract.py/store.py from870. No account/ACL/private-file/guest-code change.

An unsent signed chat proposal stays pending. Save original proposal downloads
its public signed event/grant envelope, without login tokens/private keys.
Loading a saved proposal does not send it. The original anonymous session or a
fresh login of the same registered account can explicitly submit an expired
original against the current accepted head. Server checks fresh issuer proof,
current membership, old grant/signature/scope, sequence dependencies and short
consent binding event ID/old grant/requester/current predecessor. The expired
grant proves old authorship, not current permission. App consent expires in25s;
server maximum is30s. Original ID/signature and
old author floor remain unchanged. Conflicts/gaps/bans/wrong account/signatures
fail. Duplicate acceptance returns the prior receipt; no write automatically
retries. A lost response is resolved by signed lookup before another submission.

This is chosen-controller chat acceptance, not independent replica consensus,
proof-of-work correctness/finality, general graph dependencies or durable chess.
Recovered history stays historical and is not dispatched as live chess/chat.

SourceAPI12 and current bundled app download→reload→nativefileimport→same-account
newSID→simulated15day recovery/lost reply/disposal workflow14 PASS. Exact old870
artifact in a separate interpreter/real HTTP reads the recovered receipt and
signed checkpoint, appends a normal fresh-session message, then reopens with
new081 retaining both original floors/key/data:4 PASS. Initial rollback probe
expected a tail cursor in a snapshot response; retained FAIL, corrected signed
snapshot assertion passes. IndependentSDK298/cache232 byte rebuild PASS.

Actual live sequence uses existing protected hosting/controller locks/native
and backend journals:stage→SDKfirst→backend→verify4 PASS. Both earlier currente007
and rollbacke516 already verified recovered receipts before any producer activation.
Root publishercd875e72 under /srv/codi-connected/recovery-producers reuses exact
636ddac backend transition with retained nativee007 controller. No data restore,
root minting, new ingress/ports/firewall, Caddy changes, VM gate or boot changes.

Actual ordinary-TLS full-Linux public workflow9 PASS: failed dispatch leaves
pending/count0; real app downloads proposal; page reload/new login SID; another
message becomes accepted first; real origin expiry passes (no clock override);
native file import stays pending; explicit Submit original again appends once;
actual SQL receipt keeps exact original event bytes and original author SID.
Both old/new author floors1/count2. Fresh anonymous reader verifies recovered
history without membership. Test account disabled and owned browser closed.

After recovered data existed: managed previousSDK/previousworker/verify3 PASS;
a fresh full-Linux anonymous desktop using e007/870 verifies/displays the same
original once, without writer membership,4 PASS. Re-upgrade SDK/backend/verify3
and fresh b97/081 anonymous read4 PASS. No restoring SQLite, keys or old floors.
Current UI17/36reopens/workspace drafts/identity/reload/phone-layout PASS. Final
health-r3 verifies298installed/133externalprototype/root/blog/all10sites/security/
Root4 and66test accounts (original38 retained). Latest2 QA policies independently
verified disabled in actual DB; local owned contexts/jobs0, normal Chrome untouched.

Current nativeb97+rollbacke007, worker081+rollback870, operator53aa are retained.
Superseded nativee516, workers3907/3a6d and operator417 removed with exact pins,
active-process/unit-reference checks and unchanged state/config/PIDs/hosting.
Cleanup sourcec8ffed76ea20ffa21221bce8535aa27b7e399296; server checkout stayse3f3127.
Old sourcee516 packet/3a6d worker unmaterialized; compact Git history/current code
and operator kept. First sparse check failed only because tracked files vanished
but an empty directory remained; verified empty remnants and stray --no-cone
pattern arguments were then removed. No runtime/private data change in that fix.

Final native configfa0bb0d8301207b5585afaddf4f3582179782fcefd25be1913d450841df576ef,
PIDs issuer3658696/steward3656435/guest3656436. Room3658086/proxy3658093;
file1460455/proxy1460457 unchanged. Root4/fence4 expiry2026-10-26T10:26:06Z,
explicit renewal only. Native units disabled boot; bootstrap stopped. Hosting/
egress436096d7/TURN quotas/forwarding0 preserved. Caddy never hand-edited.

Moonpie remains offline with the previous21215/50737/profile fixture unverified;
see recovery-reader.md and moonpie-browser-fixture.json. No complete outside-WAN
pass for this release is claimed. Historical512 SDK138/16Chrome PASS16 and2048
admission FAIL retain their own scope; this rollout is not an8k/scale acceptance.
Next: improve actual2048 and larger transports, redundant layers/islands, independent
replicas, durable chess and audit/operations. Whole goal remains ACTIVE.
