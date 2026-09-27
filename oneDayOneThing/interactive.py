"""Interactive TUI calendar explorer for 1D1T using curses."""

import curses
from datetime import date, timedelta
import os
import sys


def run_interactive_calendar(start, end, today, records):
    """Run interactive calendar matrix with live floating status display."""
    clean_records = [dict(r) if not isinstance(r, dict) else r for r in records]

    if not sys.stdout.isatty():
        from .calendar import show_calendar
        show_calendar(start, end, today, clean_records)
        return 0

    try:
        return curses.wrapper(_tui_loop, start, end, today, clean_records)
    except Exception:
        # Fallback to standard calendar if curses fails
        from .calendar import show_calendar
        show_calendar(start, end, today, clean_records)
        return 0


def _tui_loop(stdscr, start, end, today, records):
    records = [dict(r) if not isinstance(r, dict) else r for r in records]
    # Safely configure curses without throwing if terminal lacks capabilities
    try:
        curses.curs_set(0)
    except curses.error:
        pass

    try:
        stdscr.nodelay(False)
        stdscr.keypad(True)
    except curses.error:
        pass

    # Silver gelatin monochrome pairs
    # Pair 1: Normal silver/white
    # Pair 2: Muted gray / dim
    # Pair 3: Inverse highlight for selected cursor
    color_normal = curses.A_NORMAL
    color_dim = curses.A_DIM
    color_cursor = curses.A_REVERSE | curses.A_BOLD

    if curses.has_colors() and "NO_COLOR" not in os.environ and os.environ.get("TERM") != "dumb":
        try:
            curses.start_color()
            curses.use_default_colors()
            curses.init_pair(1, curses.COLOR_WHITE, -1)
            color_normal = curses.color_pair(1)
            color_dim = curses.color_pair(1) | curses.A_DIM
            color_cursor = curses.color_pair(1) | curses.A_REVERSE | curses.A_BOLD
        except curses.error:
            pass

    record_map = {date.fromisoformat(r["day"]): r for r in records}
    completed_days = {date.fromisoformat(r["day"]) for r in records if r.get("done_at")}

    first_monday = start - timedelta(days=start.weekday())
    total_weeks = (end - first_monday).days // 7 + 1

    # Weekday labels
    weekdays = ("Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun")

    # Start cursor at today or end
    current_date = today if start <= today <= end else end

    # Calculate navigation limits (allow exploring full visible week of end)
    nav_max_date = end + timedelta(days=6 - end.weekday())
    nav_min_date = first_monday

    while True:
        stdscr.erase()
        max_y, max_x = stdscr.getmaxyx()

        def safe_addstr(y, x, text, attr=0):
            if y < 0 or y >= max_y or x < 0 or x >= max_x:
                return
            avail = max_x - x
            if y == max_y - 1:
                avail = max(0, avail - 1)
            if avail > 0:
                try:
                    stdscr.addstr(y, x, text[:avail], attr)
                except curses.error:
                    pass

        if max_y < 12 or max_x < 46:
            safe_addstr(0, 0, "Terminal window too small, please resize (Press q to exit)", curses.A_BOLD)
            key = stdscr.getch()
            if key in (ord('q'), ord('Q'), 27):
                break
            continue

        # 1. Top Bar: Branding & Summary
        title_bar = "▪ 1D1T / ACTIVITY MATRIX (Interactive)"
        stat_bar = f"{len(completed_days)} days active · Silver Gelatin"
        safe_addstr(1, 2, title_bar, curses.A_BOLD | color_normal)
        if max_x > len(title_bar) + len(stat_bar) + 6:
            safe_addstr(1, max_x - len(stat_bar) - 4, stat_bar, curses.A_DIM)

        safe_addstr(2, 2, "─" * min(max_x - 4, 76), curses.A_DIM)

        # 2. Floating Hover/Status Card (mirrors landing page hover card)
        cur_weekday_name = weekdays[current_date.weekday()]
        date_str = f"{current_date.isoformat()} [{cur_weekday_name}]"

        card_y = 3
        card_w = min(max_x - 4, 76)

        # Border
        safe_addstr(card_y, 2, "┌" + "─" * (card_w - 2) + "┐", curses.A_DIM)

        if current_date in record_map:
            row = record_map[current_date]
            if row.get("done_at"):
                status_badge = " [COMPLETED] "
                badge_attr = curses.A_BOLD | curses.A_REVERSE
            else:
                status_badge = " [PENDING] "
                badge_attr = curses.A_DIM

            title_text = f" {date_str}  "
            safe_addstr(card_y + 1, 4, title_text, curses.A_BOLD | color_normal)
            safe_addstr(card_y + 1, 4 + len(title_text), status_badge, badge_attr)

            # Content line
            content = f"Focus: {row.get('title', '')}"
            if row.get("note"):
                content += f"  (Note: {row['note']})"
            content = content[:card_w - 8]
            safe_addstr(card_y + 2, 4, content, color_normal)
        elif current_date == today:
            safe_addstr(card_y + 1, 4, f" {date_str}   [TODAY] ", curses.A_BOLD | color_normal)
            safe_addstr(card_y + 2, 4, "No focus set for today. Run '1d1t add \"focus\"' to start.", curses.A_DIM)
        elif current_date > today:
            safe_addstr(card_y + 1, 4, f" {date_str}   [FUTURE] ", curses.A_DIM)
            safe_addstr(card_y + 2, 4, "Future date. Focus on today: one day, one thing.", curses.A_DIM)
        else:
            safe_addstr(card_y + 1, 4, f" {date_str}   [NO RECORD] ", curses.A_DIM)
            safe_addstr(card_y + 2, 4, "No focus recorded for this day. One day, one thing.", curses.A_DIM)

        safe_addstr(card_y + 3, 2, "└" + "─" * (card_w - 2) + "┘", curses.A_DIM)

        # 3. Calendar Matrix
        matrix_y = card_y + 4
        visible_weeks = min(total_weeks, (max_x - 12) // 3)
        start_week_offset = max(0, total_weeks - visible_weeks)

        mondays = [
            first_monday + timedelta(weeks=i)
            for i in range(start_week_offset, total_weeks)
        ]

        # Month labels
        labels = []
        prev_month = None
        for m in mondays:
            v = max(start, m)
            labels.append(f"{v.month:02d} " if v.month != prev_month else "   ")
            prev_month = v.month
        safe_addstr(matrix_y, 9, "".join(labels).rstrip(), curses.A_DIM)

        # Day rows
        for w_idx, name in enumerate(weekdays):
            row_y = matrix_y + 1 + w_idx
            safe_addstr(row_y, 3, f"{name} │", curses.A_DIM)

            for col_idx, monday in enumerate(mondays):
                day = monday + timedelta(days=w_idx)
                cell_x = 9 + col_idx * 3

                if day < start or day > nav_max_date:
                    cell_str = "   "
                    attr = curses.A_NORMAL
                elif day == current_date:
                    # Current selected cursor
                    if day in completed_days:
                        cell_str = "[■]"
                    elif day == today:
                        cell_str = "[□]"
                    elif day > today:
                        cell_str = "[·]"
                    else:
                        cell_str = "[▪]"
                    attr = color_cursor
                else:
                    if day in completed_days:
                        cell_str = " ■ "
                        attr = curses.A_BOLD | color_normal
                    elif day == today:
                        cell_str = " □ "
                        attr = curses.A_BOLD | color_normal
                    elif day > today:
                        cell_str = " · "
                        attr = curses.A_DIM
                    else:
                        cell_str = " ▪ "
                        attr = curses.A_DIM

                safe_addstr(row_y, cell_x, cell_str, attr)

        # 4. Footer & Controls
        footer_y = matrix_y + 9
        safe_addstr(footer_y, 2, "─" * min(max_x - 4, 76), curses.A_DIM)
        safe_addstr(
            footer_y + 1,
            2,
            "■ Recorded   ▪ No record   □ Today   [ ] Selected",
            curses.A_DIM,
        )
        safe_addstr(
            footer_y + 2,
            2,
            "Navigate: ← ↑ → ↓ / hjkl / wasd  •  q / Esc: Exit",
            curses.A_BOLD | color_normal,
        )

        stdscr.refresh()

        # Handle keyboard input
        key = stdscr.getch()

        # Handle Escape sequence for raw arrow keys in various terminals
        if key == 27:
            stdscr.nodelay(True)
            n1 = stdscr.getch()
            if n1 == -1:
                # Standalone Escape key -> exit
                break
            if n1 in (ord('['), ord('O')):
                n2 = stdscr.getch()
                if n2 == ord('A'):
                    key = curses.KEY_UP
                elif n2 == ord('B'):
                    key = curses.KEY_DOWN
                elif n2 == ord('C'):
                    key = curses.KEY_RIGHT
                elif n2 == ord('D'):
                    key = curses.KEY_LEFT
            stdscr.nodelay(False)

        if key in (ord('q'), ord('Q'), ord('x'), ord('X'), 3):  # q, Q, x, X, Ctrl-C
            break
        elif key in (curses.KEY_LEFT, ord('h'), ord('H'), ord('a'), ord('A')):
            new_date = current_date - timedelta(days=7)
            if new_date >= nav_min_date:
                current_date = new_date
        elif key in (curses.KEY_RIGHT, ord('l'), ord('L'), ord('d'), ord('D')):
            new_date = current_date + timedelta(days=7)
            if new_date <= nav_max_date:
                current_date = new_date
        elif key in (curses.KEY_UP, ord('k'), ord('K'), ord('w'), ord('W')):
            new_date = current_date - timedelta(days=1)
            if new_date >= nav_min_date:
                current_date = new_date
        elif key in (curses.KEY_DOWN, ord('j'), ord('J'), ord('s'), ord('S')):
            new_date = current_date + timedelta(days=1)
            if new_date <= nav_max_date:
                current_date = new_date

    return 0
