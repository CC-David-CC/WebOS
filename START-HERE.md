# WebOS — organized source for future development

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

The [source catalog](migration/SOURCE-CATALOG.md) lists every component and actual source/build definitions. Its [JSON form](migration/SOURCE-CATALOG.json) also lists package integration entries, dependency names and source directories. Git links, not the catalog, select exact component versions. ACAD and original JSketcher are separate. Files and WordCraft are applications, not platform folders. FFmpeg is a shared engine, not a visible standalone app.

## Desktop source decision

The intended existing viewer is [platform/desktop/active-system/](platform/desktop/active-system/), with classic-script entry index.html, bootstrap.js, app.js, desktop-apps.js, reference.js and style.css. All92 source/assets matched the original during correction. Its code has not been rewritten.

The rejected replacement src/ viewer/controller/styles and associated tests were removed. The old parent frontend.mjs/build_development.mjs and browser harnesses that depended on that replacement have also been removed. Do not restore them as the source baseline. Future composition of the existing viewer's separately owned Runtime, Terminal, engine, account and application dependencies is development work, not a reason to invent another desktop.

## Craft branches

The17 Craft app repositories now use main as their verified public-upstream tracking branch and webos/integration for the parent-selected working source. All17 main branches were fetched from their verified upstream on2026-11-16. WebOS changes were not merged with newer upstream, and working files/pins were not changed by the alignment. WordCraft and DeckCraft modifications remain on our branch.

To inspect/update upstream later, use the existing upstream remote and fast-forward main deliberately. Review and merge upstream into a separate WebOS review branch only when desired; do not silently change the parent pin. Never push to upstream. Local origin stores are separate from upstream and external publication is not authorized. Shared Craft-project branch alignment is still being checked separately. See [Craft build inputs](migration/CRAFT-BUILD-INPUTS.md) for the organized fonts/shared-library locations.

## Source and inputs

Sources/manifests/locks and required input assets are retained. Intermediate compiler builds are disposable and must not be committed. The approved cleanup removed11 compiler-output directories and recovered66.56GiB. Do not retain repeated build trees as part of the deliverable. The older migration directory also contains private recovery and unique work; do not delete source/history/inputs by directory name alone.

[artifacts/README.md](artifacts/README.md) explains the ignored public reference and input payloads. A read-only check verified6230 locked files totaling1,115,334,296 bytes, including6143 reference files. This proves those bytes, not every app's complete build graph. Build recipes may still require public dependencies, separately locked inputs or further integration. Missing inputs and source-only planned cores must appear honestly in the final production-readiness matrix.

A fresh source clone uses the trusted local bare origins and relative sibling URLs in .gitmodules. New local source-organization commits must reach their corresponding local origin before clean-clone reproducibility can be claimed. No private server address should be guessed. Original KSU.CODES remains read-only.

## Read-only inspection

- python3 scripts/inspect_assembly.py --require-core checks source Git-link/checkouts/ownership agreement.
- python3 scripts/catalog_sources.py describes source silos; --write refreshes the two source catalogs.
- python3 scripts/verify_artifacts.py verifies locked input bytes without network access.

These checks do not build or deploy. Follow each component's actual build definitions when future development requires a build, with output outside source and no automatic publishing/service actions. The final sorted category/importance matrix is being prepared from the sources; do not substitute the old runtime status matrix for it.

The two pre-existing working-tree files artifacts/input-files.json and tests/wordcraft_baseline_browser.mjs remain in place and unchanged. Their authorship is not assumed. They are explicit unfinished working material, not an instruction to run or delete anything.
