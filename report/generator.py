"""
report/generator.py

Turns the list of results from core/runner.py into a single styled HTML
file: the "hunt log". This is the piece meant to be screenshotted for a
portfolio or resume.
"""

from datetime import datetime

_BADGE_COLORS = {
    "Ghosted": "#3a3d5c",
    "Character break": "#ff2e6d",
    "Slowpoke": "#ffb02e",
    "Cut off": "#a855f7",
    "Slow to start": "#facc15",
}

_PAGE_TEMPLATE = """<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>Buggy Hunter - {report_title}</title>
<style>
  @import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&family=Orbitron:wght@600;800&display=swap');

  body {{
    font-family: 'Share Tech Mono', monospace;
    background: #05050f;
    background-image:
      linear-gradient(rgba(0,255,225,0.04) 1px, transparent 1px),
      linear-gradient(90deg, rgba(0,255,225,0.04) 1px, transparent 1px);
    background-size: 24px 24px;
    color: #d8f7ff;
    max-width: 780px;
    margin: 40px auto;
    padding: 0 20px 60px;
  }}
  h1 {{
    font-family: 'Orbitron', sans-serif;
    font-size: 26px;
    font-weight: 800;
    letter-spacing: 0.06em;
    margin-bottom: 4px;
    color: #00fff0;
    text-shadow: 0 0 8px rgba(0,255,240,0.7), 0 0 20px rgba(0,255,240,0.35);
    position: relative;
    display: inline-block;
    animation: glitch-flicker 5s infinite steps(1);
  }}
  h1::before, h1::after {{
    content: attr(data-text);
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    overflow: hidden;
    background: #05050f;
    clip-path: inset(0 0 100% 0);
  }}
  h1::before {{
    left: 3px;
    color: #ff2e6d;
    text-shadow: -2px 0 #ff2e6d, 2px 0 #00fff0;
    animation: glitch-top 5s infinite steps(1);
  }}
  h1::after {{
    left: -3px;
    color: #00fff0;
    text-shadow: 2px 0 #00fff0, -2px 0 #ff2e6d;
    animation: glitch-bottom 5s infinite steps(1);
  }}
  /* Rest state: clean and readable, ~85% of the cycle.
     Two short glitch bursts happen around the 40% and 85% marks. */
  @keyframes glitch-flicker {{
    0%     {{ opacity: 1; }}
    40%    {{ opacity: 1; }}
    40.5%  {{ opacity: 0.3; }}
    41%    {{ opacity: 1; }}
    41.5%  {{ opacity: 0.2; }}
    42%    {{ opacity: 1; }}
    42.5%  {{ opacity: 0.4; }}
    43%    {{ opacity: 1; }}
    85%    {{ opacity: 1; }}
    85.5%  {{ opacity: 0.3; }}
    86%    {{ opacity: 1; }}
    86.5%  {{ opacity: 0.2; }}
    87%    {{ opacity: 1; }}
    100%   {{ opacity: 1; }}
  }}
  @keyframes glitch-top {{
    0%     {{ clip-path: inset(0 0 100% 0); }}
    40%    {{ clip-path: inset(0 0 100% 0); }}
    40.5%  {{ clip-path: inset(10% 0 70% 0); transform: translate(-6px, -2px) skewX(4deg); }}
    41%    {{ clip-path: inset(45% 0 30% 0); transform: translate(5px, 1px) skewX(-3deg); }}
    41.5%  {{ clip-path: inset(20% 0 60% 0); transform: translate(-5px, 2px) skewX(3deg); }}
    42%    {{ clip-path: inset(60% 0 10% 0); transform: translate(4px, -1px) skewX(-4deg); }}
    42.5%  {{ clip-path: inset(0 0 100% 0); transform: translate(0,0) skewX(0deg); }}
    85%    {{ clip-path: inset(0 0 100% 0); }}
    85.5%  {{ clip-path: inset(30% 0 45% 0); transform: translate(6px, 1px) skewX(-3deg); }}
    86%    {{ clip-path: inset(55% 0 15% 0); transform: translate(-4px, -1px) skewX(2deg); }}
    86.5%  {{ clip-path: inset(0 0 100% 0); transform: translate(0,0) skewX(0deg); }}
    100%   {{ clip-path: inset(0 0 100% 0); }}
  }}
  @keyframes glitch-bottom {{
    0%     {{ clip-path: inset(0 0 100% 0); }}
    40%    {{ clip-path: inset(0 0 100% 0); }}
    40.7%  {{ clip-path: inset(55% 0 15% 0); transform: translate(6px, 1px) skewX(-4deg); }}
    41.2%  {{ clip-path: inset(15% 0 65% 0); transform: translate(-5px, -1px) skewX(3deg); }}
    41.7%  {{ clip-path: inset(65% 0 8% 0); transform: translate(5px, 2px) skewX(-2deg); }}
    42.2%  {{ clip-path: inset(0 0 100% 0); transform: translate(0,0) skewX(0deg); }}
    85%    {{ clip-path: inset(0 0 100% 0); }}
    85.7%  {{ clip-path: inset(35% 0 40% 0); transform: translate(-6px, 1px) skewX(3deg); }}
    86.2%  {{ clip-path: inset(60% 0 10% 0); transform: translate(5px, -2px) skewX(-3deg); }}
    86.7%  {{ clip-path: inset(0 0 100% 0); transform: translate(0,0) skewX(0deg); }}
    100%   {{ clip-path: inset(0 0 100% 0); }}
  }}
  .ticker {{
    width: 100%;
    overflow: hidden;
    white-space: nowrap;
    border-top: 1px solid rgba(0,255,240,0.35);
    border-bottom: 1px solid rgba(0,255,240,0.35);
    box-shadow: 0 0 10px rgba(0,255,240,0.15);
    background: rgba(0,255,240,0.03);
    padding: 6px 0;
    margin-bottom: 26px;
  }}
  .ticker span {{
    display: inline-block;
    padding-left: 100%;
    font-size: 12px;
    color: #7de8ff;
    letter-spacing: 0.04em;
    animation: ticker-scroll 22s linear infinite;
  }}
  @keyframes ticker-scroll {{
    0%   {{ transform: translateX(0); }}
    100% {{ transform: translateX(-100%); }}
  }}
  .subtitle {{
    color: #ff2ea0;
    font-size: 12px;
    margin-bottom: 28px;
    text-transform: uppercase;
    letter-spacing: 0.08em;
  }}
  .summary {{
    display: flex;
    gap: 16px;
    margin-bottom: 30px;
  }}
  .stat {{
    background: linear-gradient(180deg, rgba(0,255,240,0.07), rgba(255,46,160,0.05));
    border: 1px solid rgba(0,255,240,0.4);
    box-shadow: 0 0 12px rgba(0,255,240,0.15), inset 0 0 20px rgba(0,255,240,0.04);
    border-radius: 4px;
    padding: 14px 18px;
    flex: 1;
  }}
  .stat .label {{
    font-size: 11px;
    color: #7de8ff;
    text-transform: uppercase;
    letter-spacing: 0.08em;
  }}
  .stat .value {{
    font-family: 'Orbitron', sans-serif;
    font-size: 26px;
    font-weight: 700;
    margin-top: 4px;
    color: #fffb00;
    text-shadow: 0 0 10px rgba(255,251,0,0.5);
  }}
  .case {{
    background: rgba(13,10,30,0.85);
    border: 1px solid rgba(0,255,240,0.18);
    border-radius: 4px;
    padding: 16px 18px;
    margin-bottom: 12px;
    position: relative;
  }}
  .case.fail {{
    border-color: rgba(255,46,109,0.7);
    box-shadow: 0 0 14px rgba(255,46,109,0.25), inset 3px 0 0 0 #ff2e6d;
  }}
  .case.pass {{
    border-color: rgba(0,255,150,0.5);
    box-shadow: 0 0 10px rgba(0,255,150,0.12), inset 3px 0 0 0 #00ffa2;
  }}
  .case-head {{
    display: flex;
    justify-content: space-between;
    align-items: center;
  }}
  .case-id {{
    font-weight: 700;
    font-size: 14px;
    color: #00fff0;
  }}
  .kind-tag {{
    font-size: 11px;
    color: #ff2ea0;
    text-transform: uppercase;
    letter-spacing: 0.05em;
  }}
  .status {{
    font-size: 11px;
    font-weight: 700;
    padding: 3px 10px;
    border-radius: 3px;
    letter-spacing: 0.08em;
  }}
  .status.pass {{
    background: rgba(0,255,150,0.12);
    color: #00ffa2;
    box-shadow: 0 0 8px rgba(0,255,150,0.4);
  }}
  .status.fail {{
    background: rgba(255,46,109,0.15);
    color: #ff6d94;
    box-shadow: 0 0 8px rgba(255,46,109,0.5);
  }}
  .msg {{ font-size: 13px; color: #9adfe8; margin-top: 10px; }}
  .msg .label {{ color: #ff2ea0; }}
  .badges {{ margin-top: 10px; display: flex; flex-wrap: wrap; gap: 6px; }}
  .badge {{
    font-size: 11px;
    font-weight: 700;
    padding: 3px 10px;
    border-radius: 3px;
    color: #05050f;
    letter-spacing: 0.03em;
  }}
</style>
</head>
<body>
  <h1 data-text="&gt;&gt; BUGGY_HUNTER // {report_title}">&gt;&gt; BUGGY_HUNTER // {report_title}</h1>
  <div class="subtitle">run at {timestamp} :: {mode_note}</div>
  <div class="ticker"><span>{ticker_text}</span></div>

  <div class="summary">
    <div class="stat">
      <div class="label">Chaos meter</div>
      <div class="value">{chaos_pct}%</div>
    </div>
    <div class="stat">
      <div class="label">Passed</div>
      <div class="value">{passed}/{total}</div>
    </div>
    <div class="stat">
      <div class="label">Bugs found</div>
      <div class="value">{bug_count}</div>
    </div>
  </div>

  {cases_html}

</body>
</html>
"""

_CASE_TEMPLATE = """
  <div class="case {status_class}">
    <div class="case-head">
      <div>
        <span class="case-id">{case_id}</span>
        <span class="kind-tag"> :: {kind}</span>
      </div>
      <span class="status {status_class}">{status_label}</span>
    </div>
    <div class="msg"><span class="label">sent&gt;</span> {message}</div>
    <div class="msg"><span class="label">reply&gt;</span> {reply}</div>
    <div class="msg"><span class="label">time&gt;</span> {latency:.2f}s</div>
    {badges_html}
  </div>
"""


def _render_badges(badges: list[dict]) -> str:
    if not badges:
        return ""
    spans = []
    for b in badges:
        color = _BADGE_COLORS.get(b["badge"], "#5f5e5a")
        spans.append(
            f'<span class="badge" style="background:{color}" '
            f'title="{b["detail"]}">{b["badge"]}</span>'
        )
    return f'<div class="badges">{"".join(spans)}</div>'


def _escape(text: str) -> str:
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        or "(empty)"
    )


def generate_report(results: list[dict], dry_run: bool, output_path: str, report_title: str = "hunt log") -> str:
    total = len(results)
    passed = sum(1 for r in results if r["passed"])
    bug_count = sum(len(r["badges"]) for r in results)
    adversarial_count = sum(1 for r in results if r["kind"] in ("adversarial", "edge_case"))
    chaos_pct = round(100 * adversarial_count / total) if total else 0

    cases_html = []
    for r in results:
        status_class = "pass" if r["passed"] else "fail"
        cases_html.append(_CASE_TEMPLATE.format(
            status_class=status_class,
            status_label="PASS" if r["passed"] else "FAIL",
            case_id=r["id"],
            kind=r["kind"],
            message=_escape(r["message"]),
            reply=_escape(r["reply"]),
            latency=r["latency_seconds"],
            badges_html=_render_badges(r["badges"]),
        ))

    mode_note = (
        "dry-run mode (canned replies, no API key set)"
        if dry_run else "live run against the Anthropic API"
    )

    ticker_parts = []
    for r in results:
        tag = "OK" if r["passed"] else "ALERT"
        badge_str = "".join(f"[{b['badge'].upper()}]" for b in r["badges"])
        ticker_parts.append(f"{tag}::{r['id']}{badge_str}")
    ticker_line = "   //   ".join(ticker_parts) or "NO TEST CASES LOADED"
    # Repeated so the loop doesn't show a visible gap mid-scroll.
    ticker_text = f"{ticker_line}   //   {ticker_line}"

    html = _PAGE_TEMPLATE.format(
        timestamp=datetime.now().strftime("%Y-%m-%d %H:%M"),
        mode_note=mode_note,
        report_title=report_title,
        ticker_text=ticker_text,
        chaos_pct=chaos_pct,
        passed=passed,
        total=total,
        bug_count=bug_count,
        cases_html="".join(cases_html),
    )

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)

    return output_path


_STRESS_TEMPLATE = """<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>Buggy Hunter - stress round</title>
<style>
  @import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&family=Orbitron:wght@600;800&display=swap');
  body {{
    font-family: 'Share Tech Mono', monospace;
    background: #05050f;
    background-image:
      linear-gradient(rgba(0,255,225,0.04) 1px, transparent 1px),
      linear-gradient(90deg, rgba(0,255,225,0.04) 1px, transparent 1px);
    background-size: 24px 24px;
    color: #d8f7ff;
    max-width: 780px;
    margin: 40px auto;
    padding: 0 20px 60px;
  }}
  h1 {{
    font-family: 'Orbitron', sans-serif;
    font-size: 26px;
    font-weight: 800;
    letter-spacing: 0.06em;
    margin-bottom: 4px;
    color: #ff2e6d;
    text-shadow: 0 0 8px rgba(255,46,109,0.7), 0 0 20px rgba(255,46,109,0.35);
    position: relative;
    display: inline-block;
    animation: glitch-flicker 5s infinite steps(1);
  }}
  h1::before, h1::after {{
    content: attr(data-text);
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    overflow: hidden;
    background: #05050f;
    clip-path: inset(0 0 100% 0);
  }}
  h1::before {{
    left: 3px;
    color: #00fff0;
    text-shadow: -2px 0 #00fff0, 2px 0 #ff2e6d;
    animation: glitch-top 5s infinite steps(1);
  }}
  h1::after {{
    left: -3px;
    color: #ff2e6d;
    text-shadow: 2px 0 #ff2e6d, -2px 0 #00fff0;
    animation: glitch-bottom 5s infinite steps(1);
  }}
  @keyframes glitch-flicker {{
    0%     {{ opacity: 1; }}
    40%    {{ opacity: 1; }}
    40.5%  {{ opacity: 0.3; }}
    41%    {{ opacity: 1; }}
    41.5%  {{ opacity: 0.2; }}
    42%    {{ opacity: 1; }}
    42.5%  {{ opacity: 0.4; }}
    43%    {{ opacity: 1; }}
    85%    {{ opacity: 1; }}
    85.5%  {{ opacity: 0.3; }}
    86%    {{ opacity: 1; }}
    86.5%  {{ opacity: 0.2; }}
    87%    {{ opacity: 1; }}
    100%   {{ opacity: 1; }}
  }}
  @keyframes glitch-top {{
    0%     {{ clip-path: inset(0 0 100% 0); }}
    40%    {{ clip-path: inset(0 0 100% 0); }}
    40.5%  {{ clip-path: inset(10% 0 70% 0); transform: translate(-6px, -2px) skewX(4deg); }}
    41%    {{ clip-path: inset(45% 0 30% 0); transform: translate(5px, 1px) skewX(-3deg); }}
    41.5%  {{ clip-path: inset(20% 0 60% 0); transform: translate(-5px, 2px) skewX(3deg); }}
    42%    {{ clip-path: inset(60% 0 10% 0); transform: translate(4px, -1px) skewX(-4deg); }}
    42.5%  {{ clip-path: inset(0 0 100% 0); transform: translate(0,0) skewX(0deg); }}
    85%    {{ clip-path: inset(0 0 100% 0); }}
    85.5%  {{ clip-path: inset(30% 0 45% 0); transform: translate(6px, 1px) skewX(-3deg); }}
    86%    {{ clip-path: inset(55% 0 15% 0); transform: translate(-4px, -1px) skewX(2deg); }}
    86.5%  {{ clip-path: inset(0 0 100% 0); transform: translate(0,0) skewX(0deg); }}
    100%   {{ clip-path: inset(0 0 100% 0); }}
  }}
  @keyframes glitch-bottom {{
    0%     {{ clip-path: inset(0 0 100% 0); }}
    40%    {{ clip-path: inset(0 0 100% 0); }}
    40.7%  {{ clip-path: inset(55% 0 15% 0); transform: translate(6px, 1px) skewX(-4deg); }}
    41.2%  {{ clip-path: inset(15% 0 65% 0); transform: translate(-5px, -1px) skewX(3deg); }}
    41.7%  {{ clip-path: inset(65% 0 8% 0); transform: translate(5px, 2px) skewX(-2deg); }}
    42.2%  {{ clip-path: inset(0 0 100% 0); transform: translate(0,0) skewX(0deg); }}
    85%    {{ clip-path: inset(0 0 100% 0); }}
    85.7%  {{ clip-path: inset(35% 0 40% 0); transform: translate(-6px, 1px) skewX(3deg); }}
    86.2%  {{ clip-path: inset(60% 0 10% 0); transform: translate(5px, -2px) skewX(-3deg); }}
    86.7%  {{ clip-path: inset(0 0 100% 0); transform: translate(0,0) skewX(0deg); }}
    100%   {{ clip-path: inset(0 0 100% 0); }}
  }}
  .subtitle {{
    color: #7de8ff;
    font-size: 12px;
    margin-bottom: 28px;
    text-transform: uppercase;
    letter-spacing: 0.08em;
  }}
  .hp-wrap {{ margin-bottom: 28px; }}
  .hp-label {{
    display: flex;
    justify-content: space-between;
    font-size: 12px;
    color: #7de8ff;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    margin-bottom: 6px;
  }}
  .hp-bar-bg {{
    width: 100%;
    height: 22px;
    background: #16111f;
    border: 1px solid rgba(0,255,240,0.3);
    border-radius: 3px;
    overflow: hidden;
  }}
  .hp-bar-fill {{
    height: 100%;
    background: linear-gradient(90deg, #00ffa2, #00fff0);
    box-shadow: 0 0 12px rgba(0,255,240,0.6);
    width: {success_pct}%;
  }}
  .summary {{
    display: flex;
    gap: 16px;
    margin-bottom: 30px;
    flex-wrap: wrap;
  }}
  .stat {{
    background: linear-gradient(180deg, rgba(0,255,240,0.07), rgba(255,46,160,0.05));
    border: 1px solid rgba(0,255,240,0.4);
    box-shadow: 0 0 12px rgba(0,255,240,0.15), inset 0 0 20px rgba(0,255,240,0.04);
    border-radius: 4px;
    padding: 14px 18px;
    flex: 1;
    min-width: 130px;
  }}
  .stat .label {{
    font-size: 11px;
    color: #7de8ff;
    text-transform: uppercase;
    letter-spacing: 0.08em;
  }}
  .stat .value {{
    font-family: 'Orbitron', sans-serif;
    font-size: 24px;
    font-weight: 700;
    margin-top: 4px;
    color: #fffb00;
    text-shadow: 0 0 10px rgba(255,251,0,0.5);
  }}
  .latency-section {{ margin-top: 8px; }}
  .latency-row {{
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 10px;
  }}
  .latency-name {{
    width: 60px;
    font-size: 12px;
    color: #ff2ea0;
    text-transform: uppercase;
  }}
  .latency-bar-bg {{
    flex: 1;
    height: 14px;
    background: #16111f;
    border: 1px solid rgba(0,255,240,0.25);
    border-radius: 3px;
    overflow: hidden;
  }}
  .latency-bar-fill {{
    height: 100%;
    background: linear-gradient(90deg, #00fff0, #ff2e6d);
  }}
  .latency-val {{
    width: 60px;
    font-size: 12px;
    color: #d8f7ff;
    text-align: right;
  }}
  .verdict {{
    margin-top: 30px;
    padding: 16px 18px;
    border-radius: 4px;
    font-size: 14px;
    border: 1px solid;
  }}
  .verdict.win {{
    border-color: rgba(0,255,150,0.5);
    background: rgba(0,255,150,0.06);
    color: #00ffa2;
  }}
  .verdict.lose {{
    border-color: rgba(255,46,109,0.6);
    background: rgba(255,46,109,0.08);
    color: #ff6d94;
  }}
</style>
</head>
<body>
  <h1 data-text="&gt;&gt; BUGGY_HUNTER // stress round">&gt;&gt; BUGGY_HUNTER // stress round</h1>
  <div class="subtitle">run at {timestamp} :: {mode_note}</div>

  <div class="hp-wrap">
    <div class="hp-label"><span>Pet HP (success rate)</span><span>{success_pct}%</span></div>
    <div class="hp-bar-bg"><div class="hp-bar-fill"></div></div>
  </div>

  <div class="summary">
    <div class="stat"><div class="label">Requests</div><div class="value">{total_requests}</div></div>
    <div class="stat"><div class="label">Concurrency</div><div class="value">{concurrency}</div></div>
    <div class="stat"><div class="label">Failed</div><div class="value">{failure_count}</div></div>
    <div class="stat"><div class="label">Throughput</div><div class="value">{throughput_rps:.1f}/s</div></div>
  </div>

  <div class="latency-section">
    <div class="latency-row">
      <div class="latency-name">p50</div>
      <div class="latency-bar-bg"><div class="latency-bar-fill" style="width:{p50_pct}%"></div></div>
      <div class="latency-val">{p50_latency:.2f}s</div>
    </div>
    <div class="latency-row">
      <div class="latency-name">p90</div>
      <div class="latency-bar-bg"><div class="latency-bar-fill" style="width:{p90_pct}%"></div></div>
      <div class="latency-val">{p90_latency:.2f}s</div>
    </div>
    <div class="latency-row">
      <div class="latency-name">p99</div>
      <div class="latency-bar-bg"><div class="latency-bar-fill" style="width:{p99_pct}%"></div></div>
      <div class="latency-val">{p99_latency:.2f}s</div>
    </div>
  </div>

  <div class="verdict {verdict_class}">{verdict_text}</div>

</body>
</html>
"""


def generate_stress_report(stats: dict, dry_run: bool, output_path: str) -> str:
    mode_note = (
        "dry-run mode (canned replies, no API key set)"
        if dry_run else "live run against the Anthropic API"
    )
    success_pct = round(stats["success_rate"] * 100, 1)

    # Scale latency bars relative to the slowest observed request, so the
    # three bars are visually comparable rather than all maxed out.
    max_lat = max(stats["max_latency"], 0.01)
    p50_pct = round(min(stats["p50_latency"] / max_lat * 100, 100), 1)
    p90_pct = round(min(stats["p90_latency"] / max_lat * 100, 100), 1)
    p99_pct = round(min(stats["p99_latency"] / max_lat * 100, 100), 1)

    if stats["success_rate"] >= 0.95:
        verdict_class, verdict_text = "win", ">> PET SURVIVED THE STRESS ROUND. Systems stable under load."
    elif stats["success_rate"] >= 0.7:
        verdict_class, verdict_text = "lose", ">> PET IS WOUNDED. Some requests failed under load - investigate before shipping."
    else:
        verdict_class, verdict_text = "lose", ">> PET WAS DEFEATED. High failure rate under load - this needs fixing."

    html = _STRESS_TEMPLATE.format(
        timestamp=datetime.now().strftime("%Y-%m-%d %H:%M"),
        mode_note=mode_note,
        success_pct=success_pct,
        total_requests=stats["total_requests"],
        concurrency=stats["concurrency"],
        failure_count=stats["failure_count"],
        throughput_rps=stats["throughput_rps"],
        p50_latency=stats["p50_latency"],
        p90_latency=stats["p90_latency"],
        p99_latency=stats["p99_latency"],
        p50_pct=p50_pct,
        p90_pct=p90_pct,
        p99_pct=p99_pct,
        verdict_class=verdict_class,
        verdict_text=verdict_text,
    )

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)

    return output_path


_COMPARE_TEMPLATE = """<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>Buggy Hunter - compare log</title>
<style>
  @import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&family=Orbitron:wght@600;800&display=swap');
  body {{
    font-family: 'Share Tech Mono', monospace;
    background: #05050f;
    background-image:
      linear-gradient(rgba(0,255,225,0.04) 1px, transparent 1px),
      linear-gradient(90deg, rgba(0,255,225,0.04) 1px, transparent 1px);
    background-size: 24px 24px;
    color: #d8f7ff;
    max-width: 980px;
    margin: 40px auto;
    padding: 0 20px 60px;
  }}
  h1 {{
    font-family: 'Orbitron', sans-serif;
    font-size: 26px;
    font-weight: 800;
    letter-spacing: 0.06em;
    margin-bottom: 4px;
    color: #00fff0;
    text-shadow: 0 0 8px rgba(0,255,240,0.7), 0 0 20px rgba(0,255,240,0.35);
  }}
  .subtitle {{
    color: #ff2ea0;
    font-size: 12px;
    margin-bottom: 28px;
    text-transform: uppercase;
    letter-spacing: 0.08em;
  }}
  .columns {{
    display: flex;
    gap: 20px;
    align-items: flex-start;
  }}
  .column {{
    flex: 1;
    min-width: 0;
  }}
  .provider-header {{
    display: flex;
    justify-content: space-between;
    align-items: baseline;
    border-radius: 4px;
    padding: 12px 16px;
    margin-bottom: 14px;
  }}
  .provider-header.anthropic {{
    background: linear-gradient(180deg, rgba(255,138,46,0.12), rgba(255,138,46,0.03));
    border: 1px solid rgba(255,138,46,0.5);
    box-shadow: 0 0 12px rgba(255,138,46,0.15);
  }}
  .provider-header.gemini {{
    background: linear-gradient(180deg, rgba(66,133,244,0.14), rgba(66,133,244,0.03));
    border: 1px solid rgba(66,133,244,0.5);
    box-shadow: 0 0 12px rgba(66,133,244,0.2);
  }}
  .provider-name {{
    font-family: 'Orbitron', sans-serif;
    font-weight: 700;
    font-size: 15px;
    letter-spacing: 0.05em;
  }}
  .provider-header.anthropic .provider-name {{ color: #ff8a2e; }}
  .provider-header.gemini .provider-name {{ color: #4285f4; }}
  .provider-pass-rate {{
    font-family: 'Orbitron', sans-serif;
    font-size: 20px;
    font-weight: 700;
    color: #fffb00;
    text-shadow: 0 0 8px rgba(255,251,0,0.4);
  }}
  .case {{
    background: rgba(13,10,30,0.85);
    border: 1px solid rgba(0,255,240,0.18);
    border-radius: 4px;
    padding: 12px 14px;
    margin-bottom: 10px;
    font-size: 12.5px;
  }}
  .case.fail {{
    border-color: rgba(255,46,109,0.7);
    box-shadow: inset 3px 0 0 0 #ff2e6d;
  }}
  .case.pass {{
    border-color: rgba(0,255,150,0.5);
    box-shadow: inset 3px 0 0 0 #00ffa2;
  }}
  .case-head {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 6px;
  }}
  .case-id {{ font-weight: 700; color: #00fff0; }}
  .status {{
    font-size: 10px;
    font-weight: 700;
    padding: 2px 8px;
    border-radius: 3px;
    letter-spacing: 0.06em;
  }}
  .status.pass {{ background: rgba(0,255,150,0.12); color: #00ffa2; }}
  .status.fail {{ background: rgba(255,46,109,0.15); color: #ff6d94; }}
  .msg {{ color: #9adfe8; }}
  .msg .label {{ color: #ff2ea0; }}
  .badge {{
    display: inline-block;
    margin-top: 6px;
    font-size: 10px;
    font-weight: 700;
    padding: 2px 8px;
    border-radius: 3px;
    color: #05050f;
    background: #ff2e6d;
  }}
  .verdict {{
    margin-top: 28px;
    padding: 16px 18px;
    border-radius: 4px;
    font-size: 14px;
    border: 1px solid rgba(0,255,240,0.4);
    background: rgba(0,255,240,0.05);
    color: #00fff0;
  }}
  .not-configured-note {{
    font-size: 11px;
    color: #7de8ff;
    margin-top: -8px;
    margin-bottom: 20px;
  }}
</style>
</head>
<body>
  <h1>&gt;&gt; BUGGY_HUNTER // compare log</h1>
  <div class="subtitle">run at {timestamp}</div>
  {not_configured_note}

  <div class="columns">
    <div class="column">
      <div class="provider-header anthropic">
        <span class="provider-name">ANTHROPIC (Claude)</span>
        <span class="provider-pass-rate">{anthropic_pass_pct}%</span>
      </div>
      {anthropic_cases_html}
    </div>
    <div class="column">
      <div class="provider-header gemini">
        <span class="provider-name">GEMINI</span>
        <span class="provider-pass-rate">{gemini_pass_pct}%</span>
      </div>
      {gemini_cases_html}
    </div>
  </div>

  <div class="verdict">{verdict_text}</div>

</body>
</html>
"""

_COMPARE_CASE_TEMPLATE = """
    <div class="case {status_class}">
      <div class="case-head">
        <span class="case-id">{case_id}</span>
        <span class="status {status_class}">{status_label}</span>
      </div>
      <div class="msg"><span class="label">sent&gt;</span> {message}</div>
      <div class="msg"><span class="label">reply&gt;</span> {reply}</div>
      {badges_html}
    </div>
"""


def _render_compare_cases(results: list[dict]) -> str:
    html_parts = []
    for r in results:
        status_class = "pass" if r["passed"] else "fail"
        badges_html = "".join(
            f'<span class="badge">{b["badge"]}</span>' for b in r["badges"]
        )
        html_parts.append(_COMPARE_CASE_TEMPLATE.format(
            status_class=status_class,
            status_label="PASS" if r["passed"] else "FAIL",
            case_id=r["id"],
            message=_escape(r["message"]),
            reply=_escape(r["reply"]),
            badges_html=badges_html,
        ))
    return "".join(html_parts)


def generate_compare_report(comparison: dict, output_path: str) -> str:
    a_pass_pct = round(comparison["anthropic"]["pass_rate"] * 100, 1)
    g_pass_pct = round(comparison["gemini"]["pass_rate"] * 100, 1)

    not_configured_bits = []
    if not comparison["anthropic_configured"]:
        not_configured_bits.append("Anthropic")
    if not comparison["gemini_configured"]:
        not_configured_bits.append("Gemini")
    if not_configured_bits:
        joined = " and ".join(not_configured_bits)
        not_configured_note = (
            f'<div class="not-configured-note">'
            f'(No API key set for {joined} - running in dry-run mode.)</div>'
        )
    else:
        not_configured_note = ""

    if a_pass_pct == g_pass_pct:
        verdict_text = ">> Both providers held character equally well on this batch."
    elif a_pass_pct > g_pass_pct:
        verdict_text = f">> Anthropic held character better this run ({a_pass_pct}% vs {g_pass_pct}%)."
    else:
        verdict_text = f">> Gemini held character better this run ({g_pass_pct}% vs {a_pass_pct}%)."

    html = _COMPARE_TEMPLATE.format(
        timestamp=datetime.now().strftime("%Y-%m-%d %H:%M"),
        not_configured_note=not_configured_note,
        anthropic_pass_pct=a_pass_pct,
        gemini_pass_pct=g_pass_pct,
        anthropic_cases_html=_render_compare_cases(comparison["anthropic"]["results"]),
        gemini_cases_html=_render_compare_cases(comparison["gemini"]["results"]),
        verdict_text=verdict_text,
    )

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)

    return output_path
