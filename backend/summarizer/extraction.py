"""
Document text extraction + offline NLP helpers (no heavy dependencies).

Supports PDF (PyMuPDF), DOCX (python-docx) and plain text. The extractive
summarizer and naive metadata extractors here are used whenever no LLM
provider is configured, keeping the feature fully functional offline.
"""

from __future__ import annotations

import io
import re

STOPWORDS = {
    "the", "a", "an", "and", "or", "but", "if", "then", "of", "to", "in", "on",
    "for", "with", "as", "by", "at", "from", "this", "that", "these", "those",
    "is", "are", "was", "were", "be", "been", "being", "shall", "will", "may",
    "any", "all", "such", "which", "who", "whom", "whose", "it", "its", "their",
    "his", "her", "they", "he", "she", "we", "you", "i", "not", "no", "nor",
    "so", "than", "too", "very", "can", "would", "should", "could", "has",
    "have", "had", "do", "does", "did", "between", "into", "upon", "under",
    "hereby", "herein", "thereof", "hereof", "hereto", "agreement", "party",
    "parties", "section", "clause",
}

SENTENCE_SPLIT_RE = re.compile(r"(?<=[.!?])\s+(?=[A-Z0-9])")
WORD_RE = re.compile(r"[a-zA-Z']+")

DATE_RE = re.compile(
    r"\b("
    r"\d{1,2}(?:st|nd|rd|th)?\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{2,4}"
    r"|(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{1,2},?\s+\d{2,4}"
    r"|\d{1,2}[/-]\d{1,2}[/-]\d{2,4}"
    r")\b",
    re.IGNORECASE,
)


def extract_text(uploaded_file) -> str:
    """Extract raw text from an uploaded PDF / DOCX / TXT file object."""
    name = (getattr(uploaded_file, "name", "") or "").lower()
    data = uploaded_file.read()

    if name.endswith(".pdf"):
        return _extract_pdf(data)
    if name.endswith(".docx"):
        return _extract_docx(data)
    if name.endswith(".txt"):
        try:
            return data.decode("utf-8", errors="ignore")
        except Exception:
            return ""
    # Unknown extension: try PDF, then text.
    text = _extract_pdf(data)
    if text:
        return text
    return data.decode("utf-8", errors="ignore")


def _extract_pdf(data: bytes) -> str:
    try:
        import fitz  # PyMuPDF

        text = []
        with fitz.open(stream=data, filetype="pdf") as doc:
            for page in doc:
                text.append(page.get_text())
        return "\n".join(text)
    except Exception:
        return ""


def _extract_docx(data: bytes) -> str:
    try:
        import docx

        document = docx.Document(io.BytesIO(data))
        return "\n".join(p.text for p in document.paragraphs)
    except Exception:
        return ""


def split_sentences(text: str):
    text = re.sub(r"\s+", " ", text or "").strip()
    if not text:
        return []
    return [s.strip() for s in SENTENCE_SPLIT_RE.split(text) if len(s.strip()) > 0]


def extractive_summary(text: str, max_sentences: int = 6) -> str:
    """Frequency-based extractive summary (TextRank-lite, pure Python)."""
    sentences = split_sentences(text)
    if len(sentences) <= max_sentences:
        return " ".join(sentences)

    # Word frequency table (excluding stopwords).
    freq: dict[str, int] = {}
    for word in WORD_RE.findall(text.lower()):
        if word in STOPWORDS or len(word) <= 2:
            continue
        freq[word] = freq.get(word, 0) + 1

    if not freq:
        return " ".join(sentences[:max_sentences])

    peak = max(freq.values())
    for w in freq:
        freq[w] /= peak

    # Score each sentence by normalized word importance.
    scored = []
    for idx, sentence in enumerate(sentences):
        words = WORD_RE.findall(sentence.lower())
        if not words:
            continue
        score = sum(freq.get(w, 0) for w in words) / (len(words) ** 0.5)
        scored.append((score, idx, sentence))

    top = sorted(scored, key=lambda x: x[0], reverse=True)[:max_sentences]
    top_in_order = [s for _, _, s in sorted(top, key=lambda x: x[1])]
    return " ".join(top_in_order)


def guess_title(text: str, filename: str = "") -> str:
    for line in (text or "").splitlines():
        line = line.strip()
        if 8 <= len(line) <= 90 and not line.endswith("."):
            return line.title() if line.isupper() else line
    if filename:
        base = re.sub(r"\.[^.]+$", "", filename)
        return base.replace("_", " ").replace("-", " ").strip().title()
    return "Legal Document"


def extract_parties(text: str):
    """Naive contracting-party extraction (between X and Y)."""
    parties = []
    match = re.search(
        r"by and between\s+(.+?)\s+and\s+(.+?)(?:\.|,|\n|hereinafter|whereas)",
        text or "",
        re.IGNORECASE | re.DOTALL,
    )
    if not match:
        match = re.search(
            r"between\s+(.+?)\s+and\s+(.+?)(?:\.|,|\n|hereinafter|whereas)",
            text or "",
            re.IGNORECASE | re.DOTALL,
        )
    if match:
        for grp in (match.group(1), match.group(2)):
            cleaned = re.sub(r"\s+", " ", grp).strip(" .,")
            if 2 < len(cleaned) < 80:
                parties.append(cleaned)
    return parties


def extract_dates(text: str, limit: int = 4):
    seen = []
    for m in DATE_RE.finditer(text or ""):
        val = m.group(0).strip()
        if val not in seen:
            seen.append(val)
        if len(seen) >= limit:
            break
    return seen
