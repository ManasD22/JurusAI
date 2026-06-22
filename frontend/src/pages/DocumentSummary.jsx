import { FileText, FileUp, Send } from "lucide-react";
import { useRef, useState } from "react";
import { apiAskDocument, apiExportPdf, apiSummarize } from "../api/services";
import DemoBanner from "../components/DemoBanner.jsx";

function downloadBlob(blob, filename) {
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  a.click();
  URL.revokeObjectURL(url);
}

export default function DocumentSummary() {
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [drag, setDrag] = useState(false);
  const [question, setQuestion] = useState("");
  const [qa, setQa] = useState([]);
  const [asking, setAsking] = useState(false);
  const inputRef = useRef(null);

  async function handleFile(file) {
    if (!file) return;
    const ok = /\.(pdf|docx|txt)$/i.test(file.name);
    if (!ok) {
      setError("Invalid file format. Please upload PDF or DOCX.");
      return;
    }
    setError("");
    setLoading(true);
    setQa([]);
    try {
      const data = await apiSummarize(file);
      setResult(data);
    } catch (err) {
      setError(err?.response?.data?.error || "Could not summarize the document.");
    } finally {
      setLoading(false);
    }
  }

  async function ask() {
    const q = question.trim();
    if (!q || asking) return;
    setQuestion("");
    setQa((arr) => [...arr, { role: "user", text: q }]);
    setAsking(true);
    try {
      const res = await apiAskDocument(result?.context || result?.summary || "", q);
      setQa((arr) => [...arr, { role: "bot", text: res.answer }]);
    } finally {
      setAsking(false);
    }
  }

  async function download() {
    if (!result) return;
    const parties = (result.parties || []).join(", ");
    const content =
      `${result.title}\n\nContracting Parties: ${parties}\n` +
      `Effective: ${result.effective_date || "N/A"}\n` +
      `Termination: ${result.termination_date || "N/A"}\n\nExecutive Summary:\n${result.summary}`;
    const { blob, filename } = await apiExportPdf({ title: result.title, content });
    downloadBlob(blob, filename);
  }

  return (
    <div>
      <div className="page-eyebrow">Document Summary</div>
      <DemoBanner />

      <div className="split-two">
        {/* Upload */}
        <div
          className={`dropzone ${drag ? "drag" : ""}`}
          onClick={() => inputRef.current?.click()}
          onDragOver={(e) => {
            e.preventDefault();
            setDrag(true);
          }}
          onDragLeave={() => setDrag(false)}
          onDrop={(e) => {
            e.preventDefault();
            setDrag(false);
            handleFile(e.dataTransfer.files?.[0]);
          }}
        >
          <input
            ref={inputRef}
            type="file"
            accept=".pdf,.docx,.txt"
            hidden
            onChange={(e) => handleFile(e.target.files?.[0])}
          />
          <div className="up-icon">
            <FileUp size={28} />
          </div>
          <h4>Upload Legal Document</h4>
          <p>Drag and drop your PDF or DOCX file here for an instant AI-powered summary and analysis.</p>
          <button className="btn btn-primary" type="button">
            Choose File
          </button>
          <div className="tiny">Maximum size: 50MB. PDF, DOCX or TXT supported.</div>
          {error && <p className="error-text">{error}</p>}
        </div>

        {/* Result */}
        <div className="card summary-panel">
          {loading ? (
            <div className="center-load">
              <span className="spinner dark" /> Analyzing document…
            </div>
          ) : result ? (
            <>
              <div className="summary-head">
                <div>
                  <span className="badge badge-purple">AI Analysis Complete</span>
                  <h3>{result.title}</h3>
                  <div className="processed">
                    Processed just now{result.pages ? ` • ${result.pages} Pages` : ""}
                  </div>
                </div>
                <button className="btn btn-ghost" onClick={download}>
                  <FileText size={16} /> Download as PDF
                </button>
              </div>

              <div className="kv-grid">
                <div>
                  <h5>Contracting Parties</h5>
                  <ul>
                    {(result.parties && result.parties.length
                      ? result.parties
                      : ["Not identified"]
                    ).map((p, i) => (
                      <li key={i}>
                        <span className="dot" />
                        {p}
                      </li>
                    ))}
                  </ul>
                </div>
                <div>
                  <h5>Key Dates</h5>
                  <ul>
                    <li>
                      Effective: <b>{result.effective_date || "—"}</b>
                    </li>
                    <li>
                      Termination: <b>{result.termination_date || "—"}</b>
                    </li>
                  </ul>
                </div>
              </div>

              <div className="section-label">Executive Summary</div>
              <p className="exec-summary">{result.summary}</p>

              {qa.length > 0 && (
                <div style={{ marginTop: 22 }}>
                  <div className="section-label">Q&amp;A</div>
                  {qa.map((m, i) => (
                    <div key={i} className={`bubble-row ${m.role === "user" ? "user" : ""}`} style={{ marginBottom: 10 }}>
                      <div className={`bubble ${m.role === "user" ? "user" : "bot"}`} style={{ maxWidth: "90%" }}>
                        {m.text}
                      </div>
                    </div>
                  ))}
                </div>
              )}

              <div className="composer" style={{ marginTop: 20 }}>
                <input
                  placeholder="e.g., 'What is the governing law?'"
                  value={question}
                  onChange={(e) => setQuestion(e.target.value)}
                  onKeyDown={(e) => e.key === "Enter" && ask()}
                />
                <button className="send" onClick={ask} disabled={asking}>
                  {asking ? <span className="spinner" /> : <Send size={18} />}
                </button>
              </div>
            </>
          ) : (
            <div className="placeholder-panel">
              <div>
                <FileText size={40} style={{ color: "var(--muted-2)" }} />
                <p style={{ marginTop: 12 }}>
                  Upload a document to see its AI summary, parties, key dates and an
                  interactive Q&amp;A here.
                </p>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
