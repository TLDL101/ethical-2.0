# Ethical Scanner — Clean API Starter (Docker)

Minimal FastAPI backend with Dockerfile. Works on Railway/Render.

## Endpoints
- `/docs` — Swagger UI
- `/bundles/demo/manifest.json` — quick health check
- `/v1/reports` — evidence upload (multipart)

## Deploy (Railway)
1) Create a new empty GitHub repo.
2) Upload the **unzipped contents** (top level must be `Dockerfile`, `requirements.txt`, `api/`).
3) Railway → New → Deploy from GitHub → pick repo. Leave "Root/Directory" blank; no build command.
4) When live, open `https://<your-app>.up.railway.app/docs`.
