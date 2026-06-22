"""
Multilingual legal-document generation service.

Generates a coherent draft from a template + user details (or a free-form
custom request), then optionally translates it into the user's preferred
language. Uses the configured LLM when available; otherwise it assembles a
clean offline draft from a structured skeleton so the feature always works.
"""

from __future__ import annotations

from common.llm import active_provider, chat

from .templates_catalog import SUPPORTED_LANGUAGES, get_template

GENERATION_SYSTEM = (
    "You are an experienced legal drafting assistant for Indian law. Draft a clear, "
    "well-structured, professional legal document using the provided details. Use numbered "
    "clauses, defined terms, and standard legal formatting. Leave clearly marked blanks "
    "(e.g., [____]) only where a required detail is missing. Output only the document text."
)


def _details_block(details: dict) -> str:
    lines = []
    for key, value in (details or {}).items():
        if value in (None, ""):
            continue
        label = key.replace("_", " ").title()
        lines.append(f"- {label}: {value}")
    return "\n".join(lines) if lines else "- (no specific details provided)"


def generate_document(doc_type: str, details: dict, language: str = "English", custom_request: str = "") -> dict:
    language = language if language in SUPPORTED_LANGUAGES else "English"
    template = get_template(doc_type) if doc_type else None
    type_name = template["name"] if template else (doc_type or "Legal Document")

    if custom_request:
        prompt = (
            f"Draft a legal document for the following request:\n{custom_request}\n\n"
            f"Additional details:\n{_details_block(details)}"
        )
    else:
        prompt = (
            f"Draft a {type_name} with the following details:\n{_details_block(details)}"
        )

    draft = chat(prompt, system=GENERATION_SYSTEM, max_tokens=1600, temperature=0.3)

    if not draft:
        draft = _offline_draft(template, type_name, details, custom_request)
        provider = "offline"
    else:
        provider = active_provider()

    translated = draft
    if language != "English":
        translated = _translate(draft, language)

    title = type_name if not custom_request else "Custom Legal Draft"
    return {
        "title": title,
        "doc_type": doc_type or "custom",
        "language": language,
        "document": translated,
        "english_document": draft,
        "provider": provider,
    }


def _translate(text: str, language: str) -> str:
    translated = chat(
        f"Translate the following legal document into {language}. Preserve structure, clause "
        f"numbering and legal meaning. Output only the translation.\n\n{text[:6000]}",
        system="You are a professional legal translator.",
        max_tokens=1800,
        temperature=0.2,
    )
    if translated:
        return translated
    # Offline: keep the English draft but flag that translation needs a provider.
    return f"[Translation to {language} requires an AI provider. Showing English draft.]\n\n{text}"


def _offline_draft(template, type_name, details, custom_request) -> str:
    """A clean, fill-in-the-blank document used when no LLM is configured."""
    details = details or {}

    def val(key, placeholder="[____]"):
        return str(details.get(key) or placeholder)

    header = f"{type_name.upper()}\n" + "=" * len(type_name) + "\n"

    if custom_request and not template:
        body = (
            "THIS AGREEMENT is made on [____].\n\n"
            f"PURPOSE: {custom_request}\n\n"
            "1. The parties agree to the terms described in the purpose above.\n"
            "2. Each party shall perform its obligations in good faith.\n"
            "3. This agreement is governed by the laws of India.\n\n"
            f"Provided details:\n{_details_block(details)}\n\n"
            "IN WITNESS WHEREOF, the parties have executed this agreement.\n\n"
            "_____________________            _____________________\n"
            "Party A                          Party B\n"
        )
        return header + "\n" + body

    if template and template["id"] == "nda":
        body = (
            f"THIS NON-DISCLOSURE AGREEMENT is entered into on {val('effective_date')} "
            f"by and between {val('disclosing_party')} (\"Disclosing Party\") and "
            f"{val('receiving_party')} (\"Receiving Party\").\n\n"
            f"1. PURPOSE. The parties wish to explore: {val('purpose')}.\n"
            "2. CONFIDENTIAL INFORMATION. \"Confidential Information\" means any non-public "
            "information disclosed by the Disclosing Party, whether oral, written or electronic.\n"
            "3. OBLIGATIONS. The Receiving Party shall keep the Confidential Information strictly "
            "confidential and use it solely for the Purpose.\n"
            f"4. TERM. The confidentiality obligations survive for {val('term_months', '24')} months "
            "from the Effective Date.\n"
            "5. GOVERNING LAW. This Agreement is governed by the laws of India.\n"
        )
    elif template and template["id"] == "employment":
        body = (
            f"THIS EMPLOYMENT AGREEMENT is made on {val('start_date')} between "
            f"{val('employer')} (\"Employer\") and {val('employee')} (\"Employee\").\n\n"
            f"1. POSITION. The Employee is appointed as {val('position')}.\n"
            f"2. COMPENSATION. The Employee shall be paid {val('salary')} per annum.\n"
            f"3. COMMENCEMENT. Employment commences on {val('start_date')}.\n"
            f"4. NOTICE PERIOD. Either party may terminate by giving {val('notice_period', '30 days')} "
            "written notice.\n"
            "5. CONFIDENTIALITY. The Employee shall maintain confidentiality of Employer information.\n"
            "6. GOVERNING LAW. This Agreement is governed by the laws of India.\n"
        )
    elif template and template["id"] == "lease":
        body = (
            f"THIS LEASE AGREEMENT is made between {val('landlord')} (\"Landlord\") and "
            f"{val('tenant')} (\"Tenant\").\n\n"
            f"1. PREMISES. The Landlord leases the property at {val('property_address')}.\n"
            f"2. RENT. The monthly rent is {val('rent')}, payable in advance.\n"
            f"3. SECURITY DEPOSIT. The Tenant shall pay a refundable deposit of {val('deposit')}.\n"
            f"4. TERM. The lease is for {val('duration')}.\n"
            "5. MAINTENANCE. The Tenant shall maintain the premises in good condition.\n"
            "6. GOVERNING LAW. This Agreement is governed by the laws of India.\n"
        )
    elif template and template["id"] == "service":
        body = (
            f"THIS SERVICE AGREEMENT is made between {val('client')} (\"Client\") and "
            f"{val('service_provider')} (\"Service Provider\").\n\n"
            f"1. SERVICES. The Service Provider shall provide: {val('scope')}.\n"
            f"2. FEES. The Client shall pay {val('fee')}.\n"
            f"3. TERM. Services commence on {val('start_date')}.\n"
            "4. INTELLECTUAL PROPERTY. Deliverables vest in the Client upon full payment.\n"
            "5. GOVERNING LAW. This Agreement is governed by the laws of India.\n"
        )
    elif template and template["id"] == "affidavit":
        body = (
            f"AFFIDAVIT\n\nI, {val('deponent')}, residing at {val('address')}, do hereby solemnly "
            f"affirm and declare as under:\n\n{val('statement')}\n\n"
            f"Verified at {val('place')} on {val('date')} that the contents above are true to the "
            "best of my knowledge and belief.\n\n_____________________\nDeponent\n"
        )
    elif template and template["id"] == "partnership":
        body = (
            f"THIS DEED OF PARTNERSHIP for the firm \"{val('firm_name')}\" is made between the "
            f"following partners: {val('partners')}.\n\n"
            f"1. CAPITAL. The capital contribution is {val('capital')}.\n"
            f"2. PROFIT SHARING. Profits and losses shall be shared in the ratio {val('profit_ratio')}.\n"
            "3. MANAGEMENT. All partners shall participate in the management of the firm.\n"
            "4. GOVERNING LAW. This Deed is governed by the Indian Partnership Act, 1932.\n"
        )
    else:
        body = (
            "THIS AGREEMENT is made on [____].\n\n"
            f"Provided details:\n{_details_block(details)}\n\n"
            "1. The parties agree to the terms set out herein.\n"
            "2. This document is governed by the laws of India.\n"
        )

    footer = (
        "\nIN WITNESS WHEREOF, the parties have signed this document on the date first written "
        "above.\n\n_____________________            _____________________\nParty A                          Party B\n"
    )
    return header + "\n" + body + footer
