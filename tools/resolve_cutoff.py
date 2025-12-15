from typing import Dict, Any, List
from langchain.tools import tool

# resolve_cutoff.py

@tool
def resolve_cutoff(input: Dict[str, Any]) -> Dict[str, Any]:
    """
    Resolve WorldQuant cutoff rules based on alpha context and metrics.
    Returns structured evaluation: hard_fail / soft_fail / pass.
    """

    alpha_id = input["alpha_id"]
    ctx = input["alpha_context"]
    metrics = input["metrics"]
    policy = input["cutoff_policy"]

    results = {
        "alpha_id": alpha_id,
        "hard_fail": [],
        "soft_fail": [],
        "pass": []
    }

    # ---------- Fitness ----------
    if metrics["fitness"] < 1.0:
        results["hard_fail"].append({
            "metric": "fitness",
            "value": metrics["fitness"],
            "cutoff": 1.0
        })
    else:
        results["pass"].append("fitness")

    # ---------- Sharpe ----------
    sharpe_cutoff = 1.58 if ctx["region"] == "USA" else 1.2
    if metrics["sharpe"] < sharpe_cutoff:
        results["hard_fail"].append({
            "metric": "sharpe",
            "value": metrics["sharpe"],
            "cutoff": sharpe_cutoff
        })
    else:
        results["pass"].append("sharpe")

    # ---------- Turnover ----------
    turnover = metrics.get("turnover")
    if turnover is not None:
        if turnover < 0.01 or turnover > 0.70:
            results["soft_fail"].append({
                "metric": "turnover",
                "value": turnover,
                "range": [0.01, 0.70]
            })
        else:
            results["pass"].append("turnover")

    # ---------- Weight concentration ----------
    wc = metrics.get("weight_concentration")
    if wc is not None and wc > 0.10:
        results["soft_fail"].append({
            "metric": "weight_concentration",
            "value": wc,
            "cutoff": 0.10
        })

    # ---------- Sub-universe Sharpe ----------
    sub_sharpe = metrics.get("sub_universe_sharpe")
    if sub_sharpe is not None and sub_sharpe < 0.46:
        results["soft_fail"].append({
            "metric": "sub_universe_sharpe",
            "value": sub_sharpe,
            "cutoff": 0.46
        })

    # ---------- Ladder Sharpe ----------
    ladder = metrics.get("ladder_sharpe", {})
    for period, value in ladder.items():
        if value < 2.02:
            results["soft_fail"].append({
                "metric": f"ladder_sharpe_{period}",
                "value": value,
                "cutoff": 2.02
            })

    # ---------- Final decision ----------
    if results["hard_fail"]:
        results["final_decision"] = "REJECT"
    elif results["soft_fail"] and policy.get("allow_soft_fail"):
        results["final_decision"] = "REVIEW"
    else:
        results["final_decision"] = "PASS"

    return results

