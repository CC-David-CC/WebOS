# Desktop and website cutover

This root-only operator composes the existing native code rollout, signed mount
migration and managed website/Caddy controller. It is an explicit operation,
with no listener, timer, authority-renewal daemon or user-data restore.

An immutable operator bundle contains these three modules, `scripts/site-cutover.py`
and the existing `scripts/native-rollout.py`. The entrypoint requires exact pins
for both its manifest and a protected on-server deployment plan. The separately
sealed mount operator and native SDK remain authoritative for their own files.

The hosting lock covers the whole operation. Code rollout and website deployment
first leave the old mount usable. The mount operator owns its normal instance and
backend locks and maintenance journal. Its `committed` callback changes generated
hosting and verifies the result before that native journal may be removed. A
crash during partial hosting writes, Caddy reload or verification leaves ordinary
native start/signing blocked by the existing maintenance guard. Earlier crashes
at the coherent old mount use the existing code/website recovery mechanisms.

`site-cutover.json` is private root-owned state, not a public app asset or source
artifact. Explicit `recover` must use the same plan. A completed inner mount is
never guessed from a URL or repeated to repair a missing parent receipt. The
parent commits before the native journal is cleared, so that final receipt
recovery verifies the current mount without issuing another authority revision.

Rollback is a new inverse plan against current state. It selects retained website
code and generated hosting, and signs a higher root revision for the old mount.
It does not restore account, authority, publisher, permission, usage or document
databases. The new cache-capable native release can remain installed at hidden
during route rollback so browser cache retirement also works in that direction.

Public maintenance text warns about unsaved RAM and names the destination URL.
It does not save Linux memory or prevent browser Reload/Close. The countdown is
bounded and persisted in the parent operation; recovery does not restart it.

Before production activation, the same coordinator must pass actual private-VM
code/website/native/hosting interruption and forward rollback tests. Merely
exporting this bundle or passing existing component tests is insufficient.
