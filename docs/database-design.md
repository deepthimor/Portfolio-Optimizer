# Database Design

## Purpose

The Portfolio Optimizer MVP stores user-created portfolios, their holdings, and calculated analysis snapshots.

The database supports the Week 2 saved portfolio workflow:

- Create saved portfolios
- Read saved portfolios
- Update saved portfolio metadata
- Delete saved portfolios
- Add, update, and delete saved holdings
- Save portfolio analysis snapshots

## Database Tables

### portfolio_records

Stores one saved portfolio.

| Column | Type | Purpose |
|---|---|---|
| id | Integer | Primary key |
| name | String | User-facing portfolio name |
| cash | Float | Cash amount included in portfolio value |
| created_at | DateTime | Timestamp for when the portfolio was created |

### holding_records

Stores holdings that belong to a saved portfolio.

| Column | Type | Purpose |
|---|---|---|
| id | Integer | Primary key |
| portfolio_id | Integer | Foreign key to portfolio_records.id |
| ticker | String | Stock or ETF ticker |
| quantity | Float | Number of shares or units |
| price | Float | Price per share or unit |
| asset_class | String | Asset class such as stock, ETF, bond, or cash-like |
| sector | String | Sector grouping used for portfolio breakdowns |

### portfolio_snapshots

Stores calculated portfolio analysis results at a point in time.

| Column | Type | Purpose |
|---|---|---|
| id | Integer | Primary key |
| portfolio_id | Integer | Foreign key to portfolio_records.id |
| total_portfolio_value | Float | Total holdings value plus cash |
| total_holdings_value | Float | Total value of all holdings |
| cash_percentage | Float | Cash as a percentage of total portfolio value |
| created_at | DateTime | Timestamp for when the snapshot was created |

## Relationships

### portfolio_records to holding_records

One portfolio can have many holdings.

```text
portfolio_records.id -> holding_records.portfolio_id
```

The SQLAlchemy relationship uses:

```text
cascade="all, delete-orphan"
```

This means deleting a portfolio also deletes its related holdings.

### portfolio_records to portfolio_snapshots

One portfolio can have many snapshots.

```text
portfolio_records.id -> portfolio_snapshots.portfolio_id
```

The SQLAlchemy relationship also uses:

```text
cascade="all, delete-orphan"
```

This means deleting a portfolio also deletes its related snapshots.

## Indexes

The current MVP explicitly indexes primary key columns through SQLAlchemy:

- portfolio_records.id
- holding_records.id
- portfolio_snapshots.id

Foreign key fields are used for lookups:

- holding_records.portfolio_id
- portfolio_snapshots.portfolio_id

For the current MVP size, these are sufficient. If portfolio history grows, the next likely index would be:

```text
portfolio_snapshots.portfolio_id, portfolio_snapshots.created_at
```

That would make snapshot history queries faster.

## Tradeoffs

### Float values

The MVP uses `Float` for money-like values such as cash, price, and portfolio value.

This is simple for the current prototype and makes calculations straightforward.

A production financial system should consider fixed precision decimal types instead of floats.

### Manual table creation

The MVP uses `Base.metadata.create_all()` through `scripts/create_tables.py` for local development.

This is acceptable for the MVP because the schema is small and changing quickly.

A production system should use migrations, such as Alembic, instead of relying on `create_all()`.

### Snapshots store summary values only

Portfolio snapshots currently store:

- total_portfolio_value
- total_holdings_value
- cash_percentage

They do not store every holding weight, sector breakdown, or asset class breakdown.

This keeps the snapshot table simple. If historical dashboard views need full breakdowns later, the project can add a richer snapshot detail table or JSON column.

### Store service layer

Database logic is being moved into:

```text
backend/services/portfolio_store.py
```

This keeps route files smaller and makes database behavior easier to test and maintain.