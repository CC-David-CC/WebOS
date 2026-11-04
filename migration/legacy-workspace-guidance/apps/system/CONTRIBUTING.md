# Building a desktop app

Place an app in `apps/system/<id>/index.mjs` and export a synchronous
`mount(host)` returning `{element, dispose()}`. The element must have the
`window-content` class. Release timers, listeners and workers on disposal;
keep per-window state on the window or in the mounted view. `host.signal` is
aborted on disposal.

File-operation admission belongs to the mount, through
`host.documentOperations`. Do not create an app-private competing controller.
Call `begin('load' | 'save' | 'export')` synchronously before a picker,
confirmation, serialization, read or write. Null means busy, not permission to
queue a retry. Every button, menu, shortcut and agent command must enter the
same guarded action. Include initial/retry loads and Save As dialogs; pass the
existing token to nested helpers instead of beginning again. Finish in `finally`.

The host shares active claims among windows in the exact account session.
Use `mirror:` plus `context.path(path)` as the canonical document key; untitled
documents have no key. Acquire a selected path with `token.claimDocument(key)`
before accessing it, and refuse false. After a successful load/local save call
`token.setDocument(key)`. Save As holds both old and new paths until completion.
Idle windows may share a file; unrelated files remain usable. These claims do
not replace authorization or cross-tab/device expected-version checks.

Render Save availability using `bindControl` or `subscribe`/`busy`; embedded
editors must update native action state too. Disabled controls alone are not a
guard. Pass `token.signal` to cancellation-aware work and recheck
`token.current()` plus account/document validity after awaits. Apps retain
serialization and dirty-revision handling: an older save cannot mark newer
edits clean. Local durable completion ends busy without waiting for background
server sync. The controller retains no file bytes.

See `docs/research/save-busy/CONTROLLER-20261104.md` and its app audit for
migration status. Shared-helper tests do not qualify actual app workflows.
Unqualified apps stay on beta; promotion to main requires end-to-end evidence.

Register a new app in the explicit app builder list and desktop menu. App code
is trusted same-origin code, not a sandbox. Use the shared host's account and
storage interfaces; a folder or hidden menu item is not a security boundary.
The build process bundles declared imports and hashes output. Node and npm are
build tools, not visitor requirements. Downloaded dependencies and generated
output stay outside Git.

Some apps request shared tools from the host rather than importing them. The
standard selected-app builder includes CodeMirror when Text is selected; its
pinned packages must still be installed with
`npm ci --prefix apps/system/codemirror --ignore-scripts`. Custom source or entry overlays are
responsible for selecting their own host-loaded tools.
The standard builder also stages Files’ hash-checked Chonky patch automatically;
install the shared builder dependencies first. Custom overlays handle their own
preparation.

An app may declare its own pinned `package.json` and lockfile in its folder;
run `npm ci --prefix apps/system/<id> --ignore-scripts` before building. The
builder resolves that app's `node_modules` first and bundles dependencies only
into that app. `app.json` may declare an `inject` array of app-local JavaScript
files for build-time shims. Dependency licenses are included in each bundle.

An `app.json` can also declare packaged workers and assets. A reviewed
`patches` entry may replace one exact string in an app-local dependency only
when its complete SHA-256 matches; use this sparingly and explain the reason.
The PDF viewer uses this to prohibit PDF.js's dynamic fallback worker. The
builder permits small embedded PNG/SVG CSS data URLs but rejects external URLs.
Document Editor delegates PDF preview to the independent PDF Viewer via the
host; apps communicate through host services, not each other's private state.

Background media processing is available through `await host.tools.createFFmpeg()`.
The returned instance has `run({input, inputName, outputName, args, timeout})`
and `dispose()`; the host also disposes it when the app view closes. Data stays
in the browser unless the app explicitly saves it through the file mirror.

Audio tools are available as `await host.tools.createWaveSurfer(options)` and
`await host.tools.loadTone()`. The host destroys WaveSurfer instances with the
view; apps must dispose their own Tone instruments and scheduled audio events.
Use browser account-mirror files for inputs and outputs. The AudioMass editor is
a separately packaged app; see `audio-editor/README.md` for its prepare step.

ZIP operations are shared through `await host.tools.loadZip()`. Grid.Space's
Kiri:Moto and Mesh:Tool share one packaged system app; see `grid-tools/README.md`
for its pinned preparation step and file bridge. These tools' browser workspace
state is separate from account-mirrored Files; exports must be saved explicitly.

For an in-app confirmation use `await host.ui.confirm(message, {title, confirmLabel, cancelLabel, danger, signal: host.signal})`. It returns `true` only when the user accepts; Escape, cancellation and app disposal return `false`. Recheck the current account, document and any captured versions after awaiting the answer. Do not use synchronous browser `confirm()` for new application workflows.

For a short text entry use `await host.ui.prompt(label, {title, value, confirmLabel, cancelLabel, signal: host.signal})`. It returns the entered string, including an empty string, or `null` on cancellation or disposal. Validate the value and recheck the account and destination after awaiting.

For an account file chooser use `await host.storage.pickFile({extensions, signal: host.signal})`. It returns a My files path or null on cancellation. Read and write through `mirrorFileContext()` and check that the account context remains valid after asynchronous work. Preserve unsaved changes when switching files, and report local saves separately from server synchronization. A PC upload picker is an additional import option, not the account file chooser.

CodeMirror is available lazily via `await host.tools.loadCodeMirror()`. Each
consumer owns the result of `createEditor(...)` and must destroy its view and
ignore late loading after disposal. Do not share mutable view/document state.
JupyterLite retains its own bundled CodeMirror and JupyterLab integration.

A desktop-owned `host.ui.enableKeyboard()` capability lets an app explicitly
request the on-screen keyboard when the user taps its keyboard control. It
changes the desktop input mode; it does not grant guest pages access to host
services. Use it only for a user-initiated text-input action, and clean up any
app-owned input bridge on disposal.

For a destination folder, `await host.storage.pickFolder({signal: host.signal})`
returns an account-backed My files folder path or null on cancel. It never
selects the temporary Linux filesystem. Join a validated filename with the
folder using the current mirror context; continue to pass the correct expected
version to writes and handle collisions. Check the window and account are
still valid after the picker resolves.
