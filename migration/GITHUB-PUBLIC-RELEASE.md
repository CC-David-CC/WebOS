# Public source release on GitHub

The owner authorized publication of the WebOS source under the personal GitHub account `CC-David-CC`. The assembly comprises one parent and 130 independent component repositories. Each destination is public. Use the exact sibling names in the committed parent manifest. GitHub creation, source publication, and deployment to ksu.codes are independent operations.

## Current checkpoint and resumption

The local ledger is in `../.webos-migration/github-publication.MJn2SZsB/` relative to the WebOS repository root. Its `STATUS.md` lists all 131 destinations, on-disk paths, creation state, source state and available review results. Regenerate it with `python3 render_status.py` from that ledger directory. The ledger is outside the public tree. Keep scanner reports and authentication material out of Git and release archives.

- Read `destinations.json`, `creation.jsonl` and `published.jsonl` before writing to GitHub. Compare live owner, visibility, repository ID and refs against the ledger. Inspect any ambiguous response before retrying. An existing repository without a matching creation receipt requires independent verification.
- The first ten destinations were created. The first creation throttle occurred on WordCraft at 00:49 UTC on 19 November 2026. The next attempt waits at least 15 minutes, honors a longer GitHub cooldown, and originally spaced successful creations by 75 seconds. If GitHub continues throttling, increase the wait and retain the same account and transport. Consult the ledger for newer results. Check for an existing worker before starting a second one.
- The GitHub CLI on box-git creates repositories. Its API identity and the existing Git SSH identity both verified as `CC-David-CC`. Git sends the pack through box-git using its existing SSH identity. Credentials stay on box-git. The ledger contains the prepared creation, inventory, audit and push commands.
- The initial pin snapshot predates some active Craft work. Reconcile it with the chosen final parent and its exact gitlinks before calling the release complete. Review intended WIP branches separately. Staged changes, untracked files and uncommitted drafts require explicit selection for publication.

The parent pins 91 repositories under `apps/`, seven platform components, nine engines, 19 shared libraries, two asset repositories, one tooling repository and one legacy repository. The public-source ledger includes the three Tangency additions. The parent already references the public upstream commit for each of those three. PCBCraft and FieldCraft own editor code. The third repository, pcbcraft-app, owns PCBCraft browser packaging. Keep future WebOS edits on component branches and switch a parent URL to the owner's fork once that exact pin is published there.

SolidCraft and WordCraft now each have a public component repository with separate upstream and WebOS refs. [SolidCraft](https://github.com/CC-David-CC/solidcraft) has upstream main `c22baab6e505` and the hosted source on `webos/solidcraft-account-fillet-repairs` at `71a573e23441`. The tested WebOS source is `030b30262ede` on `webos/integration`. The public fork accepted the push at 03:18 UTC on November 19. A subsequent ref read verified [the integration branch](https://github.com/CC-David-CC/solidcraft/tree/webos/integration) and both the upstream and hosted source refs. [Upstream PR #19314](https://github.com/tangency-labs/solidcraft/pull/19314) comes from its focused geometry branch. [WordCraft](https://github.com/CC-David-CC/wordcraft) has upstream main `6ef13b2cc8a6` and `webos/integration` at `edeb4a090cd3`. Both pairs of public refs were verified through box-git. Actions were disabled on the newly provisioned WordCraft destination for the source import because its upstream build and release workflows trigger on push.

## Timing of GitHub operations

All WebOS publication workers share the private ledger’s `github-pacing.lock` and `github-pacing.json`. Wait at least 15 seconds from completion of one GitHub operation to the start of the next. This applies across repository creation, uploads, ref verification and API reads. A rate-limit response pauses every worker for at least 15 minutes. Honor a longer Retry-After or exhausted-quota reset. New repository creations and forks use a separate 20-minute minimum interval. A creator waiting for that interval releases the shared lock so pushes and verification can proceed after the normal 15-second delay. A global rate-limit cooldown applies to both queues. The `github-actions.jsonl` receipt log records timing and exit status. Manual operations for this rollout use the same `paced-bin` transport on the laptop via box-git. Credentials stay on box-git.

## Keeping Craft upstream branches current

Track the upstream default-branch tip, the owner’s published baseline, and the latest qualified WebOS integration separately. Advancing the upstream baseline requires no WebOS rebuild, integration push, parent pin change, or deployment. GitHub’s “updated” timestamp measures activity. Use commit IDs and ancestry to measure synchronization.

| Repository type | Updating the published baseline |
|---|---|
| Registered fork with a clean upstream baseline, such as SolidCraft | Fetch the verified upstream default branch and compare its exact SHA with the public fork’s default branch. After approval, fast-forward the single baseline ref if the remote tip is an ancestor. Record and reread the resulting public SHA. |
| Independent source export with rewritten portions of history, such as FilmCraft, VectorCraft, EffectCraft and LightCraft | Treat the previously published baseline and its upstream source SHA as a pair. Review the upstream commits added since that source SHA, apply the repo’s recorded exclusions and notices, and add the resulting author-preserving source commits on top of the existing public baseline. Verify the exported tree and the new upstream-to-public mapping before a non-force push. Keep prior public commits reachable for existing assembly checkouts. |
| Independent repository carrying exact upstream commit history | Apply the same fast-forward check as for registered forks if source review permits publication of the added history. Record the upstream URL explicitly because GitHub does not supply fork comparison metadata for the repository. |

Box-git can run a persistent systemd user timer, initially hourly. Use a dedicated work area and an allowlist with the verified upstream URL, upstream ref, owner repository ID, destination ref, and publication mode for each app. Each run fetches upstream, compares the recorded tips, and queues only changed refs. For registered forks, an authorized worker can apply the fast-forward automatically after checking branch ancestry, destination identity and the publication policy. For filtered exports, the timer should prepare a source update for review. A repeatable filter and successful audit of the new commit range are prerequisites for unattended publication of those exports.

Reuse one box-git worker and the shared publication pacing rules above. Stop that repository’s update on divergence, a changed upstream mapping, missing dependencies, or a source-review failure. Record the upstream tip, previous and new published tips, pending review reason, and the last verified WebOS integration SHA in the private ledger. Existing publication scripts for initial exports assume an empty destination or matching refs. Extend and test the incremental export path before scheduling writes for those repositories.

## Publishing each component

1. Record the exact source commits and intended refs. For Craft forks, retain the upstream-tracking main or master and publish the maintained WebOS branch separately. Preserve original histories locally. Inspect nested submodules, Git LFS objects and required build assets for availability on another machine.
2. Review the entire history reachable from every outgoing ref for secrets, private data, generated builds, unlicensed material, and GitHub blob limits. Review flagged fixtures in context. A clean automated scan is one input to review. The initial ACAD source pin has eight tracked test-evidence files exceeding 100 MiB. The owner placed ACAD publication on hold. Preserve the eight receipts, its original local history, and the existing parent pin. Leave the empty public ACAD repository as created. Full recursive checkout qualification remains open. The owner confirmed written permission for the public modified SolidCraft distribution under its brand licence.
3. Push reviewed refs explicitly to the confirmed public destination and verify their remote SHAs. Preserve existing local origins and upstreams. Record results in the ledger. Hold individual unresolved histories while publishing cleared components.
4. Publish the parent after every pinned component commit is reachable at its declared GitHub URL. From an independent machine, clone with the command below. Check recursive submodule status for missing or mismatched commits, resolve required build assets, and build from the checkout using the documented toolchain. Record the commands, selected parent, and results.

```sh
git clone --recurse-submodules --jobs 8 https://github.com/CC-David-CC/WebOS.git
git -C WebOS submodule status --recursive
```

Public source completion requires a successful independent checkout and build. The count of repositories created measures provisioning only.
