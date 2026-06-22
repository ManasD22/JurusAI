import axios from "axios";

const BASE_URL =
  import.meta.env.VITE_API_BASE_URL || "http://localhost:8000/api";

export const TOKEN_KEY = "jurisai_access";
export const REFRESH_KEY = "jurisai_refresh";
export const USER_KEY = "jurisai_user";

// A tiny observable flag so the UI can show a "demo data" badge whenever the
// backend is unreachable and we fall back to local mock responses.
const demoListeners = new Set();
let demoMode = false;

export function isDemoMode() {
  return demoMode;
}
export function setDemoMode(value) {
  if (demoMode !== value) {
    demoMode = value;
    demoListeners.forEach((fn) => fn(value));
  }
}
export function onDemoModeChange(fn) {
  demoListeners.add(fn);
  return () => demoListeners.delete(fn);
}

export const client = axios.create({
  baseURL: BASE_URL,
  timeout: 30000,
});

client.interceptors.request.use((config) => {
  const token = localStorage.getItem(TOKEN_KEY);
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// A request "failed because the server is unreachable" (vs. a real HTTP error
// like 400/401 returned by the backend).
export function isNetworkError(error) {
  return !error.response;
}
