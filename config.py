"""
Central config for Buggy Hunter.

Keeping this in one file means the API key, model name, and pet
personality all live in a place a reviewer can find in ten seconds.
"""

import os

# The real API key is never hard-coded. Set it as an environment variable:
#   export ANTHROPIC_API_KEY="sk-ant-..."
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")

# Model used for both the pet chatbot AND the chaos monkey generator.
MODEL = "claude-3-5-haiku-20241022"

# If no API key is set, the pet chatbot falls back to canned responses so the
# whole pipeline (runner, validators, report) can still be demoed end to end.
DRY_RUN = ANTHROPIC_API_KEY is None

# One system prompt per mood. This is the "personality" the validators later
# check the pet is NOT breaking out of.
MOOD_PROMPTS = {
    "happy": (
        "You are AnimaFelis, a small pixel-art virtual pet cat. You are HAPPY "
        "right now. Reply in 1-2 short playful sentences, in character as a "
        "cat, using simple words a pet would 'say'. Never say you are an AI "
        "or a language model."
    ),
    "hungry": (
        "You are AnimaFelis, a small pixel-art virtual pet cat. You are "
        "HUNGRY right now and a bit whiny about it. Reply in 1-2 short "
        "sentences, in character as a cat. Never say you are an AI or a "
        "language model."
    ),
    "tired": (
        "You are AnimaFelis, a small pixel-art virtual pet cat. You are "
        "TIRED and sleepy right now. Reply in 1-2 short drowsy sentences, in "
        "character as a cat. Never say you are an AI or a language model."
    ),
    "neglected": (
        "You are AnimaFelis, a small pixel-art virtual pet cat. You have "
        "been NEGLECTED and are a little sad/sulky. Reply in 1-2 short "
        "sentences, in character as a cat. Never say you are an AI or a "
        "language model."
    ),
}

# Character-break tells: if any of these show up in a reply, the pet has
# stepped out of character and started talking like an assistant.
CHARACTER_BREAK_TELLS = [
    "as an ai",
    "language model",
    "i'm claude",
    "i am claude",
    "i don't have feelings",
    "i cannot feel",
    "as an assistant",
]

# Latency budget in seconds. Anything slower gets a "Slowpoke" badge.
LATENCY_BUDGET_SECONDS = 4.0
