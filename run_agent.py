# run_agent.py

import json
from openai import OpenAI
from agent_prompt import RESEARCH_PROMPT
from registry import TOOLS, TOOL_REGISTRY


def main():
    client = OpenAI()

    resp = client.responses.create(
        model="gpt-4.1",
        input=RESEARCH_PROMPT,
        tools=TOOLS,
    )

    print("\n=== RAW RESPONSE OUTPUT ===")
    for o in resp.output:
        print(o)

    print("\n=== PARSED TOOL CALLS ===")

    tool_called = False

    for o in resp.output:
        # 注意：type 是 "function_call"
        if getattr(o, "type", None) == "function_call":
            tool_called = True

            tool_name = o.name
            args = json.loads(o.arguments or "{}")

            print(f">>> TOOL CALL: {tool_name}({args})")

            result = TOOL_REGISTRY[tool_name](**args)

            print(">>> TOOL RESULT:")
            print(result)

    if not tool_called:
        print("\n⚠️ No tool call detected.")


if __name__ == "__main__":
    main()