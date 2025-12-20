# WQ Research Agent

A research-oriented agent framework for quantitative alpha analysis, built on top of OpenAI function calling and a Postgres-backed data layer.

This project focuses on **deterministic, tool-driven research workflows**, rather than free-form LLM chat.

---

## 🚀 Overview

This agent is designed to:

- Query and analyze quantitative alpha data stored in Postgres
- Use LLMs **only for decision-making and tool selection**
- Enforce strict tool usage rules to avoid ambiguous or unsafe calls
- Support scalable research workflows (list → inspect → simulate → evaluate)

Core philosophy:

> **LLM decides *what* to do, code decides *how* to do it.**

---

## 🧠 Architecture

├── run_agent.py          # Agent main loop (LLM + tool dispatch)
├── agent_prompt.py       # Base agent / system prompt
├── RESEARCH_PROMPT.py    # Strict research prompt template
├── registry.py           # Tool registry & schemas
├── db.py                 # Postgres connection & query helpers
├── tools/                # Concrete research tools
│   ├── get_alpha_detail.py
│   ├── get_backtest_metrics.py
│   ├── list_alphas.py
│   ├── resolve_cutoff.py
│   └── simulate_alpha.py


### Separation of responsibilities

- **Prompt layer**
  - Defines strict rules for tool usage
  - Prevents hallucinated or partial tool calls

- **Tool layer**
  - Each tool corresponds to a concrete, deterministic action
  - Backed by SQL queries or simulation logic

- **Agent loop**
  - Parses LLM output
  - Validates / patches tool arguments
  - Executes tools and feeds results back

---

## 🛠️ Tools (Current)

| Tool | Description |
|-----|------------|
| `list_alphas` | List available alpha IDs |
| `get_alpha_detail` | Fetch alpha expression & metadata |
| `get_backtest_metrics` | Retrieve performance metrics (Sharpe, etc.) |
| `simulate_alpha` | Run alpha simulation |
| `resolve_cutoff` | Resolve backtest cutoffs / constraints |

> All tools are registered centrally in `registry.py`.

---

## 🧪 Prompt Design

The agent uses a **strict research prompt** that enforces:

- No tool calls with missing parameters
- No empty `{}` arguments
- No fabricated values
- Mandatory clarification if required inputs are missing

This avoids a common failure mode of LLM-based agents:  
*calling the right tool with the wrong (or empty) arguments*.

---

## 🗄️ Database

- Backend: **Postgres**
- Connection configured via environment variables:

```bash
export PG_HOST=localhost
export PG_DB=wq
export PG_USER=postgres
export PG_PASSWORD=postgres

All database access is centralized in db.py.

▶️ Running the Agent

Activate your virtual environment, then:

python run_agent.py

Example user query handled by the agent:
Show me details of alpha A123

The agent will:
	1.	Decide which tool to use
	2.	Validate arguments
	3.	Query Postgres
	4.	Return structured results


⚠️ Design Notes
	•	This is not a chat-bot
	•	This is not a LangChain-style autonomous agent
	•	Determinism and reproducibility are prioritized over autonomy
	•	Fallback logic exists at the code level to guarantee correctness

🔮 Roadmap

Planned extensions:
	•	Research-oriented tools (ranking, filtering, top-k selection)
	•	Tool planning (multi-step research flows)
	•	Alpha comparison and decision support
	•	Batch research and evaluation pipelines

