from json import tool
from typing import Dict


@tool
def get_backtest_metrics(alpha_id: str) -> Dict:
    """
    Get backtest performance metrics of an alpha.
    """
    return {
        "alpha_id": alpha_id,
        "sharpe": 1.42,
        "fitness": 1.08,
        "turnover": 0.32,
        "max_drawdown": -0.18,
        "margin": 0.05
    }
