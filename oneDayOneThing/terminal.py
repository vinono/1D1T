"""Shared terminal identity; ANSI styling is optional, never stored in data."""

import os
import shutil
import sys


TAGLINE = "Take a day. Feel the love in everything."

GREEN = "92"
MUTED = "90"
CYAN = "36"
BOLD = "1"


def paint(text, color):
    enabled = sys.stdout.isatty() and "NO_COLOR" not in os.environ and os.environ.get("TERM") != "dumb"
    return f"\033[{color}m{text}\033[0m" if enabled else text


def width():
    return shutil.get_terminal_size(fallback=(80, 24)).columns


def rule():
    print("  " + paint("─" * max(1, min(56, width() - 4)), MUTED))


def header(section, subtitle):
    print(f"\n  {paint('> ▪', GREEN)} {paint('1D1T', BOLD)} {paint('/ ' + section, MUTED)}")
    rule()
    print(f"  {paint(subtitle, MUTED)}")


def hint(command):
    print(f"  {paint('$', GREEN)} {command}\n")


def welcome():
    """Show branding on demand, without opening or changing the database."""
    import textwrap
    logo = (
        "  11    DDDD    11   TTTTT",
        " 111    D   D  111     T  ",
        "  11    D   D   11     T  ",
        "  11    D   D   11     T  ",
        " 1111   DDDD   1111    T  ",
    )
    print()
    if width() >= 32:
        for line in logo:
            print(paint(line, GREEN))
    else:
        print(paint("  > 1D1T", GREEN))
    print()
    print(textwrap.fill(TAGLINE, width=max(12, width() - 2), initial_indent="  ", subsequent_indent="  "))
    print()
    rule()
    for command in ('1d1t add "今日重点"', '1d1t done', '1d1t calendar', '1d1t --help'):
        hint(command)
