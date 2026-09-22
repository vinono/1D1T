#!/usr/bin/env python3
"""Install a reversible command link without editing shell startup files."""

import argparse
import os
from pathlib import Path
import sys


def main():
    parser = argparse.ArgumentParser(description="安装 1d1t 命令入口")
    parser.add_argument("--bin-dir", type=Path, default=Path.home() / ".local" / "bin")
    args = parser.parse_args()
    target = Path(__file__).resolve().parents[1] / "bin" / "1d1t"
    directory = args.bin_dir.expanduser().resolve()
    link = directory / "1d1t"
    if link.is_symlink() and link.resolve() == target:
        print(f"已安装：{link}")
        return 0
    if link.exists() or link.is_symlink():
        print(f"安装取消：{link} 已存在，未覆盖。", file=sys.stderr)
        return 1
    directory.mkdir(parents=True, exist_ok=True)
    link.symlink_to(target)
    print(f"已安装：{link} → {target}")
    if str(directory) not in os.environ.get("PATH", "").split(os.pathsep):
        print(f"请将 {directory} 加入 PATH，或直接运行 {link}。")
    else:
        print("现在可以在任意目录运行：1d1t --help")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except OSError as error:
        print(f"安装失败：{error}", file=sys.stderr)
        raise SystemExit(1)
