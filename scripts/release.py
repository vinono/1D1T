#!/usr/bin/env python3
"""One-command release tool for 1D1T.

Automates:
1. Running all tests before release.
2. Bumping version across code and docs.
3. Packaging source tarball and computing deterministic SHA256.
4. Updating in-repo Formula/Aliases in 1D1T.
5. Syncing and committing the new Formula in the Homebrew Tap repo (vinono/homebrew-tap).
6. Creating git commit and tag in 1D1T (with optional push).

The GitHub Release asset must be uploaded and verified before pushing the Tap.
"""
import argparse
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from oneDayOneThing import __version__ as CURRENT_VERSION


def run(cmd, cwd=ROOT, check=True):
    """Run a shell command and return stdout."""
    res = subprocess.run(cmd, cwd=cwd, shell=True, text=True, capture_output=True)
    if check and res.returncode != 0:
        print(f"\n❌ Command failed in {cwd}:\n  {cmd}")
        if res.stdout:
            print(f"Stdout:\n{res.stdout}")
        if res.stderr:
            print(f"Stderr:\n{res.stderr}")
        sys.exit(res.returncode)
    return res


def bump_semver(ver: str, part: str) -> str:
    m = re.match(r"^(\d+)\.(\d+)\.(\d+)(.*)$", ver)
    if not m:
        raise ValueError(f"Invalid semver version: {ver}")
    major, minor, patch, extra = int(m.group(1)), int(m.group(2)), int(m.group(3)), m.group(4)
    if part == "major":
        return f"{major + 1}.0.0"
    elif part == "minor":
        return f"{major}.{minor + 1}.0"
    elif part == "patch":
        return f"{major}.{minor}.{patch + 1}"
    return ver


def update_repo_files(new_version: str):
    """Update version in Python package, README, and docs."""
    init_py = ROOT / "oneDayOneThing/__init__.py"
    content = init_py.read_text()
    new_content = re.sub(r'__version__\s*=\s*["\'][^"\']+["\']', f'__version__ = "{new_version}"', content)
    init_py.write_text(new_content)

    # Update README releases link if applicable
    readme = ROOT / "README.md"
    if readme.exists():
        text = readme.read_text()
        text = re.sub(r'releases/tag/v\d+\.\d+\.\d+', f'releases/tag/v{new_version}', text)
        text = re.sub(r'v\d+\.\d+\.\d+ 发布说明', f'v{new_version} 发布说明', text)
        readme.write_text(text)

    # Create release note stub if missing
    rel_note = ROOT / f"docs/releases/v{new_version}.md"
    if not rel_note.exists():
        rel_note.parent.mkdir(parents=True, exist_ok=True)
        rel_note.write_text(
            f"# 1D1T v{new_version}\n\n"
            f"发布日期：{subprocess.getoutput('date +%Y-%m-%d')}\n\n"
            f"## 更新内容\n\n"
            f"- 发布 v{new_version} 版本。\n"
        )


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("version", nargs="?", help="Target version (e.g. 0.1.2), or 'patch', 'minor', 'major'")
    parser.add_argument("--tap-dir", help="Path to local vinono/homebrew-tap repo clone (default: ../homebrew-tap)")
    parser.add_argument("--push", action="store_true", help="Push commits and tags to remote origin")
    parser.add_argument("--skip-tests", action="store_true", help="Skip running the test suite")
    parser.add_argument("--dry-run", action="store_true", help="Validate and print planned actions without changing files or repositories")
    args = parser.parse_args()

    # 1. Determine target version
    target_version = CURRENT_VERSION
    if args.version:
        if args.version in ("patch", "minor", "major"):
            target_version = bump_semver(CURRENT_VERSION, args.version)
        else:
            target_version = args.version.lstrip("v")
    if not re.fullmatch(r"\d+\.\d+\.\d+", target_version):
        parser.error("version must be major.minor.patch")

    print(f"\n🚀 Preparing release: v{target_version} (Current: v{CURRENT_VERSION})")

    # 2. Run test suite
    if not args.skip_tests:
        print("\n🧪 Running test suite...")
        res = run("python3 -m unittest discover tests")
        print("   ✅ All tests passed!")
    else:
        print("\n⚠️ Skipping tests as requested.")

    tap_dir = Path(args.tap_dir).resolve() if args.tap_dir else ROOT.parent / "homebrew-tap"
    if args.dry_run:
        print(f"\n[dry-run] Would update version files and package v{target_version}.")
        print(f"[dry-run] Would sync Formula and alias to {tap_dir}.")
        print(f"[dry-run] Would commit and tag v{target_version}; push: {args.push}.")
        return

    if run("git diff --cached --name-only").stdout.strip():
        sys.exit("Refusing to release with pre-existing staged changes.")

    # 3. Update version in files
    print("\n📝 Updating version in files...")
    update_repo_files(target_version)
    print(f"   Updated oneDayOneThing/__init__.py -> {target_version}")

    # 4. Run packaging to produce tarball and Formula
    print("\n📦 Packaging source and generating Formula...")
    package_res = run(f"python3 scripts/package.py")
    print(package_res.stdout.strip())

    # 5. Sync to Homebrew Tap repository
    print(f"\n🍺 Syncing to Homebrew Tap repository at: {tap_dir}")

    if not tap_dir.exists():
        print(f"   Tap directory does not exist locally. Attempting to clone from GitHub...")
        clone_cmd = f"git clone https://github.com/vinono/homebrew-tap.git {tap_dir}"
        res = run(clone_cmd, check=False)
        if res.returncode != 0:
            print(f"   ⚠️ Could not clone vinono/homebrew-tap automatically.")
            print(f"   You can manually clone it to: {tap_dir}")
            print(f"   Formula files are ready in: dist/homebrew-tap/")
            tap_dir = None
        else:
            print(f"   ✅ Cloned vinono/homebrew-tap to {tap_dir}")

    if tap_dir and tap_dir.exists():
        # Copy Formula and Aliases
        tap_formula = tap_dir / "Formula"
        tap_formula.mkdir(parents=True, exist_ok=True)
        (tap_formula / "one-day-one-thing.rb").write_text((ROOT / "Formula/one-day-one-thing.rb").read_text())

        tap_aliases = tap_dir / "Aliases"
        tap_aliases.mkdir(exist_ok=True)
        alias_link = tap_aliases / "1d1t"
        if alias_link.is_symlink() or alias_link.exists():
            alias_link.unlink()
        alias_link.symlink_to("../Formula/one-day-one-thing.rb")

        # Check only the Formula and alias managed by this release.
        diff = run("git status --porcelain -- Formula/one-day-one-thing.rb Aliases/1d1t", cwd=tap_dir).stdout.strip()
        if diff:
            if not args.dry_run:
                run("git add Formula/ Aliases/", cwd=tap_dir)
                run(f'git commit -m "Bump 1d1t to v{target_version}"', cwd=tap_dir)
                print(f"   ✅ Committed update in tap repo (v{target_version})")
                print(f"   After uploading and verifying the GitHub Release asset, run 'git -C {tap_dir} push origin main'")
            else:
                print(f"   [dry-run] Would commit Formula update to {tap_dir}")
        else:
            print("   ℹ️ Tap repo is already up to date.")

    # 6. Commit & tag in 1D1T repository
    tag_name = f"v{target_version}"
    print(f"\n🔖 Git status for 1D1T repository:")
    if not args.dry_run:
        run("git add README.md assets/ docs/ oneDayOneThing/ packaging/ scripts/ site/ tests/ Formula/ Aliases/")
        # Commit only staged release paths, not unrelated working-tree changes.
        staged = run("git diff --cached --name-only").stdout.strip()
        if staged:
            run(f'git commit -m "Release v{target_version}"')
            print(f"   ✅ Created commit: Release v{target_version}")
        else:
            print("   ℹ️ No uncommitted changes in 1D1T.")

        # Tag
        tags = run("git tag").stdout.splitlines()
        if tag_name not in tags:
            run(f'git tag -a {tag_name} -m "Release {tag_name}"')
            print(f"   ✅ Created tag: {tag_name}")
        else:
            print(f"   ℹ️ Tag {tag_name} already exists.")

        if args.push:
            print("   Pushing 1D1T commits and tags to origin...")
            run(f"git push origin main {tag_name}")
            print("   ✅ Pushed 1D1T commits and tags!")
        else:
            print(f"\n👉 Next steps to publish:")
            print(f"   1. git push origin main {tag_name}")
            print(f"   2. Create GitHub Release and upload dist/1d1t-{target_version}.tar.gz:")
            print(f"      https://github.com/vinono/1D1T/releases/new?tag={tag_name}")
            print(f"      (or: gh release create {tag_name} dist/1d1t-{target_version}.tar.gz --title '{tag_name}')")
            if tap_dir and tap_dir.exists():
                print(f"   3. Verify the Release asset, then git -C {tap_dir} push origin main")
    else:
        print(f"   [dry-run] Would commit, tag {tag_name}, and push if --push was provided.")

    print("\n🎉 Done!")


if __name__ == "__main__":
    main()
