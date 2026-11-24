"""Small local SQLite conversation memory."""

import sqlite3
import time
from pathlib import Path


class ConversationMemory:
    def __init__(self, path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as db:
            db.execute(
                "CREATE TABLE IF NOT EXISTS messages (id INTEGER PRIMARY KEY, created_ns INTEGER NOT NULL, role TEXT NOT NULL, text TEXT NOT NULL)"
            )

    def _connect(self):
        return sqlite3.connect(self.path, timeout=3)

    def add(self, role: str, text: str):
        if role not in {"user", "assistant"}:
            raise ValueError("Invalid conversation role.")
        with self._connect() as db:
            db.execute(
                "INSERT INTO messages(created_ns, role, text) VALUES (?, ?, ?)",
                (time.monotonic_ns(), role, text[:4000]),
            )

    def recent(self, limit=10):
        safe_limit = max(1, min(int(limit), 50))
        with self._connect() as db:
            rows = db.execute(
                "SELECT role, text FROM messages ORDER BY id DESC LIMIT ?", (safe_limit,)
            ).fetchall()
        return list(reversed(rows))

    def clear(self):
        with self._connect() as db:
            db.execute("DELETE FROM messages")
