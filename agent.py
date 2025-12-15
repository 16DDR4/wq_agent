# agent.py

from langchain.agents import create_openai_functions_agent
from agent_prompt import WORLDQUANT_AGENT_PROMPT
from tools import *   # 你之前写的那些 @tool

from tools import get_alpha_detail
from tools.resolve_cutoff import resolve_cutoff
from tools.get_backtest_metrics import get_backtest_metrics
from tools.simulate_alpha import simulate_alpha


def evaluate_alpha(alpha_id: str):
    """
    最小闭环：
    输入 alpha_id → 输出 PASS / FAIL + reason
    """

    # 1. 拉 alpha 元信息（分类 / universe / theme）
    alpha_meta = get_alpha_detail(alpha_id)

    # 2. 拉回测指标
    metrics = get_backtest_metrics(alpha_id)

    # 3. 用 cutoff 规则做裁决
    decision = resolve_cutoff(
        alpha_meta=alpha_meta,
        metrics=metrics
    )

    return decision


agent = create_openai_functions_agent(
    llm=llm,
    tools=tools,
    prompt=WORLDQUANT_AGENT_PROMPT
)
