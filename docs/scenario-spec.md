# Scenario Report Spec

## Goal

Create deterministic scenario reports for a user-provided portfolio.

The scenario report estimates how portfolio value changes under predefined hypothetical scenarios. These are not forecasts. They are simple stress-test calculations based on fixed assumptions.

## Supported Scenarios

### market_down_25

Assumption:
- Non-cash holdings decline by 25%.
- Cash is unchanged.

### tech_down_40

Assumption:
- Holdings with sector `technology` or `tech` decline by 40%.
- Other holdings are unchanged.
- Cash is unchanged.

### rates_up

Assumption:
- Bond or fixed income holdings decline by 10%.
- Other holdings are unchanged.
- Cash is unchanged.

### cash_return

Assumption:
- Cash earns 4%.
- Holdings are unchanged.

### international_underperformance

Assumption:
- International, foreign, developed international, and emerging market holdings decline by 20%.
- Other holdings are unchanged.
- Cash is unchanged.

### concentrated_holding_drop

Assumption:
- The largest holding declines by 30%.
- Other holdings are unchanged.
- Cash is unchanged.

## Report Request

The report request should include:

- cash
- holdings
- optional list of scenario names

If no scenario names are provided, all supported scenarios should run.

## Report Result

Each scenario result should include:

- starting_value
- scenario_value
- dollar_change
- percent_change
- most_impacted_holdings
- assumptions

## Boundaries

The scenario report is educational only.

It should not:

- Pretend to forecast the future
- Predict returns
- Use live market data
- Recommend buying or selling securities
- Replace professional financial advice

## Implementation Notes

The first version should run synchronously.

Future versions may move report generation into a background job queue.