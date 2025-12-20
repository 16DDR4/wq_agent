# registry.py

from tools.get_alpha_detail import get_alpha_detail
from tools.get_backtest_metrics import get_backtest_metrics
from tools.list_alphas import list_alphas
from tools.resolve_cutoff import resolve_cutoff
from tools.simulate_alpha import simulate_alpha


def _wrap(fn_name, description, parameters):
    return {
        # 🔥 responses API 要求
        "name": fn_name,              # ← 必须有（外层）
        "type": "function",           # ← 必须有
        "function": {
            "name": fn_name,          # ← 也必须有
            "description": description,
            "parameters": parameters,
        },
    }


get_alpha_detail_schema = _wrap(
    "get_alpha_detail",
    "Get detailed information of a specific alpha by alpha_id.",
    {
        "type": "object",
        "properties": {
            "alpha_id": {"type": "string"},
        },
        "required": ["alpha_id"],
    },
)

get_backtest_metrics_schema = _wrap(
    "get_backtest_metrics",
    "Get backtest performance metrics of a specific alpha.",
    {
        "type": "object",
        "properties": {
            "alpha_id": {"type": "string"},
        },
        "required": ["alpha_id"],
    },
)

list_alphas_schema = _wrap(
    "list_alphas",
    "List available alphas with optional limit.",
    {
        "type": "object",
        "properties": {
            "limit": {"type": "integer"},
        },
    },
)

resolve_cutoff_schema = _wrap(
    "resolve_cutoff",
    "Resolve cutoff conditions for filtering alphas.",
    {
        "type": "object",
        "properties": {
            "metric": {"type": "string"},
            "threshold": {"type": "number"},
        },
        "required": ["metric", "threshold"],
    },
)

simulate_alpha_schema = _wrap(
    "simulate_alpha",
    "Run simulation for a given alpha.",
    {
        "type": "object",
        "properties": {
            "alpha_id": {"type": "string"},
        },
        "required": ["alpha_id"],
    },
)


TOOLS = [
    get_alpha_detail_schema,
    get_backtest_metrics_schema,
    list_alphas_schema,
    resolve_cutoff_schema,
    simulate_alpha_schema,
]

TOOL_REGISTRY = {
    "get_alpha_detail": get_alpha_detail,
    "get_backtest_metrics": get_backtest_metrics,
    "list_alphas": list_alphas,
    "resolve_cutoff": resolve_cutoff,
    "simulate_alpha": simulate_alpha,
}