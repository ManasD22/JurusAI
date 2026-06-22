"""
Legal Advisor service.

Implements a lightweight Retrieval-Augmented Generation (RAG) flow:

    1. Retrieve  -> pull candidate references (Indian Kanoon search + offline KB)
    2. Generate  -> ask the configured LLM to answer *grounded in* those refs
    3. Fallback  -> if no LLM is available, synthesize an answer from the KB

The response shape matches what the React "Legal Advisor" screen renders:
``{"answer", "citations": [{title, description}], "references": [{title, link}]}``.
"""

from __future__ import annotations

import logging

from django.conf import settings

from common.llm import active_provider, chat
from .knowledge_base import GENERIC_FALLBACK, match_entries

logger = logging.getLogger(__name__)


def fetch_legal_references(query: str, limit: int = 5):
    """Best-effort live retrieval of case references from Indian Kanoon.

    Returns a list of ``{"title", "link"}``. Always degrades gracefully to an
    empty list when retrieval is disabled, the network is down, or parsing
    fails — the caller still has the offline knowledge base.
    """
    if not getattr(settings, "ENABLE_WEB_RETRIEVAL", False):
        return []

    try:
        import requests
        from bs4 import BeautifulSoup

        url = f"https://indiankanoon.org/search/?formInput={requests.utils.quote(query)}"
        headers = {"User-Agent": "Mozilla/5.0 (JurisAI Legal Advisor)"}
        resp = requests.get(url, headers=headers, timeout=8)
        resp.raise_for_status()

        soup = BeautifulSoup(resp.text, "html.parser")
        references = []
        for item in soup.select(".result_title")[:limit]:
            anchor = item.find("a")
            if not anchor:
                continue
            href = anchor.get("href", "")
            references.append(
                {
                    "title": item.get_text(strip=True),
                    "link": "https://indiankanoon.org" + href if href.startswith("/") else href,
                }
            )
        return references
    except Exception as exc:  # network/parse errors are non-fatal
        logger.info("Indian Kanoon retrieval unavailable: %s", exc)
        return []


def _offline_answer(query: str):
    """Compose an answer purely from the offline knowledge base."""
    entries = match_entries(query)
    if not entries:
        return {
            "answer": GENERIC_FALLBACK["answer"],
            "citations": GENERIC_FALLBACK["citations"],
        }

    paragraphs = [e["answer"] for e in entries]
    citations = []
    seen = set()
    for e in entries:
        for c in e["citations"]:
            key = c["title"]
            if key not in seen:
                seen.add(key)
                citations.append(c)

    return {"answer": "\n\n".join(paragraphs), "citations": citations}


def _build_context(query: str, references):
    """Assemble grounding context from KB entries + retrieved references."""
    blocks = []
    for entry in match_entries(query):
        cite_lines = "; ".join(c["title"] for c in entry["citations"])
        blocks.append(f"{entry['title']}: {entry['answer']} (Authorities: {cite_lines})")
    for ref in references:
        blocks.append(f"Case reference: {ref['title']} ({ref['link']})")
    return "\n\n".join(blocks)


SYSTEM_PROMPT = (
    "You are JurisAI, a careful legal assistant focused on Indian law. "
    "Answer the user's question clearly and concisely for a non-lawyer, grounded ONLY in the "
    "provided context where possible. Be accurate, cite the relevant article/section/case by "
    "name in your prose, and never invent citations. If the context is insufficient, say so. "
    "Always end with a one-line reminder that this is general information, not legal advice."
)


def legal_advice(query: str, jurisdiction: str | None = None, matter_type: str | None = None):
    """Top-level entry point for the Legal Advisor chatbot."""
    query = (query or "").strip()
    if not query:
        return {
            "answer": "Please enter a legal question to get started.",
            "citations": [],
            "references": [],
            "provider": active_provider(),
        }

    references = fetch_legal_references(query)
    offline = _offline_answer(query)

    context = _build_context(query, references)
    meta = []
    if jurisdiction:
        meta.append(f"Jurisdiction: {jurisdiction}")
    if matter_type:
        meta.append(f"Matter type: {matter_type}")
    meta_line = (" | ".join(meta) + "\n\n") if meta else ""

    prompt = (
        f"{meta_line}"
        f"Context:\n{context if context else '(no retrieved context)'}\n\n"
        f"Question: {query}\n\n"
        "Provide a helpful, well-structured answer."
    )

    answer = chat(prompt, system=SYSTEM_PROMPT, max_tokens=900, temperature=0.2)

    if not answer:
        # Offline / failure fallback.
        return {
            "answer": offline["answer"],
            "citations": offline["citations"],
            "references": references,
            "provider": "offline",
        }

    # When the LLM answered, keep KB citations (curated + trustworthy) and add
    # any live references found.
    return {
        "answer": answer,
        "citations": offline["citations"],
        "references": references,
        "provider": active_provider(),
    }
