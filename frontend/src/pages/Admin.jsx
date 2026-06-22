import {
  Banknote,
  Building2,
  Eye,
  GraduationCap,
  HeartPulse,
  Pencil,
  Plus,
  Search,
  ShieldCheck,
  History as HistoryIcon,
} from "lucide-react";
import { useEffect, useState } from "react";
import { apiTemplates } from "../api/services";
import DemoBanner from "../components/DemoBanner.jsx";

const DEPT_ICONS = {
  education: { Icon: GraduationCap, cls: "fi-purple" },
  health: { Icon: HeartPulse, cls: "fi-amber" },
  finance: { Icon: Banknote, cls: "fi-gray" },
  property: { Icon: Building2, cls: "fi-amber" },
};

export default function Admin() {
  const [departments, setDepartments] = useState([]);
  const [query, setQuery] = useState("");

  useEffect(() => {
    apiTemplates().then((d) => setDepartments(d.departments || []));
  }, []);

  return (
    <div>
      <div className="admin-head">
        <h2 style={{ fontSize: 24 }}>Admin Console</h2>
        <div className="input-icon" style={{ width: 280 }}>
          <Search size={16} />
          <input
            className="input"
            placeholder="Search templates..."
            value={query}
            onChange={(e) => setQuery(e.target.value)}
          />
        </div>
      </div>

      <DemoBanner />

      {/* Template management */}
      <div className="page-eyebrow" style={{ marginBottom: 6 }}>
        System Configuration
      </div>
      <div className="admin-head">
        <h2 style={{ fontSize: 30, fontWeight: 800 }}>Template Management</h2>
        <div className="admin-actions">
          <button className="btn btn-ghost">
            <HistoryIcon size={16} /> Old Templates
          </button>
          <button className="btn btn-primary">
            <Plus size={16} /> Add New Template
          </button>
        </div>
      </div>

      <div className="tpl-mgmt-grid">
        <div className="mgmt-card feature">
          <div className="mgmt-top">
            <div className="tpl-icon fi-purple">
              <ShieldCheck size={20} />
            </div>
            <span className="badge badge-green">Active</span>
          </div>
          <h4>Master Service Agreement</h4>
          <p>
            Comprehensive standard for B2B legal partnerships including liability clauses
            and termination protocols.
          </p>
          <div className="mgmt-foot">
            <span style={{ display: "inline-flex", alignItems: "center", gap: 6 }}>
              <Pencil size={14} /> Edit
            </span>
            <span style={{ display: "inline-flex", alignItems: "center", gap: 6 }}>
              <Eye size={14} /> Preview
            </span>
            <span className="muted">Modified 2h ago</span>
          </div>
        </div>

        <div className="mgmt-card plain">
          <div className="mgmt-top">
            <div className="tpl-icon fi-purple">
              <ShieldCheck size={20} />
            </div>
          </div>
          <h4>Standard NDA</h4>
          <p>Confidentiality and non-disclosure for initial discovery phases.</p>
          <div className="mgmt-foot">
            <span className="muted" style={{ marginLeft: 0 }}>v2.4.1</span>
            <span style={{ display: "inline-flex", alignItems: "center", gap: 6, marginLeft: "auto" }}>
              Edit <Pencil size={14} />
            </span>
          </div>
        </div>
      </div>

      {/* Departments */}
      <div className="page-eyebrow" style={{ marginBottom: 6 }}>
        Classification
      </div>
      <div className="section-row">
        <h2>Templates by Department</h2>
        <span className="link">View All Departments →</span>
      </div>

      <div className="dept-grid">
        {departments.map((d) => {
          const { Icon, cls } = DEPT_ICONS[d.key] || DEPT_ICONS.education;
          return (
            <div className="dept-card" key={d.key}>
              <div className={`dept-icon ${cls}`}>
                <Icon size={20} />
              </div>
              <h4>{d.name}</h4>
              <p>{d.description}</p>
              <div className="dept-foot">
                <span>{String(d.template_count).padStart(2, "0")} Templates</span>
                <span>›</span>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
