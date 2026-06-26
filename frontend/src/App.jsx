import { useState } from "react";
import { analyzePortfolio } from "./services/api";
import "./App.css";

const emptyHolding = {
  ticker: "",
  quantity: "",
  price: "",
  asset_class: "",
  sector: "",
};

const samplePortfolio = {
  cash: 2500,
  holdings: [
    {
      ticker: "AAPL",
      quantity: 20,
      price: 190,
      asset_class: "stock",
      sector: "technology",
    },
    {
      ticker: "MSFT",
      quantity: 10,
      price: 420,
      asset_class: "stock",
      sector: "technology",
    },
    {
      ticker: "NVDA",
      quantity: 8,
      price: 950,
      asset_class: "stock",
      sector: "technology",
    },
    {
      ticker: "JPM",
      quantity: 12,
      price: 200,
      asset_class: "stock",
      sector: "financials",
    },
    {
      ticker: "VTI",
      quantity: 18,
      price: 260,
      asset_class: "etf",
      sector: "broad market",
    },
  ],
};

function App() {
  const [cash, setCash] = useState(0);
  const [holdings, setHoldings] = useState([{ ...emptyHolding }]);
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  function updateHolding(index, field, value) {
    const nextHoldings = [...holdings];
    nextHoldings[index] = {
      ...nextHoldings[index],
      [field]: value,
    };
    setHoldings(nextHoldings);
  }

  function addHolding() {
    setHoldings([...holdings, { ...emptyHolding }]);
  }

  function removeHolding(index) {
    if (holdings.length === 1) {
      return;
    }

    setHoldings(holdings.filter((_, currentIndex) => currentIndex !== index));
  }

  function loadSamplePortfolio() {
    setCash(samplePortfolio.cash);
    setHoldings(samplePortfolio.holdings);
    setResult(null);
    setError("");
    setSuccess("Sample portfolio loaded.");
  }

  function clearPortfolio() {
    setCash(0);
    setHoldings([{ ...emptyHolding }]);
    setResult(null);
    setError("");
    setSuccess("");
  }

  async function handleSubmit(event) {
    event.preventDefault();
    setError("");
    setSuccess("");
    setResult(null);
    setIsLoading(true);

    const payload = {
      cash: Number(cash),
      holdings: holdings.map((holding) => ({
        ticker: holding.ticker,
        quantity: Number(holding.quantity),
        price: Number(holding.price),
        asset_class: holding.asset_class,
        sector: holding.sector,
      })),
    };

    try {
      const data = await analyzePortfolio(payload);
      setResult(data);
      setSuccess("Portfolio analyzed successfully.");
    } catch (err) {
      setError(err.response?.data?.detail || "failed to analyze portfolio");
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <main>
      <h1>Portfolio Optimizer</h1>
      <p>
        Enter holdings to calculate portfolio value, weights, cash percentage,
        and allocation breakdowns.
      </p>

      <form onSubmit={handleSubmit}>
        <label>
          Cash
          <input
            type="number"
            min="0"
            step="0.01"
            value={cash}
            onChange={(event) => setCash(event.target.value)}
          />
        </label>

        {holdings.map((holding, index) => (
          <section key={index}>
            <input
              placeholder="ticker"
              value={holding.ticker}
              onChange={(event) =>
                updateHolding(index, "ticker", event.target.value)
              }
            />
            <input
              placeholder="quantity"
              type="number"
              min="0"
              step="0.01"
              value={holding.quantity}
              onChange={(event) =>
                updateHolding(index, "quantity", event.target.value)
              }
            />
            <input
              placeholder="price"
              type="number"
              min="0"
              step="0.01"
              value={holding.price}
              onChange={(event) =>
                updateHolding(index, "price", event.target.value)
              }
            />
            <input
              placeholder="asset class"
              value={holding.asset_class}
              onChange={(event) =>
                updateHolding(index, "asset_class", event.target.value)
              }
            />
            <input
              placeholder="sector"
              value={holding.sector}
              onChange={(event) =>
                updateHolding(index, "sector", event.target.value)
              }
            />
            <button type="button" onClick={() => removeHolding(index)}>
              Remove Holding
            </button>
          </section>
        ))}

        <button type="button" onClick={addHolding}>
          Add Holding
        </button>
        <button type="button" onClick={loadSamplePortfolio}>
          Load Sample Portfolio
        </button>
        <button type="button" onClick={clearPortfolio}>
          Clear
        </button>
        <button type="submit" disabled={isLoading}>
          {isLoading ? "Analyzing..." : "Analyze Portfolio"}
        </button>
      </form>

      {isLoading && <p>Analyzing portfolio...</p>}
      {success && <p>{success}</p>}
      {error && <p>{error}</p>}

      {result && (
        <section>
          <h2>Portfolio Summary</h2>
          <p>Total Portfolio Value: ${result.total_portfolio_value}</p>
          <p>Total Holdings Value: ${result.total_holdings_value}</p>
          <p>Cash: ${result.cash}</p>
          <p>Cash Percentage: {result.cash_percentage}%</p>

          <h3>Holdings</h3>
          <table>
            <thead>
              <tr>
                <th>Ticker</th>
                <th>Market Value</th>
                <th>Weight</th>
                <th>Asset Class</th>
                <th>Sector</th>
              </tr>
            </thead>
            <tbody>
              {result.holdings.map((holding) => (
                <tr key={holding.ticker}>
                  <td>{holding.ticker}</td>
                  <td>${holding.market_value}</td>
                  <td>{holding.weight}%</td>
                  <td>{holding.asset_class}</td>
                  <td>{holding.sector}</td>
                </tr>
              ))}
            </tbody>
          </table>

          <h3>Top Holdings</h3>
          <ul>
            {result.top_holdings.map((holding) => (
              <li key={holding.ticker}>
                {holding.ticker}: ${holding.market_value} ({holding.weight}%)
              </li>
            ))}
          </ul>

          <h3>Sector Breakdown</h3>
          <ul>
            {Object.entries(result.sector_breakdown).map(([sector, weight]) => (
              <li key={sector}>
                {sector}: {weight}%
              </li>
            ))}
          </ul>

          <h3>Asset Class Breakdown</h3>
          <ul>
            {Object.entries(result.asset_class_breakdown).map(
              ([assetClass, weight]) => (
                <li key={assetClass}>
                  {assetClass}: {weight}%
                </li>
              )
            )}
          </ul>
        </section>
      )}
    </main>
  );
}

export default App;