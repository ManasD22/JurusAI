# JurisAI Frontend

React (Vite) single-page app for the JurisAI Legal AI platform.

## Run

```bash
npm install
npm run dev      # http://localhost:5173
npm run build    # production build into dist/
npm run preview  # preview the production build
```

## Configuration

Create `.env` (see `.env.example`):

```
VITE_API_BASE_URL=http://localhost:8000/api
```

## Pages
- `/login`, `/register` — authentication
- `/home` — dashboard
- `/legal-advisor` — chatbot with citations
- `/document-summary` — upload + AI summary + Q&A
- `/generate` — template-driven & custom document drafting
- `/clause-verification` — contract loophole/risk analysis
- `/admin` — template management (staff users)

## Demo mode
If the backend is unreachable, the app serves realistic local sample data
(`src/api/mock.js`) so every screen remains fully demoable. A banner appears whenever
demo data is in use.
