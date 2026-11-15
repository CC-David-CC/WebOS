# Drawing command registry: source-confirmed metadata budget blocker

Source-only diagnosis/correction. No module import/evaluation, mock host,
registration call, probe, unit test, type check, build, Native or browser run.

The complete combined EqualRadius R1 timed out in h.launch before any CAD
command/save. Root preserved it as8939c7b. Its harness did not capture the
actual page exception before cleanup. This note does NOT retroactively claim
that timeout contains an observed registry error.

A deterministic source blocker nevertheless exists in the exact composed
drawing adapter0572062ab and registry:
- active-system/assets/desktop/command-registry.mjs register serializes the
  entire parameters object and rejects JSON text length>4096, throwing
  TypeError('Invalid command parameters description.').
- apps/system/jsketcher/drawing-commands.mjs adds a300-character nested
  definition.description. It is duplicated inside each create/replace schema.
- Static transcription of only the literal schema, ordinary compact JSON
  length arithmetic (not execution of registration/module code) gives:

| Schema | Qualified v1 metadata | Isometric057 | Corrected |
| --- | ---: | ---: | ---: |
| create |3989|4320|3954|
| replace |4061|4392|4026|
| remove |373|373|373|

All strings counted here are ASCII, so JSON UTF-16 character length equals
these counts. The new versions/basis enum adds14 characters. Removing the new
description removes317 serialized characters (300 text +17 field overhead).
Compacting existing dimension prose292->243 saves another49. The corrected
schemas are35 characters SMALLER than the old qualified variants, and the
largest is70 below the unchanged4096 cap. No limit was broadened.

The correction removes definition.description from parameters, retains EVERY
schema field/domain/enum/required/ref, and preserves the existing dimension
variant/axis/nonnegative-distance/paper-mm meaning in compact prose. The v1/v2
view/physical semantics move to the existing COMMAND descriptor.description:
239 chars, below its separate512 cap. Full authoritative validation stays in
the same shared Core definition/Worker/manager; argument/definition64KiB caps,
source/native budgets, drawing J and actual .cad format are unchanged.

Index source registers EqualRadius once, before Drawing; the EqualRadius
adapter uses two normal small flat schemas and performs no top-level Native
work. It needs no repair for this source blocker. The drawing helper's existing
registration unwind/custody is retained. There is no UI redesign or new fallback.

Root must compose the new host source, regenerate exact outer/package pins and
rerun the COMPLETE unchanged workflow with actual terminal diagnostics. A
source budget calculation is not an application PASS or proof that this is the
only cause of the retained launch timeout. Preserve the first failure.
