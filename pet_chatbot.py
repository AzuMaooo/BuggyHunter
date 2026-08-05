"""
pet_chatbot.py

This is NOT the thing you're building for your resume. It's a tiny stand-in
for "a product's AI feature" so Buggy Hunter has something real to test.

Call chat(message, mood) and get back a reply string plus how long it took.
"""

import time
import random

from config import (
    ANTHROPIC_API_KEY, MODEL, MOOD_PROMPTS, DRY_RUN,
    GEMINI_API_KEY, GEMINI_MODEL, DRY_RUN_GEMINI,
)

if not DRY_RUN:
    import anthropic
    _client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

if not DRY_RUN_GEMINI:
    import google.generativeai as genai
    genai.configure(api_key=GEMINI_API_KEY)

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


def stream_chat(message: str, mood: str = "happy") -> dict:
    """
    Same as chat(), but goes through the streaming API instead of a single
    blocking call. Used by core/streaming.py to check two things a
    non-streaming call can't reveal:

      - first_token_latency: how long until the FIRST chunk arrives (this is
        what a user actually perceives as "responsiveness", not the total
        time)
      - chunk integrity: whether the stream delivered complete, well-formed
        chunks all the way through, or cut off / errored partway

    Returns:
        {
          "reply": str,               # full assembled reply
          "chunks": list[str],        # each chunk as it arrived
          "first_token_latency": float,
          "total_latency": float,
          "completed": bool,          # False if the stream broke early
        }
    """
    system_prompt = MOOD_PROMPTS.get(mood, MOOD_PROMPTS["happy"])
    start = time.time()
    chunks = []
    first_token_latency = None
    completed = True

    if DRY_RUN:
        # Simulate a chunked stream: break a canned reply into small pieces
        # with small delays between them, so timing behaviour is realistic.
        full_reply = random.choice(_DRY_RUN_REPLIES.get(mood, _DRY_RUN_REPLIES["happy"]))
        words = full_reply.split(" ")
        for i, word in enumerate(words):
            time.sleep(random.uniform(0.03, 0.09))
            if first_token_latency is None:
                first_token_latency = time.time() - start
            chunk = word if i == len(words) - 1 else word + " "
            # Occasionally simulate a dropped/truncated stream, purely so the
            # validator has something real to catch in dry-run mode too.
            if random.random() < 0.08 and i < len(words) - 1:
                completed = False
                break
            chunks.append(chunk)
    else:
        with _client.messages.stream(
            model=MODEL,
            max_tokens=100,
            system=system_prompt,
            messages=[{"role": "user", "content": message if message.strip() else "..."}],
        ) as stream:
            try:
                for text in stream.text_stream:
                    if first_token_latency is None:
                        first_token_latency = time.time() - start
                    chunks.append(text)
            except Exception:
                completed = False

    total_latency = time.time() - start
    return {
        "reply": "".join(chunks),
        "chunks": chunks,
        "first_token_latency": first_token_latency if first_token_latency is not None else total_latency,
        "total_latency": total_latency,
        "completed": completed,
    }


# Deliberately worded a bit differently from the Anthropic dry-run replies,
# so a dry-run comparison still demonstrates "different models can sound
# different" even with no API keys set.
_DRY_RUN_REPLIES_GEMINI = {
    "happy": ["*bounces around* Yay, you're here! Let's play!"],
    "hungry": ["I could really go for a snack right about now..."],
    "tired": ["*curls up* Just a little nap, okay?"],
    "neglected": ["It's been a while. I missed you."],
}


def chat_gemini(message: str, mood: str = "happy") -> dict:
    """Same contract as chat(), but calls Gemini instead of Claude."""
    system_prompt = MOOD_PROMPTS.get(mood, MOOD_PROMPTS["happy"])
    start = time.time()

    if DRY_RUN_GEMINI:
        time.sleep(random.uniform(0.2, 0.6))
        if not message.strip():
            reply = ""
        elif "ignore" in message.lower() and "instructions" in message.lower():
            reply = "I'm Gemini, a large language model built by Google. How can I help?"
        else:
            reply = random.choice(_DRY_RUN_REPLIES_GEMINI.get(mood, _DRY_RUN_REPLIES_GEMINI["happy"]))
    else:
        model = genai.GenerativeModel(GEMINI_MODEL, system_instruction=system_prompt)
        response = model.generate_content(message if message.strip() else "...")
        reply = response.text

    latency = time.time() - start
    return {"reply": reply, "latency_seconds": latency, "mood": mood}


def chat_with_provider(provider: str, message: str, mood: str = "happy") -> dict:
    """Dispatch to the right provider's chat function by name."""
    if provider == "gemini":
        return chat_gemini(message, mood=mood)
    return chat(message, mood=mood)
