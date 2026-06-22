def verify_employment_agreement(text):

    text_lower = text.lower()

    verified_clauses = []
    missing_clauses = []
    recommendations = []

    # Employee
    if "employee" in text_lower:
        verified_clauses.append(
            "Employee Details"
        )
    else:
        missing_clauses.append(
            "Employee Details"
        )

    # Employer
    if "employer" in text_lower:
        verified_clauses.append(
            "Employer Details"
        )
    else:
        missing_clauses.append(
            "Employer Details"
        )

    # Salary
    if (
        "salary" in text_lower
        or "ctc" in text_lower
        or "compensation" in text_lower
    ):
        verified_clauses.append(
            "Salary Clause"
        )
    else:
        missing_clauses.append(
            "Salary Clause"
        )

    # Notice Period
    if "notice period" in text_lower:
        verified_clauses.append(
            "Notice Period"
        )
    else:
        missing_clauses.append(
            "Notice Period"
        )

        recommendations.append(
            "Add notice period clause."
        )

    # Termination
    if "termination" in text_lower:
        verified_clauses.append(
            "Termination Clause"
        )
    else:
        missing_clauses.append(
            "Termination Clause"
        )

        recommendations.append(
            "Define termination conditions."
        )

    # Risk
    if len(missing_clauses) <= 1:
        risk_level = "LOW"
    elif len(missing_clauses) <= 3:
        risk_level = "MEDIUM"
    else:
        risk_level = "HIGH"

    return {
        "document_type": "Employment Agreement",
        "verified_clauses": verified_clauses,
        "missing_clauses": missing_clauses,
        "risk_level": risk_level,
        "recommendations": recommendations
    }