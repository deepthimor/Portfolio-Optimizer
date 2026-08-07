# AI Code Review Notes

## Goal

Use AI as a code reviewer for correctness, security, maintainability, and testing gaps.

Only valid feedback should be accepted. Any accepted feedback should be documented with the change that was made.

## Review Areas

### Correctness

Reviewed:

- RAG retrieval unsupported states
- Report job failed states
- AI summary fallback behavior
- API validation errors

Accepted feedback:

- Add clearer API error responses with `error`, `message`, and `request_id`.
- Keep RAG retrieval misses unsupported instead of forcing an answer.
- Keep report failures in a failed job state instead of crashing the worker.

Rejected feedback:

- Do not add live brokerage or market-data calls because this project is educational and deterministic.
- Do not make the RAG assistant answer outside retrieved finance notes.

## Security

Reviewed:

- Secrets
- Environment documentation
- Logging behavior
- Rate limiting

Accepted feedback:

- Add request IDs to logs.
- Do not log raw holdings or secrets.
- Add basic in-memory rate limiting for abuse protection.
- Keep `.env.example` limited to placeholders.
- Keep production secrets in deployment provider environment variables.

Rejected feedback:

- Do not commit real Render, database, or API credentials.
- Do not log raw request bodies by default.

## Maintainability

Reviewed:

- Backend service organization
- Thin routes
- Documentation
- Case study readiness

Accepted feedback:

- Keep business logic inside service modules.
- Keep API route files thin.
- Add documentation for backend services, architecture, reliability, and security.
- Add a case study so an interviewer can understand the project quickly.

## Testing Gaps

Reviewed:

- Request ID tests
- RAG tests
- Report worker tests
- API hardening tests

Accepted feedback:

- Add tests for request ID headers.
- Add tests for friendly validation errors.
- Add tests for rate limiting.
- Keep existing tests for RAG unsupported questions and prompt-injection attempts.

## Changes Made

- Added request ID middleware.
- Added request ID logging for API requests and report jobs.
- Added basic rate limiting.
- Added user-friendly API error handlers.
- Replaced AI summary `print` failure logging with structured logging.
- Added reliability and security checklist.
- Added case study documentation.
- Added hardening tests.

## Remaining Future Improvements

- Replace in-memory rate limiting with Redis-backed rate limiting for multi-instance production deployments.
- Add structured JSON logs if deploying to a centralized logging service.
- Add automated secret scanning in CI.
- Add integration tests against deployed staging services.