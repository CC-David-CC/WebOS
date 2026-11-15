# WebOS migration assembly

The current migration handoff at `/path/to/workspace/Projects/webos-rebuild-handoff/AGENTS.md` and its architecture/runbook/verification documents govern this work. Read them before continuing. The original `/path/to/workspace/Documents/KSU.CODES` is read-only.

Each meaningful component has an independent repository; the parent owns composition and whole-system tests. Preserve Git histories and WIP before extraction. Keep mechanical changes separate from functionality. No external pushes, deployment, automatic restarts, or real-user data tests without specific authorization.

Runtime, Desktop, Login, Accounts, Storage, Files, and WordCraft are required independently. Server-backed account files and shared human/agent domain operations are mandatory. No Linux/v86 dependency in the minimum. Existing-user identity and file ownership must remain compatible.

Current state is partial; inspect START-HERE.md and the private checkpoint. Do not equate repository setup with a working system.

The scope is the entire existing suite and all 17 selected upstream forks. The initial seven-component milestone is not completion. Read migration/scope.json; keep all registered and nonregistered source, assets, and historical WIP accounted for.

Organize by role: platform/ holds Runtime, Desktop, Login, Accounts and Storage; apps/ holds every application including Files, WordCraft and original JSketcher; engines/ holds reusable execution engines. Shared library projects belong in libraries/, shared asset projects in assets/, and shared build tooling in tooling/ when ownership is established. These directories do not become grouped source repositories. Keep all existing apps and tools, including those being replaced. The user explicitly authorizes needed rewrites/refactors in new working copies. The old workspace stays read-only; retain extraction baselines and separate functional commits.
