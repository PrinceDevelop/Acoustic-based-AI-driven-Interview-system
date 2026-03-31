import os
import psycopg2
from psycopg2.extras import RealDictCursor
from urllib.parse import urlparse

# Use DATABASE_URL from Render environment, fallback to local SQLite-like behavior
DATABASE_URL = os.environ.get("DATABASE_URL", "")

def connect_db():
    """Connect to PostgreSQL database using DATABASE_URL."""
    if not DATABASE_URL:
        raise Exception("DATABASE_URL environment variable is not set!")
    
    # Render provides postgres:// but psycopg2 needs postgresql://
    db_url = DATABASE_URL
    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)
    
    conn = psycopg2.connect(db_url, cursor_factory=RealDictCursor)
    return conn

def create_table():
    """Create all required tables if they don't exist."""
    try:
        conn = connect_db()
        cur = conn.cursor()

        cur.execute("""
        CREATE TABLE IF NOT EXISTS users(
            id SERIAL PRIMARY KEY,
            username TEXT UNIQUE,
            email TEXT UNIQUE,
            password TEXT
        )
        """)

        # Interview result history — one row per interview session
        cur.execute("""
        CREATE TABLE IF NOT EXISTS interview_results(
            id SERIAL PRIMARY KEY,
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