# App workflow review

This is the working checklist for the Simplified desktop's app-by-app review.
“Prior evidence” refers to existing checks, not completion of the new review.
Every interactive app still needs a fresh review of its primary workflow,
account-backed open/save where applicable, first-run experience, desktop and
phone-sized interaction, cleanup, and an honest user-facing explanation.
Physical-device testing is separate. Shared tools need a tested consumer rather
than a standalone editor workflow. See `APP_WORKFLOW_CHECKS.md` for earlier
check scope and `SIMPLIFIED_HANDOFF.md` for dated deployment details.

| App | Role | Prior evidence / known boundary | New review |
| --- | --- | --- | --- |
| Files | Account and temporary Linux files | Account sync and Linux copy checked; drives are separate. Touch create/upload is live; a selected-file Open action passed local phone and desktop editing, sync, close/reopen, and fresh-context checks. | In progress |
| Text | Text and code editor | Account edit/save/reopen checked. | Pending |
| Terminal | Temporary v86 Linux | No automatic account-drive mount. | Pending |
| Help | Desktop help | No document workflow. | Pending |
| Calculator | Calculator | No document workflow. | Pending |
| Browser | Independent web browser | Experimental; temporary profile and no audio. Scroll fix verified in emulation. | In progress |
| Document Editor | Reports | Account project and PDF export checked; not a Word editor. | Pending |
| PDF Viewer | Read-only documents | Open and page navigation checked. | Pending |
| Spreadsheet | Tables | Native save and XLSX import/export checked; advanced Excel compatibility limited. | Pending |
| Data Explorer | Data analysis | CSV query and chart checked; query state is temporary. | Pending |
| Python Notebook | Browser Python | Pyodide and account notebook workflow checked; untrusted notebooks are not isolated. | Pending |
| Image Editor | Images | PNG/JPEG/WebP workflow checked; animated GIF editing unsupported. | Pending |
| Audio Editor | Audio | WAV edit/save checked; no multitrack project persistence. | Pending |
| diagrams.net | Diagrams | Basic account save/reopen checked. | Pending |
| Excalidraw | Drawings | Basic account save/reopen checked. | Pending |
| SVG Editor | SVG artwork | Basic account save/reopen checked. | Pending |
| Replicad | Code-based CAD | Basic model generation and export checked; not a full CAD editor. | Pending |
| Grid tools: Kiri:Moto | 3D printing | Model import and G-code export checked; printer settings need independent review. | Pending |
| Grid tools: Mesh:Tool | Mesh editing | Import, union and account export checked. | Pending |
| G-code Preview | G-code viewer | Viewing checked; not an editor or printer connection. | Pending |
| Arduino Simulator | AVR firmware | Blink and independent windows checked; simulation is not hardware validation. | Pending |
| Pico Simulator | RP2040 firmware | Blink checked; flash and SSI support are partial. | Pending |
| Digital Logic | Gates | Basic gate and account save/reopen checked; no full schematic editor. | Pending |
| Circuit Simulator | CircuitJS | Divider simulation and account save checked; not ngspice. | Pending |
| Electronics Design | Electronics editor | Account project save/reopen checked; sample is not a production board. | Pending |
| Embroidery Studio | Stitch design | Example generation and account save checked; physical sewing unverified. | Pending |
| Stitch Converter | Stitch formats | Example conversion and account save checked; machine compatibility unverified. | Pending |
| Personal template | Per-user app example | Template, not a completed end-user tool. | Pending |
| CodeMirror | Shared editor capability | Used by apps; no standalone file workflow. | Pending consumer review |
| FFmpeg | Shared media capability | Programmatic conversion checked. | Pending consumer review |
| WaveSurfer | Shared waveform capability | Programmatic rendering checked. | Pending consumer review |
| Tone | Shared music capability | Programmatic synthesis checked. | Pending consumer review |
| ZIP | Shared archive capability | Files archive workflow checked. | Pending consumer review |
| Mermaid | Shared diagram capability | Programmatic capability. | Pending consumer review |
| ECharts | Shared chart capability | Programmatic capability. | Pending consumer review |
| Plotly | Shared chart capability | Programmatic capability. | Pending consumer review |
| pdfme | Shared PDF capability | Programmatic capability. | Pending consumer review |
| MapLibre | Shared map capability | Programmatic capability. | Pending consumer review |
| Transformers | Shared model capability | No model configured. | Pending consumer review |

Apps are being changed to open maximized and follow viewport resizing, including 1080p and 4K; users can restore a smaller window. The live shell passed viewport-emulation checks, including multiple windows and remembered layout. Physical F11 and device behavior remain to be checked. Electronics Design’s three-view large-screen layout needs individual investigation.
