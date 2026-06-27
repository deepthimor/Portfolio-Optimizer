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
```

```text
cash_percentage = cash / total_portfolio_value * 100
```

The backend currently requires at least one holding, so a portfolio with only cash and no holdings is rejected as an empty portfolio.

For testing cash-heavy portfolios, a small placeholder holding can be used. This allows the backend to calculate a high cash percentage while still satisfying the rule that at least one holding must exist.

## Rounding

Calculated numeric values are rounded to two decimal places.

Rounded values include:

- total portfolio value
- total holdings value
- cash
- cash percentage
- holding price
- holding market value
- holding weight
- sector breakdown percentages
- asset class breakdown percentages

JSON numbers do not preserve trailing zeros, so a value like `16.10` may display as `16.1`. This is normal because the value is still rounded consistently.

## Portfolio Scenarios Tested

### Balanced Portfolio

A balanced portfolio includes multiple holdings across different sectors and asset classes.

Expected behavior:

- Total portfolio value includes holdings and cash.
- Holdings table displays each holding.
- Sector breakdown includes multiple sectors.
- Asset class breakdown includes multiple asset classes.
- Top holdings are ranked by market value.

### Concentrated Tech Portfolio

A concentrated tech portfolio includes mostly or entirely technology holdings.

Expected behavior:

- Technology has the highest sector breakdown.
- Top holdings show concentration in a few positions.
- Holding weights reveal concentration risk.

### Cash-Heavy Portfolio

A cash-heavy portfolio includes a large cash balance and a small holding.

Expected behavior:

- Cash percentage is very high.
- Total portfolio value includes both cash and holdings.
- The holding still appears in the holdings table.
- Empty portfolios with no holdings are rejected.