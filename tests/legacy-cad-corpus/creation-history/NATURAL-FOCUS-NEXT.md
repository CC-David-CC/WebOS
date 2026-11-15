# Combined-runtime natural viewport acceptance — prepared only

No runtime execution or passing claim yet. Await parent-provided combined source/runtime pins and signed fixture. This is separate from the historical menu-focused98fe/247b R2 proof. `signed.test.mjs`, `harness.mjs`, all existing evidence and their executed source hashes remain unchanged.

`files.json` continues to describe the historical96c checkpoint files; the new natural-focus files are intentionally additional preparation until their own exact runtime receipt is produced.

## Explicit natural-canvas mode

`natural-harness.mjs` requires `{focusMode:'natural-canvas'}`. `signed-natural.test.mjs` runs the same10-row creation/edit/replacement/undone-prefix Save/Open/resource corpus using that mode. It refuses historical98fe and older84406 pins.

Before every shortcut, a real click on the **outer desktop Applications button** and Escape establishes and asserts an independently unfocused iframe (top document focused, active element outside IFRAME, inner document unfocused). This is a defocus fixture precondition, not the old inner File-menu focus fallback. It then clicks the actual unobscured viewport canvas. Parent activeIFRAME and inner document focus are REQUIRED before trusted Ctrl+Z or Ctrl+Shift+Z. There is no menu fallback, programmatic `focus()`, private dispatcher or synthetic DOM keyboard event.

A passive one-shot event observer records actual `pointerdown` type/pointerType/target/isTrusted. Registration is acknowledged before the real pointer gesture; no timing guess or manufactured event. The observer only records test input metadata, never modifies the CAD model. Failure remains explicit rather than falling back.

## Narrow trusted-touch control

`touch-focus.test.mjs` launches a fresh normal app/account, pins all assets/outer index and begins with an empty actual document. Through actual Chromium CDP touch capability emulation and `Input.dispatchTouchEvent`, it taps the real viewport. The event MUST be trusted, pointerType touch, targetCANVAS; actual parent/inner focus is required. It sends no keyboard shortcuts and requires the public inspected document to remain unchanged. Emulation is disabled and its temporary CDP session detached afterward; only the owned browser context is closed.

This is a narrow browser touchscreen input/focus control on the ordinary1600×1000 test viewport. It does not qualify phone sizing, Android OS keyboard, physical hardware, full touch modeling or the whole phone UI.

## Execute only after parent supplies new pins

Use NEW output directories and the parent-owned fresh signed fixture, shared CDP19329 and existing Puppeteer/Node paths. Same environment variable names as the historical runner:

```sh
CODI_TEST_URL=http://127.0.0.1:NEW_PORT/ \
CODI_TEST_CDP=http://127.0.0.1:19329/ \
CODI_SIGNED_PINS=/absolute/NEW/runtime-pins.json \
CODI_EVIDENCE=/tmp/NEW-natural-creation-evidence \
PUPPETEER_CORE_PATH=/tmp/codi-occt-release-control/node_modules/puppeteer-core \
/tmp/codi-files-move-node/bin/node test/agent-cad-corpus/creation-history/signed-natural.test.mjs
```

Repeat with a DIFFERENT new output directory and `touch-focus.test.mjs` for the separate touch control. Parent owns fixture cleanup. Actual failures/source/asset hashes must be retained. The existing offline `check-saved.mjs` can independently check a successful new creation receipt/native file without implying new native calls.

Preparation validation only: Node `--check` on all3 new modules, plus unchanged historical R2 source-pin verification. No old98 app was rerun to pretend it supports the new focus expectation. No product edits or release changes.

## Added current service compatibility check

Before extrusion, the new runner also inspects and analyzes the genuinely public-authored rectangle's **saved single stage** using `inspect-sketch-diagnostics` and `analyze-sketch {revision,mode:'saved',faceId}`. It requires current saved-face availability and the supported version1 local estimate, with unambiguous local rank interval. Exact native snapshot/source/history and counters remain unchanged; journal content/capabilities/targets are unchanged (only its revision token is excluded from comparison). This adds one read-only row to the same10 creation rows. It is not a global freedom/satisfiability proof and supplies no multi-stage app qualification or native-file seed.
