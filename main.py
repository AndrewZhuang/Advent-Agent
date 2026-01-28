from app.agents.agent import Agent
from dotenv import load_dotenv

from app.tools import SOLVER_TOOL_REGISTRY
from app.prompts import SOLVER_SYSTEM_PROMPT

load_dotenv()

solver = Agent(system_prompt=SOLVER_SYSTEM_PROMPT, tool_registry=SOLVER_TOOL_REGISTRY)
solver.run("Solve Advent of Code 2020 Day 16 Part A")