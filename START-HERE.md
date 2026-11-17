# WebOS — organized source for future development

Current status (2026-11-17 UTC): ksu.codes serves the existing Desktop/Workspace
viewer with qualified WordCraft document integration: account-scoped rich-draft
recovery, confirmed Save/Save As identity/titles/restoration and existing-document
activation through Files and WordCraft Open. Different documents remain
independent. Requested Discord controls are removed; About retains its link.
All 92 actual-browser checks pass locally and hosted, alongside all nine native
CI stages (4,989 tests; eight pre-existing ignored) and 68 JavaScript tests.
Calculator, Files, Text, WordCraft and Help remain the five enabled apps. Server-
validated login persistence, the fixed eight-hour deadline and transfer limits
remain. Desktop CSS/reference/artwork, beta, backend/account state and original
workspace remain unchanged. Files initial-load Retry, native-picker double-click,
delegated-agent transport and multi-user/per-window capacity remain separate.
See the [current release report](deploy/WORDCRAFT-DOCUMENTS.md) for exact source,
release, rollback and limits, and the [prior Files/Text/Login record](deploy/TEST-STATUS.md)
for historical evidence. Source organization is complete; the general
[Craft guide](migration/CRAFT-INTEGRATION-GUIDE.md) and running log are current.

Work from the files in this project. The deliverable is a coherent source tree with independent owners, usable source/build entries, required inputs identified and clear remaining production gaps. It is not a full beta clone, a parity project, an interface redesign or an automatic deployment. Beta stays live separately.

## Where things belong

| Directory | Source ownership |
|---|---|
| apps/ | 85 application repositories:17 Craft,33 system/tool/CAD and35 game repositories including7 planned cores |
| platform/ | 7 platform components: Runtime, Desktop, Login, Accounts, Storage, Rendezvous, Publication |
| engines/ | 9 reusable engines, including FFmpeg and optional v86 |
| libraries/ | 19 reusable libraries, including Craft libraries, egui and TanStack Virtual |
| assets/ | Shared Craft fonts and translations |
| tooling/ | Shared Craft build tooling |
| legacy/rooms/ | Unused old Rooms source; no service implied |
| scripts/, tests/ | Parent source inspection/composition utilities and clearly scoped tests |
| artifacts/ | Ignored, locked runtime/build inputs; never credentials or compiler caches |
| deploy/ | Existing definitions and historical deployment records; no authority to execute them |
| migration/ | Source ownership/catalogs and historical evidence; historical PASS text is not a current release claim |

The [full app/component matrix](migration/APP-MATRIX.md) lists every component by category and functional importance, with its location, interfaces, build entry and production gaps. The [CSV](migration/APP-MATRIX.csv) is suitable for sorting in a spreadsheet. The [source catalog](migration/SOURCE-CATALOG.md) and its [JSON form](migration/SOURCE-CATALOG.json) record actual source/build definitions and package dependencies. Git links select exact component versions. ACAD and original JSketcher are separate. Files and WordCraft are applications, not platform folders. FFmpeg is a shared engine, not a visible standalone app.

## Desktop source decision

The intended existing viewer is [platform/desktop/active-system/](platform/desktop/active-system/), with classic-script entry index.html, bootstrap.js, app.js, desktop-apps.js, reference.js and style.css. All92 source/assets matched the original during correction. Its code has not been rewritten.

The rejected replacement src/ viewer/controller/styles and associated tests were removed. The old parent frontend.mjs/build_development.mjs and its browser harnesses remain removed. The separately authorized test composition now uses scripts/build_viewer.mjs and public account/app services with the existing viewer. Only bootstrap.js, app.js and desktop-apps.js receive integration changes; CSS, reference data and artwork remain unchanged. Five app entries are enabled; broad suite integration remains separate.

## Craft branches

The [Craft integration log](migration/CRAFT-INTEGRATION-LOG.md) tracks WordCraft's
actual integration changes, their validation status and the responsibilities to
assess when integrating each other Craft app. It separates implemented source
from qualified behavior.

The17 Craft app repositories now use main as their verified public-upstream tracking branch and webos/integration for the parent-selected working source. All17 main branches were fetched from their verified upstream on2026-11-16. WebOS changes were not merged with newer upstream, and working files/pins were not changed by the alignment. WordCraft and DeckCraft modifications remain on our branch.

The5 shared Craft projects also have upstream-tracking main branches; their selected working pins stay on WebOS branches. The [verified upstream map](migration/CRAFT-UPSTREAMS.json) makes this reproducible after a clone. Run `python3 scripts/configure_craft_upstreams.py --configure` to restore missing upstream remotes and tracking configuration locally; it does not fetch, merge, switch branches or move pins. To inspect/update upstream later, use the existing upstream remote and fast-forward main deliberately while working on a WebOS branch. Review and merge upstream into a separate WebOS review branch only when desired. Never push to upstream. Local origin stores are separate from upstream and external publication is not authorized. See [Craft build inputs](migration/CRAFT-BUILD-INPUTS.md) for the organized fonts/shared-library locations.

## Source and inputs

Sources/manifests/locks and required input assets are retained. Intermediate compiler builds are disposable and must not be committed. The approved cleanup removed11 compiler-output directories and recovered66.56GiB. Do not retain repeated build trees as part of the deliverable. The older migration directory also contains private recovery and unique work; do not delete source/history/inputs by directory name alone.

[artifacts/README.md](artifacts/README.md) explains the ignored public reference and input payloads. A read-only check verified6230 locked files totaling1,115,334,296 bytes, including6143 reference files. This proves those bytes, not every app's complete build graph. Build recipes may still require public dependencies, separately locked inputs or further integration. Missing inputs and source-only planned cores must appear honestly in the final production-readiness matrix.

A source clone uses the trusted local bare origins and relative sibling URLs in .gitmodules. All124 selected child commits are verified present in their local bare origins; the corrected Desktop branch and Craft branch updates have reached those stores through explicit fast-forward/new-branch local writes. A new full checkout/build was not created for this pass. No private server address should be guessed. Original KSU.CODES remains read-only.

## Read-only inspection

- python3 scripts/inspect_assembly.py --require-core checks source Git-link/checkouts/ownership agreement.
- python3 scripts/catalog_sources.py describes source silos; --write refreshes the two source catalogs.
- python3 scripts/verify_artifacts.py verifies locked input bytes without network access.

These checks do not build or deploy. Follow each component's actual build definitions when future development requires a build, with output outside source and no automatic publishing/service actions. The category/importance matrix is the current inventory; the old runtime status matrix is historical. Seven game cores, the PCB prototype and the template are not finished apps. Explicit input/rebuild gaps and composition work remain listed rather than being hidden behind source-present labels.

The two pre-existing working-tree files artifacts/input-files.json and tests/wordcraft_baseline_browser.mjs remain in place and unchanged. Their authorship is not assumed. They are explicit unfinished working material, not an instruction to run or delete anything.
