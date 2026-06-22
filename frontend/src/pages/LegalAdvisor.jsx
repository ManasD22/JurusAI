import {
  BookOpen,
  Copy,
  FileText,
  Paperclip,
  Send,
  Share2,
} from "lucide-react";
import { useEffect, useRef, useState } from "react";
import { apiExportPdf, apiLegalAdvice } from "../api/services";
import DemoBanner from "../components/DemoBanner.jsx";

const RELATED_DOCS = [
  { name: "Emp_Agreement_v4.pdf", meta: "2.4 MB • Oct 12" },
  { name: "CA_Labor_Code_Summary.docx", meta: "48 KB • Yesterday" },
];

function downloadBlob(blob, filename) {
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  a.click();
  URL.revokeObjectURL(url);
}

export default function LegalAdvisor() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [jurisdiction, setJurisdiction] = useState("California, USA");
  const [matterType, setMatterType] = useState("Employment Law");
  const scrollRef = useRef(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages, loading]);

  async function send() {
    const query = input.trim();
    if (!query || loading) return;
    setInput("");
    setMessages((m) => [...m, { role: "user", content: query }]);
    setLoading(true);
    try {
      const res = await apiLegalAdvice({
        query,
        jurisdiction,
        matter_type: matterType,
      });
      setMessages((m) => [
        ...m,
        { role: "bot", content: res.answer, citations: res.citations || [] },
      ]);
    } catch (err) {
      setMessages((m) => [
        ...m,
        {
          role: "bot",
          content: "Service temporarily unavailable. Please try again later.",
          citations: [],
        },
      ]);
    } finally {
      setLoading(false);
    }
  }

  async function exportPdf(msg) {
    const citationText = (msg.citations || [])
      .map((c) => `- ${c.title}: ${c.description}`)
      .join("\n");
    const content = `${msg.content}\n\nLegal Citations:\n${citationText}`;
    const { blob, filename } = await apiExportPdf({ title: "Legal Analysis", content });
    downloadBlob(blob, filename);
  }

  return (
    <div>
      <DemoBanner />
      <div className="advisor-grid">
        <div className="chat-panel">
          <div className="chat-head">
            <div className="orb" />
            <h2>Legal Advisor</h2>
            <p>A smart legal advisor and document assistant</p>
          </div>

          <div className="chat-scroll" ref={scrollRef}>
            {messages.length === 0 && (
              <div className="bubble-row">
                <div className="bubble bot">
                  Hello! I&apos;m your JurisAI Legal Advisor. Ask me a question about
                  the Constitution, contracts, employment, tenancy, or any legal topic —
                  I&apos;ll respond with grounded guidance and citations.
                </div>
              </div>
            )}

            {messages.map((m, i) => (
              <div key={i} className={`bubble-row ${m.role === "user" ? "user" : ""}`}>
                <div className={`bubble ${m.role === "user" ? "user" : "bot"}`}>
                  {m.content}

                  {m.role === "bot" && m.citations?.length > 0 && (
                    <div className="citations">
                      <div className="ctitle">
                        <BookOpen size={15} /> Legal Citations
                      </div>
                      {m.citations.map((c, idx) => (
                        <div className="citation" key={idx}>
                          <b>{c.title}</b>
                          <span>{c.description}</span>
                        </div>
                      ))}
                    </div>
                  )}

                  {m.role === "bot" && (
                    <div className="bubble-actions">
                      <button onClick={() => navigator.clipboard?.writeText(m.content)}>
                        <Copy size={14} /> Copy Analysis
                      </button>
                      <button onClick={() => exportPdf(m)}>
                        <Share2 size={14} /> Export PDF
                      </button>
                    </div>
                  )}
                </div>
              </div>
            ))}

            {loading && (
              <div className="bubble-row">
                <div className="bubble bot">
                  <span className="spinner dark" /> Researching…
                </div>
              </div>
            )}
          </div>

          <div className="composer">
            <button className="clip" title="Attach (coming soon)">
              <Paperclip size={18} />
            </button>
            <input
              placeholder="Type your legal query here..."
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && send()}
            />
            <button className="send" onClick={send} disabled={loading}>
              <Send size={18} />
            </button>
          </div>
        </div>

        <aside>
          <div className="card context-card">
            <div className="context-label">Case Context</div>
            <div className="context-field">
              <div className="k">Jurisdiction</div>
              <input
                className="v"
                value={jurisdiction}
                onChange={(e) => setJurisdiction(e.target.value)}
                style={{ border: "none", background: "transparent", width: "100%", outline: "none" }}
              />
            </div>
            <div className="context-field">
              <div className="k">Matter Type</div>
              <input
                className="v"
                value={matterType}
                onChange={(e) => setMatterType(e.target.value)}
                style={{ border: "none", background: "transparent", width: "100%", outline: "none" }}
              />
            </div>
            <div className="context-field">
              <div className="k">Active File</div>
              <div className="v">Vance-NDA-Review-2024</div>
            </div>

            <div className="context-label" style={{ marginTop: 18 }}>
              Related Documents
            </div>
            {RELATED_DOCS.map((d) => (
              <div className="doc-item" key={d.name}>
                <div className="ico">
                  <FileText size={18} />
                </div>
                <div>
                  <div className="nm">{d.name}</div>
                  <div className="meta">{d.meta}</div>
                </div>
              </div>
            ))}
          </div>
        </aside>
      </div>
    </div>
  );
}
