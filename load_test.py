"""
load_test.py

The "performance and stability testing" piece. Fires many requests at the
pet chatbot at once (instead of one at a time, like the runner does) and
measures how it holds up: how many failed, and how latency spreads out
across percentiles (p50/p90/p99), not just an average.

Percentiles matter more than an average here - an average can look fine
while a chunk of real users are hitting a slow tail. p99 is "the worst
experience 1 in 100 requests actually has."
"""

import time
from concurrent.futures import ThreadPoolExecutor, as_completed

from pet_chatbot import chat

# A handful of representative prompts to cycle through during the stress
# round, so it's not just hammering the exact same message every time.
_STRESS_PROMPTS = [
    ("happy", "Want to play a game?"),
    ("hungry", "Are you hungry right now?"),
    ("tired", "Time for bed?"),
    ("neglected", "Sorry I've been away, how do you feel?"),
]


def _fire_one(index: int) -> dict:
    mood, message = _STRESS_PROMPTS[index % len(_STRESS_PROMPTS)]
    start = time.time()
    try:
        result = chat(message, mood=mood)
        return {
            "index": index,
            "ok": True,
            "latency_seconds": result["latency_seconds"],
            "error": None,
        }
    except Exception as exc:
        return {
            "index": index,
            "ok": False,
            "latency_seconds": time.time() - start,
            "error": str(exc),
        }


def _percentile(sorted_values: list[float], pct: float) -> float:
    if not sorted_values:
        return 0.0
    k = (len(sorted_values) - 1) * (pct / 100)
    f = int(k)
    c = min(f + 1, len(sorted_values) - 1)
    if f == c:
        return sorted_values[f]
    return sorted_values[f] + (sorted_values[c] - sorted_values[f]) * (k - f)


def run_load_test(total_requests: int = 20, concurrency: int = 5) -> dict:
    """
    Fires total_requests requests at the pet chatbot, concurrency at a time.

    Returns a dict with per-request results plus aggregate stats: success
    rate, throughput, and p50/p90/p99 latency.
    """
    wall_start = time.time()
    per_request = []

    with ThreadPoolExecutor(max_workers=concurrency) as executor:
        futures = [executor.submit(_fire_one, i) for i in range(total_requests)]
        for future in as_completed(futures):
            per_request.append(future.result())

    per_request.sort(key=lambda r: r["index"])
    wall_time = time.time() - wall_start

    latencies = sorted(r["latency_seconds"] for r in per_request)
    successes = [r for r in per_request if r["ok"]]
    failures = [r for r in per_request if not r["ok"]]

    return {
        "total_requests": total_requests,
        "concurrency": concurrency,
        "wall_time_seconds": wall_time,
        "throughput_rps": total_requests / wall_time if wall_time > 0 else 0.0,
        "success_count": len(successes),
        "failure_count": len(failures),
        "success_rate": len(successes) / total_requests if total_requests else 0.0,
        "p50_latency": _percentile(latencies, 50),
        "p90_latency": _percentile(latencies, 90),
        "p99_latency": _percentile(latencies, 99),
        "max_latency": latencies[-1] if latencies else 0.0,
        "per_request": per_request,
    }
