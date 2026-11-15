# App-owned reference test source and verified baseline

Seventy-nine original test files now live in18 owning application repositories under `tests/reference/`. Source imports and byte-matching modules establish ownership, rather than filename guessing. The old jsketcher-path command tests belong to the maintained ACAD snapshot; original JSketcher remains separate. Four cross-role/view/environment cases remain held for deliberate parent integration, not copied into an arbitrary app.

Every original test body/mode is retained in a separate mechanical history commit. A following commit ports only imports and proven owned fixture/resource URLs. The complete AST, apart from those locators, is identical. No assertion, input validation, expected domain result, timeout or test case was removed or weakened. Current implementation modules and dependency versions are unchanged. Each owner exposes `npm run test:reference`; actual old app/browser/kernel integration remains independently open.

## Original and ported results

Both the exact captured baseline and current repository ports report299 Node subtests:296 pass,3 fail,0 cancelled/skipped. Top-level assertion-only files count as one Node subtest, not individual assertions. All three failures are reproduced in ACAD; they are not new import-port failures and are not marked green. Source/test compatibility fixes require a separate reviewed change.

| Owner | Files | Pass | Existing fail |
|---|---:|---:|---:|
| acad | 33 | 214 | 3 |
| arduino-simulator | 2 | 2 | 0 |
| audio-editor | 2 | 6 | 0 |
| browser | 2 | 9 | 0 |
| data-explorer | 3 | 7 | 0 |
| document-editor | 2 | 6 | 0 |
| embroidery-studio | 1 | 1 | 0 |
| excalidraw | 3 | 3 | 0 |
| falling-blocks | 2 | 2 | 0 |
| gcode-preview | 5 | 7 | 0 |
| grid-tools | 3 | 3 | 0 |
| image-editor | 4 | 8 | 0 |
| notebook | 3 | 6 | 0 |
| pico-simulator | 2 | 2 | 0 |
| replicad | 1 | 1 | 0 |
| spreadsheet | 9 | 13 | 0 |
| svg-editor | 1 | 1 | 0 |
| text | 1 | 5 | 0 |

## Captured ACAD failures

- malformed value, extra addressing fields and absent locators refuse before dispatch
- discovery, plane and all primitive kinds use same guarded craft and detached data
- register five explicit selected-profile commands with data-only schemas and no fallback/save payload

The controlled original Arduino/Browser baselines initially lacked16 already-owned demo/resource files. Copying their exact original blobs closed those fixture gaps without test changes. Existing owned current files are reached through byte-verified URL locators; no old-workspace fallback or compatibility shim is introduced. These initial missing-fixture failures are not labelled app defects.

Static source histories were reviewed before import. Private evidence retains earlier paths, explicit copy boundaries, commit/ref maps, all test AST/locator diffs and original/current logs, including the read-only inspector buffer failure and its correction. No existing test failure was hidden to obtain a green total.

No existing app view, renderer, account/file authority, engine/kernel, server service or production entrypoint changed. Unit/reference success is not browser fidelity, authorization, synchronization or whole-system compatibility proof. All minimum and actual human/agent/second-machine gates remain as separately recorded.

Private checkpoint/evidence: `/path/to/workspace/Projects/.webos-migration/run-20261115-44-app-unit-tests/`. All124 component repositories remain independently pinned;18 selections change solely for owned tests/dev metadata.
