# Public source release on GitHub

The owner authorized publication of the WebOS source under the personal GitHub account `CC-David-CC`. The assembly comprises one parent and 125 independent component repositories. Each destination is public. Use the exact sibling names in the committed parent manifest. GitHub creation, source publication, and deployment to ksu.codes are independent operations.

## Current checkpoint and resumption

The local ledger is in `../.webos-migration/github-publication.MJn2SZsB/` relative to the WebOS repository root. Its `STATUS.md` lists all 126 destinations, on-disk paths, creation state, source state and available review results. Regenerate it with `python3 render_status.py` from that ledger directory. The ledger is outside the public tree. Keep scanner reports and authentication material out of Git and release archives.

- Read `destinations.json`, `creation.jsonl` and `published.jsonl` before writing to GitHub. Compare live owner, visibility, repository ID and refs against the ledger. Inspect any ambiguous response before retrying. An existing repository without a matching creation receipt requires independent verification.
- The first ten destinations were created. The first creation throttle occurred on WordCraft at 00:49 UTC on 19 November 2026. The next attempt waits at least 15 minutes, honors a longer GitHub cooldown, and spaces successful creations by 75 seconds. If GitHub continues throttling, increase the wait and retain the same account and transport. Consult the ledger for newer results. Check for an existing worker before starting a second one.
- The GitHub CLI on box-git creates repositories. Its API identity and the existing Git SSH identity both verified as `CC-David-CC`. Git sends the pack through box-git using its existing SSH identity. Credentials stay on box-git. The ledger contains the prepared creation, inventory, audit and push commands.
- The initial pin snapshot predates some active Craft work. Reconcile it with the chosen final parent and its exact gitlinks before calling the release complete. Review intended WIP branches separately. Staged changes, untracked files and uncommitted drafts require explicit selection for publication.

The current assembly pins 128 components plus the parent. The original 126-destination ledger predates the three Tangency additions. The parent already references the public upstream commit for each of those three. PCBCraft and FieldCraft own editor code. The third repository, pcbcraft-app, owns PCBCraft browser packaging. Keep future WebOS edits on component branches and switch a parent URL to the owner's fork once that exact pin is published there.

SolidCraft and WordCraft now each have a public component repository with separate upstream and WebOS refs. [SolidCraft](https://github.com/CC-David-CC/solidcraft) has upstream main `b695a9b35294` and `webos/solidcraft-account-fillet-repairs` at `71a573e23441`. [Upstream PR #19314](https://github.com/tangency-labs/solidcraft/pull/19314) comes from its focused geometry branch. [WordCraft](https://github.com/CC-David-CC/wordcraft) has upstream main `6ef13b2cc8a6` and `webos/integration` at `edeb4a090cd3`. Both pairs of public refs were verified through box-git. Actions were disabled on the newly provisioned WordCraft destination for the source import because its upstream build and release workflows trigger on push.

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
