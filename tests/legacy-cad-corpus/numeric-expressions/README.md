# Signed numeric-expression qualification

The matched R10 control passes. Exact source, runtime, catalog, script and raw-log
hashes are in `signed-r10-receipt.json`. This is a bounded signed desktop proof;
it is not a complete CAD gate or public deployment.

| Control | Result |
| --- | --- |
| Public geometry creation, labeled native formula seed, normal native load | Pass |
| Legacy numeric source drives dependent solid; local constants shadow globals | Pass |
| No-op, invalid input, stale revision, authored undo/redo | Pass |
| Genuine pending Worker reply canceled by Open/Keep editing; late reply inert | Pass |
| Private Script draft, actual Reload with zero dispatch, actual blur apply | Pass |
| Normal Save and exact browser/server synchronization | Pass |
| Visible Close during pending genuine reply; Worker termination | Pass |
| Other account denied file; fresh Files reopen restores source/sketches/body | Pass |
| Native Open remains; no visible Import DXF tool or working removed frame route | Pass |
| Affected DXF public/menu/lifecycle and eleven native Arc regressions | Pass |

`helpers.mjs` owns fresh registered browser contexts, public command dispatch,
normal Files open/save/sync and explicitly read-only model oracles. `fixture.mjs`
first builds actual geometry using public rectangle/extrusion commands. It then
labels its test-only native-file edits establishing the initial symbolic
relationships: global `base/W/H/D`, extrusion length `D`, first sketch dimensions
`W/H`, and second sketch-local `W=30`/`LH=5*2`. The file opens normally through
signed My files and the native project loader. This does not qualify creation of
all initial formula bindings through public authoring commands.

The accepted source stays verbatim legacy numeric, with `isTyped=false`.
Changing globals produces 100×50×20 → 150×75×25, while the local rectangle stays
30×10. Later public recovery and the actual Script UI produce 170×85×28 and
180×90×30. Native constraint definitions, IDs, metadata and local constants retain
their authored intent. Only explicit normal Save changes the persisted file.
The final native server hash is
`8c356747db8cd1cea9bde8004b03ad8d7b6a38cc44895f826aa642debb420c29`.

`lifecycle.mjs` holds a genuine successful production Worker message, retaining
and later delivering the exact original data. It replaces no solver, native
loader, geometry provider or successful result. Starting ordinary File → Open
makes the host lifetime guard invalid while its real unsaved-changes
confirmation remains open. The pending edit cancels; choosing Keep editing
preserves the accepted model. Its late reply stays inert, the Worker terminates,
and another public edit succeeds. Visible app Close is a separate lifetime
cancellation control. The Script dispatch counter observes real Workers only.

Draft Reload, pending-command cancellation and command queues are distinct.
Reload resets an unsubmitted local draft without dispatching a Worker. The
public registry exposes no caller AbortSignal. Another numeric command is not
promised to preempt the current origin-wide Worker lock. Direct core signal
cancellation is separately qualified by the core lane.

Two initial harness assumptions were corrected without a product change. A
rejected geometric replay can refresh opaque numeric/journal revisions while
preserving the complete native model, table, geometry and journal intent. The
control now refreshes revisions and compares all those data except the opaque
revision strings; no-op and draft/Reload still require complete state equality.
An initial second-command preemption expectation observed Error instead of
AbortError. It was replaced by the actual host-lifetime Open/Keep editing flow.
Both earlier logs remain in the private evidence directory, alongside the final
passing log. The earlier Script Reload blur-before-click issue was fixed in the
core UI before this matched build; this signed control uses the real corrected
Reload button and actual pointer/keyboard interaction.

Reproduce with Node 24 and the pinned dependencies in `tests/package-lock.json`
(`npm ci --prefix tests`), making them available from the repository root, for
example with an untracked `node_modules` symlink to `tests/node_modules`. Use a
fresh Chromium CDP context and the exact matched CAD/host bundle. With the
isolated signed fixture running:

```sh
CODI_TEST_URL=http://127.0.0.1:20393/ \
CODI_TEST_CDP=http://127.0.0.1:19329/ \
node test/agent-cad-corpus/numeric-expressions/signed.test.mjs
```

The fixture uses strict CSP, gateway `c0465afe`, SDK `44da83bd` and a fresh
registered account per run. Desktop product source is `120195b1e`; the staged
source archive is `a02677c60` plus these tests, with CAD `a3760b172`. It was built
using the normal app builder and the current runtime asset inventory, without
source maps or obsolete hashed Workers. Only reviewed Files/Text bundles were
added to its catalog. Source, bundled apps, evidence and private temporary
fixture state use the R730 paths
`/mnt/data10tb/codi-numeric-signed-{desktop,apps,evidence,tmp}-20261105`.
Private account databases, keys and dependencies are excluded from Git. All
owned test contexts close in `finally`; fixtures through `20392` and public
hosting remain unchanged.

The public registry retains its 8 KiB JSON argument budget even though the CAD
adapter/core separately bound source text to 64 KiB. This lane uses small
scripts. It does not qualify arbitrary native documents, 64 KiB public payloads,
physical phones, RAM/performance limits, third-party CAD imports, public
full/near-coincident Arc creation or every CAD operation. Native `.jsketcher.json`
remains the editable input/source of truth; supported DXF and core 3MF are exports.
