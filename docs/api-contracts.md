# API Contracts

## Purpose

This document describes the current API contracts for the Portfolio Optimizer MVP.

It covers endpoint purpose, request shape, response shape, and error shape for the analysis API and saved portfolio CRUD APIs.

## Base URL

Local development base URL:

```text
http://127.0.0.1:8000
```

## Error Response Shape

For expected application errors, the API returns a JSON object with a `detail` field.

Example:

```json
{
  "detail": "portfolio not found"
}
```

Validation errors are handled by FastAPI and Pydantic. They return status code `422` with a `detail` array explaining the invalid input.

Example:

```json
{
  "detail": [
    {
      "type": "missing",
      "loc": ["body", "holdings", 0, "ticker"],
      "msg": "Field required"
    }
  ]
}
```

The MVP goal is that expected invalid requests return clear status codes and messages, not stack traces.

---

## POST /api/portfolio/analyze

Analyzes a manually entered portfolio without saving it.

### Request

```json
{
  "cash": 2500,
  "holdings": [
    {
      "ticker": "AAPL",
      "quantity": 10,
      "price": 190,
      "asset_class": "stock",
      "sector": "technology"
    }
  ]
}
```

### Success Response

Status: `200`

```json
{
  "total_portfolio_value": 4400,
  "total_holdings_value": 1900,
  "cash": 2500,
  "cash_percentage": 56.82,
  "holdings": [
    {
      "ticker": "AAPL",
      "quantity": 10,
      "price": 190,
      "market_value": 1900,
      "weight": 43.18,
      "asset_class": "stock",
      "sector": "technology"
    }
  ],
  "top_holdings": [
    {
      "ticker": "AAPL",
      "market_value": 1900,
      "weight": 43.18
    }
  ],
  "sector_breakdown": {
    "technology": 43.18
  },
  "asset_class_breakdown": {
    "stock": 43.18
  }
}
```

### Error Responses

Invalid request body:

Status: `422`

```json
{
  "detail": [
    {
      "loc": ["body", "holdings"],
      "msg": "List should have at least 1 item"
    }
  ]
}
```

---

## GET /api/portfolio

Lists saved portfolios.

### Request

No request body.

### Success Response

Status: `200`

```json
[
  {
    "id": 1,
    "name": "Test Portfolio",
    "cash": 2500
  }
]
```

---

## POST /api/portfolio

Creates a saved portfolio with optional initial holdings.

### Request

```json
{
  "name": "Test Portfolio",
  "cash": 2500,
  "holdings": [
    {
      "ticker": "AAPL",
      "quantity": 10,
      "price": 190,
      "asset_class": "stock",
      "sector": "technology"
    }
  ]
}
```

### Success Response

Status: `200`

```json
{
  "id": 1,
  "name": "Test Portfolio",
  "cash": 2500
}
```

### Error Responses

Invalid request body:

Status: `422`

```json
{
  "detail": [
    {
      "loc": ["body", "name"],
      "msg": "Field required"
    }
  ]
}
```

---

## GET /api/portfolio/{portfolio_id}

Reads one saved portfolio and its holdings.

### Request

Path parameter:

```text
portfolio_id: integer
```

### Success Response

Status: `200`

```json
{
  "id": 1,
  "name": "Test Portfolio",
  "cash": 2500,
  "holdings": [
    {
      "id": 1,
      "ticker": "AAPL",
      "quantity": 10,
      "price": 190,
      "asset_class": "stock",
      "sector": "technology"
    }
  ]
}
```

### Error Responses

Portfolio not found:

Status: `404`

```json
{
  "detail": "portfolio not found"
}
```

---

## PATCH /api/portfolio/{portfolio_id}

Updates saved portfolio metadata such as name and cash.

### Request

Path parameter:

```text
portfolio_id: integer
```

Body:

```json
{
  "name": "Updated Portfolio",
  "cash": 5000
}
```

Both fields are optional, but at least one should be provided for a meaningful update.

### Success Response

Status: `200`

```json
{
  "id": 1,
  "name": "Updated Portfolio",
  "cash": 5000
}
```

### Error Responses

Portfolio not found:

Status: `404`

```json
{
  "detail": "portfolio not found"
}
```

Invalid cash value:

Status: `422`

```json
{
  "detail": [
    {
      "loc": ["body", "cash"],
      "msg": "Input should be greater than or equal to 0"
    }
  ]
}
```

---

## DELETE /api/portfolio/{portfolio_id}

Deletes a saved portfolio.

Related holdings are deleted through the SQLAlchemy relationship cascade.

### Request

Path parameter:

```text
portfolio_id: integer
```

### Success Response

Status: `200`

```json
{
  "message": "portfolio deleted"
}
```

### Error Responses

Portfolio not found:

Status: `404`

```json
{
  "detail": "portfolio not found"
}
```

---

## POST /api/portfolio/{portfolio_id}/holdings

Adds a holding to an existing saved portfolio.

### Request

Path parameter:

```text
portfolio_id: integer
```

Body:

```json
{
  "ticker": "JPM",
  "quantity": 4,
  "price": 205,
  "asset_class": "stock",
  "sector": "financials"
}
```

### Success Response

Status: `201`

```json
{
  "id": 3,
  "portfolio_id": 1,
  "ticker": "JPM",
  "quantity": 4,
  "price": 205,
  "asset_class": "stock",
  "sector": "financials"
}
```

### Error Responses

Portfolio not found:

Status: `404`

```json
{
  "detail": "portfolio not found"
}
```

Invalid request body:

Status: `422`

```json
{
  "detail": [
    {
      "loc": ["body", "quantity"],
      "msg": "Input should be greater than 0"
    }
  ]
}
```

---

## PATCH /api/portfolio/holdings/{holding_id}

Updates a saved holding.

### Request

Path parameter:

```text
holding_id: integer
```

Body:

```json
{
  "quantity": 5,
  "price": 210
}
```

All fields are optional. Supported fields:

```json
{
  "ticker": "JPM",
  "quantity": 5,
  "price": 210,
  "asset_class": "stock",
  "sector": "financials"
}
```

### Success Response

Status: `200`

```json
{
  "id": 3,
  "portfolio_id": 1,
  "ticker": "JPM",
  "quantity": 5,
  "price": 210,
  "asset_class": "stock",
  "sector": "financials"
}
```

### Error Responses

Holding not found:

Status: `404`

```json
{
  "detail": "holding not found"
}
```

Invalid request body:

Status: `422`

```json
{
  "detail": [
    {
      "loc": ["body", "quantity"],
      "msg": "Input should be greater than 0"
    }
  ]
}
```

---

## DELETE /api/portfolio/holdings/{holding_id}

Deletes a saved holding.

### Request

Path parameter:

```text
holding_id: integer
```

### Success Response

Status: `200`

```json
{
  "message": "holding deleted"
}
```

### Error Responses

Holding not found:

Status: `404`

```json
{
  "detail": "holding not found"
}
```

---

## POST /api/portfolio/{portfolio_id}/snapshot

Creates a saved calculated snapshot for an existing portfolio.

### Request

Path parameter:

```text
portfolio_id: integer
```

No request body.

### Success Response

Status: `200`

```json
{
  "id": 1,
  "portfolio_id": 1,
  "total_portfolio_value": 5775,
  "total_holdings_value": 3275,
  "cash_percentage": 43.29,
  "created_at": "2026-07-08T00:00:00"
}
```

### Error Responses

Portfolio not found:

Status: `404`

```json
{
  "detail": "portfolio not found"
}
```

---

## GET /api/portfolio/{portfolio_id}/snapshots

Lists saved analysis snapshots for an existing portfolio.

### Request

Path parameter:

```text
portfolio_id: integer
```

No request body.

### Success Response

Status: `200`

```json
[
  {
    "id": 1,
    "portfolio_id": 1,
    "total_portfolio_value": 5775,
    "total_holdings_value": 3275,
    "cash_percentage": 43.29,
    "created_at": "2026-07-08T00:00:00"
  }
]
```

### Error Responses

Portfolio not found:

Status: `404`

```json
{
  "detail": "portfolio not found"
}
```

---

## MVP Error Behavior Summary

The MVP uses three main error patterns:

1. `404` for missing saved resources such as portfolios or holdings.
2. `422` for invalid request bodies, missing required fields, empty holdings, and invalid numbers.
3. `400` for business-rule errors raised during portfolio analysis.

Expected invalid requests should return JSON error responses with clear messages and should not expose stack traces.