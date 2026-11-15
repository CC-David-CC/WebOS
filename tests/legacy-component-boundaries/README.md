# Legacy cross-component references — port deliberately

These four original tests span Runtime and app/storage boundaries. They belong to parent integration source, not to one application. Their original bytes/modes/history are retained. No app or Runtime implementation is copied here and no private cross-repository imports are added to current supported code. The original import paths remain unported in this legacy area.

Three exact captured reference tests passed in isolated private fixtures: Files/document-operation close/write behavior, Runtime/ACAD rectangle registration and recipe/document binding. Those fixtures contain exact original tracked module bytes and no new model implementation. They are Node/reference tests with supplied doubles, not current browser/kernel/account-storage authorization acceptance.

The old Files/Text/mirror workflow additionally needs DOM/IndexedDB development dependencies and the old view/host contracts. Their versions were not supplied by the inspected app-builder lock. That test was not run, no replacement dependency was guessed, and fake IndexedDB must not be presented as server-backed account synchronization. The real first-slice account-file workflow has separate browser/backend evidence.

Do not run broad legacy discovery or wire old imports into the current assembly. Port through supported public Runtime/app/Storage interfaces, preserve assertion intent and fixture identity, and qualify real account authority where required. Do not introduce compatibility path/global-object shims just to make these sources green. Historical syntax and baseline checks do not authorize legacy host/source operators or current UI actions. See migration/COMPONENT-BOUNDARIES.md and private phase45.
