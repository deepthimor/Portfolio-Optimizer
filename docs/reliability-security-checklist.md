# Reliability and Security Checklist

## Goal

Keep the Portfolio Optimizer safe, debuggable, and easy to operate.

This checklist covers logging, request IDs, secrets, validation, rate limiting, failed AI calls, failed jobs, and safe errors.

## Logging

Current status:

- API requests use structured logs.
- Logs include request method, path, status code, duration, and request ID.
- Report worker logs include job ID, status transitions, duration, and request ID.

Rules:

- Do not log raw portfolio holdings unless needed for a specific local debugging task.
- Do not log full request bodies by default.
- Do not log API keys, database URLs, tokens, passwords, cookies, or authorization headers.
- Prefer IDs, counts, statuses, and durations over raw user data.

## Request IDs

Current status:

- Every API request receives a request ID.
- If the client sends `X-Request-ID`, the backend reuses it.
- If the client does not send `X-Request-ID`, the backend creates one.
- Responses include `X-Request-ID`.

Why this matters:

- Request IDs make frontend errors, backend logs, and report jobs easier to connect.
- They help debug production issues without logging sensitive data.

## Secrets

Current status:

- Real secrets should not be committed to the repo.
- `.env.example` should contain placeholders only.
- Production secrets should be stored in deployment provider environment variables.

Rules:

- Never commit `.env`.
- Never commit real database URLs.
- Never commit API keys or tokens.
- Never paste hosted database passwords into docs, tests, sample data, or README files.
- Rotate any secret that was accidentally shared or committed.

Recommended checks:

```bash
git status
git grep -n "sk-"
git grep -n "postgresql://"
git grep -n "API_KEY"
git grep -n "PASSWORD"
git grep -n "SECRET"
```

Notes:

- Placeholder values such as `your_alpha_vantage_key_here` or `change_me_for_local_development` are acceptable in `.env.example`.
- Real production values are not acceptable in tracked files.

## Validation

Current status:

- FastAPI and Pydantic validate API request and response shapes.
- Portfolio and report schemas reject malformed inputs before service logic runs.
- RAG requests require a non-empty question.

Rules:

- Keep request validation in schemas.
- Keep business logic validation in services.
- Return safe, user-readable errors.
- Do not expose stack traces to frontend users.

## Rate Limiting

Current status:

- Basic in-memory rate limiting is implemented.
- The rate limit uses the `RATE_LIMIT_PER_MINUTE` environment variable.
- The current implementation limits repeated requests by client host and path.
- When the limit is exceeded, the API returns a safe `429 Too Many Requests` response.
- The response includes a user-friendly message, `request_id`, `X-Request-ID`, and `Retry-After`.

Rules:

- Keep rate-limit responses safe and user-readable.
- Do not log raw request bodies when rate limits are exceeded.
- Keep rate limiting stricter for AI/RAG endpoints if the app expands.

Recommended future improvement:

- Replace in-memory rate limiting with Redis-backed rate limiting for multi-instance production deployments.

## Failed AI Calls

Current status:

- Current AI-style outputs are deterministic and fallback-based.
- The system should not depend on external AI calls for core portfolio calculations.

Rules for future external AI calls:

- Never block deterministic analysis if an AI call fails.
- Return a fallback explanation when AI is unavailable.
- Log only error type, request ID, and safe metadata.
- Do not log prompts that include raw portfolio data unless explicitly needed in local development.

## Failed Jobs

Current status:

- Report jobs support `pending`, `running`, `completed`, and `failed`.
- Failed jobs store user-friendly error messages.
- Worker logs include job ID, request ID, status transition, and duration.

Rules:

- Failed jobs should not crash the worker loop.
- Failed jobs should store safe error messages.
- Logs should avoid raw request payloads.
- Users should see retryable failure states in the UI.

## Safe Errors

Current status:

- API routes raise HTTP errors.
- Report worker converts known failures into user-friendly messages.
- Frontend displays friendly failure messages for report and RAG flows.

Rules:

- Do not expose stack traces to users.
- Do not expose secrets in errors.
- Do not include raw database URLs, API keys, or tokens in error messages.
- Use clear user-facing messages with enough context to retry or fix input.

## Environment Documentation

Local setup should use:

```text
DATABASE_URL=postgresql://portfolio_user:change_me_for_local_development@localhost:5433/portfolio_db
CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
VITE_API_BASE_URL=http://127.0.0.1:8000
```

Production setup should use deployment environment variables.

Production should not use committed secrets.

## Clean Clone Verification

From a clean clone, verify:

```bash
cp .env.example .env
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
PYTHONPATH=. pytest
cd frontend
npm install
npm run build
```

Pass criteria:

- Backend tests pass.
- Frontend build passes.
- No real secrets are committed.
- API request logs include request IDs.
- Report worker logs include request IDs and job IDs.
- Setup docs do not require private data.