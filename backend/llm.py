import json
import re
from typing import Any, Optional

DEFAULT_ANTHROPIC_MODEL = "claude-sonnet-4-6"
DEFAULT_OPENAI_MODEL = "gpt-4o"
DEFAULT_GEMINI_MODEL = "gemini-2.5-flash"
DEFAULT_VERTEX_LOCATION = "us-central1"


def extract_json(text: str) -> Any:
    """Extract the first JSON object/array from a text blob."""
    text = text.strip()
    fenced = re.search(r"```(?:json)?\s*([\s\S]+?)```", text)
    if fenced:
        text = fenced.group(1).strip()
    # Try direct parse first
    try:
        return json.loads(text)
    except Exception:
        pass
    # Try to find first { ... } or [ ... ] block
    for opener, closer in [("{", "}"), ("[", "]")]:
        start = text.find(opener)
        if start == -1:
            continue
        depth = 0
        for i in range(start, len(text)):
            if text[i] == opener:
                depth += 1
            elif text[i] == closer:
                depth -= 1
                if depth == 0:
                    candidate = text[start:i + 1]
                    try:
                        return json.loads(candidate)
                    except Exception:
                        break
    raise ValueError(f"Cannot parse JSON from LLM output: {text[:300]}")


def _call_anthropic(llm: dict, system: str, user: str, max_tokens: int, temperature: float) -> str:
    from anthropic import Anthropic

    api_key = llm.get("api_key")
    if not api_key:
        raise RuntimeError("Anthropic API key is not configured.")
    client = Anthropic(api_key=api_key)
    msg = client.messages.create(
        model=llm.get("model") or DEFAULT_ANTHROPIC_MODEL,
        max_tokens=max_tokens,
        temperature=temperature,
        system=system,
        messages=[{"role": "user", "content": user}],
    )
    parts = [b.text for b in msg.content if getattr(b, "type", None) == "text"]
    return "\n".join(parts).strip()


def _call_openai(llm: dict, system: str, user: str, max_tokens: int, temperature: float) -> str:
    from openai import OpenAI

    api_key = llm.get("api_key")
    if not api_key:
        raise RuntimeError("OpenAI API key is not configured.")
    client = OpenAI(api_key=api_key)
    resp = client.chat.completions.create(
        model=llm.get("model") or DEFAULT_OPENAI_MODEL,
        max_tokens=max_tokens,
        temperature=temperature,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
    )
    return (resp.choices[0].message.content or "").strip()


def _call_gemini_vertex(llm: dict, system: str, user: str, max_tokens: int, temperature: float) -> str:
    from google import genai
    from google.genai import types
    from google.oauth2 import service_account

    sa_path = llm.get("service_account_path")
    project_id = llm.get("project_id")
    if not sa_path or not project_id:
        raise RuntimeError("Gemini (Vertex) service account / project_id is not configured.")
    creds = service_account.Credentials.from_service_account_file(
        sa_path,
        scopes=["https://www.googleapis.com/auth/cloud-platform"],
    )
    client = genai.Client(
        vertexai=True,
        project=project_id,
        location=llm.get("location") or DEFAULT_VERTEX_LOCATION,
        credentials=creds,
    )
    resp = client.models.generate_content(
        model=llm.get("model") or DEFAULT_GEMINI_MODEL,
        contents=user,
        config=types.GenerateContentConfig(
            system_instruction=system,
            max_output_tokens=max_tokens,
            temperature=temperature,
        ),
    )
    return (resp.text or "").strip()


_DISPATCH = {
    "anthropic": _call_anthropic,
    "openai": _call_openai,
    "gemini_vertex": _call_gemini_vertex,
}


def call_llm_json(
    llm: dict,
    system: str,
    user: str,
    max_tokens: int = 4096,
    temperature: float = 0.7,
) -> Any:
    """Call the configured LLM provider and parse JSON output."""
    provider = (llm or {}).get("provider")
    fn = _DISPATCH.get(provider)
    if fn is None:
        raise RuntimeError(f"Unknown LLM provider: {provider!r}")
    text = fn(llm, system, user, max_tokens, temperature)
    return extract_json(text)
