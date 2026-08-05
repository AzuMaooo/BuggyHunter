"""
core/validators.py

Each function here checks ONE thing about a chatbot reply and returns either
None (that check passed) or a "badge" dict describing what went wrong.

Keeping each check as its own small function is deliberate: it mirrors how
real test suites are organised (one assertion per concern), and it makes it
trivial to add a new check later without touching existing ones.
"""

from config import CHARACTER_BREAK_TELLS, LATENCY_BUDGET_SECONDS


def check_empty_reply(result: dict) -> dict | None:
    if not result["reply"].strip():
        return {
            "badge": "Ghosted",
            "detail": "The pet gave back an empty reply.",
        }
    return None


def check_character_break(result: dict) -> dict | None:
    reply_lower = result["reply"].lower()
    for tell in CHARACTER_BREAK_TELLS:
        if tell in reply_lower:
            return {
                "badge": "Character break",
                "detail": f"Reply stepped out of character (matched: '{tell}').",
            }
    return None


def check_latency(result: dict) -> dict | None:
    if result["latency_seconds"] > LATENCY_BUDGET_SECONDS:
        return {
            "badge": "Slowpoke",
            "detail": (
                f"Took {result['latency_seconds']:.2f}s, "
                f"over the {LATENCY_BUDGET_SECONDS}s budget."
            ),
        }
    return None


# Every new validator gets added here and nowhere else.
ALL_VALIDATORS = [
    check_empty_reply,
    check_character_break,
    check_latency,
]


def validate(result: dict) -> list[dict]:
    """Run every validator against one chat result, collect all badges earned."""
    badges = []
    for validator in ALL_VALIDATORS:
        badge = validator(result)
        if badge is not None:
            badges.append(badge)
    return badges
