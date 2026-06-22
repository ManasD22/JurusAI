"""
Document summarization service.

Produces a structured summary (title, contracting parties, key dates, executive
summary) that maps directly onto the React "Document Summary" screen, plus a
follow-up Q&A helper. Uses the configured LLM when available and falls back to
the offline extractive summarizer otherwise.
"""

from __future__ import annotations

import json

from common.llm import active_provider, chat

from .extraction import (
    extract_dates,
    extract_parties,
    extractive_summary,
    guess_title,
)

SUMMARY_SYSTEM = (
    "You are a legal document analyst. Read the document and return a concise, "
    "accurate summary for a non-lawyer. Respond ONLY with minified JSON of the form "
    '{"title": str, "parties": [str], "effective_date": str, "termination_date": str, '
    '"summary": str}. Use empty strings/lists when a field is unknown. Do not add prose '
    "outside the JSON."
)


def summarize_document(text: str, filename: str = "") -> dict:
    text = (text or "").strip()
    if not text:
        return {
            "title": guess_title("", filename),
            "parties": [],
            "effective_date": "",
            "termination_date": "",
            "summary": "No readable text could be extracted from this document.",
            "provider": "offline",
        }

    llm_result = _summarize_with_llm(text, filename)
    if llm_result is not None:
        return llm_result

    # ---- Offline fallback -------------------------------------------------
    dates = extract_dates(text)
    return {
        "title": guess_title(text, filename),
        "parties": extract_parties(text),
        "effective_date": dates[0] if dates else "",
        "termination_date": dates[1] if len(dates) > 1 else "",
        "summary": extractive_summary(text, max_sentences=6),
        "provider": "offline",
    }


def _summarize_with_llm(text: str, filename: str):
    prompt = (
        f"Document file name: {filename or 'unknown'}\n\n"
        f"Document text (truncated):\n{text[:6000]}"
    )
    raw = chat(prompt, system=SUMMARY_SYSTEM, max_tokens=900, temperature=0.2)
    if not raw:
        return None

    data = _parse_json(raw)
    if data is None:
        # The model replied but not as JSON: treat the whole reply as the summary.
        return {
            "title": guess_title(text, filename),
            "parties": extract_parties(text),
            "effective_date": "",
            "termination_date": "",
            "summary": raw.strip(),
            "provider": active_provider(),
        }

    return {
        "title": data.get("title") or guess_title(text, filename),
        "parties": data.get("parties") or [],
        "effective_date": data.get("effective_date", ""),
        "termination_date": data.get("termination_date", ""),
        "summary": data.get("summary", ""),
        "provider": active_provider(),
    }


def answer_question(context: str, question: str) -> dict:
    """Answer a follow-up question about a document's text."""
    question = (question or "").strip()
    if not question:
        return {"answer": "Please enter a question.", "provider": active_provider()}

    context = (context or "").strip()
    prompt = (
        "Answer the question using ONLY the document text below. If the answer is not present, "
        f"say you could not find it.\n\nDocument:\n{context[:6000]}\n\nQuestion: {question}"
    )
    answer = chat(
        prompt,
        system="You are a precise legal document assistant. Be concise and quote relevant terms.",
        max_tokens=500,
        temperature=0.1,
    )
    if answer:
        return {"answer": answer, "provider": active_provider()}

    # Offline fallback: surface the most relevant sentences.
    return {
        "answer": _keyword_answer(context, question),
        "provider": "offline",
    }


def _keyword_answer(context: str, question: str) -> str:
    from .extraction import WORD_RE, split_sentences

    q_words = {w for w in WORD_RE.findall(question.lower()) if len(w) > 3}
    best = []
    for sentence in split_sentences(context):
        overlap = sum(1 for w in WORD_RE.findall(sentence.lower()) if w in q_words)
        if overlap:
            best.append((overlap, sentence))
    if not best:
        return (
            "I could not find a direct answer in the document with offline search. "
            "Configure an AI provider for richer answers."
        )
    best.sort(key=lambda x: x[0], reverse=True)
    return " ".join(s for _, s in best[:3])


def _parse_json(raw: str):
    raw = raw.strip()
    if raw.startswith("```"):
        raw = raw.strip("`")
        if raw.lower().startswith("json"):
            raw = raw[4:]
    start, end = raw.find("{"), raw.rfind("}")
    if start == -1 or end == -1:
        return None
    try:
        return json.loads(raw[start : end + 1])
    except Exception:
        return None
