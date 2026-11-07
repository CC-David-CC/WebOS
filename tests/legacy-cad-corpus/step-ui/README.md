# Prepared STEP File-menu phone/desktop acceptance

BROWSER NOT RUN. See PLAN.md for frozen rows and limitations. Only this new test directory is owned; production STEP controller and historical component evidence stay separate.

```sh
/tmp/codi-files-move-node/bin/node --test test/agent-cad-corpus/step-ui/layout.test.mjs
# After root supplies the NEW combined fixture and releases foreground:
CODI_TEST_URL=http://127.0.0.1:PORT/ \
CODI_TEST_CDP=http://127.0.0.1:19329 \
CODI_SIGNED_PINS=/tmp/ROOT-NEW-STEP-PINS.json \
CODI_EXPECT_SOURCE=ROOT_EXACT_CAD_SHA CODI_EXPECT_DESKTOP=ROOT_EXACT_DESKTOP_SHA \
CODI_STEP_ENGINE_REVISION=sha256:EXACT_JS_SHA:EXACT_WASM_SHA \
CODI_EVIDENCE=/tmp/NEW-STEP-UI-OUTPUT \
PUPPETEER_CORE_PATH=/tmp/codi-occt-release-control/node_modules/puppeteer-core \
/tmp/codi-files-move-node/bin/node test/agent-cad-corpus/step-ui/signed.test.mjs
```

Dependencies: existing signed sweep harness for normal account login/app launch/public command registry/read-only accepted-state observations; existing strict-join canonical serializer. Both are source-hashed in the run. Full served core hashes are checked once in the first case; actual outer index and Native runtime binding are checked in every case. This driver creates only its own synthetic test accounts through normal UI. Pure layout fixtures contain numeric rectangles only; they produce no successful browser/native claim.

First run failed before authoring: mobile emulation was set after login and could reload the RAM session (evidence-r1). The UI-only harness subset now sets the frozen viewport before navigation/login; retained shared harness stays unchanged. This adaptation changes no authoring, geometry, font, touch, containment, cancellation or file-preservation expectations. All future diagnostic connections must set defaultViewport:null; no further connection is needed while the driver owns its page.

Genuine R2 reached the actual phone File chooser but failed frozen44px sizing (label19px/buttons24px); evidence-r2 preserves raw proof/screenshots. Productdb517260c adds only STEP chooser class/scoped CSS; three actual AST/PostCSS controls fail before and pass after, and old stylesheet prefix hash is exact. style-evidence pins the updated source and82combined component/retained groups. It does not claim the new style has run in a browser; root must rebuild the real outer artifact and provide fresh pins.

Actual rebuilt20941 R3 nowPASS3viewports/40rows/3exports/6cancels with unchanged frozen checks; see evidence-r3 as current acceptance. Phone controls44px/font16, all dialogscontained; acceptedCAD/source/intent/resources/path/dirty unchanged, actualMirror/serverbytes match. Sixscreenshots/rawSTEPbytes and fresh-processchecker retained. Earlier PREPARED/R1/R2 entries are chronological, not lateststatus. No physicaldevice/generalCADUI/nativeReader claim.
