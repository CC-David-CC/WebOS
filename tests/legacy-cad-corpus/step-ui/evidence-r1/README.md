# Retained first UI run — FAIL before authoring/File flow

Exact prepared driver78e949e877cea1f0c95ee87fdc6173283737026f on root20940 f714833e80a0b6e13845de7bb33e60bcaf0456e5 / Desktop8f7a1ba7dc2725835e047ecc4430293f1cc1d86b. Run local exec61743 exit1; owned context closed and shared browser disconnected, root service retained.

No native or File-menu/layout rows reached. The driver logs in at the shared harness's1600×1000, then changes isMobile/hasTouch. Puppeteer's mobile-emulation transition reloads the document; the signed session is RAM-scoped, so the subsequent registered-session guard times out at120000ms. Failure screenshot shows login. This is a harness ordering error, not evidence of STEP/native/UI failure. Fix will set emulation before navigation/login in a new UI-only harness, preserving fonts/touch/containment/export assertions.

A diagnostic browser connection omitted defaultViewport:null; this may reset viewports on attached pages, so its observation is not an isolated causality proof. No further diagnostic attachment, service or accepted-model mutation was performed. The failure, original source hashes and overall FAIL stay unchanged. No successful workflow claim or exception waiver.
