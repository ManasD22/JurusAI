from file_manager.models import LegalDocument
from file_manager.utils import extract_text_from_pdf

from .ai_analysis import analyze_clauses
from .document_detector import detect_document_type
from .employment_verifier import verify_employment_agreement
from .property_verifier import verify_property_agreement
from .rental_verifier import verify_rental_agreement


def verify_generic_agreement(text):
    """Fallback verifier for documents that don't match a known template."""
    text_lower = (text or "").lower()

    checks = [
        ("Parties / Definitions", ["party", "parties", "between", "hereinafter"]),
        ("Term / Duration", ["term", "duration", "period", "commenc"]),
        ("Payment / Consideration", ["payment", "fee", "consideration", "amount", "rs.", "salary"]),
        ("Termination Clause", ["termination", "terminate"]),
        ("Confidentiality", ["confidential", "non-disclosure", "nda"]),
        ("Governing Law", ["governing law", "jurisdiction", "governed by"]),
        ("Dispute Resolution", ["arbitration", "dispute", "mediation"]),
    ]

    verified_clauses = []
    missing_clauses = []
    recommendations = []

    for label, keywords in checks:
        if any(k in text_lower for k in keywords):
            verified_clauses.append(label)
        else:
            missing_clauses.append(label)
            recommendations.append(f"Consider adding a clear '{label}' clause.")

    missing_count = len(missing_clauses)
    if missing_count <= 1:
        risk_level = "LOW"
    elif missing_count <= 3:
        risk_level = "MEDIUM"
    else:
        risk_level = "HIGH"

    return {
        "document_type": "General Agreement",
        "verified_clauses": verified_clauses,
        "missing_clauses": missing_clauses,
        "risk_level": risk_level,
        "recommendations": recommendations,
    }


def run_rule_based(text):
    """Detect the document type and run the matching keyword verifier."""
    document_type = detect_document_type(text)

    if document_type == "Rental Agreement":
        return verify_rental_agreement(text)
    if document_type == "Property Sale Agreement":
        return verify_property_agreement(text)
    if document_type == "Employment Agreement":
        return verify_employment_agreement(text)
    return verify_generic_agreement(text)


def analyze_text_for_ui(text, document_title=""):
    """Full pipeline returning the Clause Verification screen response shape."""
    rule_result = run_rule_based(text)
    rule_result["document_title"] = document_title
    return analyze_clauses(text, rule_result, document_title)


def analyze_document(document_id, user):
    """Legacy by-id flow: load an uploaded document then run the verifier."""
    document = LegalDocument.objects.get(id=document_id, user=user)
    extracted_text = extract_text_from_pdf(document.document.path)
    return analyze_text_for_ui(extracted_text, document.title)
