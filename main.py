from app.agent import Agent
from dotenv import load_dotenv

load_dotenv()

agent = Agent()
agent.run("Solve Advent of Code 2020 Day 1 Part B")
