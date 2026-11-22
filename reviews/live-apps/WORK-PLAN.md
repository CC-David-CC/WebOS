# WebOS work plan

Start here for release order and dependencies. Use the [fix queue](FIX-QUEUE.md) for individual defects, the [app review index](README.md) for screenshots and workflows, and the [OpenPlayground inventory](openplayground-coverage.md) for incoming apps. Status below was reconciled November 22, 2026. Newer deployed evidence in an individual row takes precedence over this snapshot.

## Order and parallel work

```text
WebOS release queue
├─ 1. Check production regressions first
│  ├─ ACAD Modeler: native model and editable Files reopen passed
│  └─ Linux X11: local Chromium input and scoped network tests passed
│     └─ Owner-browser acceptance and physical touch remain open
├─ 2. Finish current Craft fixes in parallel
│  ├─ CADCraft: compact drawing, touch selection and view controls
│  ├─ FilmCraft: compact timeline, preview, trim and playback
│  └─ TextureCraft: a held touch can produce an empty painted stroke
├─ 3. Repair remaining Files routes and editors
│  ├─ Arduino, Digital Logic, CircuitJS: native reopen candidates
│  ├─ Electronics Design, Kiri:Moto and Mesh:Tool: next associations
│  └─ Independent editor issues: menu layout, labels, fit and cold start
├─ 4. Work down remaining app and game usability rows
│  ├─ Craft layouts, editing and recovery, then other enabled apps
│  └─ 35 games already released: remaining individual play and layout fixes
├─ 5. Qualify new apps and services independently
│  ├─ Catalog forks, OpenCADStudio and the standalone harness
│  ├─ MailCraft: identity → private mail → external delivery → cutover
│  └─ GPU-backed apps, remote desktops and development tools
└─ For each passing candidate, serialize the shared release steps
   └─ Publish components → pin in WebOS → test candidate → deploy → replay live
```

**What goes next:** Continue the three independent Craft candidates and qualify the electronics Files changes. Keep the physical-device checks available to the owner while software work proceeds. A new reproducible ACAD or Chromium regression takes priority. Each ready candidate can ship independently after its own checks. Coordinate changes to shared Desktop routing and serialize promotion of the live viewer so one release cannot replace another's work.

| Order | Where we are | Next evidence needed |
|---|---|---|
| 1 · ACAD and X11 | Both workspace modes created, reopened and resized the same ACAD solid. Chromium opened local files and accepted input. The temporary network grant and live revocation were exercised. [ACAD](acad-modeler/README.md) · [Chromium input](linux-x11/chromium-input.md) · [networking](linux-x11/scoped-network.md) | Follow up on a specific modeling failure immediately. Owner checks Terminal ping and a guest Chromium HTTPS page in the normal session. Physical touch remains separately recorded. |
| 2 · Craft | The 20-app guest and signed-in native Files baseline passed. SolidCraft's standalone fillet accepted input during calculation. SoundCraft recorded and reopened a synthetic take. CADCraft desktop selection while moving passed. [Files baseline](anon-craft-files.md) · [SolidCraft](solidcraft/README.md) · [SoundCraft](soundcraft/README.md) · [CADCraft](cadcraft/README.md) | Verify compact CAD drawing, FilmCraft preview and trim, and TextureCraft's held brush through the deployed menu and Files. Keep physical mic/playback, touch, onscreen-keyboard and pen checks open where listed. [FilmCraft](filmcraft/README.md) · [held-brush reproduction](texturecraft/tablet-paint.md) |
| 3 · Native Files | Local candidate replays passed for Arduino Blink, Digital Logic and an editable CircuitJS RC circuit in Anon and signed-in modes. Their production association finding remains open. [Files queue](FIX-QUEUE.md) | Verify exact published pins, deploy and repeat all six native reopens. Then verify .dez, .kiri and .meshproj with actual edited documents. CircuitJS menu presentation has its own finding. |
| 4 · Other enabled apps and games | All 35 audited game updates are live. Seven Learning & Strategy games passed native play and Files checks. Specific games still have sizing, reachability or gameplay findings. DRAKON Python, JavaScript, Bash and Narrator are recorded in the review inventory. [Games](game-update-checks.md) · [seven-game release](learning-games-release.md) · [app reviews](README.md) | Work through individual rows, including notebook startup, fabrication workflows and Weather Maps touch. For games, first fix broken play or resume, then test controls and resizing. Verify a meaningful action, saved state where supported, and screenshots at the tested sizes. |
| 5 · New capabilities | Fork availability, integration, and hosted verification are tracked independently. The catalog check covered 43 entries. It is one catalog rather than the whole WebOS inventory. [Catalog and per-app status](openplayground-coverage.md) | Qualify each distinct app against its pinned source and browser policy. Preserve existing desktop workflows and signed-in and browser-local Files. Record a feature as live only after its deployed test. |

## Service and intake dependencies

These workstreams can be prepared while app fixes run. Their live status must be reconciled against their own release evidence before scheduling deployment. They are separate from acceptance of the current fix queue.

| Workstream | Ordered dependencies and acceptance |
|---|---|
| MailCraft | Validate current names → reserve operational aliases and bind each mailbox to a durable account identity → prove two-account isolation, Anon behavior and send/receive on a private JMAP backend → qualify spam, queue monitoring, backup/restore and controlled external delivery → decide on public DNS and mail routing. MailCraft is the user app. The server's private administration console is the first monitoring interface. [Operator guide and readiness check](https://github.com/CC-David-CC/mailcraft/blob/33a856c7de2b4d5578f6d28b94ab9c7a64665e4f/webos/MAIL-SETUP.md) |
| GPU-backed features | Reconcile the service inventory and GPU Monitor → verify a queued request, one outstanding job per signed-in user, worker restart and result isolation → test one real PhotoCraft image operation and separate code or 3D output in their consuming apps. Record model, quantization, context tested, output and hardware. [Services](https://github.com/CC-David-CC/webos-services) · [GPU Monitor](https://github.com/CC-David-CC/gpu-monitor) |
| Remote and development tools | Keep Terminal, X11, Notebook and owner-only remote viewing as separate apps. Verify account Files, local-only use and revocation first. For remote viewing, qualify one named host with monitor sharing and keyboard/mouse before repeating for the remaining hosts. Track owner-only IRC separately. [X11](linux-x11/README.md) · [Notebook](notebook/README.md) |
| App integrations and publishing | Compare upstream, fork and WebOS integration pins. Test the independent app through its menu, editable formats and Files before promoting it. For OpenCADStudio verify a supported browser engine first. For MathCraft verify multiple labs and user-supplied source. For the three DRAKON editors verify actual exported output. Verify the standalone game harness's public ref separately from the games' release. Record upstream-worthy fixes independently of WebOS wiring. [App inventory](README.md) · [MathCraft](mathcraft/README.md) · [DRAKON Python](drakon-python/README.md) |
| Shared desktop and operations | Reconcile remaining reports for Voice Input retaining its original editor target, file associations and drops, synced app-bar settings, anonymous account upgrades, weather caching and account cleanup against their deployed receipts. Track disk capacity, temporary build cleanup and upstream synchronization as operational work. A smoke-test launch alone leaves the reported behavior open. |

## How a row closes

1. Record the user-visible failure, role, input, screen size and exact starting build. Link the existing evidence before starting another build.
2. Fix and test the owning component. Publish its commit, fetch it independently, then publish the Desktop or WebOS submodule pin. Record the public release branch and whether main includes the pin.
3. Test the exact candidate from the menu. For document apps, edit, save, close, independently reopen through Files, and edit again as Anon and as a signed-in account. Check recovery when relevant. Cover phone, tablet, desktop and 4K where layout is at issue.
4. Promote one shared viewer change at a time and repeat the affected workflow on ksu.codes. Add the deployed release identifier, screenshot and result to the [fix queue](FIX-QUEUE.md). Leave a hardware-only check or a reproduced failure open with its next action. Only the owner can approve deferral.
