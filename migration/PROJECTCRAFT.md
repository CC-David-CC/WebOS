# ProjectCraft source intake

ProjectCraft lives in `apps/projectcraft/`. It is an independent productivity application for project schedules, Gantt charts and critical-path calculation. The upstream repository uses MIT and Apache-2.0 licenses. The parent pins upstream `main` at `1757247b53a5641d645bfcd0b4612504c5150785`.

The upstream example entry point is `cargo run --release -p projectcraft -- --sample`. It uses a native Rust UI and opens its own `.projectcraft` JSON files. Read the upstream README for the CLI and browser build checks. The current intake records source only. Build readiness, the WebOS mount contract, Files associations, account saves and deployment await separate integration.

ProjectCraft is included as source in the public publication queue. The public assembly uses the verified upstream URL. Website and account integration are deferred.
