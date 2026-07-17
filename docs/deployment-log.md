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

Saved portfolios require a production database. If the deployed demo does not include saved portfolios, that limitation should be documented clearly.

Required environment variable:

```text
DATABASE_URL=<render-postgres-internal-or-external-url>
```

## Required Backend Environment Variables

```text
DATABASE_URL=<hosted-postgres-url>
CORS_ORIGINS=<deployed-frontend-origin>
```

Optional / not currently required:

```text
AI_API_KEY=<not used in current MVP>
```

The current MVP does not require an AI API key because the AI summary panel is generated from deterministic backend metrics and fallback text.

## Backend Deployment Settings

Recommended Render backend settings:

```text
Service type: Web Service
Runtime: Python
Root directory: project root
Build command: pip install -r requirements.txt
Start command: uvicorn backend.api.main:app --host 0.0.0.0 --port $PORT
```

## Database Setup

After setting `DATABASE_URL`, create tables by running:

```text
PYTHONPATH=. python scripts/create_tables.py
```

This project currently uses SQLAlchemy `create_all` for MVP table creation.

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

Use this table to document every deployment issue with the error, cause, fix, and status.

| Date | Error | Cause | Fix | Status |
|---|---|---|---|---|
| TBD | TBD | TBD | TBD | TBD |

## Example Error Log Rows

Use rows like these if similar errors happen:

| Date | Error | Cause | Fix | Status |
|---|---|---|---|---|
| 2026-07-16 | Build failed: missing dependency | `requirements.txt` did not include a package used by the backend | Added missing package and redeployed | Fixed |
| 2026-07-16 | App crashed on startup | `DATABASE_URL` was missing or incorrect | Added the hosted Postgres URL to environment variables | Fixed |
| 2026-07-16 | Frontend could not call backend | Production frontend origin was missing from CORS settings | Added deployed frontend URL to `CORS_ORIGINS` | Fixed |
| 2026-07-16 | Database tables missing | Hosted Postgres existed but tables were not created | Ran `PYTHONPATH=. python scripts/create_tables.py` with production `DATABASE_URL` | Fixed |

## Current Deployment Status

| Item | Status | Notes |
|---|---|---|
| Deployment target chosen | Complete | Render selected |
| Hosted Postgres created | Pending | Required if saved portfolios are included in deployed demo |
| `DATABASE_URL` set | Pending | Use hosted Postgres URL |
| `CORS_ORIGINS` set | Pending | Add deployed frontend URL once available |
| Backend deployed | Pending | Deploy after env vars are configured |
| `GET /health` verified | Pending | Expected response: `{"status":"healthy"}` |
| `POST /api/portfolio/analyze` verified | Pending | Test against production backend URL |
| Deployment errors documented | Pending | Add rows above as errors occur |

## Final Verification Checklist

- [x] Deployment target chosen
- [ ] Hosted Postgres created if saved portfolios are enabled
- [ ] `DATABASE_URL` set
- [ ] `CORS_ORIGINS` set
- [ ] Backend deployed
- [ ] `GET /health` works
- [ ] `POST /api/portfolio/analyze` works against production URL
- [ ] CORS updated for frontend production domain
- [ ] Any deployment errors documented with cause and fix

## Notes

The repo is deployment-ready when:
- The backend can start with the production `DATABASE_URL`
- `/health` returns `{"status":"healthy"}`
- `/api/portfolio/analyze` works against the production backend URL
- Any deployment failure has a clear error, cause, and next fix documented here