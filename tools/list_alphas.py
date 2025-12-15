# tools_wq.py
import os
import time
from typing import List, Dict, Any, Optional

from dotenv import load_dotenv
from langchain.tools import tool

from wq_client import WQClient

load_dotenv()

_WQ: Optional[WQClient] = None

def _get_wq() -> WQClient:
    global _WQ
    if _WQ is not None:
        return _WQ

    username = os.getenv("WQ_USERNAME")
    password = os.getenv("WQ_PASSWORD")
    if not username or not password:
        raise RuntimeError("Missing WQ_USERNAME/WQ_PASSWORD in .env")

    _WQ = WQClient(username=username, password=password)
    return _WQ


@tool("list_alphas")
def list_alphas(limit: int = 100, max_pages: int = 5, sleep: float = 0.2) -> List[Dict[str, Any]]:
    """
    Pull alphas from WorldQuant BRAIN account via API.

    Args:
      limit: page size per request (typical 100-500)
      max_pages: safety cap to avoid infinite loops
      sleep: throttle between requests

    Returns:
      List of dicts with alpha_id, expression, dateCreated, region, universe, etc.
    """
    wq = _get_wq()
    base = os.getenv("WQ_API_BASE", "https://api.worldquantbrain.com").rstrip("/")
    out: List[Dict[str, Any]] = []

    offset = 0
    pages = 0
    while pages < max_pages:
        url = f"{base}/users/self/alphas?limit={limit}&offset={offset}&order=-dateCreated"
        data = wq.get_json(url)

        items = data.get("results", data) if isinstance(data, dict) else data
        if not items:
            break

        for a in items:
            out.append({
                "alpha_id": a.get("id") or a.get("alphaId") or a.get("alpha_id"),
                "expression": a.get("expression"),
                "region": a.get("region"),
                "universe": a.get("universe"),
                "delay": a.get("delay"),
                "neutralization": a.get("neutralization"),
                "dateCreated": a.get("dateCreated"),
            })

        offset += len(items)
        pages += 1
        time.sleep(sleep)

    # filter empties
    out = [x for x in out if x.get("alpha_id")]
    return out
