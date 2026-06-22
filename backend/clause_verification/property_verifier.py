import re


def verify_property_agreement(text):

    text_lower = text.lower()

    verified_clauses = []
    missing_clauses = []
    recommendations = []

    # Seller
    if "seller" in text_lower:
        verified_clauses.append("Seller Details")
    else:
        missing_clauses.append("Seller Details")

    # Buyer
    if "buyer" in text_lower or "purchaser" in text_lower:
        verified_clauses.append("Buyer Details")
    else:
        missing_clauses.append("Buyer Details")

    # Sale Amount
    if (
        "sale consideration" in text_lower
        or "sale price" in text_lower
    ):
        verified_clauses.append("Sale Amount")
    else:
        missing_clauses.append("Sale Amount")
        recommendations.append(
            "Specify property sale amount."
        )

    # Property Description
    if (
        "property" in text_lower
        or "schedule" in text_lower
    ):
        verified_clauses.append(
            "Property Description"
        )
    else:
        missing_clauses.append(
            "Property Description"
        )

    # Registration
    if "registration" in text_lower:
        verified_clauses.append(
            "Registration Clause"
        )
    else:
        missing_clauses.append(
            "Registration Clause"
        )

    # Possession
    if "possession" in text_lower:
        verified_clauses.append(
            "Possession Clause"
        )
    else:
        missing_clauses.append(
            "Possession Clause"
        )
        recommendations.append(
            "Specify possession date."
        )

    # Risk
    if len(missing_clauses) <= 1:
        risk_level = "LOW"
    elif len(missing_clauses) <= 3:
        risk_level = "MEDIUM"
    else:
        risk_level = "HIGH"

    return {
        "document_type": "Property Sale Agreement",
        "verified_clauses": verified_clauses,
        "missing_clauses": missing_clauses,
        "risk_level": risk_level,
        "recommendations": recommendations
    }