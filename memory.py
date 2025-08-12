from __future__ import annotations

import json
import sqlite3
from datetime import datetime
from pathlib import Path
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


class MemoryManager:
    """JSON-based memory manager for per-session conversation storage."""

    def __init__(self, path: str = "memory_store.json") -> None:
        base_path = Path(path)
        if not base_path.is_absolute():
            base_path = Path(__file__).resolve().parent / base_path
        self.path = base_path
        if self.path.exists():
            try:
                self.store: Dict[str, List[Dict[str, Any]]] = json.loads(
                    self.path.read_text(encoding="utf-8") or "{}"
                )
            except json.JSONDecodeError:
                self.store = {}
        else:
            self.store = {}
            self.path.write_text("{}", encoding="utf-8")

    def _persist(self) -> None:
        self.path.write_text(json.dumps(self.store, indent=2), encoding="utf-8")

    def log(self, session_id: str, user_input: Any, response: Any | None = None) -> None:
        """Append a conversation turn to a session.

        Parameters
        ----------
        session_id:
            Identifier for the conversation session.
        user_input:
            Either the user input (if ``response`` provided) or the result to
            store directly when ``response`` is ``None``.
        response:
            Optional response payload. If omitted, ``user_input`` is treated as
            the response and the input field is left ``None``.
        """

        if response is None:
            stored_input = None
            stored_response = user_input
        else:
            stored_input = user_input
            stored_response = response

        entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "input": stored_input,
            "response": stored_response,
        }
        self.store.setdefault(session_id, []).append(entry)
        self._persist()

    def recall(self, session_id: str) -> List[Dict[str, Any]]:
        """Return the conversation history for a session."""
        return self.store.get(session_id, [])

    def fetch_all(self) -> Dict[str, List[Dict[str, Any]]]:
        """Return the entire memory store."""
        return self.store

