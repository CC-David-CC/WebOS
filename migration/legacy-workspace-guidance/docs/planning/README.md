# Silo planning report

Open `SILO-MATRIX.html` in Chromium for the searchable/sortable offline report.
It defaults to shortest remaining implementation effort. Use `SILO-MATRIX.md`
for a plain table, `SILO-MATRIX.csv` for a spreadsheet, and `SILO-MATRIX.json`
for structured data. The HTML can export the current filtered rows as CSV.
No server or external JavaScript is required.

Rebuild all report formats with Python 3:

```sh
python3 docs/planning/build_silo_matrix.py
```

Edit the rows and assumptions in that source file, then regenerate. Preserve
working/partial/missing distinctions, evidence references and dependencies.
Percentages are coarse judgements of the stated scope, not audited metrics.
Time estimates are remaining focused engineering effort; one day is eight
hours. Proof time is additional. Dependency waits and external asset/device
acquisition are excluded. Do not add overlapping silo estimates into an
unqualified project delivery date or average the percentages.

The HTML was checked in Chromium for row rendering, search, area filtering,
implementation-time sorting, completion sorting and reset. This validates the
report behavior, not its estimates or any software feature described by a row.
An initial file smoke used snap Chromium's inaccessible `/tmp` namespace; a
later row-count assertion also counted a `<tr>` string inside script source.
Both checks were corrected to use a home-directory copy and actual DOM rows.
The interaction check then passed. No application or live service was changed.

Planning date: 2026-11-03. Status basis: saved checkpoint and scoped 2026-11-01/02
app/game evidence. Development remains paused. For scope and detailed status,
read `../WEBOS-SILOED-WORK.md`, `../WEBOS-WORK-QUEUES.md`,
`../APP_STATUS.md`, `../GAME_PREVIEW_REVIEW.md` and
`../HANDOFF-STORAGE-BETA-2026-11-02.md`.
