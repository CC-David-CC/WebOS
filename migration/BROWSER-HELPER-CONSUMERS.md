# Legacy browser test helper consumers

35 additional original browser test sources now have parent-owned locations under `tests/legacy-desktop-browser/`. Their source bytes, executable modes and selected histories are retained. They exercise app/Desktop/file workflows, so the parent owns these cross-component test sources. No app implementation is copied into the parent.

| Original source | Parent source |
|---|---|
| `tests/audio-editor-workflow.test.mjs` | `tests/legacy-desktop-browser/audio-editor-workflow.test.mjs` |
| `tests/audio-file-watch.test.mjs` | `tests/legacy-desktop-browser/audio-file-watch.test.mjs` |
| `tests/audio-large-workflow.test.mjs` | `tests/legacy-desktop-browser/audio-large-workflow.test.mjs` |
| `tests/audio-layout-restoration.test.mjs` | `tests/legacy-desktop-browser/audio-layout-restoration.test.mjs` |
| `tests/audio-lifecycle-session-review.test.mjs` | `tests/legacy-desktop-browser/audio-lifecycle-session-review.test.mjs` |
| `tests/audio-multichannel-review.test.mjs` | `tests/legacy-desktop-browser/audio-multichannel-review.test.mjs` |
| `tests/audio-multichannel-routes-review.test.mjs` | `tests/legacy-desktop-browser/audio-multichannel-routes-review.test.mjs` |
| `tests/audio-save-shortcut.test.mjs` | `tests/legacy-desktop-browser/audio-save-shortcut.test.mjs` |
| `tests/audio-saveas-race-review.test.mjs` | `tests/legacy-desktop-browser/audio-saveas-race-review.test.mjs` |
| `tests/audio-single-clipping-review.test.mjs` | `tests/legacy-desktop-browser/audio-single-clipping-review.test.mjs` |
| `tests/audio-single-clipping-stereo-review.test.mjs` | `tests/legacy-desktop-browser/audio-single-clipping-stereo-review.test.mjs` |
| `tests/audio-single-picker-review.test.mjs` | `tests/legacy-desktop-browser/audio-single-picker-review.test.mjs` |
| `tests/audio-single-transient-retry-review.test.mjs` | `tests/legacy-desktop-browser/audio-single-transient-retry-review.test.mjs` |
| `tests/audio-themed-confirm.test.mjs` | `tests/legacy-desktop-browser/audio-themed-confirm.test.mjs` |
| `tests/audio-tone-example.test.mjs` | `tests/legacy-desktop-browser/audio-tone-example.test.mjs` |
| `tests/audio-tools-browser.test.mjs` | `tests/legacy-desktop-browser/audio-tools-browser.test.mjs` |
| `tests/browser-clicked-downloads.test.mjs` | `tests/legacy-desktop-browser/browser-clicked-downloads.test.mjs` |
| `tests/browser-download-close.test.mjs` | `tests/legacy-desktop-browser/browser-download-close.test.mjs` |
| `tests/browser-download-folder.test.mjs` | `tests/legacy-desktop-browser/browser-download-folder.test.mjs` |
| `tests/browser-download-windows.test.mjs` | `tests/legacy-desktop-browser/browser-download-windows.test.mjs` |
| `tests/browser-gecko-auth-relay.test.mjs` | `tests/legacy-desktop-browser/browser-gecko-auth-relay.test.mjs` |
| `tests/browser-live-128m-url-download.test.mjs` | `tests/legacy-desktop-browser/browser-live-128m-url-download.test.mjs` |
| `tests/browser-live-clicked-download.test.mjs` | `tests/legacy-desktop-browser/browser-live-clicked-download.test.mjs` |
| `tests/browser-live-slow-download.test.mjs` | `tests/legacy-desktop-browser/browser-live-slow-download.test.mjs` |
| `tests/browser-live-url-download.test.mjs` | `tests/legacy-desktop-browser/browser-live-url-download.test.mjs` |
| `tests/browser-url-folder.test.mjs` | `tests/legacy-desktop-browser/browser-url-folder.test.mjs` |
| `tests/files-public-830-continuity.test.cjs` | `tests/legacy-desktop-browser/files-public-830-continuity.test.cjs` |
| `tests/files-public-beta-128m.test.cjs` | `tests/legacy-desktop-browser/files-public-beta-128m.test.cjs` |
| `tests/files-public-beta-early-text.test.cjs` | `tests/legacy-desktop-browser/files-public-beta-early-text.test.cjs` |
| `tests/files-public-beta-smoke.test.cjs` | `tests/legacy-desktop-browser/files-public-beta-smoke.test.cjs` |
| `tests/files-public-beta-ui-actions.test.cjs` | `tests/legacy-desktop-browser/files-public-beta-ui-actions.test.cjs` |
| `tests/notebook-ipywidgets-research.test.mjs` | `tests/legacy-desktop-browser/notebook-ipywidgets-research.test.mjs` |
| `tests/notebook-lifecycle.test.mjs` | `tests/legacy-desktop-browser/notebook-lifecycle.test.mjs` |
| `tests/spreadsheet-native-save-race.test.mjs` | `tests/legacy-desktop-browser/spreadsheet-native-save-race.test.mjs` |
| `tests/spreadsheet-open-safety.test.mjs` | `tests/legacy-desktop-browser/spreadsheet-open-safety.test.mjs` |

## Verification and limits

All 35 current files match their captured original Git blobs and modes. Selected path histories cover 93 unique source blobs; bounded credential/opaque-literal screens and Node syntax checks passed. This is not complete external-publication clearance.

The new consumers resolve 41 static relative imports to the four helpers retained in phase45. These edges belong to these newly retained tests; phase45 itself restored no edges among the earlier 760 tests. Standard Node/browser-automation imports still require an explicitly qualified test environment.

No legacy browser drivers were executed. Old live-site URLs, destructive test actions, selectors, host globals, authentication assumptions, large download fixtures and storage behavior must be deliberately reviewed and ported before execution. Do not run this directory with broad discovery against either site. Source closure is not current browser acceptance, authorized agent access, or account synchronization.

Mechanical filtered baseline `991c273dca504e308a4660801598daccf52f5305`; parent source merge `4235436f00821bdf3ef1bd25bd5a6bef903a92e3`. All 124 component pins remain unchanged. Current source, build, dependency and deployment entrypoints are unchanged. Private phase46 contains path/commit/ref maps, selected-history syntax results, exact byte/mode proofs and the resume checkpoint.
