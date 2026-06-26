# API Examples

This document contains sample requests and responses for the Portfolio Optimizer backend API.

## Health Check

### Request

```http
GET /health
```

### Response

```json
{
  "status": "healthy"
}
```

## Analyze Portfolio

### Endpoint

```http
POST /api/portfolio/analyze
```

### Purpose

Analyzes a manually entered portfolio and returns deterministic portfolio metrics.

The backend calculates:

- total portfolio value
- total holdings value
- cash percentage
- holding weights
- top holdings
- sector breakdown
- asset class breakdown

### Sample Request

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
    },
    {
      "ticker": "VTI",
      "quantity": 2,
      "price": 260,
      "asset_class": "etf",
      "sector": "broad market"
    }
  ]
}
```

### Sample Response

```json
{
  "total_portfolio_value": 3230,
  "total_holdings_value": 2730,
  "cash": 500,
  "cash_percentage": 15.48,
  "holdings": [
    {
      "ticker": "MSFT",
      "quantity": 3,
      "price": 420,
      "market_value": 1260,
      "weight": 39.01,
      "asset_class": "stock",
      "sector": "technology"
    },
    {
      "ticker": "AAPL",
      "quantity": 5,
      "price": 190,
      "market_value": 950,
      "weight": 29.41,
      "asset_class": "stock",
      "sector": "technology"
    },
    {
      "ticker": "VTI",
      "quantity": 2,
      "price": 260,
      "market_value": 520,
      "weight": 16.1,
      "asset_class": "etf",
      "sector": "broad market"
    }
  ],
  "top_holdings": [
    {
      "ticker": "MSFT",
      "market_value": 1260,
      "weight": 39.01
    },
    {
      "ticker": "AAPL",
      "market_value": 950,
      "weight": 29.41
    },
    {
      "ticker": "VTI",
      "market_value": 520,
      "weight": 16.1
    }
  ],
  "sector_breakdown": {
    "technology": 68.42,
    "broad market": 16.1
  },
  "asset_class_breakdown": {
    "stock": 68.42,
    "etf": 16.1
  }
}
```

## Saved Portfolio APIs

The backend also includes saved portfolio routes for database-backed portfolio storage.

```http
POST /api/portfolio
GET /api/portfolio
GET /api/portfolio/{portfolio_id}
PATCH /api/portfolio/{portfolio_id}
DELETE /api/portfolio/{portfolio_id}
POST /api/portfolio/{portfolio_id}/snapshot
```

## Validation Notes

The backend expects:

- ticker to be non-empty
- quantity to be greater than 0
- price to be greater than 0
- asset_class to be non-empty
- sector to be non-empty
- cash to be greater than or equal to 0
- at least one holding in the portfolio

Invalid requests return a validation error from FastAPI/Pydantic.