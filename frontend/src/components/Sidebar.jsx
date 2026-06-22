import {
  FileText,
  Gavel,
  LayoutGrid,
  LogOut,
  Scale,
  ShieldCheck,
  History as HistoryIcon,
  Settings,
} from "lucide-react";
import { useEffect, useState } from "react";
import { NavLink } from "react-router-dom";
import { apiChatHistory } from "../api/services";
import { useAuth } from "../context/AuthContext.jsx";

const NAV = [
  { to: "/home", label: "Home", icon: LayoutGrid },
  { to: "/legal-advisor", label: "Legal Advisor", icon: Scale },
  { to: "/document-summary", label: "Document Summary", icon: FileText },
  { to: "/generate", label: "Generate Document", icon: FileText },
  { to: "/clause-verification", label: "Clause Verification", icon: ShieldCheck },
];

export default function Sidebar() {
  const { user, logout } = useAuth();
  const [history, setHistory] = useState([]);

  useEffect(() => {
    apiChatHistory()
      .then((data) => setHistory(Array.isArray(data) ? data.slice(0, 4) : []))
      .catch(() => setHistory([]));
  }, []);

  const initial = (user?.full_name || user?.username || "U").trim().charAt(0).toUpperCase();

  return (
    <aside className="sidebar">
      <div className="brand">
        <div className="mark">
          <Gavel size={20} strokeWidth={2.2} />
        </div>
        <div>
          <div className="name">JurisAI</div>
          <div className="tag">A Smart Legal Advisor and Document Assistant</div>
        </div>
      </div>

      <nav>
        {NAV.map(({ to, label, icon: Icon }) => (
          <NavLink
            key={to}
            to={to}
            className={({ isActive }) => `nav-item ${isActive ? "active" : ""}`}
          >
            <Icon size={19} />
            <span>{label}</span>
          </NavLink>
        ))}

        {user?.is_staff && (
          <NavLink
            to="/admin"
            className={({ isActive }) => `nav-item ${isActive ? "active" : ""}`}
          >
            <Settings size={19} />
            <span>Admin Console</span>
          </NavLink>
        )}
      </nav>

      {history.length > 0 && (
        <>
          <div className="nav-section">History</div>
          {history.map((h) => (
            <div key={h.id} className="nav-item history">
              <HistoryIcon size={17} />
              <span>{h.title}</span>
            </div>
          ))}
        </>
      )}

      <div className="sidebar-spacer" />

      <div className="sidebar-foot">
        <div className="user-chip">
          <div className="avatar">{initial}</div>
          <div>
            <div className="who">{user?.full_name || user?.username}</div>
            <div className="role">{user?.is_staff ? "Administrator" : "Member"}</div>
          </div>
          <button className="logout-btn" onClick={logout} title="Log out">
            <LogOut size={18} />
          </button>
        </div>
      </div>
    </aside>
  );
}
