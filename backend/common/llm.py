"""
Pluggable LLM service for JurisAI.

A single, provider-agnostic entry point used by every AI feature
(Legal Advisor, summarization, document drafting, clause analysis).

Design goals
------------
* Works with **Google Gemini** (free tier), **OpenAI**, or **Anthropic** when an
  API key is configured.
* Selects a provider automatically (`LLM_PROVIDER=auto`) based on which key is
  present, or can be pinned (`gemini` / `openai` / `anthropic` / `offline`).
* Never raises to the caller: if no provider is configured or a call fails,
  :func:`chat` returns ``None`` so callers can apply a local fallback.

Usage
-----
    from common.llm import chat, is_available

    answer = chat(
        "Explain Article 21 of the Indian Constitution in simple terms.",
        system="You are a careful Indian legal assistant.",
    )
    if answer is None:
        answer = my_offline_fallback()
"""

from __future__ import annotations

import logging

from django.conf import settings

logger = logging.getLogger(__name__)


def _resolve_provider() -> str | None:
    """Return the active provider name, or ``None`` for offline mode."""
    provider = (getattr(settings, "LLM_PROVIDER", "auto") or "auto").lower()
    has_gemini = bool(getattr(settings, "GEMINI_API_KEY", ""))
    has_openai = bool(getattr(settings, "OPENAI_API_KEY", ""))
    has_anthropic = bool(getattr(settings, "ANTHROPIC_API_KEY", ""))

    if provider == "offline":
        return None
    if provider in {"gemini", "google"}:
        return "gemini" if has_gemini else None
    if provider == "openai":
        return "openai" if has_openai else None
    if provider == "anthropic":
        return "anthropic" if has_anthropic else None

    # auto: prefer Gemini (free tier), then Anthropic, then OpenAI, else offline.
    if has_gemini:
        return "gemini"
    if has_anthropic:
        return "anthropic"
    if has_openai:
        return "openai"
    return None


def is_available() -> bool:
    """True when a real LLM provider is configured and importable."""
    return _resolve_provider() is not None


def active_provider() -> str:
    """Human-readable provider label (``offline`` when no key is set)."""
    return _resolve_provider() or "offline"


def _flatten(messages, system) -> str:
    """Collapse a chat message list into a single prompt string.

    All JurisAI call sites send a single, self-contained user turn, so a flat
    prompt is sufficient and keeps provider adapters simple.
    """
    parts = []
    for m in messages:
        role = m.get("role", "user")
        prefix = "Assistant" if role in {"assistant", "model"} else "User"
        parts.append(f"{prefix}: {m['content']}")
    return "\n\n".join(parts)


def _call_gemini(messages, system, max_tokens, temperature) -> str | None:
    user_text = _flatten(messages, system)
    system = system or "You are a helpful assistant."

    # Preferred: the modern `google-genai` SDK.
    try:
        from google import genai
        from google.genai import types

        client = genai.Client(api_key=settings.GEMINI_API_KEY)
        response = client.models.generate_content(
            model=settings.GEMINI_MODEL,
            contents=user_text,
            config=types.GenerateContentConfig(
                system_instruction=system,
                max_output_tokens=max_tokens,
                temperature=temperature,
            ),
        )
        return (getattr(response, "text", "") or "").strip()
    except ImportError:
        pass
    except Exception as exc:
        logger.warning("Gemini (google-genai) call failed: %s", exc)
        # Fall through to try the legacy SDK before giving up.

    # Fallback: the legacy `google-generativeai` SDK.
    try:
        import google.generativeai as genai

        genai.configure(api_key=settings.GEMINI_API_KEY)
        model = genai.GenerativeModel(
            model_name=settings.GEMINI_MODEL,
            system_instruction=system,
        )
        response = model.generate_content(
            user_text,
            generation_config={
                "max_output_tokens": max_tokens,
                "temperature": temperature,
            },
        )
        return (getattr(response, "text", "") or "").strip()
    except Exception as exc:
        logger.warning("Gemini (google-generativeai) call failed: %s", exc)
        return None


def _call_openai(messages, system, max_tokens, temperature) -> str | None:
    try:
        from openai import OpenAI
    except Exception:
        logger.warning("openai package not installed; falling back to offline mode.")
        return None

    try:
        client = OpenAI(api_key=settings.OPENAI_API_KEY)
        payload = []
        if system:
            payload.append({"role": "system", "content": system})
        payload.extend(messages)

        response = client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=payload,
            max_tokens=max_tokens,
            temperature=temperature,
        )
        return (response.choices[0].message.content or "").strip()
    except Exception as exc:  # network / auth / quota errors
        logger.warning("OpenAI call failed: %s", exc)
        return None


def _call_anthropic(messages, system, max_tokens, temperature) -> str | None:
    try:
        import anthropic
    except Exception:
        logger.warning("anthropic package not installed; falling back to offline mode.")
        return None

    try:
        client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
        response = client.messages.create(
            model=settings.ANTHROPIC_MODEL,
            max_tokens=max_tokens,
            temperature=temperature,
            system=system or "You are a helpful assistant.",
            messages=messages,
        )
        parts = [block.text for block in response.content if getattr(block, "type", "") == "text"]
        return "".join(parts).strip()
    except Exception as exc:
        logger.warning("Anthropic call failed: %s", exc)
        return None


def chat(
    prompt_or_messages,
    system: str | None = None,
    max_tokens: int = 1024,
    temperature: float = 0.3,
) -> str | None:
    """Send a chat request to the active provider.

    ``prompt_or_messages`` may be a plain string (treated as a single user
    message) or a list of ``{"role": ..., "content": ...}`` dicts.

    Returns the model's text response, or ``None`` if no provider is
    available or the request failed (so the caller can fall back locally).
    """
    provider = _resolve_provider()
    if provider is None:
        return None

    if isinstance(prompt_or_messages, str):
        messages = [{"role": "user", "content": prompt_or_messages}]
    else:
        messages = list(prompt_or_messages)

    if provider == "gemini":
        return _call_gemini(messages, system, max_tokens, temperature)
    if provider == "anthropic":
        return _call_anthropic(messages, system, max_tokens, temperature)
    return _call_openai(messages, system, max_tokens, temperature)
