#!/usr/bin/env python3
"""Build an allowlisted source archive and a local Homebrew tap."""
import argparse
import gzip
import hashlib
import io
import json
from pathlib import Path
import tarfile
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from oned1t import __version__


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", help="Published URL of this exact archive; default: local file URL")
    args = parser.parse_args()
    output = ROOT / "dist"
    output.mkdir(exist_ok=True)
    archive = output / f"1d1t-{__version__}.tar.gz"
    files = [ROOT / "bin/1d1t", ROOT / "README.md", ROOT / "docs/storage.md"]
    files += sorted((ROOT / "oned1t").glob("*.py"))
    buffer = io.BytesIO()
    with tarfile.open(fileobj=buffer, mode="w") as tar:
        for path in files:
            info = tar.gettarinfo(str(path), arcname=f"1d1t-{__version__}/{path.relative_to(ROOT)}")
            info.mtime = 0
            info.uid = info.gid = 0
            info.uname = info.gname = ""
            info.mode = 0o755 if path.name == "1d1t" else 0o644
            with path.open("rb") as source:
                tar.addfile(info, source)
    with archive.open("wb") as target:
        with gzip.GzipFile(filename="", fileobj=target, mode="wb", mtime=0) as zipped:
            zipped.write(buffer.getvalue())
    checksum = hashlib.sha256(archive.read_bytes()).hexdigest()
    formula = (ROOT / "packaging/one-day-one-thing.rb.in").read_text()
    for key, value in {"URL": args.url or archive.as_uri(), "VERSION": __version__, "SHA256": checksum}.items():
        formula = formula.replace(f"@{key}@", json.dumps(value))
    directory = output / "homebrew-tap/Formula"
    directory.mkdir(parents=True, exist_ok=True)
    (directory / "one-day-one-thing.rb").write_text(formula)
    print(f"Archive: {archive}\nSHA256: {checksum}\nFormula: {directory / 'one-day-one-thing.rb'}")


if __name__ == "__main__":
    main()
