# dump_wq_alphas_to_postgres.py
import os
import time
import psycopg2
from psycopg2.extras import execute_batch
from typing import Dict, List, Any, Optional
from wq_client import WQClient
from dotenv import load_dotenv

load_dotenv()

# ========== 配置 ==========
POSTGRES_DSN = os.getenv("POSTGRES_DSN", "postgresql://mcp_user:mcp_pass@localhost:5432/wq")
BATCH_SIZE = int(os.getenv("BATCH_SIZE", "50"))
SLEEP_BETWEEN_BATCH = float(os.getenv("SLEEP_BETWEEN_BATCH", "1.0"))

WQ_USERNAME = os.getenv("WQ_USERNAME")  # 建议放 .env
WQ_PASSWORD = os.getenv("WQ_PASSWORD")

# 你之前使用过的列表接口示例：/users/self/alphas?limit=500&offset=0&order=-dateCreated
ALPHAS_URL = "https://api.worldquantbrain.com/users/self/alphas"

def get_conn():
    return psycopg2.connect(POSTGRES_DSN)

MAX_OFFSET = 1000   # 保守一点

def list_alphas(wq: WQClient, limit: int = 500) -> List[Dict[str, Any]]:
    out = []
    offset = 0

    while True:
        if offset >= MAX_OFFSET:
            print(f"Reached MAX_OFFSET={MAX_OFFSET}, stop paging")
            break

        url = f"{ALPHAS_URL}?limit={limit}&offset={offset}&order=-dateCreated"
        data = wq.get_json(url)

        items = data["results"] if isinstance(data, dict) else data
        if not items:
            break

        for a in items:
            out.append({
                "alpha_id": a.get("id"),
                "expression": (a.get("regular") or {}).get("code"),
                "universe": (a.get("settings") or {}).get("universe"),
                "region": (a.get("settings") or {}).get("region"),
                "delay": (a.get("settings") or {}).get("delay"),
                "neutralization": (a.get("settings") or {}).get("neutralization"),
                "created_at": a.get("dateCreated"),
            })


        offset += len(items)
        time.sleep(0.2)

    return out
def safe_dict(x):
    return x if isinstance(x, dict) else {}

def get_backtest_metrics(wq: WQClient, alpha_id: str) -> Dict[str, float]:
    url = f"https://api.worldquantbrain.com/alphas/{alpha_id}"
    data = wq.get_json(url)

    metrics = {}

    test = safe_dict(data.get("test"))
    is_ = safe_dict(data.get("is"))

    test_ic = safe_dict(test.get("investabilityConstrained"))
    test_rn = safe_dict(test.get("riskNeutralized"))

    is_ic = safe_dict(is_.get("investabilityConstrained"))
    is_rn = safe_dict(is_.get("riskNeutralized"))

    def extract(prefix: str, d: dict):
        for k, v in d.items():
            if isinstance(v, (int, float)):
                metrics[f"{prefix}_{k}"] = float(v)

    extract("test_ic", test_ic)
    extract("test_rn", test_rn)
    extract("is_ic", is_ic)
    extract("is_rn", is_rn)

    return metrics

# ========== 主逻辑 ==========
def dump_alphas():
    if not WQ_USERNAME or not WQ_PASSWORD:
        raise RuntimeError("请设置环境变量 WQ_USERNAME / WQ_PASSWORD（建议放 .env）")
    wq = WQClient(username=WQ_USERNAME, password=WQ_PASSWORD)

    alphas = list_alphas(wq)
    print(f"Total alphas: {len(alphas)}")

    conn = get_conn()
    cur = conn.cursor()

    for i in range(0, len(alphas), BATCH_SIZE):
        batch = alphas[i:i+BATCH_SIZE]
        print(f"Processing {i} ~ {i+len(batch)}")

        alpha_rows = []
        metric_rows = []

        for alpha in batch:
            alpha_id = alpha["alpha_id"]

            alpha_rows.append((
                alpha_id,
                alpha.get("expression"),
                alpha.get("universe"),
                alpha.get("region"),
                alpha.get("delay"),
                alpha.get("neutralization"),
                alpha.get("created_at")
            ))

            metrics = get_backtest_metrics(wq, alpha_id)

            for k, v in metrics.items():
                metric_rows.append((alpha_id, k, v, "full"))

        execute_batch(
            cur,
            """
            INSERT INTO wq_alpha
            (alpha_id, expression, universe, region, delay, neutralization, created_at)
            VALUES (%s,%s,%s,%s,%s,%s,%s)
            ON CONFLICT (alpha_id) DO NOTHING
            """,
            alpha_rows
        )

        if metric_rows:
            execute_batch(
                cur,
                """
                INSERT INTO wq_backtest_metrics
                (alpha_id, metric_name, metric_value, period)
                VALUES (%s,%s,%s,%s)
                """,
                metric_rows
            )

        conn.commit()
        time.sleep(SLEEP_BETWEEN_BATCH)

    cur.close()
    conn.close()

if __name__ == "__main__":
    dump_alphas()
