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

## Demo Screenshot

The current MVP lets users manually enter holdings, submit the portfolio to the FastAPI backend, and view calculated portfolio metrics in the React frontend.

![Portfolio Optimizer local app screenshot](docs/screenshots/portfolio-summary.png)

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

## Planned Features

* Dashboard charts
* Risk metrics
* Target allocation comparison
* Rebalancing recommendations
* Historical market data ingestion
* AI-generated portfolio explanations based only on backend-calculated metrics
* Scenario analysis
* Backtesting engine
* Deployment

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
├── sample_data/
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
DATABASE_URL=postgresql://portfolio_user:portfolio_password@localhost:5432/portfolio_db
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

## API Documentation

Full interactive API documentation is available at:

```text
http://127.0.0.1:8000/docs
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

## Testing

Run all tests from the project root:

```bash
pytest
```

Run the portfolio analysis tests:

```bash
pytest tests/test_portfolio_analysis.py
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

In Development | Last Updated: June 2026