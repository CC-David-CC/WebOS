# Simplified desktop: app guide

This beta desktop is intended for students exploring engineering, computing and creative work. Sign in, open **APPs** at the bottom of the right-hand bar, and choose a tool. Your account is at the top of that bar. Use **Files → Upload** to bring in a computer file; open and save app work in **My files**. My files keeps a browser copy and synchronizes it to the account service when available. A synchronization or conflict notice needs attention: keep both versions and resolve the conflict in Files. Linux's temporary home is a separate drive and resets with the guest; copy work explicitly if you need to keep it. The desktop account does not grant access to unrelated outside services.

The table describes useful starting points, not a promise that every feature or file format has been reviewed. The detailed [review tracker](APP_UNIFICATION_PROGRESS.md) records tests and remaining work. Simulated results and exports must be independently checked before use on real equipment.

| App | Start here | Current boundary |
| --- | --- | --- |
| Files | Browse My files, upload, create, copy, rename and sync. To move or copy files, select them and choose **Move to…** or **Copy to…**. Right-click a file and choose **Download** to save it to your computer. You can also drop computer files into the current folder to upload them. | Temporary Linux files are separate; folder moves are not supported. If a multi-file move stops, check the destination before retrying. Physical touch dragging is still under review. |
| Terminal | Explore the temporary Linux shell; use `nano` to edit. | Its files reset with the guest and are not automatically mounted into My files. |
| Text Editor (CodeMirror 6) | Open or create a text/code file, edit and save. | Very large files can be slow and memory-intensive. |
| Help | Read beta contact and Linux information. | Help is not an exhaustive manual. |
| Calculator | Enter an expression or use the keypad; choose angle units, then save or reopen a calculation note in My files. | Results are floating-point approximations. A reopened result is recorded, not recalculated; new notes preserve the Ans input needed to repeat that calculation, but older notes do not. Earlier Ans history is not preserved. |
| Browser | Listed under Applications as **Browser (in development)**. | Disabled while in development; its experimental profile is temporary and does not support audio. |
| Document Editor (Tiptap) | Write a report with headings, underline and strikethrough; save it and export a PDF. | Editable `.doc` is this app’s format, not Word; export PDF for sharing. |
| PDF Viewer (PDF.js) | Open, search, navigate and rotate a PDF for reading; enter its document password if prompted. Fit width restores its fitted zoom. | Read-only; rotation is view-only and resets on reload. Image-only scans need OCR. |
| Spreadsheet (Jspreadsheet CE + SheetJS CE) | Start with the optional measurement example or edit a workbook in the native format; import CSV or TSV and export CSV. | Very long cells are shown as read-only previews; export CSV to use the full value in Text. CSV/TSV imports remain limited to 8 MiB. Formula display defaults to 12 significant digits; Formula help can show full precision, while calculations and exports retain full floating-point values. XLSX is optional and compatibility is limited. For example, `=-2^2` evaluates to `-4` here; use parentheses when exchanging formulas with Excel. |
| Data Explorer (Perspective + DuckDB) | Create the synthetic resistor example, try its plot, or choose whether the first CSV/TSV row is column names or data before opening; query with SQL and save a project or CSV. | Large inputs can consume substantial memory; CSV export warns on common formula-like text but keeps original values. |
| Python Notebook (JupyterLite + Pyodide) | Run the measurement example with Shift+Enter or Run, edit it, then save to My files. File → Import data from My files copies data into browser-local Python storage; File → Save working file to My files copies output back, including a relative path such as `results/plot.svg`. | Copies do not sync automatically; reimport data in another browser using the same working name. If automatic saving pauses, use File → Save to My files. Kernel startup can fail; large copies use extra memory. Untrusted notebooks are not isolated; browser Python differs from temporary Linux. |
| Image Editor (Filerobot) | Create a blank image or open an image, add a watermark or annotation from My files, and save a copy. | Animated images are unsupported; annotation images use a temporary gallery. |
| Audio Editor (AudioMass) | Choose File → Try 440 Hz tone, open or record audio, or add tracks from My files. Save an editable MultiTrack project or export a WAV mixdown. | Tested import paths accept mono/stereo; the WAV is not an editable project. Other AudioMass tools may remove beat/snap settings and long names can be shortened. Physical microphone behavior remains unverified. |
| Diagram Editor (diagrams.net) | Open or create a diagram, save it, or export SVG/PNG to My files. | Other export formats and physical touch remain under review. |
| Sketch Board (Excalidraw) | Draw a sketch, insert raster images or self-contained static SVG from My files, save the drawing, or export PNG/SVG with optional transparent background. | Drawings with unrecognized element types are refused to protect the original. SVG insertion is limited to static self-contained artwork; large images use more memory. |
| Vector Editor (SVG-Edit) | Try the example or draw vector artwork, then save an SVG. | SMIL and common inline CSS animation are refused to protect the original. Other CSS animation, complex SVG and physical touch remain unverified. |
| Primitive 3D Modeler (Replicad) | Try the 40 × 40 × 20 mm box lesson, choose dimensions and an optional offset hole, then inspect and export the model. | The preview reports approximate solid extents. This is a limited model generator, not a full CAD system; validate manufacturing dimensions. |
| Fabrication Studio (Kiri:Moto) | Try the File menu’s 20 mm example cube or open a model, configure slicing and export; save a workspace. | Check printer profiles and output independently before printing. |
| Mesh Editor (Mesh:Tool) | Add the 20-unit example cube or import and manipulate meshes; save a workspace or export geometry. | Undo history is not saved; change tracking is incomplete, so save explicitly before closing. Verify geometry independently. |
| G-code Viewer (G-code Preview) | Open supported G-code from My files and inspect the path using the extrusion/travel legend. | Some files with G29/G30 can be shown only as an explicitly confirmed hypothetical path; unsupported commands are refused. It does not validate machine safety. |
| Arduino Simulator (AVR8js) | Run an example, try the digital-input exercise or open supported HEX; inspect output and save an example’s C source. | Executes AVR firmware, but is not an electrical simulation. Browser compilation is not live. |
| Pico Simulator (RP2040js) | Try the Blink exercise or load supported RP2040 firmware and inspect serial. | Firmware and peripheral support are partial; no physical-board validation. |
| Digital Logic Simulator (DigitalJS) | Try gates, adders, multiplexers, comparator and decoder examples, toggle inputs and inspect or save a truth table. | JSON combinational circuits only; no sequential circuits or full schematic editor. |
| Circuit Simulator (CircuitJS) | Try the voltage divider, RC filter or rectifier and inspect simulated output; save output-probe readings to CSV from the File menu. | Probe CSV is one simulated instant, not a waveform or physical measurement; verify hardware separately. |
| Electronics Design (designElectronics) | Work with breadboard, schematic and PCB views; save the project. After opening a project, use Save As with a different filename. | The original is protected because the editor may omit unsupported parts from a copy. Inspect both files; component coverage and production-board validation remain incomplete. |
| Embroidery Studio (StitchFoundry) | Try the stitched rectangle, create and save a project, and export stitches. | Pre-release editor; machine compatibility and physical sewing are unverified. |
| Stitch Converter (tsembroidery) | Open SVG artwork, set the labeled size and format, preview stitches, then save editable artwork and machine output separately. | Gradients may become one approximate thread color and masks may be ignored; other SVG features may be omitted. Inspect and test-sew. |
| Falling Blocks | Play, choose sound and volume in Settings, and save or reopen a game. | Preview; sound starts muted. |
| Owl Companion | Try an activity, save and reopen your progress. | Preview uses a procedural placeholder while authored Rive art is pending. |
| Snake Garden | Choose a garden or endless game, play and save your progress. | Preview uses a procedural guide; physical touch remains unverified. |
| Physics Playground | Create objects, run the simulation, and save a checkpoint. | Preview uses simulated physics; XR and physical-device behavior remain unverified. |
| Other Games previews | Open **APPs → Games** and choose a group. The game list below gives a starting point for each preview. | Physics and World groups have XR planned; headset support is not yet established. Many assets are placeholders. |
| Personal template | Example for app authors. | Not a finished end-user app. |

### Game previews

All games are previews. Use the in-game save controls to keep checkpoints in My files where offered. Physical touch, audio and complete playthroughs are not verified for every game; the [app review status](APP_STATUS.md) lists the current boundaries.

**Arcade**

- **Falling Blocks:** Rotate and place blocks to clear lines.
- **Chess Study:** Play either side against a local computer, or try a practice position.
- **Solitaire:** Build foundations from a Klondike deal; choose draw-one or draw-three.
- **Sky Courier:** Fly through the route, deliver and avoid obstacles.
- **Snake Garden:** Guide the snake toward food without colliding.
- **Lantern Leap:** Collect lanterns and reach the exit in each room.
- **Garden Defense:** Build and upgrade towers along a route to defend the garden.
- **Pocket Rally:** Drive laps through checkpoints and improve your time.

**Physics games — XR planned**

- **Physics Playground:** Arrange objects, run the simulated physics and try a challenge.
- **Marble Works:** Build a track and run a marble through its course.
- **Stack & Balance:** Place blocks and keep the stack stable.
- **Sling Targets:** Aim and launch to knock targets past the scoring line.
- **Gravity Pinball:** Launch the ball and use the flippers to score.
- **Kinetic Relay:** Arrange mechanisms to reach checkpoints in order.
- **Tabletop Bot Arena:** Control a toy robot against a local opponent.

**World games — XR planned**

- **Clockwork Room:** Solve the room’s four mechanisms to unlock the exit.
- **Crystal Defense:** Build and upgrade towers to defend the crystal.
- **Drone Circuit:** Fly through the ordered gates on a course.
- **Pocket Golf:** Aim and putt through miniature-golf holes.
- **Target Garden:** Aim at moving mechanical targets.
- **Orbital Courier:** Collect parcels and deliver them to the dock.
- **Clockwork Quest:** Explore the rooms, solve mechanisms and rescue Pip.

**Interactive games**

- **Owl Companion:** Try the blink, firefly and expression activities.
- **Reactive Control Desk:** Adjust instruments to complete repair orders.
- **Story Cards:** Choose paths through a branching story.
- **Expression Puppet:** Adjust facial and pose controls to match challenges.
- **Rhythm Garden:** Tap lanes in time with the notes.
- **Memory Garden:** Reveal pairs of matching cards.

### Try a model-to-toolpath workflow

In **Replicad**, set the box dimensions, save the project and select **Create model** to save an STL in My files. In **Kiri:Moto**, use **Open from My files** to choose that STL, then select a printer profile and use its slicing and export controls. Save the resulting G-code to My files. Try opening that file in **G-code Preview** to inspect the drawn path; the ordinary preview refuses G29 or G30 probing commands. For a supported file, you can choose **Analyze hypothetical path**, read the assumptions, and confirm to inspect an estimate. Probing and moves from unknown positions are omitted; unsupported files are still refused. You can reopen saved files in another signed-in browser after they have synced.

This is an example of moving work between apps, not approval to run a printer. The G-code viewer omits homing movement and supports only a subset of controller behavior. Check the profile and toolpath with tools appropriate to the actual machine before using it.

Items shown disabled under System Tools are shared capabilities for apps, not independent applications. Third-party and AI features deferred from these apps are tracked in [Deferred app features](DEFERRED_APP_FEATURES.md).

In Files, select an account file and choose **Open in Text** to edit its UTF-8 source even if Open normally launches another application. Save, then open it in the other application to see the updated file.
