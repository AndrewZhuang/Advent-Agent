from typing import Dict, Any, List

from app.llm.client import LLMClient
from app.config import MAX_STEPS


class Agent:
    def __init__(self, system_prompt: str, tool_registry: Dict[str, Any]):
        self.llm = LLMClient()
        self.memory: List[Dict[str, Any]] = []
        self.tool_registry = tool_registry
        self.system_prompt = system_prompt

    def run(self, goal: str) -> str:
        """
        Run the agent loop until the goal is complete or limits are hit.
        """
        self.memory = []
        messages = self._init_messages(goal, self.system_prompt)

        for step in range(MAX_STEPS):
            print(f"--- Step {step} ---")
            response = self.llm.complete(
                messages=messages,
                tools=self._tool_schemas(self.tool_registry),
            )

            # 1. Tool call
            if response["type"] == "tool_call":
                print(f"Step {step}: Calling tool {response['tool']} with args {response['arguments']}")
                print(" ")
                tool_name = response["tool"]
                tool_args = response["arguments"]

                if tool_name not in self.tool_registry:
                    raise ValueError(f"Unknown tool: {tool_name}")

                tool_fn = self.tool_registry[tool_name]
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
    
    def _init_messages(self, goal: str, system_prompt: str) -> List[Dict[str, str]]:
        return [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Goal: {goal}"},
        ]

    def _tool_schemas(self, tool_registry: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Convert registered tools into model-readable schemas.
        """
        schemas = []
        for name, tool in tool_registry.items():
            schemas.append({
                "type": "function",
                "function": {
                    "name": name,
                    "description": tool.__doc__ or "",
                    "parameters": tool.schema,
                }
            })
        return schemas