# Risk Score Spec

## Purpose

The risk score is a deterministic portfolio risk indicator. It is not investment advice and does not predict future returns.

The backend calculates every number used in the score. The UI only displays the backend output.

## Risk Inputs

The first version supports these inputs:

| Input | Required | Purpose |
|---|---:|---|
| `risk_tolerance` | Yes | Controls default thresholds for conservative, moderate, or aggressive users |
| `target_allocation` | Yes | Target asset allocation percentages used to calculate allocation gaps |
| `max_holding` | Yes | Maximum preferred percentage for one holding |
| `max_sector` | Yes | Maximum preferred percentage for one sector |
| `expected_return` | Optional | Reserved for future score versions |
| `volatility` | Optional | Reserved for future score versions |

## Default Risk Tolerance Settings

If the user does not supply custom values, the backend uses defaults.

| Risk Tolerance | Max Holding | Max Sector | Cash Threshold |
|---|---:|---:|---:|
| conservative | 20% | 35% | 15% |
| moderate | 30% | 45% | 25% |
| aggressive | 40% | 55% | 35% |

## Default Target Allocation

If the user does not provide a target allocation, the backend uses:

```json
{
  "stock": 60,
  "etf": 30,
  "bond": 10,
  "cash": 0
}
```

## Score Components

### Concentration Score

The concentration score measures how much of the portfolio is driven by the largest holdings.

Inputs:

- Top 1 percentage
- Top 3 percentage
- Top 5 percentage
- Max holding threshold

Formula:

```text
single_holding_score = top_1_percentage / max_holding * 100
top_three_score = top_3_percentage / (max_holding * 2) * 100
top_five_score = top_5_percentage / (max_holding * 3) * 100

concentration_score =
  50% single_holding_score +
  30% top_three_score +
  20% top_five_score
```

Each sub-score is capped at 100.

### Diversification Score

The diversification score measures how spread out the portfolio is.

Inputs:

- Number of holdings
- Number of sectors
- Concentration score

Formula:

```text
holding_count_score = number_of_holdings / 10 * 100
sector_count_score = number_of_sectors / 5 * 100
concentration_inverse = 100 - concentration_score

diversification_score =
  40% holding_count_score +
  30% sector_count_score +
  30% concentration_inverse
```

Each sub-score is capped between 0 and 100.

Higher diversification score is better.

### Sector Exposure Score

The sector exposure score measures whether one sector dominates the portfolio.

Formula:

```text
sector_exposure_score = largest_sector_percentage / max_sector * 100
```

The score is capped at 100.

### Cash Score

The cash score measures whether the cash percentage is above the selected risk tolerance threshold.

Formula:

```text
if cash_percentage <= cash_threshold:
  cash_score = 0
else:
  cash_score = (cash_percentage - cash_threshold) / (100 - cash_threshold) * 100
```

### Target Allocation Gap Score

The target allocation gap score compares current allocation to target allocation.

Formula:

```text
average_gap = average absolute difference between current and target allocation
target_allocation_gap_score = average_gap * 2
```

The score is capped at 100.

## Final Risk Score

The final `risk_score_v1` is a weighted score from 0 to 100.

```text
risk_score_v1 =
  35% concentration_score +
  25% sector_exposure_score +
  20% cash_score +
  20% target_allocation_gap_score
```

## Risk Ranges

| Score Range | Label |
|---|---|
| 0–33 | low |
| 34–66 | moderate |
| 67–100 | high |

## Explanation Boundary

Every number in the score comes from backend-calculated portfolio metrics or explicit user inputs.

The score does not use:

- Historical performance
- Predicted returns
- Personalized financial advice
- External market data
- Brokerage account data

## Explainability Checklist

Each risk score response should expose:

- Final `risk_score_v1`
- Risk level
- Concentration score
- Diversification score
- Sector exposure score
- Cash score
- Target allocation gap score
- Inputs used by the calculation
- Plain-English explanations

This makes every displayed number traceable to either user input or deterministic backend calculations.