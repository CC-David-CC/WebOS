# Public source release on GitHub

The owner authorized publication of the WebOS source under the personal GitHub account `CC-David-CC`. The assembly comprises one parent and 131 independent component repositories. Each destination is public. Use the exact sibling names in the committed parent manifest. GitHub creation, source publication, and deployment to ksu.codes are independent operations.

## Current checkpoint and resumption

The private publication ledger records all 132 destinations, exact component
pins, creation and push receipts, source reviews, and resumable checkpoints.
Regenerate its status from the ledger's `render_status.py`. The ledger stays
outside public source, along with raw scan reports and authentication material.

- Read the destination, creation and publication receipts before writing to GitHub. Compare live owner, visibility, repository ID and refs with the ledger. Inspect an ambiguous response before retrying. Verify an existing repository independently when its creation receipt is missing.
- Check the existing workers and the recorded next creation slot before starting an operation. The rate policy below applies to the publication job.
- Use the operator-managed GitHub identity. Confirm that the API and Git transports identify the same authorized owner before writing. Keep credentials in the operator environment.

- The initial pin snapshot predates some active Craft work. Reconcile it with the chosen final parent and its exact gitlinks before calling the release complete. Review intended WIP branches separately. Staged changes, untracked files and uncommitted drafts require explicit selection for publication.

The parent pins 92 app repositories, seven platform components, nine engines,
19 shared libraries, two asset repositories, one tooling repository and one
legacy repository. PCBCraft and FieldCraft own the editor sources.
`pcbcraft-app` owns the PCBCraft browser packaging. When moving a component
to an owner fork URL, verify that the selected commit is reachable at the new
URL and update the exact parent pin.

SolidCraft and WordCraft now each have a public component repository with separate upstream and WebOS refs. [SolidCraft](https://github.com/CC-David-CC/solidcraft) has upstream main `c22baab6e505` and the hosted source on `webos/solidcraft-account-fillet-repairs` at `71a573e23441`. The tested WebOS source is `030b30262ede` on `webos/integration`. The public fork accepted the push at 03:18 UTC on November 19. A subsequent ref read verified [the integration branch](https://github.com/CC-David-CC/solidcraft/tree/webos/integration) and both the upstream and hosted source refs. [Upstream PR #19314](https://github.com/tangency-labs/solidcraft/pull/19314) comes from its focused geometry branch. [WordCraft](https://github.com/CC-David-CC/wordcraft) has upstream main `6ef13b2cc8a6` and `webos/integration` at `edeb4a090cd3`. Both pairs of public refs were verified against the owner destinations. Actions were disabled on the newly provisioned WordCraft destination for the source import because its upstream build and release workflows trigger on push.

## Timing of GitHub operations

All WebOS publication workers share the private ledger’s `github-pacing.lock` and `github-pacing.json`. Wait at least 15 seconds from completion of one GitHub operation to the start of the next. This applies across repository creation, uploads, ref verification and API reads. A rate-limit response pauses every worker for at least 15 minutes. Honor a longer Retry-After or exhausted-quota reset. New repository creations and forks use a separate 20-minute minimum interval. A creator waiting for that interval releases the shared lock so pushes and verification can proceed after the normal 15-second delay. A global rate-limit cooldown applies to both queues. The `github-actions.jsonl` receipt log records timing and exit status. Manual publication operations use the same paced transport.

## Publishing each component

1. Record the exact source commits and intended refs. For Craft forks, retain the upstream-tracking main or master and publish the maintained WebOS branch separately. Preserve original histories locally. Inspect nested submodules, Git LFS objects and required build assets for availability on another machine.
2. Review the entire history reachable from every outgoing ref for secrets, private data, generated builds, unlicensed material, and GitHub blob limits. Review flagged fixtures in context. A clean automated scan is one input to review. ACAD was published as separately reviewed source at `b6c24a756e9cd6473538a33ae2ac25ec6445cb1c`. Its original history and eight oversized test receipts remain private. The public assembly selects the verified source-only commit. The owner confirmed written permission for the public modified SolidCraft distribution under its brand licence.
3. Push reviewed refs explicitly to the confirmed public destination and verify their remote SHAs. Preserve existing local origins and upstreams. Record results in the ledger. Hold individual unresolved histories while publishing cleared components.
4. Publish the parent after every pinned component commit is reachable at its declared GitHub URL. Use the shared limiter to perform the independent release checkout one submodule at a time. A normal reader can use the standard recursive clone below. Check recursive submodule status for missing or mismatched commits, resolve required build assets, and build from the checkout using the documented toolchain. Record the commands, selected parent, and results.

```sh
git clone --recurse-submodules --jobs 8 https://github.com/CC-David-CC/WebOS.git
git -C WebOS submodule status --recursive
```

Public source completion requires a successful independent checkout and build. The count of repositories created measures provisioning only.
