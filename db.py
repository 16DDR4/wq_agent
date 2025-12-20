import psycopg2
from psycopg2.extras import RealDictCursor
import os

def get_pg_conn():
    return psycopg2.connect(
        host=os.getenv("PG_HOST", "localhost"),
        port=os.getenv("PG_PORT", 5432),
        dbname=os.getenv("PG_DB", "wq"),
        user=os.getenv("PG_USER", "postgres"),
        password=os.getenv("PG_PASSWORD", "postgres"),
        cursor_factory=RealDictCursor,
    )