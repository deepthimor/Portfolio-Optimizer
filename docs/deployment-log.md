# Deployment Log

## Live Links

Backend API:

```text
https://portfolio-optimizer-033l.onrender.com
```

Health check:

```text
https://portfolio-optimizer-033l.onrender.com/health
```

Frontend:

```text
<your-vercel-frontend-url>
```

## Deployment Setup

| Area | Setup |
|---|---|
| Backend host | Render |
| Frontend host | Vercel |
| Database | Render PostgreSQL |
| Backend build command | `pip install -r requirements-backend.txt` |
| Backend start command | `uvicorn backend.api.main:app --host 0.0.0.0 --port $PORT` |
| Frontend build command | `npm run build` |
| Frontend output directory | `dist` |

## Environment Variables

Backend environment variables:

```text
DATABASE_URL=<set in Render, not committed>
CORS_ORIGINS=<vercel-frontend-url>,http://localhost:5173
PYTHON_VERSION=3.11.9
```

Frontend environment variables:

```text
VITE_API_BASE_URL=https://portfolio-optimizer-033l.onrender.com
```

No AI API key is required for the current MVP because the AI summary is generated from deterministic backend metrics and fallback text.

## Deployment Issues and Fixes

| Issue | Cause | Fix | Status |
|---|---|---|---|
| Render failed while installing `pandas` | Render was using the full development `requirements.txt` with heavy packages not needed for backend deployment | Created `requirements-backend.txt` and changed Render build command to `pip install -r requirements-backend.txt` | Fixed |
| Render failed on `pydantic-core` | Render used Python 3.14, which caused dependency compatibility issues | Set `PYTHON_VERSION=3.11.9` in Render | Fixed |
| Backend crashed on startup because `DATABASE_URL` was invalid | Render had a placeholder database URL instead of the real Postgres URL | Added the real Render Postgres URL in Render environment variables, without committing it | Fixed |
| Frontend needed production backend connection | Frontend originally pointed to local backend URL | Added `VITE_API_BASE_URL` and set it to the Render backend URL in Vercel | Fixed |
| Backend needed to allow frontend requests | Production frontend origin needed to be allowed by CORS | Added Vercel frontend URL to `CORS_ORIGINS` in Render | Fixed |

## Production Verification

| Check | Status |
|---|---|
| Backend deployed | Complete |
| `GET /health` works | Complete |
| `POST /api/portfolio/analyze` works | Complete |
| Frontend deployed | Complete |
| Frontend loads in incognito | Complete |
| Frontend calls production backend | Complete |
| README includes live links and limitations | Complete |