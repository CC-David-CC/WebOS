#!/usr/bin/env python3
"""Build the pinned browser LaTeX runtime for the WebOS WordCraft host."""
import argparse
import base64
import ctypes
from hashlib import file_digest
import json
from pathlib import Path
import tarfile

TEX = "1.4.1"
PDF = "4.10.38"
INPUTS = {
    "busytex-assets.tar.gz": (
        f"https://github.com/TeXlyre/texlyre-busytex/releases/download/assets-v{TEX}/busytex-assets.tar.gz",
        "sha256:4f63731fe4ec9238d877846074ab424350add6f6e956944def389e6752d2c78b",
    ),
    "wrapper.tgz": (
        f"https://registry.npmjs.org/texlyre-busytex/-/texlyre-busytex-{TEX}.tgz",
        "sha512:7PswiiuCIYc0HGK/HyQz0At/6Pc9pMk7Qy+DkzHk+BGVInWetXaeZq2px7V06pHscJG215YOU6as/0sgRmulNA==",
    ),
    "pdfjs.tgz": (
        f"https://registry.npmjs.org/pdfjs-dist/-/pdfjs-dist-{PDF}.tgz",
        "sha512:/Y3fcFrXEAsMjJXeL9J8+ZG9U01LbuWaYypvDW2ycW1jL269L3js3DVBjDJ0Up9Np1uqDXsDrRihHANhZOlwdQ==",
    ),
}
WRAPPER_SOURCE = "3f85c798a3ded8164bc538eaca5bc978b1d73aa0"
WASM_SOURCE = "46ebb6216a5c1fe63dd1dc885831d1a8cef2dc86"
ENGINE_FILES = ("busytex.js", "busytex.wasm", "busytex_worker.js", "busytex_biber.js", "busytex_pipeline.js", "versions.txt")
PACKAGE_MARK = 'loadPackage({"files": '
COMPRESSION_MARK = "var compressedData = "
BLOCK_SIZE = 2048
TDS = "/texlive/texmf-dist/"
ADDITIONAL_TDS = (
    "tex/latex/pgf/", "tex/generic/pgf/", "tex/latex/enumitem/",
    "tex/latex/xcolor/", "tex/latex/etoolbox/", "tex/latex/pgfplots/",
    "tex/generic/pgfplots/", "tex/latex/lm/",
    "fonts/tfm/public/lm/", "fonts/type1/public/lm/", "fonts/enc/dvips/lm/",
    "fonts/tfm/public/cm-super/", "fonts/type1/public/cm-super/", "fonts/enc/dvips/cm-super/",
)
UNUSED_PDFTEX = (
    "fonts/afm/", "fonts/opentype/", "fonts/truetype/", "fonts/source/",
    "tex/luatex/", "tex/lualatex/", "tex/latex-dev/", "tex/optex/", "tex/xelatex/",
    "texmf-var/web2c/xetex/", "texmf-var/web2c/luahbtex/", "texmf-var/web2c/luatex/",
)


def verify_inputs(directory):
    for name, (_, integrity) in INPUTS.items():
        algorithm, expected = integrity.split(":")
        with (directory / name).open("rb") as stream:
            digest = file_digest(stream, algorithm)
        actual = digest.hexdigest() if algorithm == "sha256" else base64.b64encode(digest.digest()).decode()
        if actual != expected:
            raise ValueError(f"Hash mismatch for {name}")


def write(root, name, data):
    target = root / name
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(data)


def unpack(archive, name):
    with archive.extractfile(name) as stream:
        return stream.read()


def index(script):
    start = script.index(PACKAGE_MARK) + len("loadPackage(")
    metadata, used = json.JSONDecoder().raw_decode(script[start:])
    return start, start + used, metadata


def choose(name, basic_names):
    if name == "/texlive/icudt78l.dat":
        return False
    if not name.startswith(TDS):
        return name in basic_names
    relative = name.removeprefix(TDS)
    if relative.startswith(UNUSED_PDFTEX):
        return False
    return name in basic_names or relative.startswith(ADDITIONAL_TDS)


class EmscriptenPackage:
    """Read and write the release's fixed-size raw LZ4 blocks."""

    def __init__(self, script, data):
        start = script.index(COMPRESSION_MARK) + len(COMPRESSION_MARK)
        config, consumed = json.JSONDecoder().raw_decode(script[start:])
        self.start = start
        self.end = start + consumed
        self.config = config
        self.lz4 = ctypes.CDLL("liblz4.so.1")
        for function in (self.lz4.LZ4_decompress_safe, self.lz4.LZ4_compress_default):
            function.argtypes = (ctypes.c_char_p, ctypes.c_void_p, ctypes.c_int, ctypes.c_int)
            function.restype = ctypes.c_int
        buffer = ctypes.create_string_buffer(BLOCK_SIZE)
        pieces = []
        for offset, size, compressed in zip(config["offsets"], config["sizes"], config["successes"], strict=True):
            block = data[offset:offset + size]
            if compressed:
                length = self.lz4.LZ4_decompress_safe(block, buffer, size, BLOCK_SIZE)
                if length < 0:
                    raise ValueError("Invalid TeX Live data block")
                block = buffer.raw[:length]
            if len(block) != BLOCK_SIZE and offset + size != config["cachedOffset"]:
                raise ValueError("Unexpected TeX Live block size")
            pieces.append(block)
        self.raw = b"".join(pieces)

    def encode(self, payload, stream):
        offsets, sizes, successes = [], [], []
        buffer = ctypes.create_string_buffer(BLOCK_SIZE + 32)
        for start in range(0, len(payload), BLOCK_SIZE):
            block = payload[start:start + BLOCK_SIZE].ljust(BLOCK_SIZE, b"\0")
            size = self.lz4.LZ4_compress_default(block, buffer, BLOCK_SIZE, len(buffer))
            compressed = 0 < size < BLOCK_SIZE
            data = buffer.raw[:size] if compressed else block
            offsets.append(stream.tell())
            sizes.append(len(data))
            successes.append(int(compressed))
            stream.write(data)
        cached_offset = stream.tell()
        stream.write(bytes(BLOCK_SIZE * len(self.config["cachedIndexes"])))
        self.config.update(offsets=offsets, sizes=sizes, successes=successes, cachedOffset=cached_offset)
        return stream.tell()


def pack_tex(inputs, output):
    with tarfile.open(inputs / "busytex-assets.tar.gz") as source:
        for name in ENGINE_FILES:
            write(output, f"busytex/{name}", unpack(source, f"busytex/{name}"))
        basic = unpack(source, "busytex/texlive-basic.js").decode()
        basic_names = {row["filename"] for row in index(basic)[2]["files"]}
        full = unpack(source, "busytex/texlive-extra.js").decode()
        _, _, metadata = index(full)
        selection = [row for row in metadata["files"] if choose(row["filename"], basic_names)]
        for required in ("pdflatex.fmt", "tikz.sty", "enumitem.sty", "graphicx.sty", "amsmath.sty"):
            if not any(row["filename"].endswith("/" + required) for row in selection):
                raise ValueError(f"Missing selected TeX Live asset {required}")
        folder = output / "busytex"
        package = EmscriptenPackage(full, unpack(source, "busytex/texlive-extra.data"))
        # Preserve byte sharing when two files have the same original range.
        payload = bytearray()
        offsets = {}
        for row in selection:
            low, high = row["start"], row["end"]
            key = (low, high)
            if key not in offsets:
                offsets[key] = len(payload)
                payload.extend(package.raw[low:high])
            row["start"] = offsets[key]
            row["end"] = row["start"] + high - low
        del package.raw
        with (folder / "texlive-preview.data").open("wb") as stream:
            size = package.encode(bytes(payload), stream)
        metadata["files"] = selection
        metadata["remote_package_size"] = size
        with (folder / "texlive-preview.data").open("rb") as stream:
            metadata["package_uuid"] = file_digest(stream, "sha256").hexdigest()
        loader = full[:package.start] + json.dumps(package.config, separators=(",", ":")) + full[package.end:]
        start, end, _ = index(loader)
        loader = loader[:start] + json.dumps(metadata, separators=(",", ":")) + loader[end:]
        loader = loader.replace("texlive-extra.data", "texlive-preview.data")
        write(output, "busytex/texlive-preview.js", loader.encode())
        write(output, "busytex/texlive-preview-files.txt",
              ("\n".join(row["filename"] for row in selection) + "\n").encode())

    with tarfile.open(inputs / "wrapper.tgz") as source:
        for member in source.getmembers():
            if member.isfile() and member.name.startswith("package/dist/") and member.name.endswith(".js"):
                write(output, "runner/" + member.name.removeprefix("package/dist/"), unpack(source, member.name))
        write(output, "licenses/BusyTeX.txt", unpack(source, "package/LICENSE"))


def pack_pdf(inputs, output):
    with tarfile.open(inputs / "pdfjs.tgz") as source:
        for name in ("pdf.mjs", "pdf.worker.mjs"):
            write(output, f"pdf/{name}", unpack(source, f"package/legacy/build/{name}"))
        for member in source.getmembers():
            if member.isfile() and member.name.startswith(("package/standard_fonts/", "package/cmaps/")):
                write(output, "pdf/" + member.name.removeprefix("package/"), unpack(source, member.name))
        write(output, "licenses/PDF.js.txt", unpack(source, "package/LICENSE"))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("inputs", type=Path)
    parser.add_argument("output", type=Path)
    options = parser.parse_args()
    verify_inputs(options.inputs)
    options.output.mkdir(exist_ok=False)
    pack_tex(options.inputs, options.output)
    pack_pdf(options.inputs, options.output)
    items = []
    for path in sorted(options.output.rglob("*")):
        if path.is_file():
            with path.open("rb") as stream:
                digest = file_digest(stream, "sha256").hexdigest()
            items.append({"path":path.relative_to(options.output).as_posix(), "bytes":path.stat().st_size, "sha256":digest})
    metadata = {
        "schema":"webos-wordcraft-latex-runtime/1",
        "versions":{"texlyreBusytex":TEX, "pdfjs":PDF, "texlive":"2026", "wrapperSource":WRAPPER_SOURCE, "wasmSource":WASM_SOURCE},
        "inputs": {name: {"url":url, "integrity":integrity} for name, (url, integrity) in INPUTS.items()},
        "files":items,
    }
    (options.output / "runtime-build.json").write_text(json.dumps(metadata, indent=2) + "\n")
    print(f"{len(items)} runtime files with {sum(item['bytes'] for item in items)} bytes")


if __name__ == "__main__":
    main()
