# Simplified app workflow checks

These are development-preview browser checks, not a claim that every feature of each embedded application is integrated. The source of a computer upload is a test fixture selected through Files; the output is saved to My files in browser storage and then synced where indicated. Files keeps Linux's temporary home separate; it offers an explicit copy to My files. Other desktop apps open account files, not Linux files. Linux home resets on reboot.

| App or feature | Checked workflow | Remaining integration work |
| --- | --- | --- |
| Files | Computer upload, folders, account browsing, ZIP creation/extraction, explicit Linux-to-account copy, sync and Linux reset. | Moving a newly uploaded file waits for synchronization. More error handling and larger files need work. |
| Text | Upload, browse a folder, edit, browser save, server sync, close and reopen. | More file types and edge cases. |
| Document Editor | Upload native project, open, edit, browser/server save, conflict handling, export and preview PDF. | Its `.doc` and `.codidoc` formats are not Word; no DOCX support. |
| PDF Viewer | Open an uploaded PDF and a document-generated preview; page navigation. | Read-only; no save operation is expected. |
| Browser | Gecko engine and signed relay integration are retained, but the Applications launcher is labeled “Browser (in development)” and disabled while higher-priority STEM apps are improved. | Experimental embedded browser; the latest themed download-dialog candidate remains local and is not in the live bundle. |
| Spreadsheet | Upload XLSX, open, edit formulas, save the native format, export XLSX and reopen. | Advanced Excel features and formatting may not survive conversion. |
| Data Explorer | Upload CSV, open, SQL query, grid and chart. | Query/chart configuration is not saved as an account project. |
| Image Editor | Upload PNG, open, resize, browser/server save and reopen. | PNG/JPEG/WebP only; animated GIF editing is not supported. |
| Audio Editor | Upload WAV, open, reverse, save WAV to browser and sync. | Multitrack project saving is not supported. |
| diagrams.net | Save and reopen a diagram; upload and open another. | More editing features need hands-on testing. |
| SVG-edit | Edit and save SVG, reopen, upload and open another. | More editing features need hands-on testing. |
| Excalidraw | Draw and save, reopen, upload and switch to another drawing. | More editing and complex embedded assets need testing. |
| Kiri:Moto and Mesh:Tool | Upload STL, import, mesh union, save model; slice and save G-code. | Other formats, printers, and settings need testing. |
| G-code Preview | Open and display a G-code file. | Viewer only; not a G-code editor. |
| Replicad | Generate simple box/cylinder models and save STL/STEP to account storage. | The current app generates models and has no general model import or full CAD editor. |
| Browser Python Notebook | Run NumPy, save/reopen notebook and open an uploaded notebook. | Native Linux kernel launcher remains disabled; notebook uses same-origin `unsafe-eval` and is not isolated for untrusted content. |
| Calculator, Help, Terminal | No general account-file upload/save interface to test. Terminal uses temporary Linux files. | Terminal guest has no integrated account mount; Linux networking/SSH remains unfinished in this preview. |
| ZIP, FFmpeg, WaveSurfer, Tone, Mermaid, ECharts, Plotly, pdfme, MapLibre, Transformers | Shared browser-side capabilities have programmatic smoke checks; ZIP and audio have app workflow checks. | They are libraries, not independent file editors. Transformers has no model configured; each future consumer needs its own file and UI tests. |

Account files are local-first and synchronize to the server asynchronously. Do not assume that a local save is backed up until Files reports synchronization. Per-file limits and browser storage availability still constrain engineering workloads. Tests run against an isolated local server and do not prove a production deployment or physical phone behavior.
