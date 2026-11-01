#!/usr/bin/env python3
"""Install the isolated Memory Garden browser harness in a built app directory."""
import os
import shutil
from pathlib import Path

root = Path(os.environ.get("CODI_MEMORY_BUILD", ".build/memory-garden-test"))
source = Path(__file__).with_name("memory-garden-fixture.html")
if not (root / "apps.json").is_file():
    raise SystemExit("Build the memory-garden app before preparing its harness.")
shutil.copyfile(source, root / "index.html")
