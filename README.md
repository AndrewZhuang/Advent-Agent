This is a fun side project to explore AI agents in the context of solving problems from the yearly Advent of Code event (which I have done a couple years of now). A lot of the code written is LLM-assisted as the intent is to focus more on the overall architecture and design considerations of the agent.

To run the agent, you will need both an Advent of Code session token and your OpenAI Api key.
To find your Advent of Code session token, login to adventofcode.com and look for session cookie (more details here https://github.com/wimglenn/advent-of-code-wim/issues/1). You will need to add it to an environment variable like the github issue link describes.
Add your api key to a .env file in the main directory under the name OPENAI_API_KEY.

To configure what problem to solve, modify the agent goal in main.py
