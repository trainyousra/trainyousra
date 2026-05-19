import sqlite3
from dataclasses import dataclass
from pathlib import Path


@dataclass
class Memory:
  id: int
  tweet_id: str
  author: str
  lesson: str
  source_text: str
  created_at: str


class MemoryStore:
  def __init__(self, db_path: Path) -> None:
    self._path = db_path
    self._init_db()

  def _connect(self) -> sqlite3.Connection:
    conn = sqlite3.connect(self._path)
    conn.row_factory = sqlite3.Row
    return conn

  def _init_db(self) -> None:
    with self._connect() as conn:
      conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS memories (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          tweet_id TEXT NOT NULL UNIQUE,
          author TEXT NOT NULL,
          lesson TEXT NOT NULL,
          source_text TEXT NOT NULL,
          created_at TEXT DEFAULT (datetime('now'))
        );
        CREATE TABLE IF NOT EXISTS seen_tweets (
          tweet_id TEXT PRIMARY KEY,
          handled_at TEXT DEFAULT (datetime('now'))
        );
        """
      )

  def is_seen(self, tweet_id: str) -> bool:
    with self._connect() as conn:
      row = conn.execute(
        "SELECT 1 FROM seen_tweets WHERE tweet_id = ?", (tweet_id,)
      ).fetchone()
    return row is not None

  def mark_seen(self, tweet_id: str) -> None:
    with self._connect() as conn:
      conn.execute(
        "INSERT OR IGNORE INTO seen_tweets (tweet_id) VALUES (?)",
        (tweet_id,),
      )

  def add_memory(
    self, tweet_id: str, author: str, lesson: str, source_text: str
  ) -> None:
    with self._connect() as conn:
      conn.execute(
        """
        INSERT OR REPLACE INTO memories (tweet_id, author, lesson, source_text)
        VALUES (?, ?, ?, ?)
        """,
        (tweet_id, author, lesson, source_text),
      )

  def recent_lessons(self, limit: int) -> list[str]:
    with self._connect() as conn:
      rows = conn.execute(
        "SELECT lesson FROM memories ORDER BY id DESC LIMIT ?", (limit,)
      ).fetchall()
    return [r["lesson"] for r in rows]

  def recent_memories(self, limit: int = 50) -> list[Memory]:
    with self._connect() as conn:
      rows = conn.execute(
        """
        SELECT id, tweet_id, author, lesson, source_text, created_at
        FROM memories ORDER BY id DESC LIMIT ?
        """,
        (limit,),
      ).fetchall()
    return [
      Memory(
        id=r["id"],
        tweet_id=r["tweet_id"],
        author=r["author"],
        lesson=r["lesson"],
        source_text=r["source_text"],
        created_at=r["created_at"],
      )
      for r in rows
    ]

  def count(self) -> int:
    with self._connect() as conn:
      row = conn.execute("SELECT COUNT(*) AS c FROM memories").fetchone()
    return int(row["c"])
