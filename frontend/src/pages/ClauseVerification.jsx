import {
  BarChart3,
  Download,
  FileCheck2,
  FileUp,
  Share2,
  UploadCloud,
} from "lucide-react";
import { useRef, useState } from "react";
import { apiAnalyzeClauses, apiExportPdf } from "../api/services";
import DemoBanner from "../components/DemoBanner.jsx";

function severityClass(sev) {
  const s = (sev || "").toUpperCase();
  if (s.includes("HIGH")) return { box: "", badge: "badge-red" };
  if (s.includes("INCONSIST")) return { box: "inconsistent", badge: "badge-purple" };
  if (s.includes("MED")) return { box: "medium", badge: "badge-amber" };
  return { box: "low", badge: "badge-green" };
}

function downloadBlob(blob, filename) {
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  a.click();
  URL.revokeObjectURL(url);
}

export default function ClauseVerification() {
  const [file, setFile] = useState(null);
  const [drag, setDrag] = useState(false);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");
  const inputRef = useRef(null);

  function pick(f) {
    if (!f) return;
    if (!/\.(pdf|docx|txt)$/i.test(f.name)) {
      setError("Invalid file format. Please upload PDF, DOCX or TXT.");
      return;
    }
    setError("");
    setFile(f);
  }

  async function run() {
    if (!file || loading) return;
    setLoading(true);
    setError("");
    try {
      const data = await apiAnalyzeClauses(file);
      setResult(data);
    } catch (err) {
      setError(err?.response?.data?.error || "Unable to verify document at this time.");
    } finally {
      setLoading(false);
    }
  }

  async function downloadCorrected() {
    if (!result) return;
    const body = (result.flagged_clauses || [])
      .map(
        (c, i) =>
          `${i + 1}. ${c.title} [${c.severity}]\n   Issue: ${c.loophole}\n   Corrected: ${c.corrected_version}`
      )
      .join("\n\n");
    const content =
      `Document: ${result.document_title}\nType: ${result.document_type}\n` +
      `Risk Score: ${result.risk_score}%  |  Clauses analyzed: ${result.clause_count}\n\n` +
      `FLAGGED CLAUSES & CORRECTIONS\n\n${body}`;
    const { blob, filename } = await apiExportPdf({
      title: `Corrected_${result.document_title}`,
      content,
    });
    downloadBlob(blob, filename);
  }

  return (
    <div>
      <div className="page-eyebrow">Clause Verification</div>
      <DemoBanner />

      <div className="verify-grid">
        {/* Left: upload + stats */}
        <div>
          <div className="card" style={{ padding: 20 }}>
            <div style={{ display: "flex", alignItems: "center", gap: 12, marginBottom: 14 }}>
              <div className="feature-icon fi-purple" style={{ width: 40, height: 40, margin: 0 }}>
                <UploadCloud size={20} />
              </div>
              <div>
                <div style={{ fontWeight: 700 }}>Upload Document</div>
                <div className="hint">PDF, DOCX or TXT supported</div>
              </div>
            </div>

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
                pick(e.dataTransfer.files?.[0]);
              }}
              style={{ padding: "28px 18px" }}
            >
              <input
                ref={inputRef}
                type="file"
                accept=".pdf,.docx,.txt"
                hidden
                onChange={(e) => pick(e.target.files?.[0])}
              />
              <div className="up-icon">
                <FileUp size={26} />
              </div>
              <h4 style={{ fontSize: 16 }}>Drag and drop file here</h4>
              <p style={{ fontSize: 13 }}>or click to browse local files</p>
              {file && <div className="file-pill"><FileCheck2 size={14} /> {file.name}</div>}
            </div>

            <button
              className="btn btn-primary btn-block"
              style={{ marginTop: 16 }}
              onClick={run}
              disabled={!file || loading}
            >
              {loading ? <span className="spinner" /> : "Run AI Verification"}
            </button>
            {error && <p className="error-text">{error}</p>}
          </div>

          {result && (
            <div className="stats-card">
              <div className="stats-head">
                <span>Verification Stats</span>
                <BarChart3 size={18} style={{ color: "var(--purple)" }} />
              </div>
              <div className="stats-row">
                <div className="stat-box">
                  <div className="lbl">Risk Score</div>
                  <div className="val risk">{result.risk_score}%</div>
                </div>
                <div className="stat-box">
                  <div className="lbl">Clauses</div>
                  <div className="val ok">{result.clause_count}</div>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Right: results */}
        <div className="card results-card">
          {loading ? (
            <div className="center-load">
              <span className="spinner dark" /> Running AI clause verification…
            </div>
          ) : result ? (
            <>
              <div className="results-head">
                <FileCheck2 size={20} style={{ color: "var(--purple)" }} />
                <h3>{result.document_title}</h3>
                <div className="spacer" />
                <button className="act" onClick={downloadCorrected}>
                  <Download size={16} /> Download Corrected
                </button>
                <button className="act" title="Share">
                  <Share2 size={16} />
                </button>
              </div>

              {(result.flagged_clauses || []).map((c, i) => {
                const cls = severityClass(c.severity);
                return (
                  <div className={`flagged ${cls.box}`} key={i}>
                    <div className="flagged-title">
                      <span className={`badge ${cls.badge}`}>{c.severity}</span>
                      {c.title}
                    </div>
                    <div className="compare">
                      <div className="box loop">
                        <div className="h">Identified Loop Holes</div>
                        <p>{c.loophole}</p>
                      </div>
                      <div className="box fix">
                        <div className="h">Corrected Version</div>
                        <p>{c.corrected_version}</p>
                      </div>
                    </div>
                  </div>
                );
              })}

              {result.recommendations?.length > 0 && (
                <div style={{ marginTop: 8 }}>
                  <div className="section-label">Recommendations</div>
                  <ul style={{ margin: 0, paddingLeft: 18, color: "var(--text-soft)" }}>
                    {result.recommendations.map((r, i) => (
                      <li key={i} style={{ marginBottom: 6 }}>{r}</li>
                    ))}
                  </ul>
                </div>
              )}
            </>
          ) : (
            <div className="placeholder-panel">
              <div>
                <FileCheck2 size={40} style={{ color: "var(--muted-2)" }} />
                <p style={{ marginTop: 12 }}>
                  Upload a contract and run AI verification to see flagged loopholes,
                  corrected wording and a risk score here.
                </p>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
