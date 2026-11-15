# Fresh ksu.codes test deployment

The new test desktop is available at **https://ksu.codes**. Create a fresh account
through Login. The user has identified this site as a test location with test
users only. Old account state was not migrated, reset or copied.

The frontend now selects parent source
`131e36585fa307272cb288f5800486b021c8739b`, WordCraft
`0d48f9a1bd5a2bb88d8431760a14b0ba55161563` and shared egui
`2d0ae4b4270e76c431fd62d3512237579ed6c26f`. Its33 payload files total
95,791,308bytes, plus the release manifest, hash-verified locally and on the host. The backend remains
release `217ececf045f5da98a4dcfe37b6d599c855d9d17`: all three backend component
pins, the server script and dependency lock match the new composition. Its
process, instance identity, issuer and account state were preserved.

The following original hosted workflow checks passed before this renderer-only
update. The Calculator, Files, Text, host client bundle and storage worker have
identical served bytes. The new renderer also passed the hosted checks below.

| Hosted workflow | Result |
|---|---|
| Calculator through authenticated launcher, independent instances | PASS |
| Files folder/upload/rename/move/download/delete/reload | PASS |
| Exact downloaded bytes and second clean browser retrieval | PASS |
| Text two-document save/reopen, Save As, unsaved Cancel/Save | PASS |
| Text reload and second clean browser retrieval | PASS |
| WordCraft new heading, paragraph and list | PASS |
| WordCraft account save, Files reopen, reload, second-context formatting | PASS |
| New renderer: two rounds of three concurrent editor starts | PASS (6/6) |
| New renderer: account save/reopen, stale conflicts, close guards, Save As/PDF | PASS |
| New renderer: heading/list authoring, Files reopen, reload, second context | PASS |

The earlier renderer failed both rounds of the three-editor startup matrix:
the third browser WebGPU adapter request remained pending after WASM loaded.
The new shared renderer bounds optional adapter discovery when WebGL fallback
is allowed. It passed three deadline/cancellation unit checks, a WASM compile
check, a complete isolated build, six local editor starts across two rounds,
account/conflict tests and formatting tests. Clean-checkout authoring passed
with the original workspace, primary assembly and recovery source hidden and
external networking disabled. An initial isolation failure hid Chromium's X11
socket and prevented WebGL creation; its failure reports and focused diagnostic
probes are retained. The corrected isolation preserves that socket; assertions
and product behavior are unchanged. Hosted regression qualification of this
new renderer **passed**: six starts across two rounds, with third-editor startup
of20.4 and20.3 seconds; account/conflict checks in three browser contexts; and
formatted authoring with save/reopen, reload and second-context retrieval. No
page errors were reported. The120-second host timeout was unchanged.

These are actual browser requests over HTTPS to the remote server. They do not
qualify every legacy app, delegated agents, or a physical second client machine.
The overall suite rebuild remains incomplete.

## Operation and rollback

`webos-rebuild-test.service` runs the new process as the existing deployment
user, listening only on127.0.0.1:38140. It is enabled for boot, with no automatic
restart policy. Its new private state is separate from release assets and from
all old service state. The backend was installed offline from pinned wheels on
Python3.12; dependency and packaged-source import checks passed.

Only the ksu.codes Caddy block changed. Caddy now serves the new immutable
public tree directly and proxies account, gateway, configuration, issuer and
health routes to the existing backend. The template is
`deploy/ksu-test-static.caddy.in`; replace its explicit public-root placeholder
with a verified immutable release directory. No backend restart was needed.

The current public tree is
`/srv/webos-rebuild-test-public/cde3f9a577c1f8fb6964c7eca20afc4572a195734662391dc4bf7f1f09f464d4/public`.
Its manifest includes file hashes and exact backend compatibility checks.
The current route rollback directory is root-only
`/var/backups/webos-test-static-131e365-20261115/` on box-webhost. Both before
and candidate configs validated. Activation preserved file owner/mode and
reloaded Caddy; health instance and issuer bytes, beta page bytes and checked
service PIDs stayed unchanged. Index, client and new WASM hashes were verified
over HTTPS with the required cross-origin isolation headers.

To roll back this frontend update, verify the current config matches the
candidate hash recorded in that directory's `route-plan.json`, restore its
before file with the recorded owner/mode, validate, then reload Caddy. Preserve
the backend and account data. The previous initial-route backup remains at
`/var/backups/webos-test-route-217ececf-20261115/`; that earlier rollback would
return ksu.codes to its former application and is a different action. Do not
replay staging scripts over existing destinations.

Private evidence and exact commands are in
`run-20261115-15-graphics-startup/` and the earlier
`run-20261115-14-test-deployment/` under the private migration directory. Browser
reports and screenshots use disposable test accounts; credentials and account
files are not committed. The original laptop workspace and local recovery
remain preserved. No external Git publication was performed.
