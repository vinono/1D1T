"""Shared terminal identity; ANSI styling is optional, never stored in data."""

import os
import shutil
import sys


TAGLINE = "One day. One thing.\nTake a day. Feel the love in everything."

SILVER = "97"
SOFT = "37"
MUTED = "90"
BOLD = "1;97"


def paint(text, color, *, stream=None):
    stream = stream or sys.stdout
    enabled = stream.isatty() and "NO_COLOR" not in os.environ and os.environ.get("TERM") != "dumb"
    return f"\033[{color}m{text}\033[0m" if enabled else text


def width():
    return shutil.get_terminal_size(fallback=(80, 24)).columns


def rule():
    print("  " + paint("─" * max(1, min(56, width() - 4)), MUTED))


def header(section, subtitle):
    print(f"\n  {paint('> ▪', SILVER)} {paint('1D1T', BOLD)} {paint('/ ' + section, MUTED)}")
    rule()
    print(f"  {paint(subtitle, MUTED)}")


def hint(command):
    print(f"  {paint('$', SILVER)} {paint(command, SOFT)}\n")


def welcome():
    """Show branding on demand, without opening or changing the database."""
    import textwrap
    glyphs = (
        ("  ■■  ", " ■■■  ", "   ■  ", "   ■  ", "   ■  ", "■■■■■■"),
        ("■■■■■ ", "■■  ■■", "■■  ■■", "■■  ■■", "■■  ■■", "■■■■■ "),
        ("  ■■  ", " ■■■  ", "   ■  ", "   ■  ", "   ■  ", "■■■■■■"),
        ("■■■■■■■", "   ■■  ", "   ■■  ", "   ■■  ", "   ■■  ", "   ■■  "),
    )
    logo = ("  > ▪",) + tuple(
        "  " + "  ".join(glyph[row] for glyph in glyphs).rstrip()
        for row in range(6)
    )
    print()
    if width() >= 36:
        for line in logo:
            print(paint(line, SILVER))
    else:
        print(paint("  > ▪ 1D1T", SILVER))
    print()
    for line in TAGLINE.splitlines():
        print(paint(textwrap.fill(line, width=max(12, width() - 2), initial_indent="  ", subsequent_indent="  "), SOFT))
    print()
    rule()
    print(f"\n  {paint('GET STARTED', BOLD)}\n")
    items = (
        ('1d1t add "Ship something small"', "Set today's focus"),
        ('1d1t done', "Mark it complete"),
        ('1d1t calendar', "See your contribution grid"),
    )
    for cmd, desc in items:
        if width() < 70:
            print(f"  {paint(cmd, SILVER)}")
            print(f"    {paint(desc, MUTED)}")
        else:
            print(f"  {paint(cmd.ljust(37), SILVER)} {paint(desc, MUTED)}")
    print()
