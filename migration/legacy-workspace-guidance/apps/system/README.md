# System-served desktop applications

These folders are the source used by the app builder: calculator, files, help,
terminal, text, image-editor, document-editor, pdf-viewer, spreadsheet, data-explorer and audio-editor. Background libraries include ffmpeg, wavesurfer and tone. Each exports `mount(host)` and returns an element and a
`dispose()` callback. Shared desktop services supply identity, storage and the
Linux terminal. The app builder packages only explicit entries and dependencies.

Chat, Chess and peer Rooms were removed from this simplified branch. The live
site and other branches are separate and are not changed by this worktree.
