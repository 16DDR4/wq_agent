# # agent.py
# from __future__ import annotations

# import os
# import importlib
# from typing import List, Any

# from dotenv import load_dotenv

# # LangChain core
# from langchain_core.tools import BaseTool
# from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
# from langchain_core.messages import SystemMessage

# # Agent runtime (tool-calling)
# from langchain.agents import AgentExecutor, create_tool_calling_agent


# def _load_prompt_text() -> str:
#     """
#     从 agent_prompt.py 读取系统提示词。
#     兼容变量名：SYSTEM_PROMPT / AGENT_PROMPT / PROMPT
#     """
#     mod = importlib.import_module("agent_prompt")
#     for name in ("SYSTEM_PROMPT", "AGENT_PROMPT", "PROMPT"):
#         if hasattr(mod, name):
#             return getattr(mod, name)
#     raise RuntimeError("agent_prompt.py 里找不到 SYSTEM_PROMPT / AGENT_PROMPT / PROMPT 任何一个变量")


# def _load_tools() -> List[BaseTool]:
#     """
#     从 tools/ 目录加载你现有工具：
#       - list_alphas
#       - get_alpha_detail
#       - get_backtest_metrics
#       - simulate_alpha
#       - resolve_cutoff   (关键：必须在！)
#     要求：tools/*.py 内导出同名对象（通常是 @tool 生成的 Tool 对象）。
#     """
#     tool_names = [
#         "list_alphas",
#         "get_alpha_detail",
#         "get_backtest_metrics",
#         "simulate_alpha",
#         "resolve_cutoff",
#     ]

#     loaded: List[BaseTool] = []

#     for name in tool_names:
#         m = importlib.import_module(f"tools.{name}")
#         if not hasattr(m, name):
#             raise RuntimeError(f"tools/{name}.py 里没有导出 `{name}`")
#         obj = getattr(m, name)

#         # LangChain 的 @tool 会返回一个 Tool/BaseTool；也允许你直接返回可调用函数
#         # 但为了稳定，这里优先要求是 BaseTool
#         if isinstance(obj, BaseTool):
#             loaded.append(obj)
#         else:
#             # 兼容：你如果导出的是函数，也能跑（LangChain会包装）
#             loaded.append(obj)  # type: ignore

#     # 额外兜底检查：resolve_cutoff 一定要存在
#     if not any(getattr(t, "name", None) == "resolve_cutoff" or getattr(t, "__name__", "") == "resolve_cutoff" for t in loaded):
#         raise RuntimeError("resolve_cutoff 没有被正确加载（这是决策闭环必需工具）")

#     return loaded


# def _build_llm():
#     """
#     你可以选 OpenAI / Anthropic
#     - MODEL_PROVIDER=openai   -> ChatOpenAI
#     - MODEL_PROVIDER=anthropic-> ChatAnthropic
#     默认 openai
#     """
#     provider = os.getenv("MODEL_PROVIDER", "openai").lower()
#     model = os.getenv("MODEL_NAME", "").strip()

#     if provider == "anthropic":
#         from langchain_anthropic import ChatAnthropic
#         if not model:
#             model = "claude-3-5-sonnet-latest"
#         return ChatAnthropic(model=model, temperature=float(os.getenv("TEMPERATURE", "0.2")))

#     # default: openai
#     from langchain_openai import ChatOpenAI
#     if not model:
#         model = "gpt-4o-mini"
#     return ChatOpenAI(model=model, temperature=float(os.getenv("TEMPERATURE", "0.2")))


# def build_agent_executor() -> AgentExecutor:
#     """
#     核心：把 prompt + tools + llm 组成一个可运行的 Agent。
#     """
#     tools = _load_tools()
#     llm = _build_llm()
#     system_prompt = _load_prompt_text()

#     prompt = ChatPromptTemplate.from_messages(
#         [
#             SystemMessage(content=system_prompt),
#             # 用户输入
#             ("human", "{input}"),
#             # 工具调用中间过程
#             MessagesPlaceholder(variable_name="agent_scratchpad"),
#         ]
#     )

#     agent = create_tool_calling_agent(llm=llm, tools=tools, prompt=prompt)

#     return AgentExecutor(
#         agent=agent,
#         tools=tools,
#         verbose=bool(int(os.getenv("VERBOSE", "1"))),
#         # 防止无限调用工具
#         max_iterations=int(os.getenv("MAX_ITERATIONS", "20")),
#         # 出错时也能返回中间信息，便于 debug
#         handle_parsing_errors=True,
#     )


# def run(user_input: str) -> str:
#     """
#     供 run_agent.py 调用，或者你直接在别的地方 import run().
#     """
#     executor = build_agent_executor()
#     out = executor.invoke({"input": user_input})
#     # out 通常包含 {"output": "...", ...}
#     return out.get("output", str(out))


# if __name__ == "__main__":
#     load_dotenv()
#     text = os.getenv("RUN_INPUT", "").strip()
#     if not text:
#         text = "目标：基于现有 alpha 列表，挑一个候选表达式做一次 simulate + metrics 拉取，并用 resolve_cutoff 判断是否可提交；如果不行，给出下一步改进建议。"
#     print(run(text))


# agent.py
import os
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain.agents import create_react_agent, AgentExecutor
from langchain.prompts import PromptTemplate

from tools import count_alphas

load_dotenv()

llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0
)

tools = [count_alphas]

prompt = PromptTemplate(
    input_variables=[
        "input",
        "agent_scratchpad",
        "tools",
        "tool_names",
    ],
    template="""
You are a quantitative research assistant.

You have access to the following tools:
{tools}

You may call these tools:
{tool_names}

Use the following format:

Question: {input}
Thought: you should think step by step
Action: the action to take, must be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
... (repeat if needed)
Thought: I now know the final answer
Final Answer: the answer to the user

Begin.

Question: {input}
{agent_scratchpad}
"""
)

agent = create_react_agent(
    llm=llm,
    tools=tools,
    prompt=prompt,
)

executor = AgentExecutor(
    agent=agent,
    tools=tools,
    verbose=True,
)

if __name__ == "__main__":
    print(executor.invoke({"input": "How many alphas do I have?"}))
