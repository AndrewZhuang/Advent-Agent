from app.agents.agent import Agent
from dotenv import load_dotenv
import os
import glob

from app.tools import SOLVER_TOOL_REGISTRY, get_puzzle_input
from app.prompts import SOLVER_SYSTEM_PROMPT

load_dotenv()

solver = Agent(system_prompt=SOLVER_SYSTEM_PROMPT, tool_registry=SOLVER_TOOL_REGISTRY)
solver.run("Solve Advent of Code 2020 Day 5 Part A")

# #cleaning up temp files
files = glob.glob('aoc_input_*.txt')
for f in files:
    os.remove(f)