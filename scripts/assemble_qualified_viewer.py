"""Assemble one verified browser app over the preceding WebOS viewer."""
import argparse
import base64
import gzip
from hashlib import file_digest, sha256
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tarfile


def git(checkout, *args):
    return subprocess.check_output(("git", "-C", checkout, *args))


def load(path):
    return json.loads(path.read_bytes())


def encode(value):
    return json.dumps(value, ensure_ascii=False, separators=(",", ":")).encode() + b"\n"


def record(path):
    with path.open("rb") as stream:
        return {"bytes": path.stat().st_size, "sha256": file_digest(stream, "sha256").hexdigest()}


def inventory(document):
    entries = {row["path"]: {key: row[key] for key in ("bytes", "sha256")} for row in document["files"]}
    assert len(entries) == len(document["files"])
    return entries


def write(path, data):
    # The candidate shares unchanged inodes with its baseline.
    pending = path.with_name(path.name + ".new")
    with pending.open("xb") as stream:
        stream.write(data)
    pending.replace(path)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("parent", "desktop", "base", "qualified", "output", "archive"):
        parser.add_argument(name, type=Path)
    for name in ("previous", "app", "mount", "mount_sha", "wasm_sha"):
        parser.add_argument(name)
    parser.add_argument("--source-mount-sha")
    parser.add_argument("--runtime", type=Path)
    args = parser.parse_args()
    assert re.fullmatch(r"[a-z0-9-]+", args.app)
    assert not args.output.exists() and not args.archive.exists()
    app = args.app
    src = "apps/" + app
    desktop_path = "active-system/app.js"
    base_manifest = args.base / "viewer-release.json"
    previous = base_manifest.read_bytes()
    assert sha256(previous).hexdigest() == args.previous
    before = json.loads(previous)
    assert before["schema"] == "webos-existing-viewer-release/1"
    assert app not in before["apps"]
    previous_component = before["components"].get(src)
    if previous_component is not None:
        assert git(args.parent, "rev-parse", before["parentCommit"] + ":" + src).decode().strip() == previous_component
    git(args.parent, "merge-base", "--is-ancestor", before["parentCommit"], "HEAD")
    assert git(args.desktop, "rev-parse", "HEAD^").decode().strip() == before["components"]["platform/desktop"]
    assert git(args.desktop, "show", "HEAD^:" + desktop_path) == (args.base / "app.js").read_bytes()
    parent_sha = git(args.parent, "rev-parse", "HEAD").decode().strip()
    desktop_sha = git(args.desktop, "rev-parse", "HEAD").decode().strip()
    assert git(args.parent, "rev-parse", "HEAD:platform/desktop").decode().strip() == desktop_sha
    app_sha = git(args.parent, "rev-parse", "HEAD:" + src).decode().strip()
    changes = set(git(args.parent, "diff", "--name-only", before["parentCommit"], "HEAD").decode().splitlines())
    assert {"platform/desktop", src} <= changes
    allowed_changes = {"platform/desktop", src, ".gitmodules", "scripts/assemble_qualified_viewer.py"}
    runtime_component = "platform/runtime"
    loader_path = "assets/desktop/apps.mjs"
    loader_source = "active-system/" + loader_path
    runtime_pin = {}
    if args.runtime:
        assert app == "mailcraft"
        allowed_changes.add(runtime_component)
        before_runtime = before["components"][runtime_component]
        assert git(args.runtime, "rev-parse", "HEAD^").decode().strip() == before_runtime
        assert git(args.runtime, "diff", "--name-only", "HEAD^", "HEAD").decode().splitlines() == [loader_source]
        assert git(args.runtime, "show", "HEAD^:" + loader_source) == (args.base / loader_path).read_bytes()
        runtime_sha = git(args.runtime, "rev-parse", "HEAD").decode().strip()
        assert git(args.parent, "rev-parse", "HEAD:" + runtime_component).decode().strip() == runtime_sha
        runtime_pin[runtime_component] = runtime_sha
    assert changes <= allowed_changes

    registry_path = "assets/desktop/apps.json"
    registry = load(args.base / registry_path)
    assert not any(row["id"] == app for row in registry["apps"])
    fixture = load(args.qualified / registry_path)
    entry, = [row for row in fixture["apps"] if row["id"] == app]
    assert entry["kind"] == "browser"
    assert re.fullmatch(r"[0-9a-f]{64}", entry["bundleSHA256"])
    prefix = f"assets/desktop/apps/{app}/{entry['bundleSHA256']}/"
    assert entry["path"] == prefix + "index.mjs"
    files = entry["files"]
    assert len(files) <= 4096 and entry["sha256"] == files["index.mjs"]["sha256"] == args.mount_sha
    wasm_header = b"\x00asm\x01\x00\x00\x00"
    if app == "circuit-lab":
        worker = "workers/spice.mjs"
        assert worker in files
        modules = re.findall(rb"data:application/wasm;base64,([A-Za-z0-9+/]+={0,2})",
                             (args.qualified / prefix / worker).read_bytes())
        assert modules
        for item in modules:
            wasm = base64.b64decode(item, validate=True)
            assert wasm.startswith(wasm_header) and sha256(wasm).hexdigest() == args.wasm_sha
    else:
        engine, = [name for name, item in files.items() if name.endswith((".wasm", ".wasm.gz"))
                   and item["sha256"] == args.wasm_sha]
        engine_path = args.qualified / prefix / engine
        open_engine = gzip.open if engine.endswith(".gz") else open
        with open_engine(engine_path, "rb") as stream:
            assert stream.read(8) == wasm_header
    for name, expected in files.items():
        assert all(re.fullmatch(r"[A-Za-z0-9_@+-][A-Za-z0-9_@+.-]*", part) for part in name.split("/"))
        candidate = args.qualified / prefix / name
        assert candidate.is_file() and not candidate.is_symlink()
        assert record(candidate) == expected, name
    registry["apps"].append(entry)

    profile = load(args.base / "viewer-profile.json")
    build = load(args.base / "viewer-build.json")
    assert profile["apps"] == build["apps"] == before["apps"]
    assert build["browserStudioSources"] == before["browserStudioSources"]
    profile["apps"].append(app)
    build["apps"].append(app)
    build["browserStudioSources"][app] = app_sha
    launcher = git(args.desktop, "show", "HEAD:" + desktop_path)
    source_input, = [row for row in build["sourceInputs"] if row["path"] == "platform/desktop/" + desktop_path]
    assert source_input["sha256"] == sha256((args.base / "app.js").read_bytes()).hexdigest()
    source_input["sha256"] = sha256(launcher).hexdigest()
    bridge = "active-system/webos-app-bridges/" + app + "/"
    if args.mount == "platform/desktop/" + bridge + "mount.mjs":
        bundled = {
            "mount.mjs": "index.mjs",
            "startup.mjs": "native/startup.mjs",
            "index.html": "native/index.html",
            "HOST-LICENSE": "legal/HOST-LICENSE",
        }
        if app != "mailcraft":
            bundled.update({"workspace.css": "workspace.css", "canvas.css": "native/canvas.css"})
        for filename, packaged in bundled.items():
            value = git(args.desktop, "show", "HEAD:" + bridge + filename)
            assert (args.qualified / prefix / packaged).read_bytes() == value
            build["sourceInputs"].append({
                "path": "platform/desktop/" + bridge + filename,
                "sha256": sha256(value).hexdigest(),
            })
    else:
        source_mount_sha = args.source_mount_sha or args.mount_sha
        assert re.fullmatch(r"[a-f0-9]{64}", source_mount_sha)
        build["sourceInputs"].append({"path": src + "/" + args.mount, "sha256": source_mount_sha})

    shutil.copytree(args.base, args.output, copy_function=os.link)
    shutil.copytree(args.qualified / prefix, args.output / prefix, copy_function=os.link)
    write(args.output / "app.js", launcher)
    if args.runtime:
        loader = git(args.runtime, "show", "HEAD:" + loader_source)
        runtime_input, = [entry for entry in build["sourceInputs"]
                          if entry["path"] == runtime_component + "/" + loader_source]
        assert runtime_input["sha256"] == record(args.base / loader_path)["sha256"]
        runtime_input["sha256"] = sha256(loader).hexdigest()
        write(args.output / loader_path, loader)
    write(args.output / registry_path, encode(registry))
    write(args.output / "viewer-profile.json", encode(profile))
    write(args.output / "viewer-build.json", encode(build))
    cache_path = "assets/desktop/cache-manifest.json"
    cache = load(args.base / cache_path)
    cache["id"] = sha256((args.previous + parent_sha).encode()).hexdigest()[:20]
    write(args.output / cache_path, encode(cache))

    records = inventory(before)
    changed = {"app.js", registry_path, "viewer-profile.json", "viewer-build.json", cache_path}
    if args.runtime:
        changed.add(loader_path)
    for name in changed:
        updated = record(args.output / name)
        assert updated != records[name], name
        records[name] = updated
    for name, metadata in files.items():
        full_name = prefix + name
        assert full_name not in records
        records[full_name] = metadata
        changed.add(full_name)
    release = before | {
        "parentCommit": parent_sha,
        "components": before["components"] | {".": parent_sha, "platform/desktop": desktop_sha, src: app_sha} | runtime_pin,
        "apps": profile["apps"],
        "browserStudioSources": build["browserStudioSources"],
        "files": [{"path": name, **metadata} for name, metadata in sorted(records.items())],
    }
    manifest = encode(release)
    write(args.output / "viewer-release.json", manifest)
    assert sha256(base_manifest.read_bytes()).hexdigest() == args.previous
    with tarfile.open(args.archive, "x") as archive:
        for name in sorted(changed | {"viewer-release.json"}):
            item = archive.gettarinfo(args.output / name, arcname=name)
            assert item.isfile()
            with (args.output / name).open("rb") as stream:
                archive.addfile(item, stream)
    archive_limit = (1024 if app == "honeydew" else 256) * 1024**2
    assert args.archive.stat().st_size < archive_limit
    print(json.dumps({
        "app": app, "appCommit": app_sha, "desktopCommit": desktop_sha, "parentCommit": parent_sha,
        "bundleSHA256": entry["bundleSHA256"], "previous": args.previous,
        "release": sha256(manifest).hexdigest(), "archiveSHA256": record(args.archive)["sha256"],
        "apps": len(release["apps"]), "changed": len(changed),
    }))


if __name__ == "__main__":
    main()
