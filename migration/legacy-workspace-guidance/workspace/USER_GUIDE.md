# Student guide: simplified webOS preview

This is a prototype for coursework and engineering experiments. Sign in to use the desktop. Open apps from Applications; your previous windows may be restored. Apps run in your browser, while the server provides account and file services.

## Keep your work in My files

Open **System Tools → Files** and choose **My files**. Right-click in a folder to create a file or folder or upload files from your computer. Select a supported file to open its associated app, or use **Browse My files** inside a supported app. In an editor, save explicitly and watch its status. A save first updates this browser's copy; the server sync happens afterward. If the browser is offline or a conflict is reported, do not assume the server has the latest copy. Reconnect and resolve the issue in Files before relying on another device.

A browser can clear its local storage. The server copy helps recovery only after synchronization succeeds. There is no restore/history feature yet. Deletions synchronize, so deleting a file can remove both copies. Keep independent backups of important coursework.

Linux has a separate temporary filesystem that resets on reboot. Files can browse it using the **temp_linux** drive; other desktop apps use My files. To open a Linux file in another app, select it in temp_linux and use **Copy to account**. The two drives do not automatically synchronize. My files currently has an 8 MiB per-file limit.

## Common tasks

- **Notes or code:** Create or upload a `.txt`, `.md`, `.py`, or other supported text file in Files, open it in Text Editor, edit and save. Reopen it from Files to check the saved copy.
- **Reports:** Open Document Editor, write and save its `.doc` project in My files. Its `.doc` is this application's own format, not a Microsoft Word document. Export a PDF to share, or preview it using the separate PDF Viewer.
- **Tables:** Spreadsheet saves its own `.codisheet` format and can import `.xlsx` files. Imported files may contain features that the prototype does not preserve; check the result before relying on it.
- **Data:** Upload a CSV to My files, then open Data Explorer and browse to it. DuckDB and Perspective run in the browser to query and view the data. Large datasets may exceed the preview's file and device limits.
- **Python:** Applications → Programming → Python Notebook — Browser starts JupyterLite with Pyodide. Save notebooks as `.ipynb` to My files. Browser Python is not a full Linux process environment. The separate Linux notebook launcher is not yet available; Terminal runs in the temporary Linux guest.
- **3D printing:** Kiri:Moto, Mesh:Tool and G-code Preview run in the browser. Open a supported model or G-code file from My files; explicitly export results to My files. Review the machine and print settings yourself before sending anything to a printer.
- **Diagrams and images:** The diagram and image apps have their own formats and controls. Save or export to My files; an app's temporary workspace is not necessarily saved automatically. Image Editor currently accepts PNG, JPEG and WebP, not animated GIF editing.

Some embedded tools still offer an upload from your computer or use their own file controls. Their presence does not guarantee that every feature is integrated with My files. Shared System Tools are capabilities for applications; a disabled menu entry does not mean it has its own interactive window.

## Security and current limits

The notebook currently requires an extra JavaScript capability under its notebook URL and runs on the same origin as the desktop. Treat notebooks and third-party content as trusted; isolation for untrusted notebooks is unfinished. Linux SSH, per-user relay logs, and a native Linux notebook kernel are not yet enabled in this preview. Check the app's status and keep copies of important work while the prototype is being developed.
