# Backend Services

The backend is organized around thin API routes and focused service modules.

## Service Areas

### Analytics

Portfolio analysis lives in:

- `backend/services/portfolio_analysis.py`
- `backend/services/risk_score.py`

These modules calculate portfolio value, holdings weights, allocation, concentration, risk score, and target allocation gaps.

### Optimizer

Optimizer logic lives in:

- `backend/services/optimizer.py`
- `backend/services/optimizer_explanation.py`

These modules generate deterministic portfolio recommendations and explain those recommendations without inventing investment advice.

### Reports

Scenario report and background job logic lives in:

- `backend/services/scenario_report.py`
- `backend/services/report_jobs.py`
- `backend/services/report_worker.py`

These modules create report jobs, process pending jobs, store result JSON, and handle failed states.

### AI

AI-style summary logic lives in:

- `backend/services/ai_summary.py`
- `backend/services/optimizer_explanation.py`

These modules explain deterministic backend outputs only.

### RAG

RAG retrieval logic lives in:

- `backend/services/rag_retrieval.py`

This module reads finance notes, parses chunks, retrieves relevant sections, returns citations, and safely rejects unsupported questions.

### Database

Database setup and models live in:

- `backend/database.py`
- `backend/models.py`

These modules configure SQLAlchemy and define persisted records for portfolios, holdings, snapshots, and report jobs.

## API Routes

Routes are intentionally thin:

- `backend/api/routes/portfolio.py`
- `backend/api/routes/reports.py`
- `backend/api/routes/rag.py`

Routes validate requests, call services, and return response models. Business logic should stay in service modules.