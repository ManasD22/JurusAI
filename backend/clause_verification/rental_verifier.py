import re

STANDARD_TOPICS = [
    "rent",
    "license fee",
    "deposit",
    "maintenance",
    "electricity",
    "termination",
    "notice",
    "lease",
    "licensee",
    "licensor",
    "agreement",
    "premises"
]
def extract_rent_amount(text):

    match = re.search(
        r'License fee.*?Rs\.\s*(\d+)',
        text,
        re.IGNORECASE | re.DOTALL
    )

    if match:
        return f"Rs. {match.group(1)}"

    return "Not Found"


def extract_security_deposit(text):

    match = re.search(
        r'refundable deposit.*?Rs\.\s*(\d+)',
        text,
        re.IGNORECASE | re.DOTALL
    )

    if match:
        return f"Rs. {match.group(1)}"

    return "Not Found"


def extract_lease_duration(text):

    match = re.search(
        r'period of\s*(\d+)\s*Months',
        text,
        re.IGNORECASE
    )

    if match:
        return f"{match.group(1)} Months"

    return "Not Found"

def extract_start_date(text):

    match = re.search(
        r'commencing from\s*(\d{2}/\d{2}/\d{4})',
        text,
        re.IGNORECASE
    )

    if match:
        return match.group(1)

    return "Not Found"


def extract_end_date(text):

    match = re.search(
        r'ending on\s*(\d{2}/\d{2}/\d{4})',
        text,
        re.IGNORECASE
    )

    if match:
        return match.group(1)

    return "Not Found"

def extract_maintenance_responsibility(text):

    match = re.search(
        r'shall\s+be\s+paid\s+by\s+the\s+(licensee|licensor)',
        text,
        re.IGNORECASE
    )

    if match:
        return match.group(1).capitalize()

    return "Not Found"

def extract_electricity_responsibility(text):

    match = re.search(
        r'electricity charges:.*?(licensee|licensor).*?shall pay',
        text,
        re.IGNORECASE | re.DOTALL
    )

    if match:
        return match.group(1).capitalize()

    return "Not Found"

def verify_rental_agreement(text):

    text_lower = text.lower()

    rent_amount = extract_rent_amount(text)

    security_deposit = extract_security_deposit(text)

    lease_duration = extract_lease_duration(text)

    start_date = extract_start_date(text)

    end_date = extract_end_date(text)

    maintenance_responsibility = (
    extract_maintenance_responsibility(text)
)

    electricity_responsibility = (
    extract_electricity_responsibility(text)
)

    verified_clauses = []
    missing_clauses = []
    recommendations = []

    # Licensor
    if "licensor" in text_lower:
        verified_clauses.append("Licensor Details")
    else:
        missing_clauses.append("Licensor Details")

    # Licensee
    if "licensee" in text_lower:
        verified_clauses.append("Licensee Details")
    else:
        missing_clauses.append("Licensee Details")

    # Lease Duration
    if "months" in text_lower or "month" in text_lower:
        verified_clauses.append("Lease Duration")
    else:
        missing_clauses.append("Lease Duration")

    # Notice Period
    if "notice period" in text_lower:
        verified_clauses.append("Notice Period")
    else:
        missing_clauses.append("Notice Period")
        recommendations.append(
            "Add a notice period clause."
        )

    # Security Deposit
    if security_deposit != "Not Found":
        verified_clauses.append("Security Deposit")
    else:
        missing_clauses.append("Security Deposit")

    recommendations.append("Specify the security deposit amount.")

    # Termination Clause
    if "termination" in text_lower:
        verified_clauses.append("Termination Clause")
    else:
        missing_clauses.append("Termination Clause")
        recommendations.append(
            "Define contract termination conditions."
        )

    # Maintenance Clause
    if "maintenance" in text_lower:
        verified_clauses.append("Maintenance Clause")
    else:
        missing_clauses.append("Maintenance Clause")
        recommendations.append(
            "Clarify maintenance responsibilities."
        )

    # Risk Calculation
    missing_count = len(missing_clauses)

    if missing_count <= 1:
        risk_level = "LOW"

    elif missing_count <= 3:
        risk_level = "MEDIUM"

    else:
        risk_level = "HIGH"

    return {
    "document_type": "Rental Agreement",

    "rent_amount": rent_amount,

    "security_deposit": security_deposit,

    "lease_duration": lease_duration,

    "start_date": start_date,

    "end_date": end_date,

    "maintenance_responsibility":
    maintenance_responsibility,

    "electricity_responsibility":
    electricity_responsibility,

    "verified_clauses": verified_clauses,

    "missing_clauses": missing_clauses,

    "risk_level": risk_level,

    "recommendations": recommendations
}

