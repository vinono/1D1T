"""A terminal contribution calendar, with weeks as columns."""

from datetime import date, timedelta
from .terminal import BOLD, MUTED, SILVER, header, hint, paint, rule, width


def calendar_range(today, year):
    if year is not None:
        return date(year, 1, 1), date(year, 12, 31)
    return today - timedelta(days=today.weekday() + 11 * 7), today


def show_calendar(start, end, today, records):
    completed = {date.fromisoformat(row["day"]) for row in records}
    first_monday = start - timedelta(days=start.weekday())
    weeks = (end - first_monday).days // 7 + 1
    columns = max(1, min(weeks, (width() - 10) // 3))
    header("CALENDAR", f"{start} → {end}")
    print(f"  {paint(f'{len(completed):02d}', SILVER)} {paint('DAYS', MUTED)}  ·  {len(completed)} completed\n")
    for offset in range(0, weeks, columns):
        mondays = [
            first_monday + timedelta(weeks=index)
            for index in range(offset, min(offset + columns, weeks))
        ]
        panel_start, panel_end = max(start, mondays[0]), min(end, mondays[-1] + timedelta(days=6))
        if weeks > columns:
            print("  " + paint(f"{panel_start} → {panel_end}", MUTED))
        labels = []
        previous_month = None
        for monday in mondays:
            visible = max(start, monday)
            labels.append(f"{visible.month:02d} " if visible.month != previous_month else "   ")
            previous_month = visible.month
        print("         " + paint("".join(labels).rstrip(), MUTED))
        for weekday, name in enumerate(("Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun")):
            cells = []
            for monday in mondays:
                day = monday + timedelta(days=weekday)
                if day < start or day > end or day > today:
                    cells.append("   ")
                elif day in completed:
                    cells.append(paint("■", SILVER) + "  ")
                elif day == today:
                    cells.append(paint("□", SILVER) + "  ")
                else:
                    cells.append(paint("▪", MUTED) + "  ")
            print(f"   {paint(name, MUTED)} {paint('│', MUTED)} " + "".join(cells).rstrip())
        print()
    rule()
    print(f"  {paint('■', SILVER)} Recorded  {paint('▪', MUTED)} No record  {paint('□', SILVER)} Today")
    print("  " + paint("Blank: future or out of range  ·  Run 1d1t calendar -i for interactive mode", MUTED) + "\n")
    if not completed and start <= today <= end:
        hint('1d1t today')
