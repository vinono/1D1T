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
from .terminal import BOLD, MUTED, SILVER, SOFT, TAGLINE, header, hint, paint, welcome


class SilverArgumentParser(argparse.ArgumentParser):
    def format_help(self):
        return paint(super().format_help(), SOFT)

    def error(self, message):
        self.print_usage(sys.stderr)
        self.exit(2, paint(f"1d1t: error: {message}\n", SILVER, stream=sys.stderr))


def clean_text(value):
    value = value.strip()
    if not value:
        raise UserError("Content cannot be empty.")
    if any(unicodedata.category(char) in ("Cc", "Cs") for char in value):
        raise UserError("Please use a single line without newlines or terminal control characters.")
    if len(value) > 2000:
        raise UserError("Content must be within 2000 characters.")
    return value


def parser():
    app = SilverArgumentParser(prog="1d1t", description=TAGLINE)
    app.add_argument("--version", action="version", version=f"1d1t {__version__}")
    app.add_argument("--data-dir", type=Path, help="Custom data directory (default: user Application Support)")
    commands = app.add_subparsers(dest="command", title="Commands")
    add = commands.add_parser("add", help="Set today's single focus")
    add.add_argument("title", help="Focus title, please wrap in quotes")
    commands.add_parser("welcome", help="Show welcome branding and quick start guide")
    commands.add_parser("today", help="View today's focus")
    edit = commands.add_parser("edit", help="Edit today's pending focus")
    edit.add_argument("title", help="New focus title")
    done = commands.add_parser("done", help="Mark focus completed, with an optional note")
    done.add_argument("note", nargs="?", help="Optional completion note")
    done.add_argument("--date", help="Complete an existing focus: yesterday / YYYY-MM-DD")
    commands.add_parser("undo", help="Undo today's completion and clear note")
    commands.add_parser("carry", help="Carry over yesterday's unfinished focus to today")
    stats = commands.add_parser("stats", help="View completed days and focus records")
    period = stats.add_mutually_exclusive_group()
    period.add_argument("--week", action="store_true", help="This week (default, starts Monday)")
    period.add_argument("--month", action="store_true", help="This month")
    history = commands.add_parser("history", help="View focus history log, including pending items")
    history.add_argument("--limit", type=positive_int, default=30, help="Maximum records to display (default: 30)")
    calendar = commands.add_parser("calendar", help="View contribution calendar grid (default: last 12 weeks)")
    calendar.add_argument("--year", type=calendar_year, help="View specified year, e.g. 2026")
    calendar.add_argument("-i", "--interactive", action="store_true", help="Enter interactive calendar explorer mode (navigate with arrow keys)")
    return app


def calendar_year(value):
    number = positive_int(value)
    if not 1900 <= number <= 9998:
        raise argparse.ArgumentTypeError("Year must be between 1900 and 9998.")
    return number


def positive_int(value):
    try:
        number = int(value)
        if number > 0:
            return number
    except ValueError:
        pass
    raise argparse.ArgumentTypeError("Please enter an integer greater than 0.")


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
        raise UserError("Date format must be YYYY-MM-DD or 'yesterday'.") from None
    if result > today:
        raise UserError("Cannot mark completion for future dates.")
    return result


def show_focus(row, day):
    header("FOCUS", day.isoformat())
    if row is None:
        print(f"\n  {paint('[ ]', MUTED)} No focus set for today.\n")
        hint('1d1t add "One important thing"')
    else:
        marker = paint("[+] Completed", SILVER) if row["done_at"] else paint("[ ] Pending", MUTED)
        print(f"\n  {marker}")
        print(f"  {paint('│', MUTED)} {paint(row['title'], BOLD)}")
        if row["note"]:
            print(f"  {paint('└', MUTED)} {paint(row['note'], SOFT)}")
        if row["source_day"]:
            print("  " + paint(f"↳ Carried over from {row['source_day']}", MUTED))
        print()


def show_records(rows):
    if not rows:
        print("  No records found.\n")
    for row in rows:
        symbol = paint("+", SILVER) if row["done_at"] else paint("·", MUTED)
        state = "Completed" if row["done_at"] else "Pending"
        print(f"  {paint(row['day'], MUTED)}  {symbol} {paint(f'{state:<9}', SILVER if row['done_at'] else MUTED)}  {paint(row['title'], SOFT)}")
        if row["note"]:
            print(f"              {paint('└', MUTED)} {paint(row['note'], SOFT)}")
    print()


def main(argv=None, *, today=None):
    args = parser().parse_args(argv)
    if args.command == "welcome":
        welcome()
        return 0
    today = today or date.today()
    directory = args.data_dir or Path(
        os.environ.get("ONE_DAY_ONE_THING_DATA_DIR")
        or os.environ.get("ONE_DAY_DATA_DIR")
        or os.environ.get("ONED1T_DATA_DIR")
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
            print(f"  {paint(f'{len(rows):02d}', SILVER)} {paint('DAYS', MUTED)}  ·  {len(rows)} completed\n")
            show_records(rows)
            return 0
        if args.command == "history":
            header("LOG", f"History · Last {args.limit} records")
            print()
            show_records(store.records(date.min, today, limit=args.limit))
            return 0
        if args.command == "calendar":
            start, end = calendar_range(today, args.year)
            if args.interactive:
                from .interactive import run_interactive_calendar
                return run_interactive_calendar(start, end, today, store.records(start, min(end, today)))
            show_calendar(start, end, today, store.records(start, min(end, today), completed_only=True))
            return 0
        if args.command == "add":
            row = store.add(today, title)
        elif args.command == "edit":
            row = store.edit(today, title)
        elif args.command == "done":
            existing = store.get(target)
            if existing and existing["done_at"]:
                print("  " + paint("Existing completed record found; kept original.", MUTED))
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
        print(paint(f"1d1t: {error}", SILVER, stream=sys.stderr), file=sys.stderr)
        return 1
    finally:
        if store:
            store.close()
