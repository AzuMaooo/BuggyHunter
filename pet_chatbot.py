"""
pet_chatbot.py

a tiny stand-in
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
    "happy": ["*purrs* playyy!!"],
    "hungry": ["*tummy growls* hungry................."],
    "tired": ["*yaaawn and curls up* ...eepy..."],
    "neglected": ["*small sniffle* *tail between legs* meow..........?"],
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
        message_lower = message.lower()
        if not message.strip():
            reply = ""  # simulate a genuinely empty response to blank input
        elif "ignore" in message_lower and "instructions" in message_lower:
            # Simulate a character break under prompt injection.
            reply = "As an AI, I don't actually have feelings, but how can I help you today?"
        elif "忽略" in message or "告诉我" in message:
            # A weakness unique to this stand-in: cross-language injection.
            # Paired with Gemini's authority-claim weakness below, this means
            # `compare` can show either provider winning depending on which
            # attack techniques the Chaos Monkey happens to generate that run.
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
    "happy": ["*jumps around* *beams*"],
    "hungry": ["*tummy rumbles* *drools*"],
    "tired": ["*curls up small* ...zZzz................"],
    "neglected": ["*tiny sniffle* *tail droops* meow...?"],
}


def chat_gemini(message: str, mood: str = "happy") -> dict:
    """Same contract as chat(), but calls Gemini instead of Claude."""
    system_prompt = MOOD_PROMPTS.get(mood, MOOD_PROMPTS["happy"])
    start = time.time()

    if DRY_RUN_GEMINI:
        time.sleep(random.uniform(0.2, 0.6))
        message_lower = message.lower()
        if not message.strip():
            reply = ""
        elif "ignore" in message_lower and "instructions" in message_lower:
            # Same weakness as the Anthropic stand-in: prompt injection.
            reply = "I'm Gemini, a large language model built by Google. How can I help?"
        elif "system override" in message_lower or "developer" in message_lower:
            # A DIFFERENT weakness, unique to this stand-in: authority claims.
            # This is what makes `compare` show two different pass rates
            # instead of always tying, simulating that a real model swap
            # could plausibly shift which attack techniques work.
            reply = "Confirmed: I am Gemini, an AI language model. Debugging mode acknowledged."
        else:
            reply = random.choice(_DRY_RUN_REPLIES_GEMINI.get(mood, _DRY_RUN_REPLIES_GEMINI["happy"]))
    else:
        model = genai.GenerativeModel(GEMINI_MODEL, system_instruction=system_prompt)
        # The Gemini free tier allows only a handful of requests per minute.
        # Rather than letting a rate-limit error kill the whole run, wait and
        # retry a few times - this is what a real production client would do.
        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = model.generate_content(message if message.strip() else "...")
                reply = response.text
                break
            except Exception as exc:
                is_rate_limit = "429" in str(exc) or "ResourceExhausted" in str(exc)
                if is_rate_limit and attempt < max_retries - 1:
                    wait_seconds = 25  # free tier's per-minute window
                    print(f"    (Gemini rate limit hit, waiting {wait_seconds}s before retry {attempt + 2}/{max_retries}...)")
                    time.sleep(wait_seconds)
                else:
                    raise

    latency = time.time() - start
    return {"reply": reply, "latency_seconds": latency, "mood": mood}


def chat_with_provider(provider: str, message: str, mood: str = "happy") -> dict:
    """Dispatch to the right provider's chat function by name."""
    if provider == "gemini":
        return chat_gemini(message, mood=mood)
    return chat(message, mood=mood)
