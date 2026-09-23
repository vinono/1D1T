"""Public command-line entry point."""

import argparse
from datetime import date, timedelta
import os
from pathlib import Path
import sqlite3
import sys
import unicodedata

from . import __version__
from .calendar import calendar_range, show_calendar
from .store import Store, UserError
from .terminal import BOLD, GREEN, MUTED, TAGLINE, header, hint, paint, welcome


def clean_text(value):
    value = value.strip()
    if not value:
        raise UserError("内容不能为空。")
    if any(unicodedata.category(char) in ("Cc", "Cs") for char in value):
        raise UserError("请使用单行文字，不要包含换行或终端控制字符。")
    if len(value) > 2000:
        raise UserError("内容请保持在 2000 个字符以内。")
    return value


def parser():
    app = argparse.ArgumentParser(prog="1d1t", description=TAGLINE)
    app.add_argument("--version", action="version", version=f"1d1t {__version__}")
    app.add_argument("--data-dir", type=Path, help="指定数据目录（默认使用用户目录）")
    commands = app.add_subparsers(dest="command", title="命令")
    add = commands.add_parser("add", help="设置今日唯一重点")
    add.add_argument("title", help="重点内容，请用引号包围")
    commands.add_parser("welcome", help="显示 Logo 和使用指引")
    commands.add_parser("today", help="查看今日重点")
    edit = commands.add_parser("edit", help="修改今日未完成重点")
    edit.add_argument("title", help="修改后的重点")
    done = commands.add_parser("done", help="标记完成，可附一句记录")
    done.add_argument("note", nargs="?", help="完成说明")
    done.add_argument("--date", help="补记已有重点：昨天 / yesterday / YYYY-MM-DD")
    commands.add_parser("undo", help="撤销今日完成状态，同时清除完成说明")
    commands.add_parser("carry", help="将昨天未完成的重点沿用到今天")
    stats = commands.add_parser("stats", help="查看完成天数和记录")
    period = stats.add_mutually_exclusive_group()
    period.add_argument("--week", action="store_true", help="本周（默认，周一开始）")
    period.add_argument("--month", action="store_true", help="本月")
    history = commands.add_parser("history", help="查看历史事项，包含待完成事项")
    history.add_argument("--limit", type=positive_int, default=30, help="最多显示几条（默认 30）")
    calendar = commands.add_parser("calendar", help="查看 GitHub 风格贡献日历（默认最近 12 周）")
    calendar.add_argument("--year", type=calendar_year, help="查看指定年份，例如 2026")
    return app


def calendar_year(value):
    number = positive_int(value)
    if not 1900 <= number <= 9998:
        raise argparse.ArgumentTypeError("年份范围为 1900–9998。")
    return number


def positive_int(value):
    try:
        number = int(value)
        if number > 0:
            return number
    except ValueError:
        pass
    raise argparse.ArgumentTypeError("请输入大于 0 的整数。")


def completion_day(value, today):
    if value is None or value in ("今天", "today"):
        return today
    if value in ("昨天", "yesterday"):
        return today - timedelta(days=1)
    try:
        result = date.fromisoformat(value)
        if result.isoformat() != value:
            raise ValueError
    except ValueError:
        raise UserError("日期请使用 YYYY-MM-DD 或「昨天」。") from None
    if result > today:
        raise UserError("不能为未来日期标记完成。")
    return result


def show_focus(row, day):
    header("FOCUS", day.isoformat())
    if row is None:
        print(f"\n  {paint('[ ]', MUTED)} 今天还没有重点。\n")
        hint('1d1t add "一件重要的事"')
    else:
        marker = paint("[+] 已完成", GREEN) if row["done_at"] else paint("[ ] 待完成", MUTED)
        print(f"\n  {marker}")
        print(f"  {paint('│', MUTED)} {paint(row['title'], BOLD)}")
        if row["note"]:
            print(f"  {paint('└', MUTED)} {row['note']}")
        if row["source_day"]:
            print("  " + paint(f"↳ 沿用自 {row['source_day']}", MUTED))
        print()


def show_records(rows):
    if not rows:
        print("  暂无记录。\n")
    for row in rows:
        symbol = paint("+", GREEN) if row["done_at"] else paint("·", MUTED)
        state = "已完成" if row["done_at"] else "待完成"
        print(f"  {paint(row['day'], MUTED)}  {symbol} {state}  {row['title']}")
        if row["note"]:
            print(f"              {paint('└', MUTED)} {row['note']}")
    print()


def main(argv=None, *, today=None):
    args = parser().parse_args(argv)
    if args.command == "welcome":
        welcome()
        return 0
    today = today or date.today()
    directory = args.data_dir or Path(
        os.environ.get("ONED1T_DATA_DIR")
        or Path.home() / "Library" / "Application Support" / "1D1T"
    )
    store = None
    try:
        # Reject invalid input before creating a database.
        title = clean_text(args.title) if args.command in ("add", "edit") else None
        note = clean_text(args.note) if args.command == "done" and args.note is not None else None
        target = completion_day(args.date, today) if args.command == "done" else today
        store = Store(directory.expanduser())
        if args.command == "stats":
            start = today.replace(day=1) if args.month else today - timedelta(days=today.weekday())
            rows = store.records(start, today, completed_only=True)
            header("MONTH" if args.month else "WEEK", f"{start} → {today}")
            print(f"  {paint(f'{len(rows):02d}', GREEN)} {paint('DAYS', MUTED)}  ·  完成 {len(rows)} 天\n")
            show_records(rows)
            return 0
        if args.command == "history":
            header("LOG", f"历史事项 · 最近 {args.limit} 条")
            print()
            show_records(store.records(date.min, today, limit=args.limit))
            return 0
        if args.command == "calendar":
            start, end = calendar_range(today, args.year)
            show_calendar(start, end, today, store.records(start, min(end, today), completed_only=True))
            return 0
        if args.command == "add":
            row = store.add(today, title)
        elif args.command == "edit":
            row = store.edit(today, title)
        elif args.command == "done":
            existing = store.get(target)
            if existing and existing["done_at"]:
                print("  已有完成记录，保留原记录。")
            row = store.done(target, note)
        elif args.command == "undo":
            row = store.undo(today)
        elif args.command == "carry":
            row = store.carry(today)
        else:
            row = store.get(today)
            if args.command is None and row is None and not store.records(date.min, date.max, limit=1):
                welcome()
        show_focus(row, target)
        return 0
    except (UserError, OSError, sqlite3.Error) as error:
        print(f"1d1t: {error}", file=sys.stderr)
        return 1
    finally:
        if store:
            store.close()
