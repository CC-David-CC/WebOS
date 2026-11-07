# Actual first-box creation failure, retained

The first signed execution used runner source a4df31ade, frozen CAD 0d815e1418e9368c3f80c876820d2ebda0766dd3 and desktop cf97976d965f0b57689f1d2a8c87a060d0a49369. All 73 core assets and the real mounted outer bundle matched. Preferred OCC discovery correctly advertised the native-evidence dd666/8d5 build.

The FIRST registered `create-worker-solid-box` from a truly empty document rejected with no code, `committed:false`, `possiblyCommitted:false` and message `The accepted tip is unavailable for feature creation history.` The runner stopped with exit1 and closed its own context. No Join or Undo was executed. All 17 planned geometry/history setups remain unqualified against this runtime. [Receipt](evidence-r1/receipt.json), [log](evidence-r1/browser.log).

Read-only source inspection identifies the creation-append guard at CAD craftBundle.ts171–174. It requires the journal document/head and full-tip source/material baselines to match before the first box. Full-tip sketch/material fields initialize null; the lazy material baseline in inspectAuthoredEdits requires a truthy fullTipSignature. No guard was changed by this lane.

At root's request a NEW fresh signed context captured only pristine state, without creating any feature or retrying the failed command. All served pins matched again. Actual project DEFAULT had documentGeneration1/current=true/hostLifetime=true, history[], pointer−1, modelCount0, processingfalse, feature counter0; sketch namespace TCAD.projects.DEFAULT.sketch. had no keys and revision `[]`; material inspection revision was a non-null UUID. The public session journal revision began `0:0:` despite documentGeneration1, and both Undo/Redo were false. This is also a document-generation baseline mismatch, not just a null source/material revision. [Initial observation](evidence-r1/initial-state.json).

Root owns the product correction and fresh build. R1 remains untouched; no browser rerun is authorized against this old product. The tests will retain the first-box-to-empty requirement and every geometric/operand-order/refusal invariant.
