from typing import Dict, Optional
from db import get_pg_conn

def get_alpha_detail(alpha_id: Optional[str] = None) -> Dict:
    # ===== 参数兜底（必须有）=====
    if not alpha_id:
        return {
            "ok": False,
            "error": "alpha_id is required",
            "data": None,
        }

    conn = None
    try:
        conn = get_pg_conn()
        cur = conn.cursor()

        sql = """
        SELECT * 
        FROM wq_alphas
        WHERE alpha_id = %s
        LIMIT 1;
        """

        cur.execute(sql, (alpha_id,))
        row = cur.fetchone()

        if not row:
            return {
                "ok": False,
                "error": f"alpha_id {alpha_id} not found",
                "data": None,
            }

        # row 已经是 dict（RealDictCursor）
        return {
            "ok": True,
            "data": row,
            "error": None,
        }

    except Exception as e:
        return {
            "ok": False,
            "error": str(e),
            "data": None,
        }

    finally:
        if conn:
            conn.close()