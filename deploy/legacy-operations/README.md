# Legacy operations source — review and port before execution

1075 unchanged Python sources and selected histories from `active-system/scripts/` are parent-owned historical deployment/composition tooling. The parent owns assembly/deployment composition, so these helpers do not manufacture separate repositories per ad-hoc command. App/engine implementations retain their independent owners.

Disabled historical operation/build/check sources, not current supported assembly commands. Do not import, run, bulk-discover or replay them. Before reuse, review actual host identity, credentials/custody, authorization, writable paths, external/network/process actions, source/interface dependencies, fixtures and rollback. Port against owned public interfaces; do not restore old privileged globals, publish from an old script, or make old host addresses authoritative.

These sources are not wired into build, deploy, service, test or browser entrypoints. They may contain top-level remote/system actions even if their names contain check or test. Only AST syntax, source fidelity, selected-history screens and clone composition were verified; no legacy operator or acceptance driver ran. Existing syntax warnings remain documented rather than silently repaired.

Current-source credential-related references, opaque literals, unresolved syntax/language cases, historical flags and alias collisions remain held privately for review. A flagged reference is not necessarily a real secret. This bounded screen is not external-publication clearance. No secrets were redacted in imported code to manufacture a byte-identical claim. Original recovery retains all withheld source/history.

See migration/LEGACY-OPERATIONS.md and private phase39 maps/checkpoint. No original workspace, host configuration or deployment changed.
