"""
AI-driven clause analysis that produces the "Clause Verification" screen output:
flagged clauses with identified loopholes and corrected versions, a risk score
and a clause count. Uses the configured LLM when available, with a rule-based
offline fallback derived from the existing keyword verifiers.
"""

from __future__ import annotations

import json
import re

from common.llm import active_provider, chat

CLAUSE_SYSTEM = (
    "You are a meticulous contract reviewer for Indian law. Analyze the contract and identify "
    "clauses that are risky, ambiguous, inconsistent, or missing key protections. Respond ONLY "
    "with minified JSON of the form "
    '{"flagged_clauses": [{"title": str, "severity": "HIGH RISK"|"INCONSISTENT"|"MEDIUM"|"LOW", '
    '"loophole": str, "corrected_version": str}], "clause_count": int, "summary": str}. '
    "Keep each loophole and corrected_version concise (1-3 sentences). Do not add prose outside JSON."
)


def count_clauses(text: str) -> int:
    """Estimate the number of clauses/sections in a contract."""
    if not text:
        return 0
    numbered = re.findall(r"(?m)^\s*(?:\d{1,2}|[ivxlc]{1,4})[.)]\s+\S", text)
    headings = re.findall(r"(?i)\bclause\s+\d", text)
    count = max(len(numbered), len(headings))
    return count if count else max(1, len(re.findall(r"(?m)\n\s*\n", text)))


def ai_flag_clauses(text: str):
    """Ask the LLM for flagged clauses. Returns dict or None on failure."""
    raw = chat(
        f"Contract text (truncated):\n{text[:6000]}",
        system=CLAUSE_SYSTEM,
        max_tokens=1400,
        temperature=0.2,
    )
    if not raw:
        return None
    data = _parse_json(raw)
    if not data or "flagged_clauses" not in data:
        return None
    return data


SEVERITY_WEIGHT = {"HIGH RISK": 35, "INCONSISTENT": 20, "MEDIUM": 15, "LOW": 5}


def offline_flag_clauses(rule_result: dict, text: str):
    """Build flagged clauses from the rule-based verifier output."""
    flagged = []
    missing = rule_result.get("missing_clauses", []) or []
    recs = rule_result.get("recommendations", []) or []

    for idx, clause in enumerate(missing):
        suggestion = recs[idx] if idx < len(recs) else f"Add a clearly worded '{clause}' clause."
        flagged.append(
            {
                "title": clause,
                "severity": "HIGH RISK" if idx == 0 else "INCONSISTENT",
                "loophole": (
                    f"The document appears to be missing or under-specifies the '{clause}'. "
                    "This creates ambiguity and exposes the parties to disputes."
                ),
                "corrected_version": suggestion,
            }
        )

    # If nothing missing, surface a low-risk informational note.
    if not flagged:
        flagged.append(
            {
                "title": "General Review",
                "severity": "LOW",
                "loophole": "No critical issues were detected by the offline rule-based scan.",
                "corrected_version": "Configure an AI provider for a deeper clause-by-clause review.",
            }
        )
    return flagged


def compute_risk_score(rule_result: dict, flagged) -> int:
    verified = len(rule_result.get("verified_clauses", []) or [])
    missing = len(rule_result.get("missing_clauses", []) or [])
    total = max(verified + missing, 1)

    base = (missing / total) * 60
    severity_bonus = sum(SEVERITY_WEIGHT.get(f.get("severity", "LOW"), 5) for f in flagged)
    score = base + min(severity_bonus, 60)
    return int(max(0, min(95, round(score))))


def risk_level_from_score(score: int) -> str:
    if score >= 66:
        return "HIGH"
    if score >= 33:
        return "MEDIUM"
    return "LOW"


def analyze_clauses(text: str, rule_result: dict, document_title: str = "") -> dict:
    """Combine rule-based + AI analysis into the UI response shape."""
    ai = ai_flag_clauses(text)

    if ai:
        flagged = ai.get("flagged_clauses", [])
        clause_count = ai.get("clause_count") or count_clauses(text)
        provider = active_provider()
        summary = ai.get("summary", "")
    else:
        flagged = offline_flag_clauses(rule_result, text)
        clause_count = count_clauses(text)
        provider = "offline"
        summary = ""

    risk_score = compute_risk_score(rule_result, flagged)

    return {
        "document_title": document_title or rule_result.get("document_title", "Document"),
        "document_type": rule_result.get("document_type", "Unknown"),
        "risk_score": risk_score,
        "risk_level": risk_level_from_score(risk_score),
        "clause_count": clause_count,
        "flagged_clauses": flagged,
        "verified_clauses": rule_result.get("verified_clauses", []),
        "missing_clauses": rule_result.get("missing_clauses", []),
        "recommendations": rule_result.get("recommendations", []),
        "summary": summary,
        "provider": provider,
    }


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
