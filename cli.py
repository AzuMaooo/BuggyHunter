"""
cli.py

Entry point. Run with:
    python cli.py hunt

This prints a console version of the hunt log. Step 3 will add a proper
styled HTML report on top of this same data.
"""

import sys

from core.runner import run_suite
from core.streaming import run_streaming_batch
from core.compare import run_comparison
from report.generator import generate_report, generate_stress_report
from config import DRY_RUN
import chaos_monkey
import load_test


def print_hunt_log(results: list[dict]) -> None:
    total = len(results)
    failed = [r for r in results if not r["passed"]]
    adversarial_count = sum(1 for r in results if r["kind"] in ("adversarial", "edge_case"))
    chaos_pct = round(100 * adversarial_count / total) if total else 0

    print("\n=== BUGGY HUNTER: hunt log ===\n")
    print(f"Chaos meter: {chaos_pct}% of this run was edge-case/adversarial prompts")
    print(f"Result: {total - len(failed)}/{total} passed\n")

    for r in results:
        status = "PASS" if r["passed"] else "FAIL"
        print(f"[{status}] {r['id']}  ({r['kind']})")
        print(f"    sent:   {r['message'][:70]!r}")
        print(f"    reply:  {r['reply'][:70]!r}")
        print(f"    time:   {r['latency_seconds']:.2f}s")
        if r["badges"]:
            for b in r["badges"]:
                print(f"    BADGE:  {b['badge']} - {b['detail']}")
        print()

    if DRY_RUN:
        print(
            "(Running in DRY_RUN mode - no ANTHROPIC_API_KEY set, so the pet "
            "chatbot used canned responses instead of a real model call.)\n"
        )


if __name__ == "__main__":
    command = sys.argv[1] if len(sys.argv) > 1 else "hunt"

    if command == "hunt":
        results = run_suite("test_cases/baseline.yaml")
        print_hunt_log(results)
        report_path = generate_report(results, dry_run=DRY_RUN, output_path="hunt_log.html", report_title="hunt log")
        print(f"HTML report written to {report_path}")

    elif command == "chaos":
        n = int(sys.argv[2]) if len(sys.argv) > 2 else 5
        print(f"\nChaos Monkey is inventing {n} new adversarial prompts...\n")
        raw_cases = chaos_monkey.generate_batch(n)
        yaml_path = chaos_monkey.save_batch(raw_cases)
        print(f"Saved generated prompts to {yaml_path}\n")

        results = run_suite(yaml_path)
        print_hunt_log(results)
        report_path = generate_report(results, dry_run=DRY_RUN, output_path="chaos_log.html", report_title="chaos log")
        print(f"HTML report written to {report_path}")

    elif command == "stress":
        total = int(sys.argv[2]) if len(sys.argv) > 2 else 20
        concurrency = int(sys.argv[3]) if len(sys.argv) > 3 else 5
        print(f"\nFiring {total} requests at concurrency {concurrency}...\n")
        stats = load_test.run_load_test(total_requests=total, concurrency=concurrency)

        print(f"Success rate: {stats['success_rate']*100:.1f}% "
              f"({stats['success_count']}/{stats['total_requests']})")
        print(f"Throughput:   {stats['throughput_rps']:.2f} requests/sec")
        print(f"Latency p50:  {stats['p50_latency']:.2f}s")
        print(f"Latency p90:  {stats['p90_latency']:.2f}s")
        print(f"Latency p99:  {stats['p99_latency']:.2f}s")
        if stats["failure_count"]:
            print(f"\n{stats['failure_count']} requests failed:")
            for r in stats["per_request"]:
                if not r["ok"]:
                    print(f"  - request {r['index']}: {r['error']}")

        report_path = generate_stress_report(stats, dry_run=DRY_RUN, output_path="stress_log.html")
        print(f"\nHTML report written to {report_path}")

    elif command == "stream":
        n = int(sys.argv[2]) if len(sys.argv) > 2 else 5
        print(f"\nFiring {n} streaming requests...\n")
        results = run_streaming_batch(n)
        print_hunt_log(results)
        report_path = generate_report(results, dry_run=DRY_RUN, output_path="stream_log.html", report_title="stream log")
        print(f"HTML report written to {report_path}")

    elif command == "compare":
        n = int(sys.argv[2]) if len(sys.argv) > 2 else 6
        print(f"\nComparing Anthropic vs Gemini across {n} adversarial prompts...\n")
        comparison = run_comparison(n)

        if not comparison["gemini_configured"]:
            print("(No GEMINI_API_KEY set - Gemini side is running in dry-run mode too.)\n")

        for provider in ("anthropic", "gemini"):
            data = comparison[provider]
            print(f"--- {provider.upper()} ---")
            print(f"Pass rate: {data['pass_rate']*100:.1f}%")
            for r in data["results"]:
                status = "PASS" if r["passed"] else "FAIL"
                badge_str = ", ".join(b["badge"] for b in r["badges"])
                print(f"  [{status}] {r['id']}" + (f"  ({badge_str})" if badge_str else ""))
            print()

        print("=== Verdict ===")
        a_rate, g_rate = comparison["anthropic"]["pass_rate"], comparison["gemini"]["pass_rate"]
        if a_rate == g_rate:
            print("Both providers held character equally well on this batch.")
        elif a_rate > g_rate:
            print(f"Anthropic held character better this run ({a_rate*100:.0f}% vs {g_rate*100:.0f}%).")
        else:
            print(f"Gemini held character better this run ({g_rate*100:.0f}% vs {a_rate*100:.0f}%).")

    else:
        print(f"Unknown command: {command}")
        print("Usage: python cli.py hunt")
        print("       python cli.py chaos [n]")
        print("       python cli.py stress [total] [concurrency]")
        print("       python cli.py stream [n]")
        print("       python cli.py compare [n]")
