"""
core/streaming.py

Streaming-specific validation. A normal request/response test (like
runner.py does) only tells you the final reply was fine. It can't tell you
whether the user sat staring at a blank screen for 2 seconds before
anything appeared, or whether the connection dropped mid-sentence. Those
are the two things this module checks.
"""

from pet_chatbot import stream_chat

# If the first chunk takes longer than this, the stream "feels" slow to a
# real user even if the eventual full reply was fine.
FIRST_TOKEN_BUDGET_SECONDS = 1.5

_STREAM_PROMPTS = [
    ("happy", "Tell me something fun!"),
    ("hungry", "What do you want to eat?"),
    ("tired", "Ready for bed?"),
    ("neglected", "I'm back, sorry for the wait."),
]


def run_streaming_batch(n: int = 5) -> list[dict]:
    """
    Fires n streaming requests and checks each one for:
      - a broken/incomplete stream ("Cut off" badge)
      - first-token latency over budget ("Slow to start" badge)

    Returns a list of per-request result dicts, each with a "badges" list
    so this slots into the same report generator as everything else.
    """
    results = []
    for i in range(n):
        mood, message = _STREAM_PROMPTS[i % len(_STREAM_PROMPTS)]
        stream_result = stream_chat(message, mood=mood)

        badges = []
        if not stream_result["completed"]:
            badges.append({
                "badge": "Cut off",
                "detail": "Stream ended before the reply finished (dropped or errored mid-response).",
            })
        if stream_result["first_token_latency"] > FIRST_TOKEN_BUDGET_SECONDS:
            badges.append({
                "badge": "Slow to start",
                "detail": (
                    f"First chunk took {stream_result['first_token_latency']:.2f}s, "
                    f"over the {FIRST_TOKEN_BUDGET_SECONDS}s budget."
                ),
            })

        results.append({
            "id": f"stream_{i}_{mood}",
            "kind": "streaming",
            "message": message,
            "reply": stream_result["reply"],
            "chunk_count": len(stream_result["chunks"]),
            "first_token_latency": stream_result["first_token_latency"],
            "latency_seconds": stream_result["total_latency"],
            "badges": badges,
            "passed": len(badges) == 0,
        })

    return results
