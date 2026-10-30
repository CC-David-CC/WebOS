# System-served desktop applications

These folders are the source used by the app builder: calculator, files, help,
terminal, text, image-editor, document-editor, pdf-viewer, spreadsheet, data-explorer, audio-editor, grid-tools and gcode-preview. Background libraries include ffmpeg, wavesurfer, tone and zip. Each exports `mount(host)` and returns an element and a
`dispose()` callback. Shared desktop services supply identity, storage and the
Linux terminal. The app builder packages only explicit entries and dependencies.

Chat, Chess and peer Rooms were removed from this simplified branch. The live
site and other branches are separate and are not changed by this worktree.

## Diagramming, office and shared tools

The Office menu contains Text Editor, Document Editor, Spreadsheet, Data
Explorer (Perspective), and PDF Viewer. Diagramming contains Excalidraw,
SVG-edit and diagrams.net, each with its own app folder. Their `.excalidraw`,
`.svg` and `.drawio` files use the account's Files storage; the browser mirror
and server sync use the same file service as other apps. Excalidraw's own
React dependencies stay inside its bundle. diagrams.net is pinned to a source
commit: run `python3 apps/system/diagrams-net/prepare.py` at build time to stage
its upstream files before running the public-app builder. SVG-edit similarly
has its own `prepare.py`.

Replicad's first interface creates parametric boxes and cylinders as STL or
STEP files. OpenCascade runs in a browser worker; this interface is a starter,
not a general purpose CAD editor. Its upstream license is retained in the
built bundle.

The disabled entries in System Tools are capabilities other apps call through
`host.tools`, not separate windows. `loadMermaid`, `loadECharts`, `loadPlotly`,
`loadPdfme`, `loadMapLibre` and `loadTransformers` load their libraries on
first use. MapLibre requires map data and a style; none is bundled by default.
Transformers.js uses the browser WASM runtime and blocks remote models by
default; an application must provide a compatible local model before inference
can work. These libraries do not make an editor, map or AI model available on
their own. They are bundled locally for the browser.

A new account starts with no open windows. Returning users get their last
window layout and saved file paths back on the same browser. Unsaved content,
active terminal processes and state inside embedded third-party editors are
not restored automatically; save work in Files before leaving.

## Python in the browser guest

The local guest can include i386 CPython 3.11 and the pinned static uv 0.13.6
binary. This is the existing BusyBox-based v86 Linux image with Python added;
it is not a complete Debian installation and does not provide apt. The local
preview has guest Internet disabled, so uv cannot download packages there.
The guest filesystem is temporary and is separate from account Files.

To rebuild it, prepare the same i386 Debian source root used by the guest build
and the verified uv i686 musl binary, then run:

```sh
python3 active-system/scripts/build-browser-initramfs.py \
  --guest-root /path/to/debian-root \
  --python-uv /path/to/uv \
  --work-dir active-system/.build/python-image-root \
  --output active-system/.build/python-image.cpio.gz
```

The builder checks the uv binary SHA-256 and reports the image hash. The file
and its hash in `assets/terminal/v2/image.json` must match before staging.

## Python Notebook

Programming → Python Notebook — Browser uses JupyterLite 0.8.6 with local Pyodide 314.0.6.
Its default kernel is browser Python. NumPy, pandas, SciPy and Matplotlib and
their required local wheels are staged for on-demand use. The first Save to
Files chooses the account `.ipynb` path; subsequent edits synchronize to that
file, and existing `.ipynb` files open from Files. JupyterLite's own browser
storage is scoped by account. The Linux Terminal shortcut opens a separate v86
shell; the Linux notebook entry is disabled until its kernel bridge is ready.

To prepare the notebook assets, install `requirements-build.txt` into a
build-only environment and run `python apps/system/notebook/prepare.py` with
that environment's Python before running the app builder. The preparation
verifies the Pyodide archive, package wheel hashes, and pinned comm wheel.

JupyterLite's JSON-schema validator dynamically compiles JavaScript. The local
preview grants `unsafe-eval` only to the notebook's static document and worker
paths; the rest of the desktop keeps its existing strict policy. These notebook
frames share the desktop origin and are not a security boundary for untrusted
notebooks. Do not assume this local-only policy is installed in another server
or use it as a substitute for isolating untrusted code on a separate origin.

## Files and temporary Linux storage

Files offers **My files**, the browser-first account storage synchronized to the
server, and **temp_linux**, the guest's separate temporary home. Linux files
reset on reboot and do not automatically synchronize with My files. Use **Copy
to account** to open a Linux file in another app. New folder, New file and
Upload are in Files' right-click menu.
