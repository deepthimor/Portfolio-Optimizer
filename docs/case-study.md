# Portfolio Optimizer Case Study

## Problem

Individual investors often see holdings, charts, and account balances, but they may not understand portfolio concentration, allocation drift, cash drag, or scenario risk in plain English.

The goal of this project is to build an educational portfolio analysis app that turns user-provided holdings into clear metrics, risk observations, optimizer recommendations, scenario reports, and finance-note answers.

This project is educational only and does not provide personalized financial advice.

## Stack

Frontend:

- React
- Vite
- Axios
- Recharts
- CSS

Backend:

- Python
- FastAPI
- Pydantic
- SQLAlchemy
- PostgreSQL
- pytest

Infrastructure:

- Render backend
- Render PostgreSQL
- Vercel frontend
- Environment variables for deployment configuration

Documentation and testing:

- README
- Architecture docs
- Reliability and security checklist
- Smoke tests
- Backend unit and API tests

## Architecture

The frontend sends portfolio inputs to FastAPI.

FastAPI keeps route files thin and sends business logic to focused service modules:

- Analytics services calculate portfolio value, allocation, concentration, and risk score.
- Optimizer services generate deterministic recommendation signals.
- Report services create and process scenario report jobs.
- RAG services retrieve educational finance-note chunks and return cited answers.
- AI-style summary services explain deterministic metrics without inventing advice.
- Database modules manage SQLAlchemy setup and persisted models.

The app uses PostgreSQL for saved portfolios, holdings, snapshots, and report jobs.

## Features

Core features:

- Portfolio input form
- Portfolio summary cards
- Allocation charts
- Top holdings table
- Concentration metrics
- Risk score
- Target allocation gap analysis
- Saved portfolio CRUD
- Deterministic optimizer recommendations
- Optimizer explanation panel
- Scenario report job flow
- Report status polling
- RAG finance-notes assistant
- Cited RAG sections
- Unsupported answer state
- Request ID logging
- Basic rate limiting
- Security and reliability documentation

## Hard Problems

### Keeping AI bounded

The app uses AI-style explanations, but the project avoids letting AI invent returns, recommendations, or unsupported facts.

The solution was to make deterministic backend outputs the source of truth. AI-style sections explain only metrics, recommendations, reports, or retrieved finance-note chunks.

### Handling unsupported questions

The RAG assistant should not answer questions like which stock to buy or what will happen tomorrow.

The solution was to return an unsupported state when retrieved context is missing, weak, unsafe, or affected by prompt-injection patterns.

### Making background jobs understandable

Scenario reports can take more than one request-response cycle.

The solution was to create persistent report jobs with clear statuses:

- pending
- running
- completed
- failed

The frontend polls for job status and shows safe user-facing messages.

### Keeping the repo navigable

As the project grew, route files could have become cluttered.

The solution was to organize business logic into service modules and document the backend service map.

## AI Design

AI is used as an explanation layer, not as the source of truth.

Rules:

- Use deterministic portfolio metrics.
- Use backend-generated optimizer recommendations.
- Use retrieved finance-note chunks for RAG answers.
- Cite retrieved educational notes.
- Return fallback or unsupported states when context is missing.
- Do not recommend securities.
- Do not provide personalized investment advice.

## Testing

The test suite covers:

- Portfolio analysis
- Portfolio CRUD APIs
- Risk scoring
- AI summary boundaries and fallback behavior
- Optimizer recommendations
- Optimizer API behavior
- Scenario report calculations
- Report job APIs
- Report worker success and failure paths
- RAG retrieval
- RAG API behavior
- Request ID logging
- API hardening and rate limiting

## Tradeoffs

### In-memory rate limiting

The first version uses in-memory rate limiting because it is simple and dependency-light.

Tradeoff:

- It works for a single backend instance.
- It should be replaced with Redis-backed rate limiting for multi-instance production.

### Deterministic educational logic

The app avoids live trading recommendations and external brokerage integrations.

Tradeoff:

- The app is safer and easier to validate.
- It is not a full financial advisor or trading platform.

### Simple RAG retrieval

The first RAG version uses deterministic retrieval over local finance notes.

Tradeoff:

- It is transparent and testable.
- It can be improved later with embeddings and a vector store.

## Improvements

Future improvements:

- Redis-backed rate limiting
- CI secret scanning
- Staging deployment checks
- More finance-note sources
- Embedding-based RAG retrieval
- Better UI loading states
- Exportable reports
- More scenario types
- More detailed audit logs without sensitive data

## Result

The project now looks production-aware, not just feature-complete.

It includes core portfolio analysis, explainable optimizer logic, background jobs, RAG with citations, failure handling, request IDs, security docs, tests, and a case study that makes the system easier for an interviewer to review.