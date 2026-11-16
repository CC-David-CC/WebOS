# Native file chooser: double-click returns cancellation

Deferred on 2026-11-16 at the user's request: finish the website push; investigate
Chromium/Linux separately later. This is not a reason to keep rewriting Files.

In the user's existing Chromium Snap session on Linux, double-clicking an MP4
in the native chooser closes it without delivering a file. Selecting the file
and clicking **Open** works. Drag-and-drop also works. The same difference was
reproduced by the user with temporary plain HTML file inputs, with both single-
and multiple-file selection, without Files upload handlers or a server upload.

DevTools inspection of the authorized ksu.codes tab recorded a trusted cancel
event, an empty file list and an input still connected to the page. Explicit
Open delivered trusted input/change events; the actual Files view acknowledged
a 4 MiB diagnostic account save. The user also confirms Open works for their
MP4. No file-size, media-decoding or storage-quota failure was observed on the
cancelled selection path, because no upload started.

The evidence isolates the failure to the browser/native-chooser selection
path in this session. It does **not** identify the precise Chromium, Snap or
GTK defect or establish that every Chromium/Linux installation has this bug.
The plain controls were on the existing page; a standalone page without the
desktop is a useful next control if further browser work is authorized.

Current workaround: select the file and click **Open**, or drop it into Files.
Automated CDP file-chooser acceptance does not reproduce a physical native
double-click and must not be used to close this issue. Raw Chromium launched
directly and isolated GTK-dialog tests also do not reproduce all conditions of
the normally launched, Snap-confined existing browser.

No browser permissions, flags, global settings or installed packages were
changed. The existing browser was not restarted. Any later change requiring a
restart must account for open tabs and unsaved work first.

The separate Files breadcrumb bug used an invalid empty Chonky root ID; its
source fix and eight focused hosted checks are in the current
[website release report](TEST-STATUS.md). That fix is not claimed to repair the
native double-click issue.

Private reproduction records and cleanup evidence live in
/home/dflanag3/Projects/.webos-migration/files-upload-20261116-01/.
They contain user-authorized UI diagnostics and must stay outside source control
and web roots. Event probes record type, connection state and file sizes, not
authentication secrets or private file contents.
