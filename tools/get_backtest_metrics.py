from typing import Dict, Optional
import psycopg2
import psycopg2.extras


def get_backtest_metrics(
    alpha_id: str,
    conn
) -> Optional[Dict]:
    """
    Fetch backtest metrics for a single alpha from Postgres.

    This function:
    - Reads factual data only
    - Does NOT do any aggregation
    - Is NOT intended to be called by LLM
    """

    sql = """
        SELECT
            alpha_id,
            sharpe,
            fitness,
            turnover,
            max_drawdown,
            margin
        FROM alpha_backtest_results
        WHERE alpha_id = %s
        ORDER BY updated_at DESC
        LIMIT 1
    """

    with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
        cur.execute(sql, (alpha_id,))
        row = cur.fetchone()

    if row is None:
        return None

    return {
        "alpha_id": row["alpha_id"],
        "sharpe": float(row["sharpe"]),
        "fitness": float(row["fitness"]),
        "turnover": float(row["turnover"]),        # percentage
        "max_drawdown": float(row["max_drawdown"]),# percentage
        "margin": float(row["margin"])              # percentage
    }