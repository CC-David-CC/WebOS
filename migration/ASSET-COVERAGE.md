# Declared app asset coverage

Across 75 registered entries, 4,609 paths are declared. Component source contains 62, the frozen beta reference covers 4,438 and verified prepared inputs cover 36. These counts overlap. The 130 absent paths all belong to the historical CAD-host build.

All 36 previously missing Notebook paths are available under `artifacts/inputs/notebook/prepared/`. These include widget frontend assets and Python wheels. Each reference and prepared input is checked against its locked SHA-256 and size. The audit covers paths declared in the app manifests. Each app still needs its own build and functional checks for dependencies loaded at runtime.

| Registered ID | Declared | Source | Beta reference | Prepared inputs | Still absent |
|---|---:|---:|---:|---:|---:|---:|
| microduck | 4 | 1 | 4 | 0 | 0 |
| falling-blocks | 3 | 1 | 3 | 0 | 0 |
| owl-companion | 3 | 1 | 3 | 0 | 0 |
| physics-playground | 0 | 0 | 0 | 0 | 0 |
| snake-garden | 0 | 0 | 0 | 0 | 0 |
| clockwork-room | 0 | 0 | 0 | 0 | 0 |
| chess-study | 0 | 0 | 0 | 0 | 0 |
| solitaire | 0 | 0 | 0 | 0 | 0 |
| sky-courier | 0 | 0 | 0 | 0 | 0 |
| marble-works | 0 | 0 | 0 | 0 | 0 |
| stack-balance | 0 | 0 | 0 | 0 | 0 |
| crystal-defense | 0 | 0 | 0 | 0 | 0 |
| drone-circuit | 0 | 0 | 0 | 0 | 0 |
| reactive-control-desk | 0 | 0 | 0 | 0 | 0 |
| story-cards | 0 | 0 | 0 | 0 | 0 |
| expression-puppet | 3 | 1 | 3 | 0 | 0 |
| rhythm-garden | 2 | 0 | 2 | 0 | 0 |
| lantern-leap | 0 | 0 | 0 | 0 | 0 |
| garden-defense | 0 | 0 | 0 | 0 | 0 |
| pocket-rally | 0 | 0 | 0 | 0 | 0 |
| sling-targets | 0 | 0 | 0 | 0 | 0 |
| gravity-pinball | 0 | 0 | 0 | 0 | 0 |
| kinetic-relay | 0 | 0 | 0 | 0 | 0 |
| tabletop-bot-arena | 0 | 0 | 0 | 0 | 0 |
| pocket-golf | 1 | 0 | 1 | 0 | 0 |
| target-garden | 0 | 0 | 0 | 0 | 0 |
| orbital-courier | 0 | 0 | 0 | 0 | 0 |
| clockwork-quest | 0 | 0 | 0 | 0 | 0 |
| memory-garden | 0 | 0 | 0 | 0 | 0 |
| calculator | 0 | 0 | 0 | 0 | 0 |
| files | 0 | 0 | 0 | 0 | 0 |
| help | 0 | 0 | 0 | 0 | 0 |
| browser | 27 | 20 | 27 | 0 | 0 |
| codemirror | 0 | 0 | 0 | 0 | 0 |
| opencascade | 0 | 0 | 0 | 0 | 0 |
| gltf-transform | 0 | 0 | 0 | 0 | 0 |
| terminal | 0 | 0 | 0 | 0 | 0 |
| text | 0 | 0 | 0 | 0 | 0 |
| image-editor | 0 | 0 | 0 | 0 | 0 |
| document-editor | 1 | 1 | 1 | 0 | 0 |
| pdf-viewer | 0 | 0 | 0 | 0 | 0 |
| spreadsheet | 0 | 0 | 0 | 0 | 0 |
| data-explorer | 0 | 0 | 0 | 0 | 0 |
| ffmpeg | 0 | 0 | 0 | 0 | 0 |
| wavesurfer | 0 | 0 | 0 | 0 | 0 |
| tone | 0 | 0 | 0 | 0 | 0 |
| audio-editor | 44 | 0 | 44 | 0 | 0 |
| zip | 0 | 0 | 0 | 0 | 0 |
| gcode-preview | 0 | 0 | 0 | 0 | 0 |
| grid-tools | 48 | 0 | 48 | 0 | 0 |
| mermaid | 0 | 0 | 0 | 0 | 0 |
| echarts | 0 | 0 | 0 | 0 | 0 |
| plotly | 0 | 0 | 0 | 0 | 0 |
| pdfme | 0 | 0 | 0 | 0 | 0 |
| maplibre | 0 | 0 | 0 | 0 | 0 |
| transformers | 0 | 0 | 0 | 0 | 0 |
| trystero | 0 | 0 | 0 | 0 | 0 |
| tanstack-virtual | 0 | 0 | 0 | 0 | 0 |
| onnx-runtime | 1 | 0 | 1 | 0 | 0 |
| webtorrent | 0 | 0 | 0 | 0 | 0 |
| yjs | 0 | 0 | 0 | 0 | 0 |
| replicad | 0 | 0 | 0 | 0 | 0 |
| diagrams-net | 2765 | 1 | 2765 | 0 | 0 |
| notebook | 592 | 8 | 551 | 36 | 0 |
| excalidraw | 234 | 0 | 234 | 0 | 0 |
| svg-editor | 264 | 0 | 264 | 0 | 0 |
| arduino-simulator | 9 | 9 | 9 | 0 | 0 |
| pico-simulator | 0 | 0 | 0 | 0 | 0 |
| circuitjs | 411 | 0 | 411 | 0 | 0 |
| jsketcher | 130 | 0 | 0 | 0 | 130 |
| electronics-design | 18 | 12 | 18 | 0 | 0 |
| digital-logic | 0 | 0 | 0 | 0 | 0 |
| embroidery-studio | 49 | 7 | 49 | 0 | 0 |
| stitch-converter | 0 | 0 | 0 | 0 | 0 |
| personal-template | 0 | 0 | 0 | 0 | 0 |

Regenerate with `python3 scripts/inspect_app_assets.py`. Zero declarations do not establish a complete asset graph. JSketcher in this chart is the historical source-only ACAD host registration, distinct from the original JSketcher project. Hosted Rooms is unused legacy source and is outside this app inventory.

The 130 CAD paths are under generated JSketcher, adaptive-solver and related runtime trees in the historical ACAD host manifest. The organized sources and rebuild records are in `apps/acad/` and `apps/jsketcher/`. Validate the selected CAD build when that integration resumes.

Phase42 closes the optional speech runtime/model graph:34 locked public files (97,100,582 bytes), including13 original-source-pinned model files and verified npm package runtime assets/notices. Every model matches captured size/SHA256; both package tarballs match captured SHA1/SHA512, member counts and unpacked sizes. No package script ran. Offline assembly and actual isolated-browser WASM speech inference pass. Exact release notice/model redistribution review and Desktop/microphone/agent integration remain OPEN; no voice or new minimum dependency is enabled. See SPEECH-ENGINE.md.
