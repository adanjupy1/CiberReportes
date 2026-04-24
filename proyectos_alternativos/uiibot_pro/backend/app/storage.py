# -*- coding: utf-8 -*-
import sqlite3, json, threading, datetime
from typing import Any, Optional

class Storage:
    """
    Simple SQLite storage (works out-of-the-box). You can swap to Postgres later.
    """
    def __init__(self, db_path: str = "uiibot.db"):
        self.db_path = db_path
        self._lock = threading.Lock()
        self._init_db()

    def _conn(self):
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        with self._conn() as conn:
            conn.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                session_id TEXT PRIMARY KEY,
                state TEXT NOT NULL,
                context_json TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )""")
            conn.execute("""
            CREATE TABLE IF NOT EXISTS reports (
                report_id TEXT PRIMARY KEY,
                session_id TEXT,
                created_at TEXT NOT NULL,
                name TEXT,
                state TEXT,
                age INTEGER,
                sex TEXT,
                incident_type TEXT,
                description TEXT,
                extra_json TEXT
            )""")
            conn.execute("""
            CREATE TABLE IF NOT EXISTS counters (
                k TEXT PRIMARY KEY,
                v INTEGER NOT NULL
            )""")
            conn.execute("INSERT OR IGNORE INTO counters (k,v) VALUES ('report_seq', 0)")
            conn.commit()

    def get_session(self, session_id: str) -> dict[str, Any]:
        with self._lock, self._conn() as conn:
            row = conn.execute("SELECT * FROM sessions WHERE session_id=?", (session_id,)).fetchone()
            if not row:
                return {
                    "session_id": session_id,
                    "state": "ROOT",
                    "context": {},
                }
            return {
                "session_id": row["session_id"],
                "state": row["state"],
                "context": json.loads(row["context_json"] or "{}"),
            }

    def save_session(self, session_id: str, state: str, context: dict[str, Any]) -> None:
        now = datetime.datetime.utcnow().isoformat()
        with self._lock, self._conn() as conn:
            conn.execute("""
            INSERT INTO sessions(session_id, state, context_json, updated_at)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(session_id) DO UPDATE SET
                state=excluded.state,
                context_json=excluded.context_json,
                updated_at=excluded.updated_at
            """, (session_id, state, json.dumps(context, ensure_ascii=False), now))
            conn.commit()

    def next_report_seq(self) -> int:
        with self._lock, self._conn() as conn:
            cur = conn.execute("SELECT v FROM counters WHERE k='report_seq'").fetchone()["v"]
            nxt = cur + 1
            conn.execute("UPDATE counters SET v=? WHERE k='report_seq'", (nxt,))
            conn.commit()
            return nxt

    def save_report(
        self,
        report_id: str,
        session_id: str,
        name: str|None,
        state: str|None,
        age: int|None,
        sex: str|None,
        incident_type: str|None,
        description: str|None,
        extra: dict[str, Any]|None = None,
    ) -> None:
        now = datetime.datetime.utcnow().isoformat()
        with self._lock, self._conn() as conn:
            conn.execute("""
            INSERT INTO reports(report_id, session_id, created_at, name, state, age, sex, incident_type, description, extra_json)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (report_id, session_id, now, name, state, age, sex, incident_type, description, json.dumps(extra or {}, ensure_ascii=False)))
            conn.commit()
