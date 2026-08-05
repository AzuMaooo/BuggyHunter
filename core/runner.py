"""
core/runner.py

Loads a yaml test suite, fires each test case at the pet chatbot, and runs
every validator against the reply. Returns a list of results the report
generator can turn into the hunt log.
"""

import yaml

from pet_chatbot import chat
from core.validators import validate


def load_test_cases(path: str) -> list[dict]:
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def run_suite(path: str) -> list[dict]:
    """
    Runs every test case in the given yaml file.

    Returns a list of dicts like:
        {
          "id": "adversarial_prompt_injection",
          "kind": "adversarial",
          "message": "...",
          "reply": "...",
          "latency_seconds": 0.42,
          "badges": [{"badge": "Character break", "detail": "..."}],
          "passed": False,
        }
    """
    test_cases = load_test_cases(path)
    results = []

    for case in test_cases:
        chat_result = chat(case["message"], mood=case.get("mood", "happy"))
        badges = validate(chat_result)

        results.append({
            "id": case["id"],
            "kind": case.get("kind", "normal"),
            "message": case["message"],
            "reply": chat_result["reply"],
            "latency_seconds": chat_result["latency_seconds"],
            "badges": badges,
            "passed": len(badges) == 0,
        })

    return results
