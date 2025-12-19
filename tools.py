# tools.py
from langchain.tools import tool
import psycopg2
import os

POSTGRES_DSN = os.getenv("POSTGRES_DSN")

@tool
def count_alphas() -> str:
    """Count total alphas in database."""
    conn = psycopg2.connect(POSTGRES_DSN)
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM wq_alpha;")
    n = cur.fetchone()[0]
    cur.close()
    conn.close()
    return f"Total alphas: {n}"
