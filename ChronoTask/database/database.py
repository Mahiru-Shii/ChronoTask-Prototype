import sqlite3
from pathlib import Path


class Database:
    """Small SQLite connection/schema manager for ChronoTask."""

    def __init__(self, db_path="chronotask.db"):
        self.db_path = Path(db_path)
        self.connection = None

    def connect(self):
        if self.connection is None:
            self.db_path.parent.mkdir(parents=True, exist_ok=True)
            self.connection = sqlite3.connect(self.db_path)
            self.connection.row_factory = sqlite3.Row
            self.connection.execute("PRAGMA foreign_keys = ON")
        return self.connection

    def create_tables(self):
        conn = self.connect()
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT NOT NULL DEFAULT '',
                deadline_date TEXT NOT NULL,
                deadline_time TEXT NOT NULL,
                is_urgent INTEGER NOT NULL DEFAULT 0 CHECK (is_urgent IN (0, 1)),
                is_important INTEGER NOT NULL DEFAULT 0 CHECK (is_important IN (0, 1)),
                completed INTEGER NOT NULL DEFAULT 0 CHECK (completed IN (0, 1)),
                created_date TEXT NOT NULL,
                include_rest_day INTEGER NOT NULL DEFAULT 0 CHECK (include_rest_day IN (0, 1))
            );

            CREATE TABLE IF NOT EXISTS chrono_steps (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_id INTEGER NOT NULL,
                description TEXT NOT NULL,
                completed INTEGER NOT NULL DEFAULT 0 CHECK (completed IN (0, 1)),
                scheduled_date TEXT,
                position INTEGER NOT NULL DEFAULT 0,
                FOREIGN KEY (task_id) REFERENCES tasks(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS rest_dates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_id INTEGER NOT NULL,
                rest_date TEXT NOT NULL,
                FOREIGN KEY (task_id) REFERENCES tasks(id) ON DELETE CASCADE,
                UNIQUE(task_id, rest_date)
            );

            CREATE INDEX IF NOT EXISTS idx_tasks_deadline
                ON tasks(deadline_date, deadline_time);
            CREATE INDEX IF NOT EXISTS idx_chrono_steps_task
                ON chrono_steps(task_id, position);
            CREATE INDEX IF NOT EXISTS idx_chrono_steps_date
                ON chrono_steps(scheduled_date);
            CREATE INDEX IF NOT EXISTS idx_rest_dates_date
                ON rest_dates(rest_date);
        """)
        conn.commit()

    def close(self):
        if self.connection is not None:
            self.connection.close()
            self.connection = None

    def __enter__(self):
        self.connect()
        self.create_tables()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if exc_type is None and self.connection is not None:
            self.connection.commit()
        elif self.connection is not None:
            self.connection.rollback()
        self.close()
