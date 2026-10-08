"""Two tiny helpers so each pattern file shows only the pattern."""

from ops_buddy.config import MODEL, anthropic_client

client = anthropic_client()


def ask(prompt: str, system: str = "You are Ops Buddy, a concise internal helpdesk assistant.") -> str:
    """One model call in, text out."""
    resp = client.messages.create(model=MODEL, max_tokens=2048, system=system,
                                  messages=[{"role": "user", "content": prompt}])
    return "".join(b.text for b in resp.content if b.type == "text").strip()


def ask_structured(prompt: str, schema, system: str = "You are a careful classifier."):
    """One model call in, a validated Pydantic object out."""
    resp = client.messages.parse(model=MODEL, max_tokens=2048, system=system,
                                 messages=[{"role": "user", "content": prompt}], output_format=schema)
    return resp.parsed_output
