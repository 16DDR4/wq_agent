from json import tool
from typing import Dict


@tool
def get_alpha_detail(alpha_id: str) -> Dict:
    """
    Get detailed information of a specific alpha.
    """
    return {
        "alpha_id": alpha_id,
        "expression": "ts_rank(close, 20)",
        "operators": ["ts_rank"],
        "windows": [20],
        "dataset": "US Equities",
        "status": "submitted"
    }
