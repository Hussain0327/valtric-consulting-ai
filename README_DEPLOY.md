# ValtricAI – Deployment Guide (Same‑Day Launch)

This repo includes everything to deploy the backend on Render (Docker) and host the frontend statically (Netlify/Vercel/S3). Supabase SQL for the tenant database is included.

## 1) Backend (Render – Docker)

- Prereqs: Render account, a Git repo with this code, your API keys.
- Files used: `Dockerfile`, `render.yaml`

Steps
- Push this repo to GitHub/GitLab.
- In Render, “New +” → “Blueprint” → connect repo → select `render.yaml`.
- Service: `valtricai-backend` (web, Docker). Health path: `/api/v1/health`.
- Set env vars (all required):
  - `ENABLE_TEST_CHAT=true` (exposes `/api/v1/test-chat` for the demo UI)
  - `OPENAI_API_KEY`
  - `GLOBAL_SUPABASE_URL`, `GLOBAL_SUPABASE_ANON_KEY`, `GLOBAL_SUPABASE_SERVICE_ROLE_KEY`
  - `TENANT_SUPABASE_URL`, `TENANT_SUPABASE_ANON_KEY`, `TENANT_SUPABASE_SERVICE_ROLE_KEY`, `TENANT_SUPABASE_JWT_SECRET`
  - Optional: `REDIS_URL` (if using managed Redis). If omitted, caching is disabled gracefully.
- Deploy. The container runs: `uvicorn backend.main:app --host 0.0.0.0 --port 8000`.

Notes
- `.env` loading supports both repo root and `backend/.env` for local dev; on Render, use env vars.
- Redis is optional: if `REDIS_URL` is not set, the app uses a no‑op cache (no startup failure).

## 2) Frontend (Netlify or Vercel)

- Files used: `frontend/chat.html`, `frontend/index.html`, `netlify.toml`
- The chat UI is static; no build required.

Netlify
- New site → “Import from Git”, select repo.
- Build command: `echo 'Static site'` (already in `netlify.toml`).
- Publish directory: `frontend` (already in `netlify.toml`).
- After deploy, open the URL: `https://<your-site>.netlify.app/chat.html?api=https://<render-app>.onrender.com`.
- The UI persists `API_URL` in localStorage; you can omit the `?api=` query param after first load.

Vercel
- Project → Framework: “Other”.
- Output/public dir: `frontend`.
- Open `https://<your-site>.vercel.app/chat.html?api=https://<render-app>.onrender.com`.

S3/CloudFront
- Upload `frontend/*` to your bucket (with `index.html` as default).
- Use the same `?api=` trick for the backend base URL.

## 3) Supabase – Tenant DB Tables + RPC

- In the TENANT Supabase project SQL editor, run:
  - `backend/sql/tenant_setup.sql`
  - `backend/minimal_rpc_function.sql` (recommended minimal RPC for `search_project_chunks_arr`)
- If you already have a function with a different schema, align it or use `minimal_rpc_function.sql` for today’s launch.

## 4) Optional Redis

- If you want caching today, provision a managed Redis and set `REDIS_URL` in Render.
- If not set, the app will still run (cache disabled).

## 5) Smoke Tests

Replace `API` with your backend origin.

- Health checks
  - `GET API/api/v1/health`
  - `GET API/api/v1/monitoring/health`
- Test chat (unauth demo route)
  - `POST API/api/v1/test-chat` with `{ "message": "Give me a SWOT for an AI startup" }`
  - Expect `model_used` and a response message; UI shows the model badge.
- RAG + Exports (end‑to‑end)
  - Ask a SWOT; exports queue will enqueue files. Poll `GET API/api/v1/export/status/{job_id}` if used from the main `/chat` route.
  - Download Excel: `GET API/api/v1/export/excel/{file_id}` (from returned URLs).

## 6) Local Dev

- Install deps: `pip install -r backend/requirements.txt`
- Copy your keys to `backend/.env` (already supported by the settings loader).
- Run: `uvicorn backend.main:app --reload`
- Open: `frontend/chat.html` in a browser with `?api=http://localhost:8000`.

## 7) Troubleshooting

- 401 on secured routes: use the `test-chat` endpoint for the demo UI (it’s unauth when `ENABLE_TEST_CHAT=true`).
- No Redis available: ensure `REDIS_URL` is unset; the app will continue with a no‑op cache.
- Supabase retrieval empty: verify the `search_project_chunks_arr` RPC exists and returns rows.
- OpenAI issues: confirm `OPENAI_API_KEY` is set and valid.

---
This guide and configs are optimized for a same‑day launch. We can harden with proper secrets management, S3 export storage, and auth gating as follow‑ups.
