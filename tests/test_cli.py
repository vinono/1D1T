import contextlib
import io
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
from datetime import date

from oned1t.cli import main


class CLITest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.today = date(2026, 9, 22)

    def run_cli(self, *args, day=None):
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = main(
                ["--data-dir", self.temp.name, *args],
                today=day or self.today,
            )
        return code, out.getvalue(), err.getvalue()

    def test_add_is_persistent_and_never_overwrites_today(self):
        self.assertEqual(self.run_cli("add", "完成博客首页")[0], 0)
        code, output, _ = self.run_cli("today")
        self.assertEqual(code, 0)
        self.assertIn("完成博客首页", output)
        self.assertIn("待完成", output)
        code, _, error = self.run_cli("add", "另一个重点")
        self.assertEqual(code, 1)
        self.assertIn("edit", error)
        self.assertIn("完成博客首页", self.run_cli("today")[1])

    def test_complete_edit_and_undo_preserve_one_focus(self):
        self.run_cli("add", "写首页")
        self.assertEqual(self.run_cli("edit", "完成首页布局")[0], 0)
        self.assertEqual(self.run_cli("done", "支持手机浏览")[0], 0)
        output = self.run_cli("today")[1]
        self.assertIn("已完成", output)
        self.assertIn("支持手机浏览", output)
        self.assertEqual(self.run_cli("edit", "写第二件事")[0], 1)
        self.assertEqual(self.run_cli("add", "写第二件事")[0], 1)
        self.assertEqual(self.run_cli("done", "重复记录")[0], 0)
        self.assertNotIn("重复记录", self.run_cli("today")[1])
        self.assertEqual(self.run_cli("undo")[0], 0)
        output = self.run_cli("today")[1]
        self.assertIn("待完成", output)
        self.assertIn("完成首页布局", output)
        self.assertNotIn("支持手机浏览", output)
        self.assertEqual(self.run_cli("edit", "调整首页布局")[0], 0)

    def test_missing_focus_and_invalid_input_have_clear_errors(self):
        for command in ("done", "undo"):
            self.assertEqual(self.run_cli(command)[0], 1)
        self.assertEqual(self.run_cli("edit", "新内容")[0], 1)
        for text in ("   ", "危险\x1b[2J", "多行\n内容"):
            self.assertEqual(self.run_cli("add", text)[0], 1)
        self.assertIn("还没有重点", self.run_cli("today")[1])

    def test_carry_keeps_yesterday_and_backfill_belongs_to_original_day(self):
        yesterday = date(2026, 9, 21)
        self.run_cli("add", "整理照片", day=yesterday)
        self.assertIn("还没有重点", self.run_cli("today")[1])
        self.assertEqual(self.run_cli("carry")[0], 0)
        self.assertIn("整理照片", self.run_cli("today")[1])
        self.assertIn("待完成", self.run_cli("today", day=yesterday)[1])
        self.assertEqual(self.run_cli("carry")[0], 1)
        self.assertEqual(self.run_cli("done", "昨天其实做完了", "--date", "昨天")[0], 0)
        self.assertIn("昨天其实做完了", self.run_cli("today", day=yesterday)[1])
        self.assertIn("待完成", self.run_cli("today")[1])

    def test_backfill_rejects_future_missing_and_invalid_dates(self):
        for value in ("2026-09-23", "2026-09-20", "2026-02-30", "garbage"):
            with self.subTest(value=value):
                self.assertEqual(self.run_cli("done", "--date", value)[0], 1)
        self.assertEqual(self.run_cli("carry")[0], 1)
        yesterday = date(2026, 9, 21)
        self.run_cli("add", "已完成的事", day=yesterday)
        self.run_cli("done", day=yesterday)
        self.assertEqual(self.run_cli("carry")[0], 1)
        self.assertIn("还没有重点", self.run_cli("today")[1])

    def test_statistics_count_original_days_and_history_keeps_pending_days(self):
        for day, title, complete in (
            (date(2026, 8, 31), "八月记录", True),
            (date(2026, 9, 1), "月初记录", True),
            (date(2026, 9, 20), "上周记录", True),
            (date(2026, 9, 21), "昨天的重点", False),
        ):
            self.run_cli("add", title, day=day)
            if complete:
                self.run_cli("done", day=day)
        self.run_cli("add", "今日待完成")
        self.run_cli("done", "补记说明", "--date", "昨天")
        week = self.run_cli("stats", "--week")[1]
        self.assertIn("完成 1 天", week)
        self.assertIn("昨天的重点", week)
        self.assertNotIn("上周记录", week)
        month = self.run_cli("stats", "--month")[1]
        self.assertIn("完成 3 天", month)
        self.assertNotIn("八月记录", month)
        self.assertNotIn("%", month)
        history = self.run_cli("history")[1]
        self.assertIn("今日待完成", history)
        self.assertIn("补记说明", history)
        self.assertLess(history.index("今日待完成"), history.index("八月记录"))
        limited = self.run_cli("history", "--limit", "1")[1]
        self.assertIn("今日待完成", limited)
        self.assertNotIn("昨天的重点", limited)

    def test_calendar_lights_only_completed_days_including_leap_day(self):
        self.run_cli("add", "闰日重点", day=date(2024, 2, 29))
        self.run_cli("done", day=date(2024, 2, 29))
        self.run_cli("add", "尚未完成", day=date(2024, 3, 1))
        self.run_cli("add", "其他年份", day=date(2025, 1, 1))
        self.run_cli("done", day=date(2025, 1, 1))
        with patch.dict("os.environ", {"COLUMNS": "48", "NO_COLOR": "1"}):
            code, output, _ = self.run_cli("calendar", "--year", "2024")
        self.assertEqual(code, 0)
        self.assertIn("2024-01-01", output)
        self.assertIn("2024-12-31", output)
        self.assertIn("完成 1 天", output)
        self.assertEqual(output.count("■"), 2)  # one day plus the legend
        self.assertNotIn("\x1b", output)
        self.assertNotIn("%", output)
        # Each seven-row panel shows weekdays vertically like GitHub.
        self.assertGreaterEqual(output.count("周一"), 4)
        self.assertEqual(output.count("周一"), output.count("周日"))

    def test_rolling_calendar_and_undo_update_contributions(self):
        self.run_cli("add", "今日重点")
        self.run_cli("done")
        output = self.run_cli("calendar")[1]
        self.assertIn("完成 1 天", output)
        self.assertEqual(output.count("■"), 2)
        self.run_cli("undo")
        self.assertIn("完成 0 天", self.run_cli("calendar")[1])

    def test_week_crosses_year_and_month_stops_at_its_boundary(self):
        for day in (date(2025, 12, 28), date(2025, 12, 29), date(2026, 1, 1)):
            self.run_cli("add", day.isoformat(), day=day)
            self.run_cli("done", day=day)
        self.assertIn("完成 2 天", self.run_cli("stats", "--week", day=date(2026, 1, 1))[1])
        self.assertIn("完成 1 天", self.run_cli("stats", "--month", day=date(2026, 1, 1))[1])

    def test_executable_uses_same_data_from_other_working_directories(self):
        command = Path(__file__).resolve().parents[1] / "bin" / "1d1t"
        env = dict(os.environ, ONED1T_DATA_DIR=self.temp.name)
        added = subprocess.run(
            [sys.executable, str(command), "add", "跨目录使用"],
            cwd="/tmp", env=env, text=True, capture_output=True,
        )
        self.assertEqual(added.returncode, 0, added.stderr)
        shown = subprocess.run(
            [sys.executable, str(command)],
            cwd="/", env=env, text=True, capture_output=True,
        )
        self.assertEqual(shown.returncode, 0, shown.stderr)
        self.assertIn("跨目录使用", shown.stdout)

    def test_simultaneous_adds_preserve_a_single_focus(self):
        command = Path(__file__).resolve().parents[1] / "bin" / "1d1t"
        env = dict(os.environ, ONED1T_DATA_DIR=self.temp.name)
        processes = [subprocess.Popen(
            [sys.executable, str(command), "add", title],
            env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
        ) for title in ("第一个终端", "第二个终端")]
        for process in processes:
            process.communicate(timeout=15)
        self.assertEqual(sorted(process.returncode for process in processes), [0, 1])
        result = subprocess.run(
            [sys.executable, str(command), "history"],
            env=env, text=True, capture_output=True,
        )
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stdout.count("待完成"), 1)


if __name__ == "__main__":
    unittest.main()
