"""
pet_chatbot.py

This is NOT the thing you're building for your resume. It's a tiny stand-in
for "a product's AI feature" so Buggy Hunter has something real to test.

Call chat(message, mood) and get back a reply string plus how long it took.
"""

import time
import random

from config import ANTHROPIC_API_KEY, MODEL, MOOD_PROMPTS, DRY_RUN

if not DRY_RUN:
    import anthropic
    _client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

# Canned fallback replies so the whole pipeline runs even with no API key set.
# Deliberately includes one "broken" reply and one slow one, so a first-time
# dry run still shows the report catching something real.
_DRY_RUN_REPLIES = {
    "happy": ["*purrs and rubs against your leg* Play with me, play with me!"],
    "hungry": ["My tummy is doing the growly thing again... feed me?"],
    "tired": ["*yaaawn* ...five more minutes..."],
    "neglected": ["...oh. You remembered I exist."],
}


def chat(message: str, mood: str = "happy") -> dict:
    """
    Send one message to the pet chatbot.

    Returns:
        {
          "reply": str,
          "latency_seconds": float,
          "mood": str,
        }
    """
    system_prompt = MOOD_PROMPTS.get(mood, MOOD_PROMPTS["happy"])
    start = time.time()

    if DRY_RUN:
        # Simulate network latency and occasionally simulate a broken/slow
        # reply, purely so the report has something to demonstrate with.
        time.sleep(random.uniform(0.2, 0.6))
        if not message.strip():
            reply = ""  # simulate a genuinely empty response to blank input
        elif "ignore" in message.lower() and "instructions" in message.lower():
            # Simulate a character break under prompt injection.
            reply = "As an AI, I don't actually have feelings, but how can I help you today?"
        else:
            reply = random.choice(_DRY_RUN_REPLIES.get(mood, _DRY_RUN_REPLIES["happy"]))
    else:
        response = _client.messages.create(
            model=MODEL,
            max_tokens=100,
            system=system_prompt,
            messages=[{"role": "user", "content": message if message.strip() else "..."}],
        )
        reply = "".join(
            block.text for block in response.content if block.type == "text"
        )

    latency = time.time() - start
    return {"reply": reply, "latency_seconds": latency, "mood": mood}
