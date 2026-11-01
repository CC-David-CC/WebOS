#!/usr/bin/env python3
"""Isolated test preview that can force the real gateway request-window limit."""
import os
import runpy
import sys
import time
from pathlib import Path

root = Path(__file__).resolve().parents[1]
if '--isolated' not in sys.argv or '--port' not in sys.argv:
    raise SystemExit('Requires a dedicated --isolated --port preview')
flag = Path(os.environ['CODI_TEST_GATEWAY_CAPACITY_FLAG']).resolve()
if not flag.is_relative_to((root / 'active-system/.build').resolve()):
    raise SystemExit('Capacity flag must be in the isolated build directory')
sys.path.insert(0, str(root / 'active-system'))
from gateway_service.http import FileGateway
original = FileGateway._headers
def controlled(self, request):
    if flag.exists():
        self.window = int(time.monotonic()) // 60
        self.requests = self.max_requests_per_minute
        self._test_limited = True
    elif getattr(self, '_test_limited', False):
        self.requests = 0
        self._test_limited = False
    return original(self, request)
FileGateway._headers = controlled
runpy.run_path(str(root / 'active-system/scripts/run-simplified-local.py'), run_name='__main__')
