import { useEffect, useState } from "react";
import {
  analyzePortfolio,
  createPortfolio,
  deleteHolding,
  deletePortfolio,
  getPortfolio,
  listPortfolios,
  updatePortfolio,
} from "./services/api";
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
      ticker: "VTI",
      quantity: 18,
      price: 260,
      asset_class: "etf",
      sector: "broad market",
    },
  ],
};

function App() {
  const [portfolioName, setPortfolioName] = useState("");
  const [cash, setCash] = useState(0);
  const [holdings, setHoldings] = useState([{ ...emptyHolding }]);
  const [portfolioAnalysis, setPortfolioAnalysis] = useState(null);

  const [savedPortfolios, setSavedPortfolios] = useState([]);
  const [selectedPortfolio, setSelectedPortfolio] = useState(null);

  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    refreshSavedPortfolios();
  }, []);

  function showError(err, fallbackMessage) {
    setSuccess("");
    setError(err.response?.data?.detail || fallbackMessage);
  }

  async function refreshSavedPortfolios() {
    try {
      const data = await listPortfolios();
      setSavedPortfolios(data);
    } catch (err) {
      showError(err, "Failed to load saved portfolios.");
    }
  }

  function updateHoldingInput(index, field, value) {
    const nextHoldings = [...holdings];

    nextHoldings[index] = {
      ...nextHoldings[index],
      [field]: value,
    };

    setHoldings(nextHoldings);
  }

  function addHoldingInput() {
    setHoldings([...holdings, { ...emptyHolding }]);
  }

  function removeHoldingInput(index) {
    if (holdings.length === 1) {
      return;
    }

    setHoldings(
      holdings.filter((_, currentIndex) => currentIndex !== index),
    );
  }

  function buildPortfolioPayload() {
    return {
      cash: Number(cash),
      holdings: holdings.map((holding) => ({
        ticker: holding.ticker,
        quantity: Number(holding.quantity),
        price: Number(holding.price),
        asset_class: holding.asset_class,
        sector: holding.sector,
      })),
    };
  }

  function loadSamplePortfolio() {
    setPortfolioName("Sample Portfolio");
    setCash(samplePortfolio.cash);
    setHoldings(samplePortfolio.holdings);
    setPortfolioAnalysis(null);
    setError("");
    setSuccess("Sample portfolio loaded.");
  }

  function clearPortfolioForm() {
    setPortfolioName("");
    setCash(0);
    setHoldings([{ ...emptyHolding }]);
    setPortfolioAnalysis(null);
    setError("");
    setSuccess("");
  }

  async function handleAnalyze(event) {
    event.preventDefault();

    setError("");
    setSuccess("");
    setPortfolioAnalysis(null);
    setIsLoading(true);

    try {
      const result = await analyzePortfolio(buildPortfolioPayload());
      setPortfolioAnalysis(result);
      setSuccess("Portfolio analyzed successfully.");
    } catch (err) {
      showError(err, "Failed to analyze portfolio.");
    } finally {
      setIsLoading(false);
    }
  }

  async function handleSavePortfolio() {
    if (!portfolioName.trim()) {
      setError("Portfolio name is required before saving.");
      return;
    }

    setIsLoading(true);
    setError("");
    setSuccess("");

    try {
      const createdPortfolio = await createPortfolio({
        name: portfolioName.trim(),
        ...buildPortfolioPayload(),
      });

      await refreshSavedPortfolios();

      const fullPortfolio = await getPortfolio(createdPortfolio.id);
      setSelectedPortfolio(fullPortfolio);

      setSuccess("Portfolio saved successfully.");
    } catch (err) {
      showError(err, "Failed to save portfolio.");
    } finally {
      setIsLoading(false);
    }
  }

  async function handleSelectPortfolio(portfolioId) {
    setError("");
    setSuccess("");

    try {
      const data = await getPortfolio(portfolioId);
      setSelectedPortfolio(data);
    } catch (err) {
      showError(err, "Failed to load the selected portfolio.");
    }
  }

  async function handleUpdateSelectedPortfolio() {
    if (!selectedPortfolio) {
      return;
    }

    try {
      await updatePortfolio(selectedPortfolio.id, {
        name: selectedPortfolio.name,
        cash: Number(selectedPortfolio.cash),
      });

      const refreshedPortfolio = await getPortfolio(selectedPortfolio.id);

      setSelectedPortfolio(refreshedPortfolio);
      await refreshSavedPortfolios();

      setSuccess("Portfolio updated successfully.");
      setError("");
    } catch (err) {
      showError(err, "Failed to update portfolio.");
    }
  }

  async function handleDeleteSelectedPortfolio() {
    if (!selectedPortfolio) {
      return;
    }

    try {
      await deletePortfolio(selectedPortfolio.id);

      setSelectedPortfolio(null);
      await refreshSavedPortfolios();

      setSuccess("Portfolio deleted successfully.");
      setError("");
    } catch (err) {
      showError(err, "Failed to delete portfolio.");
    }
  }

  async function handleDeleteSavedHolding(holdingId) {
    if (!selectedPortfolio) {
      return;
    }

    try {
      await deleteHolding(holdingId);

      const refreshedPortfolio = await getPortfolio(selectedPortfolio.id);
      setSelectedPortfolio(refreshedPortfolio);

      setSuccess("Holding deleted successfully.");
      setError("");
    } catch (err) {
      showError(err, "Failed to delete holding.");
    }
  }

  return (
    <main>
      <h1>Portfolio Optimizer</h1>

      <p>
        Analyze portfolios, save them to PostgreSQL, and manage saved holdings.
      </p>

      <form onSubmit={handleAnalyze}>
        <label>
          Portfolio Name
          <input
            value={portfolioName}
            onChange={(event) => setPortfolioName(event.target.value)}
            placeholder="My Portfolio"
          />
        </label>

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
                updateHoldingInput(index, "ticker", event.target.value)
              }
            />

            <input
              placeholder="quantity"
              type="number"
              min="0"
              step="0.01"
              value={holding.quantity}
              onChange={(event) =>
                updateHoldingInput(index, "quantity", event.target.value)
              }
            />

            <input
              placeholder="price"
              type="number"
              min="0"
              step="0.01"
              value={holding.price}
              onChange={(event) =>
                updateHoldingInput(index, "price", event.target.value)
              }
            />

            <input
              placeholder="asset class"
              value={holding.asset_class}
              onChange={(event) =>
                updateHoldingInput(index, "asset_class", event.target.value)
              }
            />

            <input
              placeholder="sector"
              value={holding.sector}
              onChange={(event) =>
                updateHoldingInput(index, "sector", event.target.value)
              }
            />

            <button
              type="button"
              onClick={() => removeHoldingInput(index)}
            >
              Remove
            </button>
          </section>
        ))}

        <button type="button" onClick={addHoldingInput}>
          Add Holding
        </button>

        <button type="button" onClick={loadSamplePortfolio}>
          Load Sample
        </button>

        <button type="button" onClick={clearPortfolioForm}>
          Clear
        </button>

        <button type="submit" disabled={isLoading}>
          Analyze Portfolio
        </button>

        <button
          type="button"
          onClick={handleSavePortfolio}
          disabled={isLoading}
        >
          Save Portfolio
        </button>
      </form>

      {success && <p className="success">{success}</p>}
      {error && <p className="error">{error}</p>}

      {portfolioAnalysis && (
        <section>
          <h2>Portfolio Summary</h2>

          <p>
            Total Portfolio Value: $
            {portfolioAnalysis.total_portfolio_value}
          </p>

          <p>
            Total Holdings Value: $
            {portfolioAnalysis.total_holdings_value}
          </p>

          <p>Cash: ${portfolioAnalysis.cash}</p>

          <p>
            Cash Percentage: {portfolioAnalysis.cash_percentage}%
          </p>

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
              {portfolioAnalysis.holdings.map((holding) => (
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
        </section>
      )}

      <section>
        <div className="section-header">
          <h2>Saved Portfolios</h2>

          <button type="button" onClick={refreshSavedPortfolios}>
            Refresh
          </button>
        </div>

        {savedPortfolios.length === 0 ? (
          <p>No saved portfolios yet.</p>
        ) : (
          <div className="saved-portfolio-list">
            {savedPortfolios.map((portfolio) => (
              <button
                type="button"
                key={portfolio.id}
                className="saved-portfolio-button"
                onClick={() => handleSelectPortfolio(portfolio.id)}
              >
                {portfolio.name} — ${portfolio.cash} cash
              </button>
            ))}
          </div>
        )}
      </section>

      {selectedPortfolio && (
        <section>
          <h2>Saved Portfolio Details</h2>

          <label>
            Name
            <input
              value={selectedPortfolio.name}
              onChange={(event) =>
                setSelectedPortfolio({
                  ...selectedPortfolio,
                  name: event.target.value,
                })
              }
            />
          </label>

          <label>
            Cash
            <input
              type="number"
              min="0"
              step="0.01"
              value={selectedPortfolio.cash}
              onChange={(event) =>
                setSelectedPortfolio({
                  ...selectedPortfolio,
                  cash: event.target.value,
                })
              }
            />
          </label>

          <div className="portfolio-actions">
            <button
              type="button"
              onClick={handleUpdateSelectedPortfolio}
            >
              Update Portfolio
            </button>

            <button
              type="button"
              className="danger-button"
              onClick={handleDeleteSelectedPortfolio}
            >
              Delete Portfolio
            </button>
          </div>

          <h3>Saved Holdings</h3>

          {selectedPortfolio.holdings.length === 0 ? (
            <p>No holdings saved for this portfolio.</p>
          ) : (
            <table>
              <thead>
                <tr>
                  <th>Ticker</th>
                  <th>Quantity</th>
                  <th>Price</th>
                  <th>Asset Class</th>
                  <th>Sector</th>
                  <th>Action</th>
                </tr>
              </thead>

              <tbody>
                {selectedPortfolio.holdings.map((holding) => (
                  <tr key={holding.id}>
                    <td>{holding.ticker}</td>
                    <td>{holding.quantity}</td>
                    <td>${holding.price}</td>
                    <td>{holding.asset_class}</td>
                    <td>{holding.sector}</td>
                    <td>
                      <button
                        type="button"
                        className="danger-button"
                        onClick={() =>
                          handleDeleteSavedHolding(holding.id)
                        }
                      >
                        Delete Holding
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </section>
      )}
    </main>
  );
}

export default App;