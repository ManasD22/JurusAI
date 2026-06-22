import {
  ArrowRight,
  ArrowUpRight,
  Bot,
  FileText,
  MessageSquare,
  Pencil,
  ShieldCheck,
  Sparkles,
} from "lucide-react";
import { useNavigate } from "react-router-dom";
import DemoBanner from "../components/DemoBanner.jsx";
import { useAuth } from "../context/AuthContext.jsx";

function greeting() {
  const h = new Date().getHours();
  if (h < 12) return "Morning";
  if (h < 17) return "Afternoon";
  return "Evening";
}

const CARDS = [
  {
    key: "summary",
    title: "Document Summarizer",
    desc: "Transform 100-page contracts into concise 5-point summaries in seconds. Our AI extracts key obligations, dates, and risks with high accuracy.",
    icon: FileText,
    iconClass: "fi-purple",
    action: "Upload Document",
    actionIcon: ArrowRight,
    inline: true,
    to: "/document-summary",
  },
  {
    key: "verify",
    title: "Clause Verification",
    desc: "Instantly verify if your clauses align with current regional case law and regulatory standards. Stay compliant with real-time updates.",
    icon: ShieldCheck,
    iconClass: "fi-amber",
    action: "Verify Now",
    actionIcon: ArrowUpRight,
    to: "/clause-verification",
  },
  {
    key: "chat",
    title: "Legal Chatbot",
    desc: "Ask complex legal questions and receive cited answers from our curated database of supreme court rulings and legislative codes.",
    icon: Bot,
    iconClass: "fi-gray",
    action: "Start Chat",
    actionIcon: MessageSquare,
    to: "/legal-advisor",
  },
  {
    key: "draft",
    title: "Generate Draft",
    desc: "Draft standard NDAs, Employment Agreements, or Lease documents using smart templates that learn from your firm's specific style.",
    icon: Sparkles,
    iconClass: "fi-purple",
    action: "Create Draft",
    actionIcon: Pencil,
    to: "/generate",
  },
];

export default function Home() {
  const { user } = useAuth();
  const navigate = useNavigate();
  const firstName = (user?.full_name || user?.username || "there").split(" ")[0];

  return (
    <div>
      <DemoBanner />
      <h1 className="greeting">
        {greeting()}, {firstName}
      </h1>

      <div className="feature-grid">
        {CARDS.map((c) => {
          const Icon = c.icon;
          const ActionIcon = c.actionIcon;
          return (
            <div
              key={c.key}
              className="feature-card"
              role="button"
              tabIndex={0}
              onClick={() => navigate(c.to)}
              onKeyDown={(e) => e.key === "Enter" && navigate(c.to)}
            >
              <div className={`feature-icon ${c.iconClass}`}>
                <Icon size={26} />
              </div>
              <h3>{c.title}</h3>
              <p>{c.desc}</p>
              {c.inline ? (
                <div className="feature-action" style={{ color: "var(--purple-dark)" }}>
                  <span style={{ display: "inline-flex", alignItems: "center", gap: 8 }}>
                    {c.action} <ActionIcon size={16} />
                  </span>
                </div>
              ) : (
                <div className="feature-action">
                  <span>{c.action}</span>
                  <span className="round">
                    <ActionIcon size={16} />
                  </span>
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
