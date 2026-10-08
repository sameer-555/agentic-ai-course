"""One place to set the model and build API clients."""

import os

from dotenv import load_dotenv

load_dotenv()

MODEL = os.getenv("OPS_BUDDY_MODEL", "claude-haiku-5-5")


def anthropic_client():
    """Raw Anthropic SDK client (Levels 1-4, 12-14)."""
    import anthropic

    return anthropic.Anthropic()


def chat_model(**kwargs):
    """LangChain chat model (Levels 5-11).

    max_tokens is set explicitly: the model thinks before answering, and a small
    limit can cut the answer off.
    """
    from langchain_anthropic import ChatAnthropic

    return ChatAnthropic(model=MODEL, max_tokens=kwargs.pop("max_tokens", 8000), **kwargs)
