# Signed numeric-expression controls — prepared

This directory is a new bounded qualification lane, not a passing receipt yet.
Wait for the root's matching combined CAD runtime and desktop host pins before
running it or claiming integration. Desktop base `120195b1e` registers the public
`inspect-numeric-expressions` and `apply-numeric-expressions` adapters and removes
the WebOS DXF import route. CAD input is native project saves only; DXF/3MF remain
exports. Prior DXF fixtures and their evidence must stay unchanged.

The planned control uses public rectangle/extrusion creation and normal native
Save. It explicitly seeds the first formula references into that synthetic
native file, then opens it through signed My files and the normal project
loader. Accepted legacy numeric scripts must drive the dependent model while a
second sketch's local constants shadow global names. Public edits, refusals,
no-op, undo/redo, the real component-local Script draft/Reload/blur behavior,
normal Save/server sync, cross-account denial and fresh Files reopen are tested.

Pending cancellation and draft cancellation have different contracts. Reload
resets an unsubmitted local draft; it is not an abort API for a running command.
The current public command registry has no caller AbortSignal. The signed lane
will use visible window Close and a genuine held Worker response for host
lifetime cancellation, and test a superseded candidate through public commands
where supported. Direct core AbortSignal tests remain separately attributed.
No fake successful Worker replies or private geometry-authoring path is allowed.

Prepared implementation: `helpers.mjs` owns fresh registered contexts, public
command dispatch and ordinary Files open/save/sync. `fixture.mjs` labels the
first native-file formula/local-constant edits. `lifecycle.mjs` holds only a
genuine successful production Worker message, then exercises public candidate
supersession or visible app Close before releasing that original message. The
public registry has no explicit caller AbortSignal; this does not claim one.
`signed.test.mjs` joins those with the real Script draft and Reload controls.
The passive UI counter observes dispatch only, using genuine Workers.

All scripts are syntax checked only at this preparation checkpoint. Formula
sources are small; the registry's existing 8 KiB JSON argument cap still applies,
even though the CAD adapter/core separately bound source text to 64 KiB. This
lane does not qualify large source payloads, arbitrary native models, physical
phones, third-party imports or public deployment. The matched build must contain
the corrected Script Reload behavior (`data-expression-reload="true"`).
