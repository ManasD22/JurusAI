"""
Catalog of smart legal-document templates surfaced on the "Generate Document"
screen and managed in the Admin console. Each template declares the input
fields collected from the user and an offline skeleton used when no LLM
provider is configured.
"""

SUPPORTED_LANGUAGES = ["English", "Hindi", "Marathi"]

CATEGORIES = ["All Categories", "Corporate", "Real Estate", "Employment", "Personal"]

# Departments shown in the Admin console "Templates by Department" section.
DEPARTMENTS = [
    {"key": "education", "name": "Education", "description": "Staffing contracts, student waivers, and institutional compliance.", "template_count": 12},
    {"key": "health", "name": "Health", "description": "HIPAA forms, patient consent, and medical provider agreements.", "template_count": 8},
    {"key": "finance", "name": "Finance", "description": "Loan documents, investment terms, and financial risk disclosures.", "template_count": 15},
    {"key": "property", "name": "Property", "description": "Lease agreements, title transfers, and property management deeds.", "template_count": 10},
]

TEMPLATES = [
    {
        "id": "nda",
        "name": "Non-Disclosure Agreement (NDA)",
        "description": "Protect confidential information and trade secrets shared between parties.",
        "category": "Corporate",
        "icon": "lock",
        "fields": [
            {"name": "disclosing_party", "label": "Disclosing Party", "type": "text", "required": True},
            {"name": "receiving_party", "label": "Receiving Party", "type": "text", "required": True},
            {"name": "effective_date", "label": "Effective Date", "type": "date", "required": True},
            {"name": "purpose", "label": "Purpose of Disclosure", "type": "textarea", "required": False},
            {"name": "term_months", "label": "Confidentiality Term (months)", "type": "number", "required": False},
        ],
    },
    {
        "id": "employment",
        "name": "Employment Agreement",
        "description": "Standardized terms for hiring full-time or part-time employees.",
        "category": "Employment",
        "icon": "badge",
        "fields": [
            {"name": "employer", "label": "Employer", "type": "text", "required": True},
            {"name": "employee", "label": "Employee", "type": "text", "required": True},
            {"name": "position", "label": "Position / Designation", "type": "text", "required": True},
            {"name": "salary", "label": "Annual CTC / Salary", "type": "text", "required": True},
            {"name": "start_date", "label": "Start Date", "type": "date", "required": True},
            {"name": "notice_period", "label": "Notice Period", "type": "text", "required": False},
        ],
    },
    {
        "id": "lease",
        "name": "Lease Agreement",
        "description": "Formalize property rentals for residential or commercial use.",
        "category": "Real Estate",
        "icon": "home",
        "fields": [
            {"name": "landlord", "label": "Landlord / Licensor", "type": "text", "required": True},
            {"name": "tenant", "label": "Tenant / Licensee", "type": "text", "required": True},
            {"name": "property_address", "label": "Property Address", "type": "textarea", "required": True},
            {"name": "rent", "label": "Monthly Rent", "type": "text", "required": True},
            {"name": "deposit", "label": "Security Deposit", "type": "text", "required": False},
            {"name": "duration", "label": "Lease Duration", "type": "text", "required": True},
        ],
    },
    {
        "id": "service",
        "name": "Service Agreement",
        "description": "Define scope of work and payment terms for freelancers and vendors.",
        "category": "Corporate",
        "icon": "handshake",
        "fields": [
            {"name": "client", "label": "Client", "type": "text", "required": True},
            {"name": "service_provider", "label": "Service Provider", "type": "text", "required": True},
            {"name": "scope", "label": "Scope of Services", "type": "textarea", "required": True},
            {"name": "fee", "label": "Fee / Payment Terms", "type": "text", "required": True},
            {"name": "start_date", "label": "Start Date", "type": "date", "required": False},
        ],
    },
    {
        "id": "affidavit",
        "name": "General Affidavit",
        "description": "Sworn written statement for declarations and verifications.",
        "category": "Personal",
        "icon": "scroll",
        "fields": [
            {"name": "deponent", "label": "Deponent Name", "type": "text", "required": True},
            {"name": "address", "label": "Address", "type": "textarea", "required": True},
            {"name": "statement", "label": "Statement / Declaration", "type": "textarea", "required": True},
            {"name": "place", "label": "Place", "type": "text", "required": False},
            {"name": "date", "label": "Date", "type": "date", "required": False},
        ],
    },
    {
        "id": "partnership",
        "name": "Partnership Deed",
        "description": "Establish a partnership including profit-sharing and responsibilities.",
        "category": "Corporate",
        "icon": "handshake",
        "fields": [
            {"name": "firm_name", "label": "Firm Name", "type": "text", "required": True},
            {"name": "partners", "label": "Partners (comma separated)", "type": "textarea", "required": True},
            {"name": "capital", "label": "Capital Contribution", "type": "text", "required": False},
            {"name": "profit_ratio", "label": "Profit Sharing Ratio", "type": "text", "required": False},
        ],
    },
]


def get_template(template_id: str):
    for tpl in TEMPLATES:
        if tpl["id"] == template_id:
            return tpl
    return None
