import os
import psycopg2
from psycopg2 import sql

def get_db_connection():
    """
    Establishes and returns a connection to the PostgreSQL database
    using the DATABASE_URL environment variable.
    """
    db_url = os.environ.get("DATABASE_URL")
    if not db_url:
        raise ValueError("DATABASE_URL environment variable is not set.")
    
    conn = psycopg2.connect(db_url)
    return conn

def init_db():
    """
    Initializes the database by creating the required generic schema
    if it does not already exist.
    """
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            # Create a generic urls table
            cur.execute("""
                CREATE TABLE IF NOT EXISTS urls (
                    id SERIAL PRIMARY KEY,
                    original_url TEXT NOT NULL,
                    short_code VARCHAR(255) UNIQUE NOT NULL,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                );
            """)
        conn.commit()
    finally:
        conn.close()

def save_url_mapping(original_url: str, short_code: str):
    """
    Saves the original URL and its corresponding short code into the database.
    """
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO urls (original_url, short_code) VALUES (%s, %s)",
                (original_url, short_code)
            )
        conn.commit()
    except psycopg2.IntegrityError:
        # Re-raise if there's a unique violation or other integrity issue
        conn.rollback()
        raise
    finally:
        conn.close()
