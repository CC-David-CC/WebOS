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
