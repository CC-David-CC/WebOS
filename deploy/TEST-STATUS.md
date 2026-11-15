# Fresh ksu.codes test deployment

The new test desktop is available at **https://ksu.codes**. Create a fresh account
through Login. The user has identified this site as a test location with test
users only. Old account state was not migrated, reset or copied.

The served release selects parent source
`217ececf045f5da98a4dcfe37b6d599c855d9d17`; its application/component pins include
WordCraft `5ee1726037e6ff97ae4f69d46213ef75a32e0c83`. Later parent commits add
service definitions and test/reporting changes, not different served app bits.
The immutable package contains55 files totaling105,646,592bytes. All files were
hash-verified locally and again on the target before installation.

| Hosted workflow | Result |
|---|---|
| Calculator through authenticated launcher, independent instances | PASS |
| Files folder/upload/rename/move/download/delete/reload | PASS |
| Exact downloaded bytes and second clean browser retrieval | PASS |
| Text two-document save/reopen, Save As, unsaved Cancel/Save | PASS |
| Text reload and second clean browser retrieval | PASS |
| WordCraft new heading, paragraph and list | PASS |
| WordCraft account save, Files reopen, reload, second-context formatting | PASS |

The supplemental three-simultaneous-editor hosted test remains **OPEN**: two
editors loaded, a confirmed save and stale-revision rejection worked, but the
third editor timed out during startup. The failure is retained for diagnosis;
it does not invalidate the separately passing two-context authoring test, and
it is not reported as a full concurrency pass. No assertions were removed.

These are actual browser requests over HTTPS to the remote server. They do not
qualify every legacy app, delegated agents, or a physical second client machine.
The overall suite rebuild remains incomplete.

## Operation and rollback

`webos-rebuild-test.service` runs the new process as the existing deployment
user, listening only on127.0.0.1:38140. It is enabled for boot, with no automatic
restart policy. Its new private state is separate from release assets and from
all old service state. The backend was installed offline from pinned wheels on
Python3.12; dependency and packaged-source import checks passed.

Only the ksu.codes Caddy site block was replaced. The prior configuration is
preserved root-only at `/var/backups/webos-test-route-217ececf-20261115/` on
box-webhost, with before/candidate SHA256 records in `route-plan.json` and an
activation receipt. Both configurations validated before activation. Caddy was
reloaded without a process restart. The beta site block and beta page bytes
were verified unchanged; checked existing service PIDs remained unchanged.

For rollback, first verify the current configuration still matches the recorded
candidate hash. Restore the recorded before file with its original ownership
and mode, validate it, and reload Caddy. Do not overwrite a concurrent config
change or remove new account data. The new test service can be stopped
separately if rollback is needed. Do not replay one-time staging scripts against
existing destinations.

Private evidence and exact commands are in
`run-20261115-14-test-deployment/` under the private migration directory. Browser
reports and screenshots use disposable test accounts; credentials and account
files are not committed. The original laptop workspace and local recovery
remain preserved. No external Git publication was performed.
