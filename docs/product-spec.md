# Product Spec

## Project Name

Portfolio Optimizer

## Problem

Individual investors often hold portfolios across stocks, ETFs, and cash without a clear view of allocation, concentration, or portfolio balance. This project helps users manually enter holdings and understand their portfolio composition through deterministic backend calculations.

## Target User

The target user is an individual investor, student investor, or early-stage financial technology user who wants a simple way to analyze holdings without connecting a brokerage account.

## Current Scope

The MVP supports manual portfolio input, backend portfolio analysis, a React frontend, and database-backed saved portfolios.

## Input Fields

Each holding includes:

- ticker
- quantity
- price
- asset_class
- sector
- cash
- target_allocation

## Field Definitions

| Field | Type | Required | Description |
|---|---|---:|---|
| ticker | string | yes | Stock, ETF, or cash symbol such as AAPL, VTI, or CASH |
| quantity | number | yes | Number of shares or units held |
| price | number | yes | Current price per unit |
| asset_class | string | yes | Category such as stock, ETF, bond, cash, crypto, or other |
| sector | string | yes | Sector such as technology, financials, healthcare, broad market, or cash |
| cash | number | yes | Cash amount included in the portfolio |
| target_allocation | object | no | Desired allocation by asset class for future comparison |

## Current Calculations

The backend calculates:

- total portfolio value
- total holdings value
- cash percentage
- holding weights
- top holdings
- sector breakdown
- asset class breakdown

## Planned Features

- dashboard charts
- risk metrics
- target allocation comparison
- rebalancing recommendations
- AI-generated portfolio explanations
- scenario analysis
- deployment

## Known Limitations

- This project is educational only and does not provide financial advice.
- Prices are manually entered in the MVP.
- There is no brokerage integration.
- There is no authentication yet.