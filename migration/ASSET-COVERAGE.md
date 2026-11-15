# Declared app asset coverage

Current source declarations were compared with owned source files and the frozen beta reference payload. Every reported reference file was checked against its locked SHA256 and size. This covers declared file paths, not the complete dynamic import graph or reproducible source builds.

Across75 registered source entries:4609 declarations;62 files present in component source;4438 declarations have verified reference bytes. These overlap.166 declarations are absent from both locations:36 Notebook widget-extension paths and130 historical JSketcher/ACAD host build paths. Private preserved runtime/build archives have not yet been reconciled by this check. Absence here does not prove loss.

JSketcher here is the source-only historical ACAD host registration, not the separately maintained original JSketcher repository. Hosted Rooms is legacy and is not part of this app inventory.

| Registered ID | Declared files | In owned source | Verified beta reference | Absent from both |
|---|---:|---:|---:|---:|
| microduck | 4 | 1 | 4 | 0 |
| falling-blocks | 3 | 1 | 3 | 0 |
| owl-companion | 3 | 1 | 3 | 0 |
| physics-playground | 0 | 0 | 0 | 0 |
| snake-garden | 0 | 0 | 0 | 0 |
| clockwork-room | 0 | 0 | 0 | 0 |
| chess-study | 0 | 0 | 0 | 0 |
| solitaire | 0 | 0 | 0 | 0 |
| sky-courier | 0 | 0 | 0 | 0 |
| marble-works | 0 | 0 | 0 | 0 |
| stack-balance | 0 | 0 | 0 | 0 |
| crystal-defense | 0 | 0 | 0 | 0 |
| drone-circuit | 0 | 0 | 0 | 0 |
| reactive-control-desk | 0 | 0 | 0 | 0 |
| story-cards | 0 | 0 | 0 | 0 |
| expression-puppet | 3 | 1 | 3 | 0 |
| rhythm-garden | 2 | 0 | 2 | 0 |
| lantern-leap | 0 | 0 | 0 | 0 |
| garden-defense | 0 | 0 | 0 | 0 |
| pocket-rally | 0 | 0 | 0 | 0 |
| sling-targets | 0 | 0 | 0 | 0 |
| gravity-pinball | 0 | 0 | 0 | 0 |
| kinetic-relay | 0 | 0 | 0 | 0 |
| tabletop-bot-arena | 0 | 0 | 0 | 0 |
| pocket-golf | 1 | 0 | 1 | 0 |
| target-garden | 0 | 0 | 0 | 0 |
| orbital-courier | 0 | 0 | 0 | 0 |
| clockwork-quest | 0 | 0 | 0 | 0 |
| memory-garden | 0 | 0 | 0 | 0 |
| calculator | 0 | 0 | 0 | 0 |
| files | 0 | 0 | 0 | 0 |
| help | 0 | 0 | 0 | 0 |
| browser | 27 | 20 | 27 | 0 |
| codemirror | 0 | 0 | 0 | 0 |
| opencascade | 0 | 0 | 0 | 0 |
| gltf-transform | 0 | 0 | 0 | 0 |
| terminal | 0 | 0 | 0 | 0 |
| text | 0 | 0 | 0 | 0 |
| image-editor | 0 | 0 | 0 | 0 |
| document-editor | 1 | 1 | 1 | 0 |
| pdf-viewer | 0 | 0 | 0 | 0 |
| spreadsheet | 0 | 0 | 0 | 0 |
| data-explorer | 0 | 0 | 0 | 0 |
| ffmpeg | 0 | 0 | 0 | 0 |
| wavesurfer | 0 | 0 | 0 | 0 |
| tone | 0 | 0 | 0 | 0 |
| audio-editor | 44 | 0 | 44 | 0 |
| zip | 0 | 0 | 0 | 0 |
| gcode-preview | 0 | 0 | 0 | 0 |
| grid-tools | 48 | 0 | 48 | 0 |
| mermaid | 0 | 0 | 0 | 0 |
| echarts | 0 | 0 | 0 | 0 |
| plotly | 0 | 0 | 0 | 0 |
| pdfme | 0 | 0 | 0 | 0 |
| maplibre | 0 | 0 | 0 | 0 |
| transformers | 0 | 0 | 0 | 0 |
| trystero | 0 | 0 | 0 | 0 |
| tanstack-virtual | 0 | 0 | 0 | 0 |
| onnx-runtime | 1 | 0 | 1 | 0 |
| webtorrent | 0 | 0 | 0 | 0 |
| yjs | 0 | 0 | 0 | 0 |
| replicad | 0 | 0 | 0 | 0 |
| diagrams-net | 2765 | 1 | 2765 | 0 |
| notebook | 592 | 8 | 551 | 36 |
| excalidraw | 234 | 0 | 234 | 0 |
| svg-editor | 264 | 0 | 264 | 0 |
| arduino-simulator | 9 | 9 | 9 | 0 |
| pico-simulator | 0 | 0 | 0 | 0 |
| circuitjs | 411 | 0 | 411 | 0 |
| jsketcher | 130 | 0 | 0 | 130 |
| electronics-design | 18 | 12 | 18 | 0 |
| digital-logic | 0 | 0 | 0 | 0 |
| embroidery-studio | 49 | 7 | 49 | 0 |
| stitch-converter | 0 | 0 | 0 | 0 |
| personal-template | 0 | 0 | 0 | 0 |

Regenerate the full per-file report with `python3 scripts/inspect_app_assets.py`. It prints JSON and does not fetch, write component files, install packages, or enable apps. A zero declaration count is not a complete-asset-graph claim.

Next: reconcile the36 Notebook declarations with preserved runtime inputs, then the130 historical CAD host paths with its independent build outputs and preservation records. Do not copy obsolete compiled bundles into current source or treat unused legacy services as current dependencies.
