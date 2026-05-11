import sqlite3
from pathlib import Path

DB_PATH= Path("data/app.db")

def get_connection():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    return sqlite3.connect(DB_PATH)

def init_db():
    with get_connection() as conn:
        conn.execute(
            """
                CREATE TABLE IF NOT EXISTS documents (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL UNIQUE,
                text TEXT NOT NULL,
                char_count INTEGER NOT NULL,
                word_count INTEGER NOT NULL
            )
            """
        )

        conn.execute(
            """
                CREATE TABLE IF NOT EXISTS chunks (
                id TEXT PRIMARY KEY,
                document_id TEXT NOT NULL,
                chunk_index INTEGER NOT NULL,
                text TEXT NOT NULL,
                char_count INTEGER NOT NULL,
                word_count INTEGER NOT NULL,
                FOREIGN KEY (document_id) REFERENCES documents (id)
                )
            """
        )

        conn.execute(
            """
                CREATE TABLE IF NOT EXISTS chunk_embeddings (
                id TEXT PRIMARY KEY,
                chunk_id TEXT NOT NULL,
                embedding TEXT NOT NULL,
                model_name TEXT NOT NULL,
                dimensions INTEGER NOT NULL,
                FOREIGN KEY (chunk_id) REFERENCES chunks (id)
                )
            """
        )