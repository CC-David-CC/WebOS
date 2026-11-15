# Shared drawing command bridge source

The four registered public commands are `inspect-linked-part-drawing`, `create-linked-part-drawing`, `replace-linked-part-drawing`, and `remove-linked-part-drawing`. They use the same active manager and shared authored metadata transaction as the human operation. There is no adapter model, geometry writer, measurement cache, or Undo stack. Existing `travel-authored-edit` handles metadata Undo/Redo. Native realization and authorized SVG file export are separate.

Inspection returns `{version:1,unit:'millimeter',revision,geometryRevision,definition|null,ready,reason,quality:'authored-definition-only',authoredUndo,limits}`. Creation accepts `{version:1,unit:'millimeter',revision,geometryRevision,definition}`; replacement additionally requires `drawingId`; removal has `{version:1,unit:'millimeter',revision,geometryRevision,drawingId}`. The manager's existing linked drawing schema is authoritative, including datum-space axes and semantic eligibility. Definitions may retain valid unresolved authored references.

Before any asynchronous dispatch the adapter detaches and freezes bounded own JSON data, rejects accessors/sparse arrays/cycles/symbols and retains the 64KiB UTF-8 request budget. Host lifetime and committed/unknown outcomes follow the existing scoped command helper. Manager metadata publication controls strict schema, currentness, preparation ownership, journal charging and actual commit. Save remains separate and uses the native envelope path.

Source-only checkpoint: no tests, TSC, builds, browser actions or deployment were run, following the user's request to verify the completed end-to-end workflow afterward. This is not evidence of Native projection, measured dimensions, publication or persistence success.
