# Terminal session source ownership

Terminal now owns its original PTY/session/startup/render glue and unchanged startup test, plus four historical upgrade/scroll/touch/voice notes. Six added file bodies/modes and their selected histories are retained exactly. The original three startup-output assertions pass with original/primary/recovery source hidden. They execute the reference functions in a Node VM; no real shell/PTY/guest or browser was started.

Selected Terminal `7041257d48f232a5908b5ed3ff54c1312edf2465`; mechanical baseline `4d15d6f44c48a616a291a83e4ad0e2f14d6b0c37`. Existing view and CSS remain unchanged. The view still expects old host terminal/UI/window APIs, and the glue uses old guest/global state. Public Runtime/Desktop/Linux session interfaces, assets/dependencies and actual guest/host lifecycle must be ported before activation. Human/agent actions must reach the same explicit instance/session/resource operations; view disposal must not implicitly kill shared services/jobs.

Historical documentation is old evidence, not new acceptance or permission to execute commands. No microphone, clipboard, touch, account synchronization or agent acceptance was run. Terminal and Linux/v86 are still optional, outside the minimum. No new service or dependency is enabled.

Private maps, source/history checks and checkpoint: `/home/dflanag3/Projects/.webos-migration/run-20261115-43-terminal/`.
