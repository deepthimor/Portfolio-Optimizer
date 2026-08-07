# AI-Powered Portfolio Optimizer

A full-stack portfolio analysis tool that lets users manually enter holdings and view portfolio-level metrics such as total value, holding weights, cash allocation, top holdings, sector exposure, and asset class exposure.

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-Vite-purple.svg)](https://vite.dev/)
[![Status](https://img.shields.io/badge/status-in%20development-pink.svg)](#)

## Problem

Individual investors often hold portfolios across stocks, ETFs, and cash without a clear view of their allocation, cash percentage, or concentration. This project provides a simple way to manually enter holdings and calculate portfolio-level metrics through a full-stack application.

## Target User

This project is designed for individual investors, students, and early-stage fintech users who want a clear breakdown of their portfolio without connecting a brokerage account.

## Overview

The current MVP focuses on deterministic portfolio calculations. Users enter holdings in a React frontend, the frontend sends the portfolio to a FastAPI backend, and the backend returns clean JSON with calculated metrics.

The project is intentionally structured so future AI features can explain the calculated metrics, while the backend remains responsible for the actual financial calculations.

## Dashboard

The current MVP includes a demo-friendly dashboard for entering, analyzing, saving, and explaining portfolios.

![Portfolio Optimizer dashboard screenshot](docs/screenshots/top-holdings-dashboard.png)

### Dashboard Features

- Manual holdings input for ticker, quantity, price, asset class, and sector
- Cash input and cash percentage calculation
- Total portfolio value and total holdings value
- Saved portfolio CRUD backed by PostgreSQL
- Portfolio snapshot support
- Asset allocation chart
- Sector exposure chart
- Top holdings table sorted by weight
- Top holdings chart
- Concentration cards for top 1, top 3, and top 5 exposure
- AI summary panel with portfolio overview, concentration observations, allocation observations, educational note, and limitations
- Visible disclaimer: educational information only; not financial advice
- Fallback behavior when AI summary generation is unavailable

## Live Demo

Live backend API:

```text
https://portfolio-optimizer-033l.onrender.com
```

Production health check:

```text
https://portfolio-optimizer-033l.onrender.com/health
```

Frontend deployment target: Vercel.

The frontend uses this production environment variable:

```text
VITE_API_BASE_URL=https://portfolio-optimizer-033l.onrender.com
```

After the frontend is deployed, add the live frontend link here:

```text
https://portfolio-optimizer-theta.vercel.app
```

## Known Limitations

- Educational information only; not financial advice
- No brokerage integration
- Manual portfolio input only
- Simple deterministic risk model
- No authentication yet
- Does not verify whether ticker symbols are valid securities
- Does not include taxes, fees, historical performance, valuation, or user-specific financial goals

## Current Features

* Manual holdings input for ticker, quantity, price, asset class, and sector
* Cash input and cash percentage calculation
* Total portfolio value calculation
* Total holdings value calculation
* Holding weight calculation
* Top holdings ranking
* Sector allocation breakdown
* Asset class allocation breakdown
* FastAPI backend with clean JSON responses
* React frontend connected to the backend
* PostgreSQL-backed saved portfolio storage
* Create, read, update, and delete portfolio APIs
* Portfolio snapshot creation after analysis
* Basic unit tests for portfolio calculations
* Market data collector files for future historical data work
* Dashboard charts for asset allocation and sector exposure
* Top 1, top 3, and top 5 concentration metrics
* AI summary panel based only on backend-calculated metrics
* AI fallback summary when summary generation is unavailable
* Visible educational disclaimer that the summary is not financial advice

## Planned Features

* Risk metrics
* Target allocation comparison
* Rebalancing recommendations
* Historical market data ingestion
* AI-generated portfolio explanations based only on backend-calculated metrics
* Scenario analysis
* Backtesting engine
* Deployment

## Optimizer v1

The optimizer is a deterministic portfolio review engine that generates structured recommendations from backend-calculated portfolio metrics.

It currently supports:

- Overweight holding detection
- Overweight sector detection
- Underweight asset class detection
- Cash requirement checks
- Balanced / no-action behavior
- Recommendation priority
- Reason-coded recommendation output
- Educational optimizer explanations

## Background Jobs and Scenario Reports

The project now includes a deterministic scenario report workflow backed by persistent report jobs.

Users can generate a scenario report from the frontend. The frontend creates a report job through the backend, receives a `job_id`, and polls the report status endpoint until the job is complete or failed.

### Report Job States

Supported report job states:

- `pending`
- `running`
- `completed`
- `failed`

The frontend displays these as:

- `pending`
- `processing`
- `complete`
- `failed`

### Scenario Report Output

Scenario reports include:

- assumptions
- portfolio impact
- largest losses
- educational explanation
- disclaimer

The report is educational only and does not predict future performance or provide financial advice.

### Worker Command

Run the local report worker with:

```bash
PYTHONPATH=. python scripts/run_worker.py
```

### Architecture Diagram

```mermaid
flowchart LR
    Frontend[React Frontend] --> ReportsAPI[FastAPI Reports API]
    ReportsAPI --> Jobs[(PostgreSQL report_jobs)]
    Jobs --> Worker[Report Worker]
    Worker --> ScenarioEngine[Scenario Report Engine]
    ScenarioEngine --> Jobs
    Frontend --> ReportsAPI
```

### Screenshot

Scenario report UI screenshot:

```text
docs/screenshots/scenario-report-status.png
```

The screenshot should show the report status UI, scenario result sections, and educational disclaimer.

### Recommendation Output

Example recommendation:

```json
{
  "action": "reduce_exposure",
  "ticker": "AAPL",
  "amount_or_percent": 40.0,
  "reason_code": "OVERWEIGHT_HOLDING",
  "human_reason": "AAPL is 70.0% of the portfolio, which is above the max holding threshold of 30.0%.",
  "before_weight": 70.0,
  "after_weight_estimate": 30.0,
  "priority": "high"
}
```

### Reason Codes

The optimizer currently supports:

- `OVERWEIGHT_HOLDING`
- `OVERWEIGHT_SECTOR`
- `BELOW_CASH_TARGET`
- `UNDERWEIGHT_ASSET_CLASS`
- `BALANCED_NO_ACTION`

### AI Explanation Boundary

The optimizer explanation layer only explains deterministic backend recommendations after they have already been generated.

It does not:

- Invent expected returns
- Forecast future prices
- Recommend securities outside the deterministic optimizer output
- Replace professional financial advice
- Use live brokerage or market data

All optimizer output is educational only and not financial advice.

### Runtime Complexity

The optimizer runs in:

```text
O(h + s + g + r log r)
```

Where:

- `h` = number of holdings
- `s` = number of sectors
- `g` = number of target allocation gap rows
- `r` = number of recommendations

## Tech Stack

**Backend**

* Python
* FastAPI
* Pydantic
* SQLAlchemy
* PostgreSQL
* pytest

**Frontend**

* React
* Vite
* Axios
* CSS

**Data Collection**

* yfinance
* Alpha Vantage
* Mock data generator for local testing

**Infrastructure**

* Docker
* Docker Compose
* PostgreSQL
* Redis

## Architecture

```text
React frontend
    |
    | POST /api/portfolio/analyze
    v
FastAPI backend
    |
    | deterministic portfolio calculations
    v
Clean JSON response
    |
    v
Frontend portfolio summary and allocation display
```

For saved portfolios:

```text
React frontend
    |
    | portfolio CRUD requests
    v
FastAPI backend
    |
    | SQLAlchemy
    v
PostgreSQL database
```

## Project Review Materials

Helpful review docs:

- `docs/case-study.md`
- `docs/ai-code-review.md`
- `docs/reliability-security-checklist.md`
- `docs/rag-ui-smoke-test.md`
- `backend/services/README.md`

## Architecture Overview

The project is organized around thin API routes and focused service modules.

```mermaid
flowchart LR
    Frontend[React Frontend] --> PortfolioRoutes[Portfolio Routes]
    Frontend --> ReportRoutes[Report Routes]
    Frontend --> RagRoutes[RAG Routes]

    PortfolioRoutes --> Analytics[Analytics Services]
    Analytics --> Risk[Risk Score]
    Analytics --> Optimizer[Optimizer]
    Optimizer --> OptimizerExplanation[Optimizer Explanation]

    ReportRoutes --> ReportJobs[Report Job Service]
    ReportJobs --> Postgres[(PostgreSQL)]
    Postgres --> Worker[Report Worker]
    Worker --> ScenarioReports[Scenario Report Engine]
    ScenarioReports --> Postgres

    RagRoutes --> RagRetrieval[RAG Retrieval Service]
    RagRetrieval --> FinanceNotes[Finance Notes Chunks]
    RagRetrieval --> RagAnswer[RAG Answer with Citations]

    Analytics --> AiSummary[AI Summary Service]
    RagAnswer --> Frontend
    AiSummary --> Frontend
    ScenarioReports --> Frontend
```

### Backend Organization

- Analytics: portfolio calculations and risk scoring
- Optimizer: deterministic recommendation logic
- Reports: scenario reports and background job lifecycle
- AI: AI-style explanations based only on deterministic outputs
- RAG: finance-note retrieval, citations, and unsupported-question handling
- Database: SQLAlchemy models and database session setup

Routes stay thin and call service modules instead of holding business logic directly.

## Project Structure

```text
portfolio-optimizer/
├── backend/
│   ├── api/
│   │   ├── main.py
│   │   └── routes/
│   │       └── portfolio.py
│   ├── data/
│   │   └── collectors/
│   ├── schemas/
│   │   └── portfolio.py
│   ├── services/
│   │   └── portfolio_analysis.py
│   ├── database.py
│   └── models.py
├── frontend/
│   ├── src/
│   │   ├── services/
│   │   │   └── api.js
│   │   ├── App.jsx
│   │   └── main.jsx
├── scripts/
│   ├── create_tables.py
│   └── setup_database.py
├── tests/
│   └── test_portfolio_analysis.py
├── docs/
│   ├── api-examples.md
│   ├── edge-cases.md
│   ├── product-spec.md
│   └── screenshots/
├── sample_data/
│   └── sample_portfolio.json
├── docker-compose.yml
├── requirements.txt
└── README.md
```

## Quick Start

### Prerequisites

* Python 3.10+
* Node.js 18+
* Docker and Docker Compose
* PostgreSQL, if running without Docker

### Clone the Repository

```bash
git clone https://github.com/deepthimor/Portfolio-Optimizer.git
cd Portfolio-Optimizer
```

### Set Up Environment Variables

```bash
cp .env.example .env
```

Update `.env` with your local database URL if needed.

Example:

```env
DATABASE_URL=postgresql://portfolio_user:change_me_for_local_development@localhost:5433/portfolio_db
```

### Start Infrastructure Services

```bash
docker-compose up -d postgres redis
```

### Backend Setup

From the project root:

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Create local database tables:

```bash
python scripts/create_tables.py
```

Run the backend:

```bash
uvicorn backend.api.main:app --reload
```

Backend URLs:

```text
API root: http://127.0.0.1:8000
API health: http://127.0.0.1:8000/health
API docs: http://127.0.0.1:8000/docs
```

## Database Setup and Schema Summary

The MVP uses PostgreSQL for saved portfolio storage.

Start the local database with Docker Compose:

```bash
docker-compose up -d postgres redis
```

Create local database tables:

```bash
python scripts/create_tables.py
```

The main database tables are:

| Table | Purpose |
|---|---|
| portfolio_records | Stores saved portfolio metadata such as name and cash |
| holding_records | Stores holdings attached to saved portfolios |
| portfolio_snapshots | Stores saved analysis snapshots for portfolios |

Relationship summary:

```text
portfolio_records 1 -> many holding_records
portfolio_records 1 -> many portfolio_snapshots
```

Deleting a portfolio also deletes related holdings and snapshots through SQLAlchemy cascade behavior.

Detailed database design notes are available in:

```text
docs/database-design.md
```

### Frontend Setup

Open a second terminal:

```bash
cd frontend
npm install
npm run dev
```

Frontend URL:

```text
http://localhost:5173
```

If port `5173` is already in use, run:

```bash
npm run dev -- --port 5175
```

Then open:

```text
http://localhost:5175
```

## API Documentation

Full interactive API documentation is available at:

```text
http://127.0.0.1:8000/docs
```

## Backend Deployment Notes

Recommended backend deployment target: Render.

Render is a good fit for this MVP because it supports:
- Python web services
- FastAPI deployment
- Hosted PostgreSQL
- Environment variable configuration
- Simple demo deployments from GitHub

### Required Production Environment Variables

```text
DATABASE_URL=<hosted-postgres-url>
CORS_ORIGINS=<deployed-frontend-origin>
```

### Optional Environment Variables

```text
AI_API_KEY=<not used in current MVP>
```

The current MVP does not require an AI API key because the AI summary is generated from deterministic backend metrics and fallback text.

### Recommended Production Start Command

```bash
uvicorn backend.api.main:app --host 0.0.0.0 --port $PORT
```

### Health Check Endpoint

```text
GET /health
```

Expected response:

```json
{
  "status": "healthy"
}
```

### Production Analyze Endpoint

```text
POST /api/portfolio/analyze
```

This endpoint should return:
- Deterministic portfolio metrics
- Concentration metrics
- Risk score
- Target allocation gap analysis
- AI summary or fallback section

### Production CORS

Set `CORS_ORIGINS` to the deployed frontend domain.

Example:

```text
CORS_ORIGINS=https://your-frontend-domain.vercel.app
```

For multiple origins, use a comma-separated list:

```text
CORS_ORIGINS=https://your-frontend-domain.vercel.app,http://localhost:5173
```

Do not include a trailing slash.

### Production Database Setup

If saved portfolios are included in the deployed demo, create a hosted PostgreSQL database and set:

```text
DATABASE_URL=<hosted-postgres-url>
```

Then create the database tables:

```bash
PYTHONPATH=. python scripts/create_tables.py
```

This project currently uses SQLAlchemy `create_all` for MVP table creation.

## Reliability and Security

The backend includes request ID logging for API requests and report jobs.

Each API request receives an `X-Request-ID` response header. If a client sends an `X-Request-ID`, the backend reuses it. Otherwise, the backend creates one.

Security and reliability rules are documented in:

```text
docs/reliability-security-checklist.md
```

Current safety rules:

- Do not commit real `.env` files.
- Do not commit production database URLs, API keys, tokens, or passwords.
- Keep `.env.example` limited to placeholders.
- Do not log raw portfolio data unless needed for local debugging.
- Do not log API keys, database URLs, passwords, cookies, authorization headers, or tokens.
- Use safe user-facing errors for failed jobs and failed API calls.

### Deployment Log

Deployment errors, fixes, environment variable decisions, and production verification should be documented in:

```text
docs/deployment-log.md
```

### Analyze Portfolio

```http
POST /api/portfolio/analyze
```

Sample request:

```json
{
  "cash": 500,
  "holdings": [
    {
      "ticker": "AAPL",
      "quantity": 5,
      "price": 190,
      "asset_class": "stock",
      "sector": "technology"
    },
    {
      "ticker": "MSFT",
      "quantity": 3,
      "price": 420,
      "asset_class": "stock",
      "sector": "technology"
    }
  ]
}
```

Sample response:

```json
{
  "total_portfolio_value": 2710,
  "total_holdings_value": 2210,
  "cash": 500,
  "cash_percentage": 18.45,
  "holdings": [
    {
      "ticker": "MSFT",
      "quantity": 3,
      "price": 420,
      "market_value": 1260,
      "weight": 46.49,
      "asset_class": "stock",
      "sector": "technology"
    },
    {
      "ticker": "AAPL",
      "quantity": 5,
      "price": 190,
      "market_value": 950,
      "weight": 35.06,
      "asset_class": "stock",
      "sector": "technology"
    }
  ],
  "top_holdings": [
    {
      "ticker": "MSFT",
      "market_value": 1260,
      "weight": 46.49
    },
    {
      "ticker": "AAPL",
      "market_value": 950,
      "weight": 35.06
    }
  ],
  "sector_breakdown": {
    "technology": 81.55
  },
  "asset_class_breakdown": {
    "stock": 81.55
  }
}
```

### Saved Portfolio APIs

```http
POST /api/portfolio
GET /api/portfolio
GET /api/portfolio/{portfolio_id}
PATCH /api/portfolio/{portfolio_id}
DELETE /api/portfolio/{portfolio_id}
POST /api/portfolio/{portfolio_id}/snapshot
```

## Documentation

Additional project documentation is available in the `docs/` folder:

* `docs/product-spec.md` describes the product scope and current MVP.
* `docs/api-examples.md` provides API examples.
* `docs/edge-cases.md` explains validation, duplicate ticker behavior, cash handling, rounding, and tested portfolio scenarios.
* `docs/database-design.md` explains schema, relationships, indexes, and database tradeoffs.

## Testing

Run all tests from the project root:

```bash
PYTHONPATH=. pytest
```

Run the portfolio analysis tests:

```bash
PYTHONPATH=. pytest tests/test_portfolio_analysis.py
```

## Current Limitations

* This project is for educational use only.
* It does not provide financial advice.
* Prices are manually entered in the current MVP.
* There is no brokerage integration.
* There is no authentication yet.
* AI summaries, optimization, risk metrics, and backtesting are planned but not part of the current MVP.

## Development Roadmap

### Phase 1: Portfolio Analysis MVP

* Manual holdings input
* Backend portfolio analysis endpoint
* Frontend holdings form
* Allocation metrics
* PostgreSQL saved portfolios
* Basic tests

### Phase 2: Dashboard and Risk

* Dashboard charts
* Concentration metrics
* Risk score
* Target allocation comparison

### Phase 3: Optimization and AI Explanation

* Rule-based rebalancing recommendations
* AI-generated explanations based only on deterministic backend outputs
* Clear educational disclaimer and fallback behavior

### Phase 4: Scenario Analysis and Deployment

* Scenario reports
* Background jobs
* Frontend and backend deployment
* Demo-ready README and screenshots

## Disclaimer

This project is for educational purposes only. It is not financial advice. Do not use this system for actual trading or investment decisions without proper due diligence and professional guidance. Past performance does not guarantee future results.

## Author

**Deepthi Morusupalli**

* GitHub: [@deepthimor](https://github.com/deepthimor)
* LinkedIn: [Deepthi Morusupalli](https://linkedin.com/in/deepthimor)

## Status

In Development | Last Updated: July 2026
