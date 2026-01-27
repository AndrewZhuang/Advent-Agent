from aocd import get_data, get_puzzle, submit, examples
import subprocess
import tempfile
import textwrap
from pathlib import Path
from typing import Optional
import requests
from app.utils import strip_tags

def get_puzzle_description(day: int, year: int = 2024, part: str='a') -> str:
    """
    Fetch the Advent of Code puzzle description for a given day.
    """
    puzzle = get_puzzle(day=day, year=year)
    page = examples.Page.from_raw(html=puzzle._get_prose(force_precheck=True))
    print(strip_tags(page.a_raw) if part == 'a' else strip_tags(page.b_raw))
    return strip_tags(page.a_raw) if part == 'a' else strip_tags(page.b_raw)


get_puzzle_description.schema = {
    "type": "object",
    "properties": {
        "day": {"type": "integer"},
        "year": {"type": "integer"},
        "part": {"type": "string", "enum": ["a", "b"]},
    },
    "required": ["day"],
}


def get_puzzle_input(day: int, year: int = 2024) -> str:
    """
    Fetch your personal Advent of Code input for a given day.
    """
    return get_data(day=day, year=year).strip()


get_puzzle_input.schema = {
    "type": "object",
    "properties": {
        "day": {"type": "integer"},
        "year": {"type": "integer"},
    },
    "required": ["day"],
}


def submit_answer(
    day: int,
    part: str,
    answer: str,
    year: int = 2024,
    confirm: bool = False,
) -> str:
    """
    Submit an Advent of Code answer.
    confirm must be True to allow submission.
    """
    if not confirm:
        return (
            "Submission blocked. "
            "Set confirm=True after validating the answer locally."
        )

    result = submit(
        answer=answer,
        part=part,
        day=day,
        year=year,
    )

    return str(result)


submit_answer.schema = {
    "type": "object",
    "properties": {
        "day": {"type": "integer"},
        "part": {"type": "string", "enum": ["a", "b"]},
        "answer": {"type": "string"},
        "year": {"type": "integer"},
        "confirm": {"type": "boolean"},
    },
    "required": ["day", "part", "answer"],
}


def run_python(code: str) -> str:
    """
    Execute Python code and return stdout or error output.
    Use this to test solution logic.
    """
    code = textwrap.dedent(code)

    with tempfile.NamedTemporaryFile(
        suffix=".py", mode="w", delete=False
    ) as f:
        f.write(code)
        path = f.name

    try:
        result = subprocess.run(
            ["python", path],
            capture_output=True,
            text=True,
            timeout=5,
        )
    except subprocess.TimeoutExpired:
        return "Error: Code execution timed out."

    if result.returncode != 0:
        return f"Error:\n{result.stderr}"

    return result.stdout.strip()


run_python.schema = {
    "type": "object",
    "properties": {
        "code": {"type": "string"},
    },
    "required": ["code"],
}


TOOL_REGISTRY = {
    "get_puzzle_description": get_puzzle_description,
    "get_puzzle_input": get_puzzle_input,
    "submit_answer": submit_answer,
    "run_python": run_python
}
