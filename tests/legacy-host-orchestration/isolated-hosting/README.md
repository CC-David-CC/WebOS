# Historical isolated-host orchestration tests — port before execution

This parent-owned reference area preserves41 unchanged Python source paths and
their52 relevant commits. Forty paths came from the captured isolated-host test
directory. `historical-inputs/native-continuity-fixture.py` is the distinct older
fixture from which the signed-native fixture was copied; both existed at capture
and retain separate identities. No source body or assertion was rewritten.

These drivers exercise old namespace, process, Caddy, systemd, release, issuer,
file-assembly and controller behavior. Some act at module import time. They are
not installed, imported or registered by supported WebOS test/build commands.
Do not execute them, run broad test discovery, install their old services or
follow their deployment locators. Current Accounts/Storage remain the authority.

Before any deliberate port, review each driver's side effects, authorization,
fixture/input closure and imports. Replace obsolete locators through actual
public interfaces in a separate functional change. Use disposable private
accounts and state; never import production credentials or account documents,
fall back to the old workspace, simulate missing persistence or weaken assertions.
Component-specific tests should acquire the proper component owner when ported.

Verification covers exact source bytes, Git executable modes, original scoped
index/working state, recovered state, all51 retained historical Python blobs,
author/committer/message fidelity, independent Git integrity and isolated restore
of all41 current files. Syntax and bounded credential screening passed; no old
driver ran. This is source preservation, not runtime acceptance or complete
external-publication clearance. Private phase82 retains source/commit maps and
commands; see `migration/ISOLATED-HOST-TEST-SOURCE.md` in the parent.

One additional unchanged browser driver, `real-backend-browser-test.mjs`, is preserved with its history after bounded review of its explicit disposable fixture credential and loopback origin mapping. It remains unexecuted and unregistered; do not reuse old browser flags or run it without a deliberate isolated fixture/public-interface port. See migration/HOST-REFERENCE-INPUTS.md.
