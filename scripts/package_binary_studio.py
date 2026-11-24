"""Package the native browser build from a clean, pinned source checkout."""
from hashlib import file_digest
import json
from pathlib import Path
import shutil
import subprocess
import sys

component, checkout, artifact, build_log, output = sys.argv[1:]
checkout, artifact, build_log, output = map(Path, (checkout, artifact, build_log, output))
if component not in {"subcraft", "transit", "mathcraft2", "scriobh", "tracedraw", "hdl-workbench"}:
    raise ValueError(component)

def git(*args):
    return subprocess.check_output(["git", "-C", checkout, *args])

def digest(path):
    with path.open("rb") as file:
        return file_digest(file, "sha256").hexdigest()

pin = git("rev-parse", "HEAD").decode().strip()
if git("status", "--porcelain") or pin not in build_log.read_text().splitlines():
    raise ValueError("The build and clean source checkout must have the same pin")
page = (artifact / "index.html").read_text()
if "<script" not in page or not list(artifact.rglob("*.wasm")):
    raise ValueError("The site has no browser entry or WASM")
output.mkdir()
shutil.copytree(artifact, output / "native")
(output / "legal").mkdir()
for name in (["LICENSE"] if component in {"scriobh", "hdl-workbench"} else ["LICENSE-MIT", "LICENSE-APACHE"]):
    (output / "legal" / name).write_bytes(git("show", "HEAD:" + name))
package_locks = {"scriobh": "web/webos/package-lock.json", "hdl-workbench": "webos/package-lock.json"}
lock = ({"packageLockSHA256": digest(checkout / package_locks[component])}
        if component in package_locks else {"cargoLockSHA256": digest(checkout / "Cargo.lock")})
receipt = {
    "schema": "webos-component-build/1",
    "component": component,
    "sourceCommit": pin,
    "sourceTree": git("rev-parse", "HEAD^{tree}").decode().strip(),
    **lock,
    "files": [
        {"path": file.relative_to(output).as_posix(), "sha256": digest(file), "bytes": file.stat().st_size}
        for file in sorted(output.rglob("*")) if file.is_file()
    ],
}
(output / "component-build.json").write_text(json.dumps(receipt, indent=2) + "\n")
