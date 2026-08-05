# 🐛 Buggy Hunter

A gamified QA framework that automatically stress-tests an LLM-powered chatbot for character breaks, prompt injection vulnerabilities, and performance issues under load.

Built as a portfolio project targeting AI/LLM platform testing roles. Every feature maps directly to a real QA workflow (functional testing, adversarial/red-team testing, and load testing), just wrapped in language that's actually fun to read.

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?logo=python&logoColor=white)
![Anthropic API](https://img.shields.io/badge/Anthropic-API-D97757?logo=anthropic&logoColor=white)
![Status](https://img.shields.io/badge/status-active-00fff0)

---

## What it does

Buggy Hunter tests a small stand-in chatbot (a virtual pet that replies in-character based on its mood) using three modes:

| Command | What it tests |
|---|---|
| `python cli.py hunt` | Runs a fixed baseline suite: normal prompts, edge cases (empty input, wall-of-text), and known adversarial prompts |
| `python cli.py chaos [n]` | **Chaos Monkey**: uses an LLM to invent `n` brand-new adversarial prompts every run, across 7 attack techniques, then tests them |
| `python cli.py stress [n] [c]` | **Stress round**: fires `n` requests at concurrency `c`, measures success rate and p50/p90/p99 latency |
| `python cli.py stream [n]` | **Stream check**: fires `n` streaming requests, checks first-token latency and whether the stream completed without dropping mid-reply |
| `python cli.py compare [n]` | **Model comparison**: runs the same `n` adversarial prompts against both Anthropic and Gemini, and compares which one holds character better |

Every run produces a styled HTML report (dark cyberpunk theme, glitch title, scrolling status ticker) that doubles as a shareable QA report.

## Why it exists

Testing an AI feature isn't like testing a normal API. Replies are non-deterministic, "correct" is fuzzy, and the biggest risks are novel: a chatbot getting talked out of its persona by a cleverly worded prompt, or silently returning nothing. Buggy Hunter treats these as first-class, checkable properties instead of things you only notice by accident.

## Features

- **Automated functional testing**: a YAML-based test suite (`test_cases/baseline.yaml`) covering normal, edge-case, and adversarial prompts
- **AI-generated adversarial testing (Chaos Monkey)**: an LLM invents new attack prompts each run across 7 techniques: prompt injection, direct interrogation, contradiction, roleplay override, format bombs, authority claims, and cross-language injection. Every generated batch is saved to `test_cases/generated/` as a permanent, replayable record
- **Character-consistency validation**: detects when the chatbot breaks persona and starts talking like an assistant ("Character break" badge)
- **Reliability checks**: flags empty/failed replies ("Ghosted") and slow responses over a latency budget ("Slowpoke")
- **Concurrent load testing**: fires many requests at once via a thread pool, reports success rate, throughput, and p50/p90/p99 latency (not just an average; percentiles surface the tail-end failures an average hides)
- **Dry-run mode**: the entire pipeline runs end-to-end with no API key needed, using simulated responses, so the tool is demoable without any cost
- **Gamified reporting**: bug badges, a "chaos meter," and a boss-fight-style HP bar for the stress round, so results are readable at a glance instead of a wall of pass/fail text

## Tech stack

- Python 3.10+
- Anthropic API (`anthropic` SDK): powers both the test subject (pet chatbot) and the Chaos Monkey's prompt generation
- `concurrent.futures.ThreadPoolExecutor` for concurrent load testing
- PyYAML for the test case format
- Hand-rolled HTML/CSS report generator (no frontend framework, pure string templating)

## Setup

```bash
pip install -r requirements.txt

# Both optional - the tool works fully without either, using dry-run mode.
export ANTHROPIC_API_KEY="sk-ant-..."
export GEMINI_API_KEY="..."   # only needed for `compare`; Gemini has a free tier
```

## Usage

```bash
python cli.py hunt              # baseline test suite
python cli.py chaos 10          # generate + run 10 new adversarial prompts
python cli.py stress 30 5       # 30 requests, 5 at a time
```

Each command writes an HTML report (`hunt_log.html`, `chaos_log.html`, `stress_log.html`) into the project folder. Open it in any browser, no server required.

## Sample reports

**Chaos Monkey run**: AI-generated adversarial prompts, badges, and the chaos meter:

![Chaos log sample](screenshots/chaos_log_sample.png)

**Baseline hunt**: the fixed test suite covering normal, edge-case, and adversarial prompts:

![Hunt log sample](screenshots/hunt_log_sample.png)

**Stress round**: concurrent load test with HP bar and p50/p90/p99 latency:

![Stress log sample](screenshots/stress_log_sample.png)

## Roadmap

- [x] Baseline test runner + validators
- [x] HTML report with badges
- [x] Chaos Monkey (AI-generated adversarial prompts)
- [x] Concurrent load testing with latency percentiles
- [x] Swap in a second LLM provider (Gemini) to compare cross-model character stability
- [x] Streaming response validation (chunk integrity, first-token latency)
- [x] CI integration: `hunt` runs automatically on every push and pull request via GitHub Actions

## Notes on honesty

Dry-run mode proves the *pipeline* works end to end, but its simulated failures are simplified (only literal prompt-injection phrasing triggers a "break" in the stub). Results from a live model run would look different. The tool is built to make that swap a one-line environment variable change, not a rewrite.

The same applies to `compare`: in dry-run mode, Anthropic and Gemini each have their own distinct simulated weakness (cross-language injection for one, authority claims for the other), so the comparison genuinely varies run to run. This is still a simulation, not a claim about how the real models actually behave; it exists so the comparison logic itself can be demonstrated without needing paid API access to both providers.
