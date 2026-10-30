# Compact and powerful: the experience contract

## The target is task coverage, not button coverage

A useful plain-text editor lets someone open a file, understand its identity,
read and edit, find a passage, move through a longer document, adjust readability,
save safely, and recover from ordinary failures. “80%” is a product aspiration,
not a measured feature-completeness claim. A nearly complete collection of
buttons is less important than these workflows behaving predictably.

The baseline is calm. A temporary tool occupies space only while being used.
Settings do not belong beside the commands repeatedly invoked during work.
A rare but consequential event (save failure/conflict) must remain visible.

## Desktop arrangement

```text
File  Edit  View  |  Reload from disk  Find…         document.txt  [Save]
─────────────────────────────────────────────────────────────────────
Document
─────────────────────────────────────────────────────────────────────
Save / error state                         Line, column · counts · UTF-8
```

One normal desktop command row is 40 CSS pixels tall. The v0.1.0 36+44px pair
consumed 80px, so this revision returns 40px to the document without shrinking
its font. This is measured in the default fine-pointer desktop preview, not a
universal height under every font/input configuration.

Open moves to File on desktop. Word wrap defaults on and moves to View. Reload
and Find sit immediately to the right of View, as requested. Save remains a
single prominent action at the far right because persisting work deserves a
stable visible target. The filename/dirty mark can shrink without pushing the
commands out of the window; the complete path is also available as a tooltip.
The outer shell title continues to carry the document title.

“Reload from disk” is the requested UI label. It still invokes the existing
mirrored-file sync/read flow. It does not bypass authorization, imply physical
disk access, or claim the remote server is reachable.

## Command map (implemented)

| Surface | Commands |
| --- | --- |
| File | Open, Save, Save As, Reload from disk |
| Edit | Undo, Redo, Find, Replace, Find next, Find previous, Go to line, Select all, Indent and Outdent |
| View | Word wrap (checked initially), Increase / Decrease / Reset text size |
| Desktop quick actions | Reload from disk, Find, Save |
| Phone bottom actions | Open, Save, Find |
| Phone overflow | The same File / Edit / View commands in grouped sections |

Find opens an inline strip with query, case toggle, match count, previous/next,
and close. Replace adds a temporary second strip for one or all matches.
Enter/Shift+Enter navigate from the query; F3/Shift+F3 work in the editor. Matching text is selected and revealed. Escape returns to the editor.
Go to line uses a temporary inline input; it is not another permanent panel.
Text size lives under View, leaving browser zoom shortcuts untouched.

The phone keeps the approved top document header and bottom actions. The shared
command definitions, document and file operations are unchanged by layout.
A narrow desktop window gets the compact layout too. Container width controls
layout; a touch-capable wide device may still receive larger interactive targets.
No device-name or user-agent branch selects a second application.

## Deliberate exclusions this pass

No ribbon, file tree, minimap, document tab strip, global command palette, font
family picker or permanent formatting controls. Those are not prerequisites for
ordinary text editing. No disabled placeholder features advertising work that
is not implemented.

CodeMirror owns history, selections and text editing. Undo, redo, replace and
indentation are editor transactions; Tab continues to move focus rather than
trapping keyboard users. Line numbers are visible, and Python and JavaScript/
TypeScript files use syntax highlighting. Additional languages, folding and
further editor controls can be added based on real use rather than placeholders.

New documents continue to use the shell's existing new-editor workflow. A future
in-app New command should be based on an explicit unsaved draft versus loaded
file model, not a magic path named Untitled.txt that may already exist.

The shell prompts before closing a window with unsaved edits. Files and the
shared account picker handle access to My files; disk picking and system-wide
dialog behavior remain shell responsibilities.

## CodeMirror as a reusable system capability

The disabled-looking **CodeMirror 6** System Tools entry is a capability for
applications, not an interactive window. `host.tools.loadCodeMirror()` loads a
locally bundled, pinned module on demand. Every Text window creates and destroys
its own view, document, selection and history. The editor surface remains the
editing authority; the host receives text snapshots at save, load and disposal
boundaries, not a second editable document.

JupyterLite already embeds CodeMirror through JupyterLab. At the user's request,
it keeps that separate copy: notebook cells and Text use independent packages
and state. Replacing JupyterLab's internal bundle with the desktop module is not
required and should not be attempted by manipulating private Jupyter internals.

The browser tests cover independent Text windows, replace and indentation with
undo, delayed-load disposal, touch-sized layout, save during editing, file
conflicts and voice insertion through an editor transaction. Physical Android
keyboard and IME testing remains outstanding. Future consumers must own their
views and release them on close; a shared module is not a shared document.

## Small next usability session

Use the real shell on a PC and physical phone. Open a long note, make an edit,
find the second occurrence of a word, jump to a line, change wrap/text size,
save, provoke an external revision conflict, recover with Save As, then close
the app. Repeat with the phone keyboard open. Observe missed commands and
interrupted typing, not how many buttons a participant can identify. This
package's simulated checks do not replace that end-to-end session.

## Primary technical references

CodeMirror System Guide: https://codemirror.net/docs/guide/
CodeMirror API Reference: https://codemirror.net/docs/ref/
CodeMirror multiple-view example: https://codemirror.net/examples/split/
WAI-ARIA menu button pattern: https://www.w3.org/WAI/ARIA/apg/patterns/menu-button/
WAI-ARIA menu keyboard behavior: https://www.w3.org/WAI/ARIA/apg/patterns/menubar/

These references support the editor and interaction conventions; they do not
constitute an accessibility certification.
