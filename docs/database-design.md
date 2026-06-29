# Database Design

## Purpose

This document explains the database schema currently used by the Portfolio Optimizer MVP.

The MVP stores manually created portfolios, the holdings inside each portfolio, and calculated portfolio snapshots. The goal is to keep the schema simple, normalized, and aligned with the current backend implementation.

Authentication and user accounts are not part of the current MVP. A future `users` table is documented separately as a planned extension.

## Current MVP Tables

The current MVP uses three tables:

1. `portfolio_records`
2. `holding_records`
3. `portfolio_snapshots`

These tables support saved portfolios, portfolio holdings, and saved calculation snapshots.

## Table: portfolio_records

The `portfolio_records` table stores one row per saved portfolio.

| Column | Type | Purpose |
|---|---|---|
| `id` | Integer | Primary key for the portfolio |
| `name` | String | User-provided portfolio name |
| `cash` | Float | Cash amount included in the portfolio |
| `created_at` | DateTime | Timestamp for when the portfolio was created |

### Why this table exists

A portfolio is the parent record. It represents the overall portfolio container, while individual holdings and snapshots are stored in separate related tables.

## Table: holding_records

The `holding_records` table stores the individual holdings that belong to a portfolio.

| Column | Type | Purpose |
|---|---|---|
| `id` | Integer | Primary key for the holding |
| `portfolio_id` | Integer | Foreign key linking the holding to a portfolio |
| `ticker` | String | Stock, ETF, or asset ticker |
| `quantity` | Float | Number of shares or units |
| `price` | Float | Manually entered price per unit |
| `asset_class` | String | Asset class such as stock, ETF, bond, or cash equivalent |
| `sector` | String | Sector such as technology, financials, healthcare, or broad market |

### Why holdings are stored separately

Holdings are stored in their own table because a portfolio can have many holdings. If holdings were stored as columns directly on the portfolio table, the database would need a fixed number of holding columns such as `ticker_1`, `ticker_2`, `ticker_3`, and so on.

That would be hard to query, hard to update, and would not scale as users add different numbers of holdings. A separate holdings table allows each portfolio to have any number of holdings while keeping the schema clean and flexible.

## Table: portfolio_snapshots

The `portfolio_snapshots` table stores saved calculation results for a portfolio at a point in time.

| Column | Type | Purpose |
|---|---|---|
| `id` | Integer | Primary key for the snapshot |
| `portfolio_id` | Integer | Foreign key linking the snapshot to a portfolio |
| `total_portfolio_value` | Float | Total value of holdings plus cash |
| `total_holdings_value` | Float | Total market value of holdings only |
| `cash_percentage` | Float | Percentage of the portfolio held as cash |
| `created_at` | DateTime | Timestamp for when the snapshot was created |

### Why snapshots are stored separately

Snapshots are stored separately because portfolio calculations can change over time as prices, holdings, and cash values change.

Saving snapshots makes it possible to compare portfolio values across different points in time without overwriting older calculation results.

## Text ERD

```text
portfolio_records
  id
  name
  cash
  created_at
      |
      | one portfolio has many holdings
      v
holding_records
  id
  portfolio_id
  ticker
  quantity
  price
  asset_class
  sector


portfolio_records
  id
  name
  cash
  created_at
      |
      | one portfolio has many snapshots
      v
portfolio_snapshots
  id
  portfolio_id
  total_portfolio_value
  total_holdings_value
  cash_percentage
  created_at
```

## Relationships

### portfolio_records to holding_records

One portfolio can have many holdings.

```text
portfolio_records.id -> holding_records.portfolio_id
```

This is a one-to-many relationship.

### portfolio_records to portfolio_snapshots

One portfolio can have many snapshots.

```text
portfolio_records.id -> portfolio_snapshots.portfolio_id
```

This is also a one-to-many relationship.

## Index Plan

The current MVP should prioritize indexes on foreign keys used for lookups.

### Current MVP indexes

| Table | Column | Reason |
|---|---|---|
| `holding_records` | `portfolio_id` | Quickly retrieve all holdings for a portfolio |
| `portfolio_snapshots` | `portfolio_id` | Quickly retrieve all snapshots for a portfolio |

These indexes support the most common backend access patterns:

1. Load a saved portfolio.
2. Retrieve all holdings for that portfolio.
3. Retrieve snapshot history for that portfolio.

## Future Auth Extension

Authentication is not part of the current MVP.

If authentication is added later, the project may introduce a future `users` table.

Possible future table:

```text
users
  id
  email
  created_at
```

Possible future relationship:

```text
users.id -> portfolio_records.user_id
```

Possible future index:

| Table | Column | Reason |
|---|---|---|
| `users` | `email` | Quickly find a user account by email during login or account lookup |

The `users` table is intentionally documented as future scope so the current MVP remains focused on portfolio storage and analysis.

## Design Summary

The database is designed around three main ideas:

1. A portfolio is the parent record.
2. Holdings are separate child records because each portfolio can contain many holdings.
3. Snapshots are separate child records because calculated results can be saved over time.

This keeps the schema normalized, flexible, and aligned with the current Portfolio Optimizer MVP.