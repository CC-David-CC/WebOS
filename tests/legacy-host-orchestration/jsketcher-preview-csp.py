#!/usr/bin/env python3
"""Run only an isolated local preview with the live CSP for app testing.

This in-memory test adapter leaves the standard preview source unmodified.
It deliberately refuses non-isolated state. The header is a captured policy,
not a production configuration or a deployment tool.
"""
import sys
from pathlib import Path

if '--isolated' not in sys.argv[1:]:
    raise SystemExit('The CSP test adapter requires --isolated.')
source_path=Path(__file__).resolve().parent.parent/'active-system/scripts/run-simplified-local.py'
source=source_path.read_text()
needle="            response_headers={k:v for k,v in upstream.headers.items() if k.lower() not in hop}\n"
if source.count(needle)!=1:
    raise SystemExit('The preview response hook changed; review the test adapter.')
csp="default-src 'self'; script-src 'self' 'wasm-unsafe-eval'; style-src 'self' 'unsafe-inline'; img-src 'self' data: blob:; media-src 'self' blob:; connect-src 'self' wss://ksu.codes; font-src 'self' data:; frame-src 'self' blob:; worker-src 'self' blob:; object-src 'none'; base-uri 'none'; form-action 'self'; frame-ancestors 'self'"
source=source.replace(needle,needle+f"            if 'Content-Security-Policy' in response_headers: response_headers['Content-Security-Policy'] = {csp!r}\n")
sys.argv[0]=str(source_path)
exec(compile(source,str(source_path),'exec'),{'__name__':'__main__','__file__':str(source_path)})
