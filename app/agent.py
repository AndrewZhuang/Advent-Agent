from typing import Dict, Any, List

from app.llm.client import LLMClient
from app.prompts import SYSTEM_PROMPT
from app.tools import TOOL_REGISTRY
from app.config import MAX_STEPS


class Agent:
    def __init__(self):
        self.llm = LLMClient()
        self.memory: List[Dict[str, Any]] = []

    def run(self, goal: str) -> str:
        """
        Run the agent loop until the goal is complete or limits are hit.
        """
        self.memory = []
        messages = self._init_messages(goal)

        for step in range(MAX_STEPS):
            response = self.llm.complete(
                messages=messages,
                tools=self._tool_schemas(),
            )

            # 1. Tool call
            if response["type"] == "tool_call":
                print(f"Step {step}: Calling tool {response['tool']} with args {response['arguments']}")
                tool_name = response["tool"]
                tool_args = response["arguments"]

                if tool_name not in TOOL_REGISTRY:
                    raise ValueError(f"Unknown tool: {tool_name}")

                tool_fn = TOOL_REGISTRY[tool_name]
                observation = tool_fn(**tool_args)

                self.memory.append({
                    "step": step,
                    "tool": tool_name,
                    "input": tool_args,
                    "observation": observation,
                })

                messages.append({
                    "role": "assistant",
                    "content": response["raw"],
                })

                messages.append({
                    "role": "assistant",
                    "tool_calls": [
                        {
                            "id": f"call_{step}",
                            "type": "function",
                            "function": {
                                "name": tool_name,
                                "arguments": str(tool_args)
                            }
                        }
                    ]
                })

                messages.append({
                    "role": "tool",
                    "tool_name": tool_name,
                    "tool_call_id": f"call_{step}",
                    "content": observation,
                })

            # 2. Final answer
            elif response["type"] == "final":
                print(f"Step {step}: Final answer received: {response['content']}")
                return response["content"]

            # 3. Plain reasoning (optional)
            else:
                print(f"Step {step}: Assistant message {response['content']}")
                messages.append({
                    "role": "assistant",
                    "content": response["content"],
                })

        return "Stopped: max steps reached."


    def _init_messages(self, goal: str) -> List[Dict[str, str]]:
        return [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Goal: {goal}"},
        ]


    def _tool_schemas(self) -> List[Dict[str, Any]]:
        """
        Convert registered tools into model-readable schemas.
        """
        schemas = []
        for name, tool in TOOL_REGISTRY.items():
            schemas.append({
                "type": "function",
                "function": {
                    "name": name,
                    "description": tool.__doc__ or "",
                    "parameters": tool.schema,
                }
            })
        return schemas
