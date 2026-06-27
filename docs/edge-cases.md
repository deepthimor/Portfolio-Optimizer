# Edge Cases

This document explains validation behavior, duplicate handling, cash handling, and rounding for the Portfolio Optimizer backend.

## Validation Rules

The backend validates portfolio input before running calculations.

Required rules:

- `ticker` is required and cannot be empty.
- `quantity` must be greater than 0.
- `price` must be greater than 0.
- `asset_class` is required and cannot be empty.
- `sector` is required and cannot be empty.
- `cash` must be greater than or equal to 0.
- The portfolio must include at least one holding.

Invalid inputs return a clean FastAPI/Pydantic validation error instead of running portfolio analysis.

## Duplicate Tickers

Duplicate tickers are currently allowed.

The backend treats each holding row as a separate position. For example, if the user enters AAPL twice, the backend keeps both rows and analyzes both of them separately.

Current decision:

- Do not automatically combine duplicate tickers.
- Preserve the user-entered rows.
- Include duplicate values in total holdings value, sector breakdown, and asset class breakdown.

This keeps the calculation logic simple and transparent. A future version could add a warning or combine duplicate tickers into one row.

## Cash Handling

Cash is entered separately from holdings.

The backend includes cash in total portfolio value and cash percentage.

Formula:

```text
total_portfolio_value = total_holdings_value + cash