# Source organization checkpoint — 2026-11-16

This checkpoint precedes the separately authorized [existing-viewer test integration](../deploy/VIEWER-TEST.md). Its source-organization results remain historical; current integration changes and hosted verification are recorded separately.

The source layout and category/importance matrix are ready for further development in this directory. This checkpoint does not certify that every application can already be produced or that the corrected viewer is assembled into a running website.

| Check | Result | Evidence / limit |
|---|---|---|
| Independent source ownership | PASS | 124 initialized Git-link repositories; 85 app repositories, including incomplete models/prototypes/templates |
| Intended Desktop source | PASS | 92 existing viewer files match the original; `platform/desktop/active-system/` is the intended source |
| Unrequested replacement removed | PASS | Replacement Desktop implementation, parent frontend/builder and dependent browser harnesses removed; ordinary history retained |
| Required core source owners | PASS | Runtime, Desktop, Login, Accounts, Storage, Files and WordCraft independently present |
| Source assembly checks | PASS | Seven metadata/layout/core-source checks; no browser-functionality claim |
| Selected source available in local Git stores | PASS | All 124 selected trees match local bare origins; 93,130 selected file blobs available; no old-workspace Git pointers/alternates |
| Craft branch policy | PASS | 17 apps and 5 shared projects: main tracks the fetched public upstream, working source stays on WebOS branches; no merge of newer upstream into our source |
| Temporary output in selected tracked files | PASS for checked patterns | Zero `target/`, `node_modules/`, root `dist/`, `__pycache__/` or `.pyc` candidates across parent/components after removing one generated LightCraft cache on our branch; upstream main/history unchanged |
| Required locked local inputs checked | PASS for checked locks | 6,230 files / 1,115,334,296 bytes; this is byte verification, not a complete all-app build graph |
| Prior unfinished working files preserved | PASS | `artifacts/input-files.json` and `tests/wordcraft_baseline_browser.mjs` retain their exact prior bytes and remain uncommitted |
| Full category/importance matrix | PASS | 124 unique rows with source/build entries and interfaces; Markdown and sortable CSV |
| Every application independently producible | NOT PROVEN | Six explicit external-input/rebuild gaps; incomplete models/prototype/template distinguished; full builds not run |
| Corrected viewer with all components assembled | NOT RUN | Original bootstrap path composition and future interface work remain; no replacement created |
| Site/deployment changes during this source correction/report | NONE | No service, route, website, account data or external publication changed; original workspace received no writes |

Read [APP-MATRIX.md](APP-MATRIX.md) for every location, category, priority and source/build gap. Priority puts authority, account files and usable editing before games. Source readiness and runtime readiness are separate columns/claims.

The six explicit input/rebuild gaps concern Browser's separately pinned Gecko build, Notebook wheels, ACAD generated native workers/host assets, Microduck's exact MuJoCo cold rebuild, Embroidery Studio's separately acquired upstream source/provenance, and Circuit Lab's research-runtime/release terms. Desktop, Linux, Terminal and Publication additionally have composition/interface work. Seven planned game repositories have models but no completed app; PCB Design is a Node research prototype; Personal Template is starting material.

The older beta remains independently live. Full beta parity, historical data recovery and new feature development are not this source-organization checkpoint's completion tests. Older runtime/host/operator documents are retained references, not authority to execute them.

No new full clone, large source copy, dependency installation or application build was made for this pass. Disk has approximately 67 GiB free after the previously approved compiler-cache cleanup. Local Git stores are same-disk recovery, not an off-machine backup. Required ignored input payloads and the two working files are not automatically included by a Git clone.

Resumable private evidence: `/path/to/workspace/Projects/.webos-migration/source-organization-20261116/`. Its final checkpoint records exact revisions, commands/exit codes, source checks, upstream alignment and remaining limits. Use the parent `webos/source-organization` branch and its Git links; do not resume the superseded broad functional-rebuild objective or restore the removed replacement.
