import os
import psycopg2
from psycopg2.extras import RealDictCursor
from urllib.parse import urlparse

import sqlite3

# Use DATABASE_URL from Render environment, fallback to local SQLite
DATABASE_URL = os.environ.get("DATABASE_URL", "")
IS_PRODUCTION = bool(DATABASE_URL)

def connect_db():
    """Connect to PostgreSQL on Render, or SQLite locally."""
    if IS_PRODUCTION:
        # PostgreSQL Logic
        db_url = DATABASE_URL
        if db_url.startswith("postgres://"):
            db_url = db_url.replace("postgres://", "postgresql://", 1)
        return psycopg2.connect(db_url, cursor_factory=RealDictCursor)
    else:
        # SQLite Logic
        conn = sqlite3.connect("users.db")
        conn.row_factory = sqlite3.Row
        return conn

# Syntax Helper: SQLite uses ? while Postgres uses %s
Q = "%s" if IS_PRODUCTION else "?"

def create_table():
    """Create all required tables if they don't exist."""
    try:
        conn = connect_db()
        cur = conn.cursor()

        # Handle SERIAL (Postgres) vs AUTOINCREMENT (SQLite)
        id_type = "SERIAL" if IS_PRODUCTION else "INTEGER PRIMARY KEY AUTOINCREMENT"
        id_col = "id SERIAL PRIMARY KEY" if IS_PRODUCTION else "id INTEGER PRIMARY KEY AUTOINCREMENT"

        cur.execute(f"""
        CREATE TABLE IF NOT EXISTS users(
            {id_col},
            username TEXT UNIQUE,
            email TEXT UNIQUE,
            password TEXT
        )
        """)

        # Interview result history
        cur.execute(f"""
        CREATE TABLE IF NOT EXISTS interview_results(
            {id_col},
            username TEXT,
            job_role TEXT,
            score INTEGER,
            feedback TEXT,
            transcript TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)

        # Async job tracking table
        cur.execute("""
        CREATE TABLE IF NOT EXISTS processing_jobs(
            job_id TEXT PRIMARY KEY,
            status TEXT,
            result_json TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)

        conn.commit()
        conn.close()
        print("[DB] Tables created successfully!")
    except Exception as e:
        print(f"[DB] Error creating tables: {e}")