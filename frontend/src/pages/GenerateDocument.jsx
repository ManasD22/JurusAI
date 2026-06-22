import {
  FileText,
  Handshake,
  Home as HomeIcon,
  IdCard,
  Lock,
  ScrollText,
  Sparkles,
} from "lucide-react";
import { useEffect, useState } from "react";
import {
  apiExportPdf,
  apiGenerateDocument,
  apiRecentDrafts,
  apiTemplates,
} from "../api/services";
import DemoBanner from "../components/DemoBanner.jsx";
import Modal from "../components/Modal.jsx";

const ICONS = {
  lock: { Icon: Lock, cls: "fi-purple" },
  badge: { Icon: IdCard, cls: "fi-purple" },
  home: { Icon: HomeIcon, cls: "fi-gray" },
  handshake: { Icon: Handshake, cls: "fi-amber" },
  scroll: { Icon: ScrollText, cls: "fi-purple" },
};

function downloadBlob(blob, filename) {
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  a.click();
  URL.revokeObjectURL(url);
}

export default function GenerateDocument() {
  const [catalog, setCatalog] = useState({ templates: [], categories: ["All Categories"], languages: ["English"] });
  const [drafts, setDrafts] = useState([]);
  const [activeCat, setActiveCat] = useState("All Categories");
  const [customPrompt, setCustomPrompt] = useState("");
  const [language, setLanguage] = useState("English");

  const [modalTemplate, setModalTemplate] = useState(null);
  const [formValues, setFormValues] = useState({});
  const [generating, setGenerating] = useState(false);
  const [output, setOutput] = useState(null);

  useEffect(() => {
    apiTemplates().then((d) => {
      setCatalog(d);
      if (d.languages?.length) setLanguage(d.languages[0]);
    });
    apiRecentDrafts().then((d) => setDrafts(Array.isArray(d) ? d : []));
  }, []);

  const visibleTemplates =
    activeCat === "All Categories"
      ? catalog.templates
      : catalog.templates.filter((t) => t.category === activeCat);

  function openTemplate(tpl) {
    setModalTemplate(tpl);
    setFormValues({});
    setOutput(null);
  }

  async function generateFromTemplate() {
    setGenerating(true);
    try {
      const res = await apiGenerateDocument({
        type: modalTemplate.id,
        details: formValues,
        language,
      });
      setOutput(res);
      refreshDrafts();
    } finally {
      setGenerating(false);
    }
  }

  async function generateCustom() {
    if (!customPrompt.trim()) return;
    setModalTemplate({ id: "custom", name: "Custom Legal Draft", fields: [] });
    setGenerating(true);
    setOutput(null);
    try {
      const res = await apiGenerateDocument({
        custom_request: customPrompt,
        language,
      });
      setOutput(res);
      refreshDrafts();
    } finally {
      setGenerating(false);
    }
  }

  function refreshDrafts() {
    apiRecentDrafts().then((d) => setDrafts(Array.isArray(d) ? d : []));
  }

  async function downloadOutput() {
    if (!output) return;
    const { blob, filename } = await apiExportPdf({
      title: output.title,
      content: output.document,
    });
    downloadBlob(blob, filename);
  }

  return (
    <div>
      <DemoBanner />
      <h1 className="page-title">Generate Draft</h1>
      <p className="page-sub">
        Draft professional legal documents in seconds using smart templates powered by JurisAI.
      </p>

      {/* Custom generation */}
      <div className="card custom-gen">
        <h3>Custom Draft Generation</h3>
        <p>
          Describe the specific requirements, parties involved, and key terms for your document.
          Our AI will synthesize a custom legal draft tailored to your needs.
        </p>
        <textarea
          className="textarea"
          rows={3}
          placeholder="e.g., I need a partnership agreement for a small creative studio with two founders, including profit-sharing clauses and intellectual property protection..."
          value={customPrompt}
          onChange={(e) => setCustomPrompt(e.target.value)}
        />
        <div style={{ display: "flex", alignItems: "center", gap: 14, marginTop: 14 }}>
          <select className="input" style={{ maxWidth: 180 }} value={language} onChange={(e) => setLanguage(e.target.value)}>
            {(catalog.languages || ["English"]).map((l) => (
              <option key={l}>{l}</option>
            ))}
          </select>
          <button className="btn btn-primary" onClick={generateCustom} disabled={!customPrompt.trim()}>
            <Sparkles size={18} /> Generate Custom Draft
          </button>
        </div>
      </div>

      {/* Smart templates */}
      <div className="section-row">
        <h2>Smart Templates</h2>
        <div className="tabs">
          {(catalog.categories || []).slice(0, 4).map((c) => (
            <button
              key={c}
              className={`tab ${activeCat === c ? "active" : ""}`}
              onClick={() => setActiveCat(c)}
            >
              {c}
            </button>
          ))}
        </div>
      </div>

      <div className="template-grid">
        {visibleTemplates.map((t) => {
          const { Icon, cls } = ICONS[t.icon] || ICONS.scroll;
          return (
            <div className="template-card" key={t.id}>
              <div className={`tpl-icon ${cls}`}>
                <Icon size={20} />
              </div>
              <h4>{t.name}</h4>
              <p>{t.description}</p>
              <button className="tpl-btn" onClick={() => openTemplate(t)}>
                Use Template
              </button>
            </div>
          );
        })}
      </div>

      {/* Recent drafts */}
      <div className="card recent">
        <div className="recent-head">
          <h3>Recent Drafts</h3>
          <span className="link">View all activity →</span>
        </div>
        {drafts.length === 0 && <p className="hint">No drafts yet. Generate one above to get started.</p>}
        {drafts.map((d) => (
          <div className="draft-row" key={d.id}>
            <div className="ic">
              <FileText size={18} />
            </div>
            <div>
              <div className="nm">{d.title}</div>
              <div className="meta">Modified {typeof d.updated_at === "string" && d.updated_at.length < 30 ? d.updated_at : "recently"}</div>
            </div>
            <div className="right">
              <span className={`badge ${d.status === "completed" ? "badge-green" : "badge-amber"}`}>
                {d.status}
              </span>
            </div>
          </div>
        ))}
      </div>

      {/* Modal */}
      {modalTemplate && (
        <Modal
          title={output ? output.title : `New ${modalTemplate.name}`}
          wide={!!output}
          onClose={() => {
            setModalTemplate(null);
            setOutput(null);
          }}
        >
          {output ? (
            <>
              <div className="doc-output">{output.document}</div>
              <div style={{ display: "flex", gap: 12, marginTop: 18 }}>
                <button className="btn btn-primary" onClick={downloadOutput}>
                  <FileText size={16} /> Download as PDF
                </button>
                <button className="btn btn-ghost" onClick={() => setOutput(null)}>
                  Edit details
                </button>
              </div>
            </>
          ) : (
            <>
              {modalTemplate.fields?.map((f) => (
                <div className="field" key={f.name}>
                  <label>
                    {f.label}
                    {f.required ? " *" : ""}
                  </label>
                  {f.type === "textarea" ? (
                    <textarea
                      className="textarea"
                      value={formValues[f.name] || ""}
                      onChange={(e) => setFormValues((v) => ({ ...v, [f.name]: e.target.value }))}
                    />
                  ) : (
                    <input
                      className="input"
                      type={f.type === "number" ? "number" : f.type === "date" ? "date" : "text"}
                      value={formValues[f.name] || ""}
                      onChange={(e) => setFormValues((v) => ({ ...v, [f.name]: e.target.value }))}
                    />
                  )}
                </div>
              ))}
              <div className="field">
                <label>Language</label>
                <select className="input" value={language} onChange={(e) => setLanguage(e.target.value)}>
                  {(catalog.languages || ["English"]).map((l) => (
                    <option key={l}>{l}</option>
                  ))}
                </select>
              </div>
              <button className="btn btn-primary btn-block" onClick={generateFromTemplate} disabled={generating}>
                {generating ? <span className="spinner" /> : "Generate Document"}
              </button>
            </>
          )}
        </Modal>
      )}
    </div>
  );
}
