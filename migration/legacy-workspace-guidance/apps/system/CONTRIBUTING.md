# Building a desktop app

Place an app in `apps/system/<id>/index.mjs` and export a synchronous
`mount(host)` returning `{element, dispose()}`. The element must have the
`window-content` class. Release timers, listeners and workers on disposal;
keep per-window state on the window or in the mounted view. `host.signal` is
aborted on disposal.

Register a new app in the explicit app builder list and desktop menu. App code
is trusted same-origin code, not a sandbox. Use the shared host's account and
storage interfaces; a folder or hidden menu item is not a security boundary.
The build process bundles declared imports and hashes output. Node and npm are
build tools, not visitor requirements. Downloaded dependencies and generated
output stay outside Git.

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

For an account file chooser use `await host.storage.pickFile({extensions, signal: host.signal})`. It returns a My files path or null on cancellation. Read and write through `mirrorFileContext()` and check that the account context remains valid after asynchronous work. Preserve unsaved changes when switching files, and report local saves separately from server synchronization. A PC upload picker is an additional import option, not the account file chooser.
