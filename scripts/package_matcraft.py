"""Collect an exact MatCraft Studio Trunk build for WebOS's app registry."""
from hashlib import file_digest
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys

source, trunk, output = map(Path, sys.argv[1:])
inputs = {
    "craft-libs": "c4599af4b074cbd48f93723612513ab4067f1a5b",
    "simcraft": "ed8c09a7a16f77ca6e59f1079aec083c72d32564",
}

def git(root, *args):
    return subprocess.check_output(["git", "-C", root, *args], text=True).strip()

def digest(path):
    with path.open("rb") as stream:
        return file_digest(stream, "sha256").hexdigest()

sources = {}
for name, pin in {"matcraft": git(source, "rev-parse", "HEAD"), **inputs}.items():
    checkout = source if name == "matcraft" else source.parent / name
    assert git(checkout, "rev-parse", "HEAD") == pin, name
    assert not git(checkout, "status", "--porcelain"), name
    sources[name] = pin

launch = (trunk / "index.html").read_text()
wasms = list(trunk.glob("matcraft-web-*_bg.wasm"))
assert len(wasms) == 1
wasm = wasms[0]
assert re.fullmatch(r"matcraft-web-[0-9a-f]+_bg\.wasm", wasm.name)
js = wasm.with_name(wasm.name.removesuffix("_bg.wasm") + ".js")
assert wasm.name in launch and js.name in launch
with wasm.open("rb") as stream:
    assert stream.read(8) == b"\x00asm\x01\x00\x00\x00"
for export in ("replace_script", "run_script", "script_saved", "script_snapshot", "take_file_request", "workspace_ready"):
    assert "export function " + export + "(" in js.read_text(), export

output.mkdir(exist_ok=False)
files = {"native/engine.js": js, "native/engine_bg.wasm": wasm}
for name in sources:
    checkout = source if name == "matcraft" else source.parent / name
    for license_name in ("LICENSE-MIT", "LICENSE-APACHE"):
        files[f"legal/{name}-{license_name}"] = checkout / license_name
files["legal/matcraft-NOTICE"] = source / "NOTICE"
records = []
for relative, original in sorted(files.items()):
    target = output / relative
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(original, target)
    records.append({"path": relative, "bytes": target.stat().st_size, "sha256": digest(target)})
receipt = {
    "schema": "webos-component-build/1",
    "component": "matcraft",
    "sourceCommit": sources["matcraft"],
    "sourceTree": git(source, "rev-parse", "HEAD^{tree}"),
    "sources": sources,
    "cargoLockSHA256": digest(source / "Cargo.lock"),
    "wasmBindgen": "0.2.129",
    "files": records,
}
(output / "component-build.json").write_text(json.dumps(receipt, indent=2) + "\n")
print(json.dumps(receipt))
