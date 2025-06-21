from __future__ import annotations

import json
import sqlite3
from datetime import datetime
from typing import Any, Dict, List, Tuple


class Memory:
    """Simple SQLite-based memory for storing agent call history."""

    def __init__(self, db_path: str = "memory.db") -> None:
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.conn.execute(
            """
            CREATE TABLE IF NOT EXISTS history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                agent TEXT,
                input TEXT,
                output TEXT
            )
            """
        )
        self.conn.commit()

    def record(self, agent: str, input_data: Dict[str, Any], output: Any) -> None:
        self.conn.execute(
            "INSERT INTO history (timestamp, agent, input, output) VALUES (?,?,?,?)",
            (
                datetime.utcnow().isoformat(),
                agent,
                json.dumps(input_data),
                json.dumps(output),
            ),
        )
        self.conn.commit()

    def fetch_all(self) -> List[Tuple[str, str, str, str]]:
        cur = self.conn.execute(
            "SELECT timestamp, agent, input, output FROM history ORDER BY id DESC"
        )
        return cur.fetchall()
