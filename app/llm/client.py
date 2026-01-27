from typing import List, Dict, Any, Optional
import os

from openai import OpenAI


class LLMClient:
    """
    Thin wrapper around the OpenAI API for agent-style interactions.
    """

    def __init__(
        self,
        model: Optional[str] = None,
        temperature: float = 1,
    ):
        self.client = OpenAI()
        self.model = model or os.getenv("OPENAI_MODEL", "gpt-5-mini")
        self.temperature = temperature

    def complete(
        self,
        messages: List[Dict[str, Any]],
        tools: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """
        Send messages to the LLM.
        Returns a normalized response dict:
          - type: "tool_call" | "final" | "message"
        """

        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            tools=tools,
            tool_choice="auto" if tools else None,
            temperature=self.temperature,
        )

        msg = response.choices[0].message

        # -------------------------
        # Tool call
        # -------------------------
        if msg.tool_calls:
            tool_call = msg.tool_calls[0]

            return {
                "type": "tool_call",
                "tool": tool_call.function.name,
                "arguments": self._parse_args(tool_call.function.arguments),
                "raw": msg.content or "",
            }

        # -------------------------
        # Final answer detection
        # -------------------------
        if msg.content and msg.content.strip().startswith("FINAL"):
            return {
                "type": "final",
                "content": msg.content.replace("FINAL", "", 1).strip(),
            }

        # -------------------------
        # Normal assistant message
        # -------------------------
        return {
            "type": "message",
            "content": msg.content or "",
        }

    def _parse_args(self, arguments: Any) -> Dict[str, Any]:
        """
        Tool arguments may arrive as a JSON string.
        """
        if isinstance(arguments, dict):
            return arguments

        if isinstance(arguments, str):
            import json
            return json.loads(arguments)

        raise ValueError(f"Unexpected tool arguments: {arguments}")
