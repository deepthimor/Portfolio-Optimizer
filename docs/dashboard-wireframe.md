# Dashboard Wireframe

## Purpose

The MVP dashboard should help a user understand their portfolio quickly after entering or loading holdings.

The dashboard should tell a clear visual story in under 20 seconds:

1. What is my portfolio worth?
2. How much cash do I have?
3. What am I invested in?
4. Which sectors and asset classes dominate?
5. Am I concentrated in a few holdings?

## Dashboard Layout

```text
Portfolio Optimizer
Short project description

------------------------------------------------------------
Input Panel
------------------------------------------------------------
Portfolio name
Cash
Holding rows:
- Ticker
- Quantity
- Price
- Asset class
- Sector

Actions:
- Add Holding
- Load Sample
- Clear
- Analyze Portfolio
- Save Portfolio

------------------------------------------------------------
Status Area
------------------------------------------------------------
Loading state:
Analyzing portfolio...

Error state:
Show clear error banner for failed API calls.

Empty state:
No portfolio analyzed yet. Enter holdings or load the sample portfolio to see dashboard results.

------------------------------------------------------------
Summary Cards
------------------------------------------------------------
Card 1: Total Portfolio Value
Card 2: Total Holdings Value
Card 3: Cash
Card 4: Cash Percentage

------------------------------------------------------------
Allocation Charts
------------------------------------------------------------
Asset Allocation Chart:
Shows portfolio exposure by asset class.

Sector Exposure Chart:
Shows portfolio exposure by sector.

Charts should use the backend response first.
If no backend response exists, sample data can be used only for layout/demo fallback.

------------------------------------------------------------
Top Holdings Table
------------------------------------------------------------
Columns:
- Ticker
- Market value
- Weight
- Asset class
- Sector

Purpose:
Show the holdings that drive the portfolio.

------------------------------------------------------------
Concentration Cards
------------------------------------------------------------
Card 1: Largest Holding
Card 2: Largest Holding Weight
Card 3: Top 3 Holdings Weight

Purpose:
Help users quickly see whether the portfolio is concentrated.

------------------------------------------------------------
Future AI Summary Panel
------------------------------------------------------------
This panel is not responsible for financial calculations.

It should eventually explain backend-calculated metrics in plain English.

Potential inputs:
- Total portfolio value
- Cash percentage
- Top holdings
- Asset allocation
- Sector allocation
- Concentration metrics

Example future output:
"Your portfolio is heavily weighted toward technology, with your top three holdings making up most of the invested value."