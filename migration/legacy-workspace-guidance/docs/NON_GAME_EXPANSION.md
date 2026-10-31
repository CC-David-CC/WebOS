# Non-game desktop expansion

The user requested the listed non-game, non-XR/AR apps and capabilities be
integrated with the Simplified desktop. Games and XR/AR are being developed
separately by the user. This is a working scope, not a claim that these features
already work. Treat listed engines as candidates, verify their browser support,
licenses, build size and maintenance before adopting them, and record any
replacement or unavailable capability in `DEFERRED_APP_FEATURES.md`.

Each app needs its own workflow review: account-scoped My files where relevant,
explicit import from the user's device, local-first save and server sync, phone
and desktop controls, cleanup on close, and honest limitations. Load heavy
libraries on demand. Do not add third-party account prompts; where the user
explicitly connects a provider, credentials and permissions need their own design.

## Existing starting points

- Files, xterm terminal with temporary browser Linux, CodeMirror text editor,
  Tiptap Document Editor, Jspreadsheet, PDF.js Viewer, Pyodide/JupyterLite
  Notebook, DuckDB/Perspective Data Explorer, Filerobot Image Editor, SVG-edit,
  Replicad, Kiri:Moto, AVR8js, RP2040js, and CircuitJS exist but remain under
  app-by-app review. CircuitJS is not ngspice. Circuit Lab/ngspice and PCB
  tooling exist as source/probes and are not yet proven integrated apps.
- WaveSurfer, Tone, MapLibre, Plotly, Transformers.js and zip.js are existing
  shared tools. Three.js is an internal dependency of 3D printing tools, not a
  general shared tool. CesiumJS is not currently packaged as a shared tool.
- Trystero, WebTorrent, Yjs, TanStack Virtual and ONNX Runtime Web are being
  added as disabled lazy tools; no collaboration, transfer or model is enabled
  just by installing them. Verify actual rollout and consumer support before
  marking any of them complete.

## Requested work remaining

- **Reading and feeds:** Readability.js, an RSS/Atom parser, a News Reader,
  Podcast Player, E-book Reader (evaluate foliate-js and epub.js), and a comic
  archive/image workflow. Build a usable feed interface with TanStack Virtual;
  AI is optional and must not be required to read. Integrate source fetching
  with the existing browser/server network policy and account files.
- **Media:** video player (evaluate Shaka Player, Video.js and hls.js), music
  player (Howler), Photos gallery (PhotoSwipe; evaluate lightGallery), audio
  and music workflows, and video editing (evaluate WebAV/FFmpeg). Browser Canvas,
  MediaDevices, MediaRecorder and WebCodecs are browser APIs, not packages;
  check device support and explicit user permissions before using them.
- **Communication:** user-connected email providers, PostalMime and JMAP
  clients; chat, video calling and file sharing. Provider APIs are user supplied;
  secure credential handling, CORS, signaling, account access, privacy, and
  connection cleanup must be designed and tested before enabling a service.
- **Productivity:** Calendar (FullCalendar), tasks/Kanban (SortableJS), and
  notes integrated with existing document/text tools and account storage.
- **Science and engineering:** complete analog/SPICE, PCB, and MCU workflows;
  add math input/calculation/rendering (MathLive, math.js, KaTeX), evaluate
  GeoGebra and custom browser-WASM simulations, and a physics playground
  (Rapier). Simulations must distinguish modeled results from hardware tests.
- **Maps and automation:** usable Maps app based on MapLibre; evaluate
  OpenLayers, Leaflet and CesiumJS for appropriate mapping uses; MQTT.js for
  user-selected home-automation connections. External map tiles and MQTT
  servers are separate services that require explicit configuration.
- **AI and vision:** evaluate MediaPipe, OpenCV.js, Transformers.js,
  ONNX Runtime Web and WebLLM for local vision, chat, image generation and
  voice workflows. Model selection, device limits, loading and actual supported
  operations require separate implementation and tests; a runtime alone is not
  an AI app.
- **Creative:** animation tooling (evaluate Rive/PixiJS) and the existing
  image, vector and audio editors need unified open/save and touch workflows.

Do not claim a category is complete just because its library loads. Record
what is operational, partial or deferred in `APP_UNIFICATION_PROGRESS.md`, and
keep the user guide and live deployment evidence current. Retain the 100-user
storage-capacity work as a separate measurable requirement.
