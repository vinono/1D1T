"""A terminal contribution calendar, with weeks as columns."""

from datetime import date, timedelta
import os
import shutil
import sys


def paint(text, color):
    enabled = sys.stdout.isatty() and "NO_COLOR" not in os.environ and os.environ.get("TERM") != "dumb"
    return f"\033[{color}m{text}\033[0m" if enabled else text


def calendar_range(today, year):
    if year is not None:
        return date(year, 1, 1), date(year, 12, 31)
    return today - timedelta(days=today.weekday() + 11 * 7), today


def show_calendar(start, end, today, records):
    completed = {date.fromisoformat(row["day"]) for row in records}
    first_monday = start - timedelta(days=start.weekday())
    weeks = (end - first_monday).days // 7 + 1
    width = shutil.get_terminal_size(fallback=(80, 24)).columns
    columns = max(1, min(weeks, (width - 8) // 3))
    print(f"\n  1D1T · 贡献日历")
    print(f"  {start} — {end}")
    print(f"  完成 {len(completed)} 天\n")
    for offset in range(0, weeks, columns):
        mondays = [
            first_monday + timedelta(weeks=index)
            for index in range(offset, min(offset + columns, weeks))
        ]
        panel_start, panel_end = max(start, mondays[0]), min(end, mondays[-1] + timedelta(days=6))
        print(f"  {panel_start} — {panel_end}")
        labels = []
        previous_month = None
        for monday in mondays:
            visible = max(start, monday)
            labels.append(f"{visible.month:02d} " if visible.month != previous_month else "   ")
            previous_month = visible.month
        print("       " + "".join(labels).rstrip())
        for weekday, name in enumerate(("周一", "周二", "周三", "周四", "周五", "周六", "周日")):
            cells = []
            for monday in mondays:
                day = monday + timedelta(days=weekday)
                if day < start or day > end or day > today:
                    cells.append("   ")
                elif day in completed:
                    cells.append(paint("■", "32") + "  ")
                else:
                    cells.append(paint("·", "90") + "  ")
            print(f"  {name} " + "".join(cells).rstrip())
        print()
    print(f"  {paint('■', '32')} 有完成记录   {paint('·', '90')} 无完成记录   空白：未来或范围外\n")
