"""
A small, offline legal knowledge base used by the Legal Advisor when no LLM
provider is configured (or a live request fails). It keeps the chatbot useful
for common Indian constitutional / contract questions during demos without any
external dependency.

Each entry: keywords that trigger it, a plain-language explanation, and the
authoritative citations to surface in the UI.
"""

KNOWLEDGE_BASE = [
    {
        "id": "article-21",
        "keywords": ["article 21", "right to life", "personal liberty", "life and liberty"],
        "title": "Right to Life and Personal Liberty (Article 21)",
        "answer": (
            "Article 21 of the Constitution of India states that \"no person shall be "
            "deprived of his life or personal liberty except according to procedure "
            "established by law.\" The Supreme Court has read this expansively to include "
            "the right to live with dignity, the right to privacy (K.S. Puttaswamy, 2017), "
            "the right to a clean environment, the right to livelihood, and the right to a "
            "speedy and fair trial. It is available to both citizens and non-citizens."
        ),
        "citations": [
            {"title": "Constitution of India, Article 21", "description": "Protection of life and personal liberty."},
            {"title": "Maneka Gandhi v. Union of India (1978)", "description": "Procedure under Article 21 must be just, fair and reasonable."},
            {"title": "K.S. Puttaswamy v. Union of India (2017)", "description": "Right to privacy is a fundamental right under Article 21."},
        ],
    },
    {
        "id": "article-14",
        "keywords": ["article 14", "equality before law", "equal protection", "discrimination"],
        "title": "Right to Equality (Article 14)",
        "answer": (
            "Article 14 guarantees equality before the law and equal protection of the laws "
            "within the territory of India. It forbids class legislation but permits reasonable "
            "classification that has an intelligible differentia and a rational nexus to the "
            "objective sought. It also prohibits arbitrary State action (E.P. Royappa)."
        ),
        "citations": [
            {"title": "Constitution of India, Article 14", "description": "Equality before law and equal protection of laws."},
            {"title": "E.P. Royappa v. State of Tamil Nadu (1974)", "description": "Arbitrariness is the antithesis of equality."},
        ],
    },
    {
        "id": "article-19",
        "keywords": ["article 19", "freedom of speech", "freedom of expression", "right to assemble", "fundamental freedoms"],
        "title": "Protection of Certain Freedoms (Article 19)",
        "answer": (
            "Article 19(1) guarantees to all citizens six freedoms, including freedom of speech "
            "and expression, assembly, association, movement, residence, and profession. These "
            "freedoms are not absolute and may be subject to reasonable restrictions under "
            "Articles 19(2)-(6) on grounds such as public order, decency, morality, and the "
            "sovereignty and integrity of India."
        ),
        "citations": [
            {"title": "Constitution of India, Article 19", "description": "Freedom of speech, assembly, movement and profession."},
            {"title": "Shreya Singhal v. Union of India (2015)", "description": "Struck down Section 66A IT Act as violative of Article 19(1)(a)."},
        ],
    },
    {
        "id": "article-32",
        "keywords": ["article 32", "writ", "constitutional remedies", "habeas corpus", "mandamus", "supreme court remedy"],
        "title": "Right to Constitutional Remedies (Article 32)",
        "answer": (
            "Article 32 lets a person move the Supreme Court directly for the enforcement of "
            "fundamental rights, and the Court may issue writs such as habeas corpus, mandamus, "
            "prohibition, quo warranto and certiorari. Dr. Ambedkar called Article 32 the "
            "\"heart and soul\" of the Constitution. High Courts have a similar, wider power "
            "under Article 226."
        ),
        "citations": [
            {"title": "Constitution of India, Article 32", "description": "Right to move the Supreme Court for enforcement of fundamental rights."},
            {"title": "Constitution of India, Article 226", "description": "Power of High Courts to issue writs."},
        ],
    },
    {
        "id": "non-compete",
        "keywords": ["non-compete", "non compete", "restraint of trade", "section 27", "compete"],
        "title": "Non-Compete Clauses and Restraint of Trade",
        "answer": (
            "In India, Section 27 of the Indian Contract Act, 1872 declares every agreement "
            "that restrains a person from exercising a lawful profession, trade or business to "
            "be void to that extent. Post-employment non-compete covenants are therefore "
            "generally unenforceable; only the narrow statutory exception (sale of goodwill) "
            "and reasonable restraints *during* employment tend to hold up. Confidentiality and "
            "non-solicitation obligations are treated more favourably than blanket non-competes."
        ),
        "citations": [
            {"title": "Indian Contract Act, 1872, Section 27", "description": "Agreements in restraint of trade are void."},
            {"title": "Niranjan Shankar Golikari v. Century Spinning (1967)", "description": "Restraints operating during the term of employment may be valid."},
            {"title": "Percept D'Mark v. Zaheer Khan (2006)", "description": "Post-contract restraints are hit by Section 27."},
        ],
    },
    {
        "id": "rental",
        "keywords": ["rent", "rental agreement", "lease", "tenant", "landlord", "leave and license", "security deposit"],
        "title": "Rental / Leave & License Agreements",
        "answer": (
            "Residential tenancies in India are governed by state Rent Control Acts and, for "
            "leave-and-license arrangements, the Maharashtra Rent Control Act / equivalent state "
            "law plus the Registration Act. A sound agreement should clearly state the parties, "
            "licensed premises, licence fee, refundable security deposit, term, lock-in and "
            "notice periods, maintenance and utility responsibilities, and termination rights. "
            "Agreements of 12 months or more generally require registration."
        ),
        "citations": [
            {"title": "Registration Act, 1908, Section 17", "description": "Leases of immovable property from year to year require registration."},
            {"title": "Transfer of Property Act, 1882, Section 105", "description": "Defines a lease of immovable property."},
        ],
    },
    {
        "id": "consumer",
        "keywords": ["consumer", "deficiency in service", "consumer protection", "defective"],
        "title": "Consumer Rights",
        "answer": (
            "The Consumer Protection Act, 2019 lets a consumer complain about defective goods or "
            "deficient services before District, State or National Consumer Commissions, with "
            "pecuniary jurisdiction based on the value of consideration. It also recognises "
            "product liability and unfair trade practices, and allows e-filing and mediation."
        ),
        "citations": [
            {"title": "Consumer Protection Act, 2019", "description": "Framework for consumer dispute redressal and product liability."},
        ],
    },
]

GENERIC_FALLBACK = {
    "title": "General Legal Guidance",
    "answer": (
        "I can offer general legal information, but I could not match your question to a "
        "specific provision in my offline knowledge base. Please rephrase with the relevant "
        "statute, article, or contract type (for example, \"What does Article 21 protect?\" or "
        "\"Are non-compete clauses enforceable in India?\"). For advice on a specific dispute, "
        "consult a licensed advocate. Note: this is informational guidance, not legal advice."
    ),
    "citations": [
        {"title": "Constitution of India", "description": "Primary source for fundamental rights and duties."},
        {"title": "Indian Contract Act, 1872", "description": "Governs the formation and enforceability of contracts."},
    ],
}


def match_entries(query: str):
    """Return knowledge-base entries whose keywords appear in the query."""
    q = (query or "").lower()
    matches = [entry for entry in KNOWLEDGE_BASE if any(k in q for k in entry["keywords"])]
    return matches
