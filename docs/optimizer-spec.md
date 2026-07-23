# Optimizer Spec

## Goal

Create deterministic portfolio review signals that are structured enough for UI display, tests, and later AI explanation.

The optimizer is educational only. It explains portfolio structure using backend-calculated metrics and does not provide personalized financial advice.

## Inputs

The optimizer may use:

- holdings
- cash_percentage
- risk_tolerance
- max_holding
- max_sector
- target_allocation
- target_allocation_gap_analysis
- sector_breakdown
- asset_class_breakdown

## Risk Tolerance Defaults

| Risk tolerance | Max holding | Max sector | Cash requirement |
|---|---:|---:|---:|
| Conservative | 20% | 35% | 15% |
| Moderate | 30% | 45% | 10% |
| Aggressive | 40% | 55% | 5% |

User-provided `max_holding` and `max_sector` override the risk-tolerance defaults.

## Recommendation JSON

Each recommendation should use this shape:

```json
{
  "action": "review",
  "ticker": "AAPL",
  "amount_or_percent": 32.5,
  "reason_code": "OVERWEIGHT_HOLDING",
  "human_reason": "AAPL is above the max holding threshold.",
  "before_weight": 32.5,
  "after_weight_estimate": null,
  "priority": "high"
}
```

## Actions

Allowed actions:

- `review`
- `reduce_exposure`
- `add_exposure`
- `no_action`

## Reason Codes

Allowed reason codes:

- `OVERWEIGHT_HOLDING`
- `OVERWEIGHT_SECTOR`
- `BELOW_CASH_TARGET`
- `UNDERWEIGHT_ASSET_CLASS`
- `BALANCED_NO_ACTION`

## Priority

Allowed priorities:

- `high`
- `medium`
- `low`

## Rules

### OVERWEIGHT_HOLDING

Trigger when a holding weight is above `max_holding`.

### OVERWEIGHT_SECTOR

Trigger when the largest sector weight is above `max_sector`.

### BELOW_CASH_TARGET

Trigger when `cash_percentage` is below the cash requirement for the selected risk tolerance.

### UNDERWEIGHT_ASSET_CLASS

Trigger when target allocation gap analysis shows an asset class is underweight by more than 1%.

### BALANCED_NO_ACTION

Return when no other recommendation is triggered.

## Output Boundary

Recommendations should explain what metric triggered the signal. They should not tell a user to buy or sell a specific security. The language should remain educational and review-oriented.