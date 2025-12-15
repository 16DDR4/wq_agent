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

# ========== WQ API ==========
def list_alphas(wq: WQClient, limit: int = 500) -> List[Dict[str, Any]]:
    """
    拉取你的 alpha 列表（分页）。
    """
    out: List[Dict[str, Any]] = []
    offset = 0

    while True:
        url = f"{ALPHAS_URL}?limit={limit}&offset={offset}&order=-dateCreated"
        data = wq.get_json(url)

        # 这里按常见 REST 返回处理：可能是 list，也可能是 {"results": [...]}
        if isinstance(data, dict) and "results" in data:
            items = data["results"]
        else:
            items = data

        if not items:
            break

        for a in items:
            # 这里字段按你常见的 alpha 结构做容错映射
            out.append({
                "alpha_id": a.get("id") or a.get("alphaId") or a.get("alpha_id"),
                "expression": a.get("expression"),
                "universe": a.get("universe"),
                "region": a.get("region"),
                "delay": a.get("delay"),
                "neutralization": a.get("neutralization"),
                "created_at": a.get("dateCreated") or a.get("created_at"),
            })

        offset += len(items)
        # 可选：防止太快
        time.sleep(0.2)

    # 过滤掉没 id 的脏数据
    out = [x for x in out if x.get("alpha_id")]
    return out

def get_backtest_metrics(wq: WQClient, alpha_id: str) -> Dict[str, Any]:
    """
    你需要把这个 URL 改成你实际的 metrics endpoint。
    先给一个“你去替换”的模板，不再 NotImplemented。
    """
    # 常见形态示例（你自己确认）：
    # url = f"https://api.worldquantbrain.com/alphas/{alpha_id}/backtest"
    # 或 url = f"https://api.worldquantbrain.com/alphas/{alpha_id}"
    url = f"https://platform.worldquantbrain.com/alpha/{alpha_id}"

    data = wq.get_json(url)

    # TODO: 你把这里改成你实际看到的字段路径，比如 data["backtest"]["metrics"]
    # 先做一个尽量通用的兜底：如果存在 metrics 字段就取出来
    metrics = {}
    if isinstance(data, dict):
        if "metrics" in data and isinstance(data["metrics"], dict):
            metrics = data["metrics"]
        elif "backtest" in data and isinstance(data["backtest"], dict):
            bt = data["backtest"]
            if "metrics" in bt and isinstance(bt["metrics"], dict):
                metrics = bt["metrics"]

    # 只保留标量（数字）值
    cleaned: Dict[str, Any] = {}
    for k, v in metrics.items():
        if v is None:
            continue
        if isinstance(v, (int, float)):
            cleaned[k] = float(v)
    return cleaned

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
