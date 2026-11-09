# CAD file export finish: bounded source review

Reviewed Host be24fbc232c967912f529053d34a9d407b369a39. This is a
source-only review: no parser, tests, fault injection, probe, build, Native,
browser, file operation or functional execution. Root's frozen candidate and
acceptance packets are unchanged.

Conclusion: the conditional catch in settleCadFileExport does discard a
secondary exception if an arbitrary supplied token.finish throws after run
already failed. However, no ordinary reachable throwing finish was found in
the actual mounted Host token and coordinator implementation. This is not a
confirmed production cleanup-evidence defect and no product repair is proposed.

## Exact reviewed source

| Path | Git blob |
| --- | --- |
| apps/system/jsketcher/file-export-outcome.mjs | d6bbf624140f9d213cd5fcfb0499701071ce4686 |
| active-system/assets/desktop/document-operations.mjs | d0593093f8146a5ee385e56d6af6a875a83d1c6c |
| active-system/assets/desktop/app-instance.mjs | 91fb0e4109222b29e4c6e698f71ce719eb8ad774 |
| apps/system/jsketcher/index.mjs | b22f08feeca7df8db262e68f3b88584f0efbce20 |
| apps/system/jsketcher/step-export-commands.mjs | ac3e58dc1459e385cb3421bded9cd17cef07d28c |

Additional source read: active-system/app.js requestWindowClose;
apps/system/jsketcher/scoped-command.mjs; native-project-file.mjs and
file-read.mjs. The task's settlement file is actually named
file-export-outcome.mjs, not cad-file-export-outcome.mjs.

## Actual token and callback graph

app-instance.mjs mountApp constructs createDocumentOperations itself and
passes that object into module.mount. Its coordinator comes from the actual
createDocumentOperationCoordinator, separately keyed by the exact session
object and owner. It does not receive a public replacement coordinator/token.

In index.mjs begin (line 121) calls those operations.begin. saveProject,
exportDerivedModel (3MF and drawing SVG), and exportDxf pass the actual returned
token to settleCadFileExport. It is an Object.freeze result with its own finish
method (document-operations.mjs lines 104-143), closing over one private record.

The actual non-aborting finish path is:

1. finish(record,false), lines 72-78, returns if active is a different record.
2. Otherwise it sets active=null, calls coordinator.release(record), then notify.
3. The actual release, lines 49-52, deletes only claims whose private holder
   owner is exactly that record from its private Map. It calls no file provider,
   archive/Worker/Native release, Blob lease, UI destroy method, subscriber
   unsubscribe, account switch or arbitrary cleanup hook.
4. Coordinator notify (line 27) catches every subscriber exception. Local
   notify (line 71) likewise catches state computation and each callback;
   isValid (line 66) also catches host-validity callback errors. The coordinator
   object is frozen and the claims Map contains actual internally created
   plain records/strings, not caller-owned accessors.

There is no explicit throw or unguarded application/provider callback on this
finish(false) path. Replacing the coordinator/token, overriding intrinsic Map/
Set behavior, or resource exhaustion is not evidence of an ordinary supported
Host cleanup failure. A custom injected token whose finish throws would only
demonstrate the generic helper's conditional catch, not this production graph.

## Ownership, close, disposal and reentrancy

- Normal completion releases only its exact record. A late or repeated finish
  cannot clear a newer operation: active!==record is an immediate no-op.
- Claim deletion completes before coordinator notifications. A listener may
  begin a new operation during notification, but its new private record is not
  the old release owner. The old local notification observes the current state
  and does not overwrite or retire that new owner.
- Account/session/window validity is captured by mountApp. Forced app disposal
  aborts its own controller; operations.dispose marks disposed and finishes its
  own active record with abort=true. That path also uses the real coordinator.
  A later settleCadFileExport finish is then a no-op. It does not acquire or
  release a different session's coordinator.
- requestWindowClose blocks ordinary close while this own operation is in
  local-write (active-system/app.js lines 558-569), including commit receipt and
  accepted baseline publication. This is distinct from advisory peer busy.
  Forced disposal remains cancellation, not proof that a submitted write failed.
- Actual archive/source/lease/Worker cleanup is elsewhere: the Save run's finally
  releases rebaseFile and capture (index.mjs lines 453-455); nativeBackings.close
  preserves WORKER_CLEANUP_FAILED; scoped-command.mjs explicitly reports
  listener cleanupUnconfirmed/cleanupCause. Those operations are not hidden
  inside token.finish. If they reject/throw within run, settlement receives that
  run failure. This review does not certify every independent finally/error
  precedence chain in the storage/Core implementations.

## File-outcome knowledge and error preservation

| Actual state | What establishes it | Settlement on run failure |
| --- | --- | --- |
| No write started | outcome remains null | Returns/throws the original arbitrary run exception unchanged; no invented file-commit claim. |
| Submitted/uncertain | write.begin immediately before awaiting files.write | Preserves original exception as cause and marks possiblyCommitted, subject to an already explicit committed flag. A rejected write/invalid receipt/cancellation does not establish absence. |
| Browser committed | write.accept validates bounded own-data version/status receipt after files.write | Marks committed and retains the original exception as cause; browser acknowledgement never claims server synchronization. |

failure is a wrapper record rather than a truthiness sentinel, so null, false,
zero or undefined thrown by run is still retained. fileOutcomeError leaves
prewrite failures identical; pending/committed wrapping reads only bounded data
descriptors for display/name/code and keeps the exact original value as cause.
Post-write early return with no result is converted into an interrupted result
rather than a successful missing receipt. Post-finish ownerCurrent uses the
captured Host account/window validity, not token.current (which must be false
after finish). A changed owner gets a generic inspect-My-files warning while
the pending/committed knowledge is preserved.

The real finish cannot supply an independent ordinary cleanup exception to
lose here. UI tell/onError callbacks are separately guarded presentation
notifications, not file-retirement authority. STEP has its own analogous
failure/finish block (step-export-commands.mjs execute, line 76) using the same
actual token; it does not introduce a different fallible finish implementation.

## Disposition

No source edit, new runtime case, generic error aggregation policy or interface
change is required for this suspected finish-specific defect on the reviewed
Host. This is a bounded source conclusion, not a successful failure-injection
test or a blanket guarantee against engine exhaustion or future token changes.
If a later real token contract adds fallible cleanup, its settlement/error
evidence contract must be reviewed with that actual implementation; such a
future change is not silently assumed in this review.
