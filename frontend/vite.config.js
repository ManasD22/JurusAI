import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// JurisAI React dev server. Runs on http://localhost:5173 by default.
// The Django backend (http://localhost:8000) is allowed via CORS.
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    open: true,
  },
});
