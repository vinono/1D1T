"""Transactional storage shared by all commands."""

from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
from pathlib import Path
import sqlite3


class UserError(Exception):
    """An expected error that should be shown without a traceback."""


def timestamp():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


class Store:
    def __init__(self, directory: Path):
        directory.mkdir(parents=True, exist_ok=True, mode=0o700)
        self.db = sqlite3.connect(directory / "focus.sqlite3", timeout=10)
        self.db.row_factory = sqlite3.Row
        try:
            with self.write():
                version = self.db.execute("PRAGMA user_version").fetchone()[0]
                if version not in (0, 1):
                    raise UserError("数据由更新版本创建，请升级 1d1t 后再打开。")
                self.db.execute("""
                    CREATE TABLE IF NOT EXISTS focus_days (
                        day TEXT PRIMARY KEY,
                        title TEXT NOT NULL,
                        created_at TEXT NOT NULL,
                        done_at TEXT,
                        note TEXT,
                        source_day TEXT,
                        CHECK (done_at IS NOT NULL OR note IS NULL)
                    )
                """)
                self.db.execute("PRAGMA user_version = 1")
        except Exception:
            self.db.close()
            raise

    @contextmanager
    def write(self):
        # Serialize the read/check/write sequence across simultaneous terminals.
        self.db.execute("BEGIN IMMEDIATE")
        try:
            yield
            self.db.commit()
        except Exception:
            self.db.rollback()
            raise

    def close(self):
        self.db.close()

    def get(self, day):
        return self.db.execute(
            "SELECT * FROM focus_days WHERE day = ?", (day.isoformat(),)
        ).fetchone()

    def add(self, day, title):
        with self.write():
            if self.get(day):
                raise UserError("今天已有重点，请使用 1d1t edit 修改；完成后不能追加。")
            self.db.execute(
                "INSERT INTO focus_days (day, title, created_at) VALUES (?, ?, ?)",
                (day.isoformat(), title, timestamp()),
            )
        return self.get(day)

    def require(self, day):
        row = self.get(day)
        if row is None:
            raise UserError(f"{day.isoformat()} 还没有重点。请先用 1d1t add 设置今日重点。")
        return row

    def edit(self, day, title):
        with self.write():
            if self.require(day)["done_at"]:
                raise UserError("今日重点已完成；如需纠正，请先用 1d1t undo 撤销完成。")
            self.db.execute(
                "UPDATE focus_days SET title = ? WHERE day = ?", (title, day.isoformat())
            )
        return self.get(day)

    def done(self, day, note):
        with self.write():
            row = self.require(day)
            if not row["done_at"]:
                self.db.execute(
                    "UPDATE focus_days SET done_at = ?, note = ? WHERE day = ?",
                    (timestamp(), note, day.isoformat()),
                )
        return self.get(day)

    def undo(self, day):
        with self.write():
            if not self.require(day)["done_at"]:
                raise UserError("今日重点尚未完成，无需撤销。")
            self.db.execute(
                "UPDATE focus_days SET done_at = NULL, note = NULL WHERE day = ?",
                (day.isoformat(),),
            )
        return self.get(day)

    def carry(self, day):
        yesterday = day - timedelta(days=1)
        with self.write():
            if self.get(day):
                raise UserError("今天已有重点，不能沿用覆盖；请使用 1d1t edit 修改。")
            previous = self.get(yesterday)
            if previous is None or previous["done_at"]:
                raise UserError("昨天没有未完成的重点可以沿用。")
            self.db.execute(
                "INSERT INTO focus_days (day, title, created_at, source_day) VALUES (?, ?, ?, ?)",
                (day.isoformat(), previous["title"], timestamp(), yesterday.isoformat()),
            )
        return self.get(day)

    def records(self, start, end, *, completed_only=False, limit=None):
        query = "SELECT * FROM focus_days WHERE day BETWEEN ? AND ?"
        parameters = [start.isoformat(), end.isoformat()]
        if completed_only:
            query += " AND done_at IS NOT NULL"
        query += " ORDER BY day DESC"
        if limit is not None:
            query += " LIMIT ?"
            parameters.append(limit)
        return self.db.execute(query, parameters).fetchall()
