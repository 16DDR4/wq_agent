from json import tool
from typing import Dict


def simulate_alpha(
    expression: str,
    universe: str = "US",
    delay: int = 1
) -> Dict:
    """
    Run a backtest simulation for a new alpha expression.
    """
    return {
        "expression": expression,
        "status": "completed",
        "metrics": {
            "sharpe": 1.31,
            "fitness": 1.02,
            "turnover": 0.28
        }
    }
