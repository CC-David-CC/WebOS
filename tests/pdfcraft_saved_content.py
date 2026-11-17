#!/usr/bin/env python3
"""Check actual account PDFs from the browser fixtures with the native PDF parser.

These checks complement browser state assertions; a dirty flag/recovery dialog
does not prove the saved PDF contains pending text. Inputs are synthetic fixture
outputs, never a user's account home. The caller supplies an existing CLI.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess


def main():
    os.umask(0o077)
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('cli', 'documents', 'lifecycle', 'blanks', 'report'):
        parser.add_argument('--' + name, type=Path, required=True)
    args = parser.parse_args()
    if args.report.exists():
        parser.error('Use a new private report path; do not overwrite evidence')
    cases = [
        (args.blanks / 'Explicit-blank.pdf', []),
        (args.blanks / 'Save-blank.pdf', []),
        (args.documents / 'Authoring.pdf', ['WebOS PdfCraft authoring sentinel']),
        (args.documents / 'pending-snapshot.pdf', ['WebOS PdfCraft authoring sentinel', 'Unfinished native text recovery sentinel']),
        (args.documents / 'Recovered-before-conflict.pdf', ['WebOS PdfCraft authoring sentinel', 'Unfinished native text recovery sentinel']),
        (args.documents / 'Recovered.pdf', ['WebOS PdfCraft authoring sentinel']),
        (args.documents / 'Conflict-rescue.pdf', ['WebOS PdfCraft authoring sentinel', 'Unfinished native text recovery sentinel']),
        (args.documents / 'Account-A-recovery.pdf', ['Account A private recovery sentinel']),
        (args.documents / 'Uncertain.pdf', ['Unknown account save sentinel']),
        (args.lifecycle / 'minimized-snapshot.pdf', ['Minimized unfinished PDF recovery sentinel']),
        (args.lifecycle / 'Minimized-recovery.pdf', ['Minimized unfinished PDF recovery sentinel']),
    ]
    records = []
    try:
        for file, expected in cases:
            record = {'file': str(file), 'expectedText': expected}
            records.append(record)
            data = file.read_bytes()
            assert data.startswith(b'%PDF-'), 'Not a PDF: ' + file.name
            record.update(bytes=len(data), sha256=hashlib.sha256(data).hexdigest())
            results = {}
            for operation in ('info', 'text'):
                command = [str(args.cli), operation, str(file)]
                run = subprocess.run(command, env=dict(os.environ, PDFCRAFT_SYSTEM_FONTS='0'),
                                     capture_output=True, text=True, timeout=30)
                record[operation + 'ExitCode'] = run.returncode
                assert run.returncode == 0, operation + ' failed: ' + file.name
                results[operation] = run.stdout
            info = json.loads(results['info'])
            assert info['pages'] == 1, 'Expected one page: ' + file.name
            assert not info['repairs'] and not info['warnings'], 'PDF parser reported repairs/warnings: ' + file.name
            for sentinel in expected:
                assert sentinel in results['text'], 'Missing expected text in ' + file.name + ': ' + sentinel
            if not expected:
                assert not results['text'].strip(), 'Blank PDF contains text: ' + file.name
            record['status'] = 'PASS'
        status, error = 'PASS', None
    except (AssertionError, OSError, ValueError, subprocess.TimeoutExpired) as failure:
        status, error = 'FAIL', str(failure)
    report = {'status': status, 'files': records, 'error': error}
    args.report.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({'status': status, 'filesChecked': len(records), 'error': error}))
    return 0 if status == 'PASS' else 1


if __name__ == '__main__':
    raise SystemExit(main())
