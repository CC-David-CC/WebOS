# jSketcher upstream integration

The goal is a coherent jSketcher application for the signed-in ksu.codes
browser desktop. This is a work list, not a release claim. Preserve My files,
per-window state, browser security policy and disposal while reviewing upstream
work as connected features. Native Electron/Tauri packaging is outside this
website integration.

Current references inspected 2026-11-02: upstream `main` `c1905c4f`, upstream
`dev` `ca3e2b19`, and fork `webos-integration` `ceac5a1b`. Upstream `dev` has
95 commits not in `main`; the branches diverged, so integration requires more
than copying its current tree. The user's fork is on box-git and GitHub. Source
refs for [PR #217](https://github.com/xibyte/jsketcher/pull/217) and
[PR #220](https://github.com/xibyte/jsketcher/pull/220) are also preserved on
box-git under `reference/upstream-pr217` and `reference/upstream-pr220`.

| Work | Current state and required evidence |
| --- | --- |
| Polynomial correctness ([#216](https://github.com/xibyte/jsketcher/pull/216)) | Contributor change and regression are in the fork and local host candidate. Correctness test and desktop/emulated-phone account modeling workflow passed; not deployed. |
| Spline tools ([#217](https://github.com/xibyte/jsketcher/pull/217)) | Separate research worktree; interpolation, control-vertex, open and closed curves, geometry conversion, serialization and English comments are being reconciled. Test degenerate inputs, endpoints, editing and constraints, independent windows, save/reopen, actual OCC and extrusion. Preserve existing shapes and construction geometry. |
| Sketch history ([#220](https://github.com/xibyte/jsketcher/pull/220)) | Separate research worktree. Proposed redo could discard new edits, and reversing certain patches failed; a candidate addresses both with checked directional patches and bounded history. In-place sketch loading can skip failed objects: transactional recovery, active tools, real Chromium workflows and lifecycle still need verification. |
| Marquee selection ([#220](https://github.com/xibyte/jsketcher/pull/220)) | Separate research worktree. Reconcile selection, panning, cancel/release outside the canvas, zoom, touch and listener disposal. Not shipped. |
| Autosave ([#220](https://github.com/xibyte/jsketcher/pull/220)) | Upstream writes localStorage on timers. Design a host-My-files-aware equivalent with clear save/sync state, per-account isolation, version conflicts, lifecycle cleanup and no false recovery promises. |
| Existing model correctness and IDs | Review Bézier deserialization `5c915a6a`, point-based holes `0f547064`, `bf8f9652`, `0dea626e`, and related primitive/pattern/mirror IDs `ee4a19e7`, `77f75de7`, `b5dc6681`, `f8443e03`, `92cf2ce9`. Test older files, tilted planes, reconstruction and references. These commits have dependencies and overlap with spline work. |
| DXF workflow | Review `2fa28662`, `22cdafd3`, `0066b414`, `b809dcfe`, `322d47f8` and dependent parser changes as a group. Test representative fixtures, My files, browser policy, attribution and bad input. |
| Camera and touch | Review zoom `2c7fca94`, view-cube work `9f287e77`, `b96ba9d7`, `817b3fe3` and touchpad work `ecc9491b` through `9d007cd1`. Adapt to the embedded desktop; do not use an unchecked cross-window message handler or assume a camera patch matches our separate raycaster fix. |
| Geometry and engine | Review tessellation `10295d0e`, geometry operations including simplify and move-body, and boolean-engine update `2326c75b` with their dependencies. Qualify actual OCC outputs, tiny/large models, existing files, ABI, exact source and license notices before distributing an updated WASM binary. |
| Experiments | Keep PR #217's voxel and generated-sample work distinct from the spline feature. Its original source is preserved in the reference branch; evaluate whether and how it belongs in user-facing tools. Do not silently add browser downloads or hidden account storage. |

For each feature, use actual Chromium desktop and emulated-phone workflows,
keep physical-device claims separate, test save/close/reopen and failures,
and repeat integration checks after combining branches. A temporary candidate
or passing isolated test is not evidence of live release or manufacturing
accuracy. Full dependency and corresponding-source review remains open.

## Required full validation follow-up

The user explicitly requested that we return and properly validate **every**
carried-forward feature. Keep this work open after the first integration pass:
check each feature individually and in combination in the actual ksu.codes
browser desktop, including representative and edge-case geometry, existing-file
compatibility, My files save/sync/reopen, account isolation, multiple windows,
undo/redo, lifecycle and error recovery. Check Chromium on desktop and
phone-sized layouts; record physical-device and hardware limitations separately.
Track failures and feature gaps rather than treating a focused smoke test or an
upstream claim as full validation. Requalify after combining changes or updating
the geometry engine.

## Closed upstream PR review

Reviewed the closed-PR list on 2026-11-02. Closed does not imply merged into our
fork; check each destination branch and current source. [#204](https://github.com/xibyte/jsketcher/pull/204)
addresses Escape during dimension creation, but its submitted patch can delete
unrelated selected objects; adapt and test cancellation instead. [#190](https://github.com/xibyte/jsketcher/pull/190)
proposes DXF layer colors; test color parsing, defaults, round trips and source
attribution before adoption. [#218](https://github.com/xibyte/jsketcher/pull/218)
is a broad community fork with camera and editing ideas; review features in
small pieces against the host and geometry changes rather than applying it as a
single patch. Its tessellation fallback can hide missing geometry and needs
explicit error handling. Some older merged DXF work, including #180-related
dimension support, is already substantially present; validate actual output
rather than assuming complete compatibility. Large divergent branches and old
native packaging are references, not automatic dependencies.
