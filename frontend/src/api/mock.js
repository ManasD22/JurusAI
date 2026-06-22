// Local mock responses used as a graceful fallback whenever the Django backend
// is unreachable. They mirror the sample content in the product mockups so the
// app is fully demoable from `npm run dev` alone.

export const MOCK_TEMPLATES = {
  categories: ["All Categories", "Corporate", "Real Estate", "Employment", "Personal"],
  languages: ["English", "Hindi", "Marathi"],
  templates: [
    {
      id: "nda",
      name: "Non-Disclosure Agreement (NDA)",
      description: "Protect confidential information and trade secrets shared between parties.",
      category: "Corporate",
      icon: "lock",
      fields: [
        { name: "disclosing_party", label: "Disclosing Party", type: "text", required: true },
        { name: "receiving_party", label: "Receiving Party", type: "text", required: true },
        { name: "effective_date", label: "Effective Date", type: "date", required: true },
        { name: "purpose", label: "Purpose of Disclosure", type: "textarea", required: false },
        { name: "term_months", label: "Confidentiality Term (months)", type: "number", required: false },
      ],
    },
    {
      id: "employment",
      name: "Employment Agreement",
      description: "Standardized terms for hiring full-time or part-time employees.",
      category: "Employment",
      icon: "badge",
      fields: [
        { name: "employer", label: "Employer", type: "text", required: true },
        { name: "employee", label: "Employee", type: "text", required: true },
        { name: "position", label: "Position / Designation", type: "text", required: true },
        { name: "salary", label: "Annual CTC / Salary", type: "text", required: true },
        { name: "start_date", label: "Start Date", type: "date", required: true },
        { name: "notice_period", label: "Notice Period", type: "text", required: false },
      ],
    },
    {
      id: "lease",
      name: "Lease Agreement",
      description: "Formalize property rentals for residential or commercial use.",
      category: "Real Estate",
      icon: "home",
      fields: [
        { name: "landlord", label: "Landlord / Licensor", type: "text", required: true },
        { name: "tenant", label: "Tenant / Licensee", type: "text", required: true },
        { name: "property_address", label: "Property Address", type: "textarea", required: true },
        { name: "rent", label: "Monthly Rent", type: "text", required: true },
        { name: "deposit", label: "Security Deposit", type: "text", required: false },
        { name: "duration", label: "Lease Duration", type: "text", required: true },
      ],
    },
    {
      id: "service",
      name: "Service Agreement",
      description: "Define scope of work and payment terms for freelancers and vendors.",
      category: "Corporate",
      icon: "handshake",
      fields: [
        { name: "client", label: "Client", type: "text", required: true },
        { name: "service_provider", label: "Service Provider", type: "text", required: true },
        { name: "scope", label: "Scope of Services", type: "textarea", required: true },
        { name: "fee", label: "Fee / Payment Terms", type: "text", required: true },
        { name: "start_date", label: "Start Date", type: "date", required: false },
      ],
    },
  ],
  departments: [
    { key: "education", name: "Education", description: "Staffing contracts, student waivers, and institutional compliance.", template_count: 12 },
    { key: "health", name: "Health", description: "HIPAA forms, patient consent, and medical provider agreements.", template_count: 8 },
    { key: "finance", name: "Finance", description: "Loan documents, investment terms, and financial risk disclosures.", template_count: 15 },
    { key: "property", name: "Property", description: "Lease agreements, title transfers, and property management deeds.", template_count: 10 },
  ],
};

export const MOCK_DRAFTS = [
  { id: 1, title: "TechSolutions_NDA_Final.docx", doc_type: "nda", language: "English", status: "completed", updated_at: "2 hours ago" },
  { id: 2, title: "Consultancy_Service_Agreement_Draft.docx", doc_type: "service", language: "English", status: "draft", updated_at: "Yesterday" },
];

export const MOCK_HISTORY = [
  { id: 101, title: "Contract Review v1.2", message_count: 4 },
  { id: 102, title: "NDA Interpretation", message_count: 6 },
];

export function mockLegalAdvice(query) {
  const q = (query || "").toLowerCase();
  if (q.includes("non-compete") || q.includes("non compete") || q.includes("compete")) {
    return {
      answer:
        "In India, non-compete agreements are governed by Section 27 of the Indian Contract Act, 1872, which renders every agreement that restrains a person from exercising a lawful profession, trade or business void to that extent. As a result, blanket post-employment non-compete covenants are generally unenforceable. Restraints that operate *during* the term of employment, reasonable confidentiality obligations, and non-solicitation clauses are treated more favourably by Indian courts.\n\nFor a US context (e.g., California), Business & Professions Code §16600 takes an even stronger stance, voiding most non-competes, and the FTC's 2024 rule sought a nationwide ban with narrow exceptions. The practical takeaway is the same: rely on confidentiality and non-solicitation, not broad non-competes.\n\nNote: this is general information, not legal advice.",
      citations: [
        { title: "Indian Contract Act, 1872, Section 27", description: "Agreements in restraint of trade are void." },
        { title: "Niranjan Shankar Golikari v. Century Spinning (1967)", description: "Restraints during the term of employment may be valid." },
        { title: "Cal. Bus. & Prof. Code § 16600", description: "General prohibition against restraints of trade in California." },
      ],
      references: [],
      provider: "demo",
    };
  }
  if (q.includes("article 21") || q.includes("right to life")) {
    return {
      answer:
        "Article 21 of the Constitution of India guarantees that no person shall be deprived of life or personal liberty except according to a procedure established by law. The Supreme Court has read it expansively to include the right to live with dignity, privacy (K.S. Puttaswamy, 2017), livelihood, a clean environment, and a speedy, fair trial. It protects citizens and non-citizens alike.\n\nNote: this is general information, not legal advice.",
      citations: [
        { title: "Constitution of India, Article 21", description: "Protection of life and personal liberty." },
        { title: "Maneka Gandhi v. Union of India (1978)", description: "Procedure under Article 21 must be just, fair and reasonable." },
        { title: "K.S. Puttaswamy v. Union of India (2017)", description: "Right to privacy is a fundamental right under Article 21." },
      ],
      references: [],
      provider: "demo",
    };
  }
  return {
    answer:
      `Here is general guidance on your question: "${query}".\n\nThis demo response is generated locally because the JurisAI backend is not connected. Connect the Django API (and optionally an AI provider key) to get grounded, citation-backed answers from the Legal Advisor module.\n\nNote: this is general information, not legal advice.`,
    citations: [
      { title: "Constitution of India", description: "Primary source for fundamental rights and duties." },
      { title: "Indian Contract Act, 1872", description: "Governs the formation and enforceability of contracts." },
    ],
    references: [],
    provider: "demo",
  };
}

export function mockSummary(filename) {
  return {
    title: "Master Services Agreement",
    parties: ["Global Tech Solutions Inc.", "Innovate Soft LLC"],
    effective_date: "Jan 01, 2024",
    termination_date: "Dec 31, 2026",
    summary:
      "This agreement outlines the provision of software engineering and cloud migration services. The primary focus lies on the iterative delivery of modular architecture with a fixed-fee structure for the first three milestones, transitioning to a time-and-materials basis thereafter. Intellectual property rights are assigned to Global Tech Solutions Inc. upon full payment of each respective milestone.",
    provider: "demo",
    filename: filename || "Master_Services_Agreement.pdf",
    context: "",
    pages: 14,
  };
}

export function mockGenerate({ title, language }) {
  return {
    title: title || "Generated Legal Document",
    doc_type: "custom",
    language: language || "English",
    provider: "demo",
    document:
      `${(title || "LEGAL DOCUMENT").toUpperCase()}\n\nTHIS AGREEMENT is made on [____].\n\n1. PARTIES. This document is entered into between Party A and Party B.\n2. PURPOSE. The parties agree to the terms and obligations described herein.\n3. CONFIDENTIALITY. Each party shall keep confidential information secure.\n4. TERM. This agreement remains in force until terminated per Clause 6.\n5. GOVERNING LAW. This agreement is governed by the laws of India.\n6. TERMINATION. Either party may terminate with 30 days' written notice.\n\n(This is a locally generated demo draft. Connect the backend and an AI provider for full drafting.)\n\nIN WITNESS WHEREOF, the parties have executed this agreement.\n\n_____________________            _____________________\nParty A                          Party B`,
  };
}

export function mockClauseAnalysis(filename) {
  return {
    document_title: filename || "Employment_Contract_v2.docx",
    document_type: "Employment Agreement",
    risk_score: 78,
    risk_level: "HIGH",
    clause_count: 24,
    flagged_clauses: [
      {
        title: "Non-Compete Clause (Clause 4.2)",
        severity: "HIGH RISK",
        loophole:
          'The current wording "unlimited geographical scope" is legally unenforceable in most jurisdictions and exposes the employer to the risk of the entire clause being struck out.',
        corrected_version:
          "The Employee agrees not to compete within a 50-mile radius of the headquarters for a period of 12 months post-termination.",
      },
      {
        title: "Termination Notice (Clause 7.1)",
        severity: "INCONSISTENT",
        loophole:
          'Vague definition of "reasonable notice". Does not align with the statutory minimums of the governing state law (Delaware).',
        corrected_version:
          "Either party may terminate this agreement by providing 30 days' written notice, or as required by applicable state law.",
      },
    ],
    verified_clauses: ["Employee Details", "Employer Details", "Salary Clause"],
    missing_clauses: ["Non-Compete Clause", "Termination Notice"],
    recommendations: [],
    provider: "demo",
    extracted_text: "",
  };
}
