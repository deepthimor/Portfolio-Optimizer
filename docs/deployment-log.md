# Deployment Log

## Deployment Target

Selected backend deployment target: Render.

Reason:
- Supports FastAPI backend deployment
- Supports hosted PostgreSQL
- Simple environment variable configuration
- Good fit for a demo project

## Production Database

Production database target: hosted PostgreSQL on Render.

Saved portfolios require a production database. If saved portfolio features are included in the deployed demo, the backend must have a valid production `DATABASE_URL`.

Required environment variable:

```text
DATABASE_URL=<actual-render-postgres-url>
```

Use the **Internal Database URL** if the backend service and database are both hosted on Render.

The value should look like this:

```text
postgresql://username:password@hostname:5432/database_name
```

It should not be a placeholder like this:

```text
<your-render-postgres-url>
```

## Required Backend Environment Variables

```text
DATABASE_URL=<actual-render-postgres-url>
CORS_ORIGINS=<deployed-frontend-origin>
PYTHON_VERSION=3.11.9
```

Optional / not currently required:

```text
AI_API_KEY=<not used in current MVP>
```

The current MVP does not require an AI API key because the AI summary panel is generated from deterministic backend metrics and fallback text.

## Backend Deployment Settings

Current backend deployment target: Render Web Service.

Recommended Render backend settings:

```text
Service type: Web Service
Runtime: Python
Root directory: project root
Build command: pip install -r requirements-backend.txt
Start command: uvicorn backend.api.main:app --host 0.0.0.0 --port $PORT
```

## Lightweight Backend Requirements

The deployment uses:

```text
requirements-backend.txt
```

instead of the full development file:

```text
requirements.txt
```

Reason:
- `requirements.txt` contains heavy development/data-science packages that are not required for the backend MVP.
- Render failed while trying to build unnecessary packages like `pandas`.
- The backend only needs FastAPI, Uvicorn, Pydantic, SQLAlchemy, psycopg2, and python-dotenv for the current MVP.

Current backend requirements:

```text
fastapi==0.104.1
uvicorn[standard]==0.24.0
pydantic==2.5.0
sqlalchemy==2.0.23
psycopg2-binary==2.9.9
python-dotenv==1.0.0
```

## Python Version

Render initially used Python 3.14, which caused dependency build failures for `pydantic-core`.

The backend should use Python 3.11.

Current Python version configuration:

```text
PYTHON_VERSION=3.11.9
```

Optional repo file:

```text
.python-version
```

with:

```text
3.11.9
```

## Database Setup

After setting the production `DATABASE_URL`, create database tables by running:

```text
PYTHONPATH=. python scripts/create_tables.py
```

This project currently uses SQLAlchemy `create_all` for MVP table creation.

If running locally against the Render external database URL:

```bash
DATABASE_URL="<render-postgres-external-url>" PYTHONPATH=. python scripts/create_tables.py
```

## Health Check

Production health endpoint:

```text
GET https://<backend-production-url>/health
```

Expected response:

```json
{
  "status": "healthy"
}
```

## Analyze Endpoint Production Test

Production analyze endpoint:

```text
POST https://<backend-production-url>/api/portfolio/analyze
```

Example request:

```json
{
  "cash": 2500,
  "target_allocation": {
    "stock": 60,
    "etf": 30,
    "cash": 10
  },
  "holdings": [
    {
      "ticker": "AAPL",
      "quantity": 20,
      "price": 190,
      "asset_class": "stock",
      "sector": "technology"
    },
    {
      "ticker": "MSFT",
      "quantity": 10,
      "price": 420,
      "asset_class": "stock",
      "sector": "technology"
    },
    {
      "ticker": "VTI",
      "quantity": 18,
      "price": 260,
      "asset_class": "etf",
      "sector": "broad market"
    }
  ]
}
```

Expected result:
- Returns deterministic portfolio metrics
- Returns concentration metrics
- Returns risk score
- Returns target allocation gap analysis
- Returns AI summary or fallback section
- Does not expose secrets

## CORS

Production backend must include the deployed frontend origin in:

```text
CORS_ORIGINS=https://<frontend-production-domain>
```

Do not include a trailing slash.

For multiple allowed origins, use a comma-separated list:

```text
CORS_ORIGINS=https://<frontend-production-domain>,http://localhost:5173
```

## Deployment Errors

| Date | Error | Cause | Fix | Status |
|---|---|---|---|---|
| 2026-07-17 | Build failed: `metadata-generation-failed` for `pandas` | Render was installing the full development `requirements.txt`, which includes heavy packages not needed for the backend MVP | Created `requirements-backend.txt` with only backend deployment dependencies and updated Render build command to `pip install -r requirements-backend.txt` | Fixed |
| 2026-07-17 | Build failed again with `metadata-generation-failed` for `pydantic-core` | Render was using Python 3.14, while the backend dependencies are intended for Python 3.11 | Added Python version configuration and set `PYTHON_VERSION=3.11.9` in Render environment settings | Fixed |
| 2026-07-17 | App crashed on startup: `Could not parse SQLAlchemy URL from string '<your-render-postgres-url>'` | `DATABASE_URL` was still set to a placeholder instead of the actual Render Postgres connection string | Replace placeholder with the real Render Postgres Internal Database URL in backend environment variables | In progress |

## Current Deployment Status

| Item | Status | Notes |
|---|---|---|
| Deployment target chosen | Complete | Render selected |
| Lightweight backend requirements created | Complete | Use `requirements-backend.txt` |
| Render build command updated | Complete | `pip install -r requirements-backend.txt` |
| Python version issue identified | Complete | Render was using Python 3.14 |
| Python version fix applied | Complete | Use `PYTHON_VERSION=3.11.9` |
| Hosted Postgres created | Pending | Required if saved portfolios are included in deployed demo |
| `DATABASE_URL` set | In progress | Must replace placeholder with actual Render Postgres URL |
| `CORS_ORIGINS` set | Pending | Add frontend production URL once available |
| Backend deployed | In progress | Deployment is currently blocked by invalid `DATABASE_URL` |
| `GET /health` verified | Pending | Test after backend starts successfully |
| `POST /api/portfolio/analyze` verified | Pending | Test after backend starts successfully |
| Deployment errors documented | Complete through current blocker | All observed failures through current step are logged above |

## Final Verification Checklist

- [x] Deployment target chosen
- [x] Build dependency issue documented
- [x] Lightweight backend requirements created
- [x] Python version issue documented
- [x] Python version fix identified and applied
- [ ] Hosted Postgres created if saved portfolios are enabled
- [ ] `DATABASE_URL` set to the actual Render Postgres URL
- [ ] `CORS_ORIGINS` set
- [ ] Backend deployed successfully
- [ ] `GET /health` works
- [ ] `POST /api/portfolio/analyze` works against production URL
- [ ] CORS updated for frontend production domain
- [x] Current deployment errors documented with cause and fix

## Next Fix

The current blocker is the `DATABASE_URL`.

Next action:
1. Open the Render PostgreSQL service.
2. Copy the real Internal Database URL.
3. Open the Render backend web service.
4. Replace the placeholder `DATABASE_URL=<your-render-postgres-url>` with the real database URL.
5. Redeploy.
6. If the service starts, test `/health`.
7. If another error appears, add it to the Deployment Errors table above.

## Notes

The repo is deployment-ready when:
- The backend can start with the production `DATABASE_URL`
- `/health` returns `{"status":"healthy"}`
- `/api/portfolio/analyze` works against the production backend URL
- Any deployment failure has a clear error, cause, and next fix documented here