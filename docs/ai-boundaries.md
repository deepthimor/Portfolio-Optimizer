# AI Boundaries

## Purpose

The portfolio optimizer may eventually use an LLM to explain portfolio metrics in plain English.

The LLM should not calculate financial metrics directly. The backend calculates deterministic metrics first, then the AI layer can explain only those supplied metrics.

## Backend Calculates

The backend is responsible for calculating:

- Total portfolio value
- Cash percentage
- Number of holdings
- Asset class allocation percentages
- Sector allocation percentages
- Top 1 concentration
- Top 3 concentration
- Top 5 concentration
- Largest holding
- Largest sector
- Top holdings
- Risk flags based on deterministic rules
- Limitations

## LLM Explains

The LLM may explain:

- What the supplied allocation percentages mean
- What top holding concentration means
- What risk flags were triggered
- What limitations apply to the summary

The LLM should not invent additional metrics, performance history, expected returns, or personalized investment recommendations.

## Data Boundaries

The LLM receives only the AI summary input object created by the backend.

The LLM should not receive:

- Raw secrets
- API keys
- Credentials
- Account numbers
- User identity information
- Unsupported data
- Raw unfiltered backend objects
- Full raw holdings if not needed for explanation
- Quantity-level or price-level inputs unless explicitly required later

## Prompt Boundaries

The AI prompt must tell the LLM to:

- Summarize only supplied metrics
- Do not invent performance
- Do not assume future returns
- Do not give personalized financial advice
- Do not recommend buying, selling, or holding any security
- Include uncertainty and limitations

## Fallback Behavior

If AI is unavailable, the app should still show a deterministic fallback summary.

The fallback summary should use the same backend-calculated AI summary input object and should clearly state that the output is based only on supplied metrics and is not personalized financial advice.

## Current Limitation

The current MVP prepares the AI summary input and fallback text. It does not need to call an LLM yet.