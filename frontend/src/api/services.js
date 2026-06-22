import { client, isNetworkError, setDemoMode } from "./client";
import {
  MOCK_DRAFTS,
  MOCK_HISTORY,
  MOCK_TEMPLATES,
  mockClauseAnalysis,
  mockGenerate,
  mockLegalAdvice,
  mockSummary,
} from "./mock";

// Run a real API call; if the backend is unreachable, switch on demo mode and
// return the provided local fallback instead. Real HTTP errors (400/401/...)
// are re-thrown so the UI can show proper validation messages.
async function withFallback(realCall, fallback) {
  try {
    const res = await realCall();
    setDemoMode(false);
    return res.data;
  } catch (error) {
    if (isNetworkError(error) && fallback !== undefined) {
      setDemoMode(true);
      return typeof fallback === "function" ? fallback() : fallback;
    }
    throw error;
  }
}

/* ------------------------------------------------------------------ Auth */
export async function apiLogin({ username, password }) {
  return withFallback(
    () => client.post("/auth/login/", { username, password }),
    () => {
      const email = username.includes("@") ? username : `${username}@jurisai.demo`;
      const namePart = (email.split("@")[0] || "User").replace(/[._-]/g, " ");
      const full_name = namePart.replace(/\b\w/g, (c) => c.toUpperCase());
      return {
        access: "demo-token",
        refresh: "demo-refresh",
        user: {
          id: 0,
          username,
          email,
          full_name,
          is_staff: /admin/i.test(username),
        },
      };
    }
  );
}

export async function apiRegister({ full_name, email, password }) {
  return withFallback(
    () => client.post("/auth/register/", { full_name, email, password }),
    () => ({
      access: "demo-token",
      refresh: "demo-refresh",
      user: {
        id: 0,
        username: email.split("@")[0],
        email,
        full_name: full_name || email.split("@")[0],
        is_staff: /admin/i.test(email),
      },
    })
  );
}

export async function apiProfile() {
  return withFallback(() => client.get("/auth/profile/"), undefined);
}

/* -------------------------------------------------------- Legal Advisor */
export async function apiLegalAdvice(payload) {
  return withFallback(
    () => client.post("/chatbot/advice/", payload),
    () => mockLegalAdvice(payload.query)
  );
}

export async function apiChatHistory() {
  return withFallback(() => client.get("/chatbot/history/"), () => MOCK_HISTORY);
}

/* ----------------------------------------------------------- Summarizer */
export async function apiSummarize(file) {
  const form = new FormData();
  form.append("file", file);
  return withFallback(
    () =>
      client.post("/summarizer/summarize/", form, {
        headers: { "Content-Type": "multipart/form-data" },
      }),
    () => mockSummary(file?.name)
  );
}

export async function apiAskDocument(context, question) {
  return withFallback(
    () => client.post("/summarizer/ask/", { context, question }),
    () => ({
      answer:
        "Demo mode: connect the backend to ask grounded questions about this document.",
      provider: "demo",
    })
  );
}

/* --------------------------------------------------------- Documents */
export async function apiTemplates() {
  return withFallback(() => client.get("/documents/templates/"), () => MOCK_TEMPLATES);
}

export async function apiGenerateDocument(payload) {
  return withFallback(
    () => client.post("/documents/generate/", payload),
    () =>
      mockGenerate({
        title: payload.custom_request ? "Custom Legal Draft" : payload.type,
        language: payload.language,
      })
  );
}

export async function apiRecentDrafts() {
  return withFallback(() => client.get("/documents/drafts/"), () => MOCK_DRAFTS);
}

export async function apiExportPdf({ title, content }) {
  // Returns a Blob for download. Falls back to a client-side text blob.
  try {
    const res = await client.post(
      "/documents/export/",
      { title, content },
      { responseType: "blob" }
    );
    setDemoMode(false);
    return { blob: res.data, filename: `${safeName(title)}.pdf` };
  } catch (error) {
    if (isNetworkError(error)) {
      setDemoMode(true);
      const blob = new Blob([`${title}\n\n${content}`], { type: "text/plain" });
      return { blob, filename: `${safeName(title)}.txt` };
    }
    throw error;
  }
}

/* -------------------------------------------------- Clause verification */
export async function apiAnalyzeClauses(file) {
  const form = new FormData();
  form.append("file", file);
  return withFallback(
    () =>
      client.post("/clauses/analyze/", form, {
        headers: { "Content-Type": "multipart/form-data" },
      }),
    () => mockClauseAnalysis(file?.name)
  );
}

function safeName(title) {
  return (title || "document").replace(/[^A-Za-z0-9_-]+/g, "_").slice(0, 60);
}
