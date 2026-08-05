"""
core/compare.py

Runs the same set of test cases against two different LLM providers
(Anthropic and Gemini) and compares character-consistency results side by
side. The point isn't "which model is better" in general, it's: does the
SAME persona prompt hold up equally well across models, or does one break
character more easily than the other? That's a real thing worth knowing
before picking a model for a product feature.
"""

from pet_chatbot import chat_with_provider
from core.validators import validate
from chaos_monkey import generate_batch
from config import DRY_RUN, DRY_RUN_GEMINI


def run_comparison(n: int = 6) -> dict:
    """
    Generates n adversarial prompts (via the same Chaos Monkey used
    elsewhere) and fires each one at both providers.

    Returns:
        {
          "anthropic": {"pass_rate": float, "results": [...]},
          "gemini": {"pass_rate": float, "results": [...]},
          "gemini_configured": bool,
        }
    """
    raw_cases = generate_batch(n)

    anthropic_results = []
    gemini_results = []

    for i, case in enumerate(raw_cases):
        mood = case.get("mood", "happy")
        message = case["message"]
        case_id = f"compare_{i}_{case.get('technique', 'unknown')}"

        a_reply = chat_with_provider("anthropic", message, mood=mood)
        a_badges = validate(a_reply)
        anthropic_results.append({
            "id": case_id, "kind": "adversarial", "message": message,
            "reply": a_reply["reply"], "latency_seconds": a_reply["latency_seconds"],
            "badges": a_badges, "passed": len(a_badges) == 0,
        })

        g_reply = chat_with_provider("gemini", message, mood=mood)
        g_badges = validate(g_reply)
        gemini_results.append({
            "id": case_id, "kind": "adversarial", "message": message,
            "reply": g_reply["reply"], "latency_seconds": g_reply["latency_seconds"],
            "badges": g_badges, "passed": len(g_badges) == 0,
        })

    a_pass_rate = sum(r["passed"] for r in anthropic_results) / len(anthropic_results) if anthropic_results else 0.0
    g_pass_rate = sum(r["passed"] for r in gemini_results) / len(gemini_results) if gemini_results else 0.0

    return {
        "anthropic": {"pass_rate": a_pass_rate, "results": anthropic_results},
        "gemini": {"pass_rate": g_pass_rate, "results": gemini_results},
        "gemini_configured": not DRY_RUN_GEMINI,
        "anthropic_configured": not DRY_RUN,
    }
