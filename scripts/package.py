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
from oneDayOneThing import __version__


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--url",
        help="Published URL of this exact archive; default: https://github.com/vinono/1D1T/releases/download/v<version>/1d1t-<version>.tar.gz",
    )
    parser.add_argument(
        "--local",
        action="store_true",
        help="Use local file URI instead of GitHub release URL",
    )
    args = parser.parse_args()

    default_release_url = f"https://github.com/vinono/1D1T/releases/download/v{__version__}/1d1t-{__version__}.tar.gz"
    if args.local:
        published_url = None
    elif args.url:
        published_url = args.url
    else:
        published_url = default_release_url

    output = ROOT / "dist"
    output.mkdir(exist_ok=True)
    archive = output / f"1d1t-{__version__}.tar.gz"
    files = [ROOT / "bin/1d1t", ROOT / "README.md", ROOT / "docs/storage.md"]
    files += sorted((ROOT / "oneDayOneThing").glob("*.py"))
    files += sorted(path for path in (ROOT / "oneDayOneThing/assets").rglob("*") if path.is_file())
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
    formula_template = (ROOT / "packaging/one-day-one-thing.rb.in").read_text()
    formula_content = formula_template
    replacements = {
        "URL": published_url or archive.as_uri(),
        "VERSION": __version__,
        "SHA256": checksum,
    }
    for key, value in replacements.items():
        formula_content = formula_content.replace(f"@{key}@", json.dumps(value))

    # 1. Package Homebrew Tap directly into the repository root
    root_formula_dir = ROOT / "Formula"
    root_formula_dir.mkdir(exist_ok=True)
    (root_formula_dir / "one-day-one-thing.rb").write_text(formula_content)

    root_aliases_dir = ROOT / "Aliases"
    root_aliases_dir.mkdir(exist_ok=True)
    root_alias = root_aliases_dir / "1d1t"
    if root_alias.is_symlink() or root_alias.exists():
        root_alias.unlink()
    root_alias.symlink_to("../Formula/one-day-one-thing.rb")

    # 2. Also output to dist/homebrew-tap/ for separate tap repo sync if needed
    dist_tap = output / "homebrew-tap"
    dist_formula_dir = dist_tap / "Formula"
    dist_formula_dir.mkdir(parents=True, exist_ok=True)
    (dist_formula_dir / "one-day-one-thing.rb").write_text(formula_content)

    dist_aliases_dir = dist_tap / "Aliases"
    dist_aliases_dir.mkdir(exist_ok=True)
    dist_alias = dist_aliases_dir / "1d1t"
    if dist_alias.is_symlink() or dist_alias.exists():
        dist_alias.unlink()
    dist_alias.symlink_to("../Formula/one-day-one-thing.rb")

    (dist_tap / "README.md").write_text(
        "# 1D1T Homebrew Tap\n\n"
        "```sh\nbrew tap vinono/tap\nbrew install 1d1t\n```\n\n"
        "One day. One thing.\nTake a day. Feel the love in everything. [Usage and source](https://github.com/vinono/1D1T).\n\n"
        "If Homebrew reports `untrusted tap`, trust this formula and retry:\n\n"
        "```sh\nbrew trust --formula vinono/tap/one-day-one-thing\nbrew install 1d1t\n```\n"
    )

    print("=" * 60)
    print(f"📦 1D1T v{__version__} packaged successfully!")
    print(f"Archive:      {archive}")
    print(f"SHA256:       {checksum}")
    print(f"URL:          {replacements['URL']}")
    print(f"Root Tap:     {root_formula_dir / 'one-day-one-thing.rb'}")
    print(f"              {root_alias}")
    print(f"Dist Tap:     {dist_formula_dir / 'one-day-one-thing.rb'}")
    print("=" * 60)
    print("Installation via repository Tap:")
    print("  brew tap vinono/tap")
    print("  brew install 1d1t")
    print("Or one-liner:")
    print("  brew install vinono/tap/1d1t")
    print("=" * 60)


if __name__ == "__main__":
    main()
