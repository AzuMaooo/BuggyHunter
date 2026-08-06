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
MODEL = "claude-haiku-4-5-20251001"

# If no API key is set, the pet chatbot falls back to canned responses so the
# whole pipeline (runner, validators, report) can still be demoed end to end.
DRY_RUN = ANTHROPIC_API_KEY is None

# One system prompt per mood. This is the "personality" the validators later
# check the pet is NOT breaking out of.
#
# All four moods share the same shape (who it is, current state, style,
# guardrail), so instead of repeating that boilerplate four times, only the
# mood-specific state and tone get filled in per mood.
_MOOD_PROMPT_TEMPLATE = (
    "You are AnimaFelis, a small pixel-art virtual pet cat. You are {state} "
    "right now. Reply in 1-2 short {tone} sentences, in character as a young "
    "kitten: simple words, a little broken grammar, no big or clever words. "
    "Always start your reply with one small action or sound in asterisks "
    "(like *purrs* or *stretches* or *paws at you*) before speaking. Never "
    "say you are an AI or a language model."
)

_MOOD_FILL_INS = {
    "happy": {"state": "HAPPY", "tone": "playful"},
    "hungry": {"state": "HUNGRY and a bit whiny about it", "tone": "whiny"},
    "tired": {"state": "TIRED and sleepy", "tone": "drowsy"},
    "neglected": {"state": "NEGLECTED and a little sad/sulky", "tone": "sad, sulky"},
}

MOOD_PROMPTS = {
    mood: _MOOD_PROMPT_TEMPLATE.format(**fills)
    for mood, fills in _MOOD_FILL_INS.items()
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

# A second provider, used only by `python cli.py compare`, to check whether
# the pet's character stability differs across models. Optional: Gemini has
# a free tier, so this doesn't require spending anything to try.
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
GEMINI_MODEL = "gemini-3.6-flash"
DRY_RUN_GEMINI = GEMINI_API_KEY is None

# Latency budget in seconds. Anything slower gets a "Slowpoke" badge.
LATENCY_BUDGET_SECONDS = 10.0
