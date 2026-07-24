import { useEffect, useMemo, useState } from "react";
import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
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

const defaultTargetAllocation = {
  stock: 60,
  etf: 30,
  bond: 10,
  cash: 0,
};

const samplePortfolio = {
  cash: 2500,
  target_allocation: {
    stock: 60,
    etf: 30,
    cash: 10,
  },
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

const sampleAnalysis = {
  total_portfolio_value: 15180,
  total_holdings_value: 12680,
  cash: 2500,
  cash_percentage: 16.47,
  number_of_holdings: 3,
  largest_holding: "VTI",
  largest_sector: "technology",
  top_1_percentage: 30.83,
  top_3_percentage: 83.53,
  top_5_percentage: 83.53,
  holdings: [
    {
      ticker: "VTI",
      quantity: 18,
      price: 260,
      market_value: 4680,
      weight: 30.83,
      asset_class: "etf",
      sector: "broad market",
    },
    {
      ticker: "MSFT",
      quantity: 10,
      price: 420,
      market_value: 4200,
      weight: 27.67,
      asset_class: "stock",
      sector: "technology",
    },
    {
      ticker: "AAPL",
      quantity: 20,
      price: 190,
      market_value: 3800,
      weight: 25.03,
      asset_class: "stock",
      sector: "technology",
    },
  ],
  top_holdings: [
    {
      ticker: "VTI",
      market_value: 4680,
      weight: 30.83,
      asset_class: "etf",
      sector: "broad market",
    },
    {
      ticker: "MSFT",
      market_value: 4200,
      weight: 27.67,
      asset_class: "stock",
      sector: "technology",
    },
    {
      ticker: "AAPL",
      market_value: 3800,
      weight: 25.03,
      asset_class: "stock",
      sector: "technology",
    },
  ],
  sector_breakdown: {
    technology: 52.7,
    "broad market": 30.83,
  },
  asset_class_breakdown: {
    stock: 52.7,
    etf: 30.83,
  },
  risk_score: {
    risk_score_v1: 58.42,
    risk_level: "moderate",
    concentration_score: 63.78,
    diversification_score: 41.87,
    sector_exposure_score: 100,
    cash_score: 0,
    target_allocation_gap_score: 41.77,
    target_allocation_gap_analysis: [
      {
        asset_class: "stock",
        current_weight: 52.7,
        target_weight: 60,
        difference: -7.3,
        status: "underweight",
      },
      {
        asset_class: "cash",
        current_weight: 16.47,
        target_weight: 10,
        difference: 6.47,
        status: "overweight",
      },
      {
        asset_class: "etf",
        current_weight: 30.83,
        target_weight: 30,
        difference: 0.83,
        status: "on target",
      },
    ],
    inputs: {
      risk_tolerance: "moderate",
      max_holding: 30,
      max_sector: 45,
      cash_threshold: 25,
      target_allocation: {
        stock: 60,
        etf: 30,
        cash: 10,
      },
      expected_return: null,
      volatility: null,
    },
    explanations: [
      "Risk score v1 is a deterministic weighted score using concentration, sector exposure, cash percentage, and target allocation gaps.",
      "Concentration score is based on top 1, top 3, and top 5 holding exposure.",
      "Diversification score is based on number of holdings, number of sectors, and concentration.",
    ],
  },
  optimizer: {
    recommendations: [
      {
        action: "no_action",
        ticker: null,
        amount_or_percent: 0,
        reason_code: "BALANCED_NO_ACTION",
        human_reason:
          "Optimizer recommendation logic is initialized. Future versions will add deterministic portfolio review signals.",
        before_weight: null,
        after_weight_estimate: null,
        priority: "low",
      },
    ],
    disclaimer: "Educational information only; not financial advice.",
  },
  ai_summary: {
    is_fallback: false,
    message: "AI summary generated from deterministic metrics.",
    disclaimer: "Educational information only; not financial advice.",
    sections: {
      portfolio_overview:
        "Total portfolio value is $15,180.00. The portfolio has 3 holdings and 16.47% held in cash.",
      concentration_observations:
        "Top 1 concentration is 30.83%, top 3 concentration is 83.53%, and top 5 concentration is 83.53%. The largest holding is VTI.",
      allocation_observations:
        "The largest sector is technology. Asset allocation is stock and ETF. Sector allocation is technology and broad market.",
      educational_note:
        "Educational information only; not financial advice. This summary explains supplied metrics and does not recommend buying, selling, or holding any security.",
      limitations:
        "This summary is based only on user-supplied holdings and backend-calculated metrics.",
      risk_flags:
        "High single-holding concentration, High top-three concentration, High top-five concentration",
    },
  },
};

const chartColors = ["#60a5fa", "#34d399", "#fbbf24", "#f472b6", "#a78bfa"];

function formatCurrency(value) {
  return `$${Number(value || 0).toLocaleString(undefined, {
    maximumFractionDigits: 2,
  })}`;
}

function objectToChartData(source) {
  return Object.entries(source || {}).map(([name, value]) => ({
    name,
    value,
  }));
}

function getConcentrationMetrics(analysis) {
  return {
    largestHoldingName: analysis?.largest_holding || "N/A",
    largestHoldingWeight: analysis?.top_1_percentage || 0,
    topThreeWeight: analysis?.top_3_percentage || 0,
    topFiveWeight: analysis?.top_5_percentage || 0,
  };
}

function PortfolioForm({
  portfolioName,
  setPortfolioName,
  cash,
  setCash,
  targetAllocation,
  updateTargetAllocation,
  holdings,
  updateHoldingInput,
  addHoldingInput,
  removeHoldingInput,
  loadSamplePortfolio,
  clearPortfolioForm,
  handleAnalyze,
  handleSavePortfolio,
  isLoading,
}) {
  return (
    <form onSubmit={handleAnalyze} className="input-panel">
      <div className="form-grid">
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
      </div>

      <h2>Target Allocation</h2>

      <div className="form-grid">
        {Object.entries(targetAllocation).map(([assetClass, targetWeight]) => (
          <label key={assetClass}>
            {assetClass} Target %
            <input
              type="number"
              min="0"
              max="100"
              step="0.01"
              value={targetWeight}
              onChange={(event) =>
                updateTargetAllocation(assetClass, event.target.value)
              }
            />
          </label>
        ))}
      </div>

      <h2>Holdings Input</h2>

      {holdings.map((holding, index) => (
        <section key={index} className="holding-input-row">
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

          <button type="button" onClick={() => removeHoldingInput(index)}>
            Remove
          </button>
        </section>
      ))}

      <div className="button-row">
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
          {isLoading ? "Analyzing..." : "Analyze Portfolio"}
        </button>

        <button type="button" onClick={handleSavePortfolio} disabled={isLoading}>
          Save Portfolio
        </button>
      </div>
    </form>
  );
}

function StatusArea({ isLoading, error, success, hasAnalysis }) {
  return (
    <section className="status-area">
      {isLoading && <p className="loading">Analyzing portfolio...</p>}
      {error && <p className="error">{error}</p>}
      {success && <p className="success">{success}</p>}
      {!isLoading && !error && !success && !hasAnalysis && (
        <p className="empty-state">
          No portfolio analyzed yet. Enter holdings or load the sample portfolio
          to see dashboard results.
        </p>
      )}
    </section>
  );
}

function SummaryCards({ analysis, isSample }) {
  return (
    <section className="dashboard-section">
      <div className="section-title-row">
        <h2>Summary Cards</h2>
        {isSample && <span className="sample-pill">sample preview</span>}
      </div>

      <div className="summary-grid">
        <article className="summary-card">
          <span>Total Value</span>
          <strong>{formatCurrency(analysis.total_portfolio_value)}</strong>
        </article>

        <article className="summary-card">
          <span>Cash Percentage</span>
          <strong>{analysis.cash_percentage}%</strong>
        </article>

        <article className="summary-card">
          <span>Number of Holdings</span>
          <strong>{analysis.number_of_holdings}</strong>
        </article>

        <article className="summary-card">
          <span>Largest Holding</span>
          <strong>{analysis.largest_holding}</strong>
        </article>

        <article className="summary-card">
          <span>Largest Sector</span>
          <strong>{analysis.largest_sector}</strong>
        </article>
      </div>
    </section>
  );
}

function BreakdownSection({ title, data }) {
  return (
    <article className="chart-card">
      <h3>{title}</h3>

      <ResponsiveContainer width="100%" height={260}>
        <PieChart>
          <Pie
            data={data}
            dataKey="value"
            nameKey="name"
            outerRadius={90}
            label
          >
            {data.map((entry, index) => (
              <Cell
                key={entry.name}
                fill={chartColors[index % chartColors.length]}
              />
            ))}
          </Pie>
          <Tooltip />
        </PieChart>
      </ResponsiveContainer>
    </article>
  );
}

function AllocationCharts({ analysis, isSample }) {
  const assetClassData = objectToChartData(analysis.asset_class_breakdown);
  const sectorData = objectToChartData(analysis.sector_breakdown);

  return (
    <section className="dashboard-section">
      <div className="section-title-row">
        <h2>Allocation Charts</h2>
        {isSample && <span className="sample-pill">sample preview</span>}
      </div>

      <div className="chart-grid">
        <BreakdownSection title="Asset Allocation" data={assetClassData} />
        <BreakdownSection title="Sector Exposure" data={sectorData} />
      </div>
    </section>
  );
}

function TopHoldingsTable({ topHoldings }) {
  const sortedTopHoldings = [...topHoldings].sort(
    (firstHolding, secondHolding) => secondHolding.weight - firstHolding.weight,
  );

  return (
    <section className="dashboard-section">
      <h2>Top Holdings Table</h2>

      <table>
        <thead>
          <tr>
            <th>Ticker</th>
            <th>Value</th>
            <th>Weight</th>
            <th>Asset Class</th>
            <th>Sector</th>
          </tr>
        </thead>

        <tbody>
          {sortedTopHoldings.map((holding) => (
            <tr key={`${holding.ticker}-${holding.market_value}`}>
              <td>{holding.ticker}</td>
              <td>{formatCurrency(holding.market_value)}</td>
              <td>{holding.weight}%</td>
              <td>{holding.asset_class}</td>
              <td>{holding.sector}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </section>
  );
}

function TopHoldings({ topHoldings }) {
  return (
    <section className="dashboard-section">
      <h2>Top Holdings Chart</h2>

      <ResponsiveContainer width="100%" height={260}>
        <BarChart data={topHoldings}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="ticker" />
          <YAxis />
          <Tooltip />
          <Bar dataKey="weight">
            {topHoldings.map((holding, index) => (
              <Cell
                key={holding.ticker}
                fill={chartColors[index % chartColors.length]}
              />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </section>
  );
}

function ConcentrationCards({ analysis }) {
  const concentration = getConcentrationMetrics(analysis);

  return (
    <section className="dashboard-section">
      <h2>Concentration Cards</h2>

      <div className="summary-grid">
        <article className="summary-card">
          <span>Top 1 Concentration</span>
          <strong>{concentration.largestHoldingWeight}%</strong>
        </article>

        <article className="summary-card">
          <span>Top 3 Concentration</span>
          <strong>{concentration.topThreeWeight}%</strong>
        </article>

        <article className="summary-card">
          <span>Top 5 Concentration</span>
          <strong>{concentration.topFiveWeight}%</strong>
        </article>
      </div>
    </section>
  );
}

function RiskCards({ analysis }) {
  const risk = analysis.risk_score;

  if (!risk) {
    return null;
  }

  return (
    <section className="dashboard-section">
      <h2>Risk Score</h2>

      <div className="summary-grid">
        <article className="summary-card">
          <span>Risk Score v1</span>
          <strong>{risk.risk_score_v1}</strong>
        </article>

        <article className="summary-card">
          <span>Risk Level</span>
          <strong>{risk.risk_level}</strong>
        </article>

        <article className="summary-card">
          <span>Concentration Score</span>
          <strong>{risk.concentration_score}</strong>
        </article>

        <article className="summary-card">
          <span>Diversification Score</span>
          <strong>{risk.diversification_score}</strong>
        </article>

        <article className="summary-card">
          <span>Sector Exposure Score</span>
          <strong>{risk.sector_exposure_score}</strong>
        </article>

        <article className="summary-card">
          <span>Cash Score</span>
          <strong>{risk.cash_score}</strong>
        </article>

        <article className="summary-card">
          <span>Target Gap Score</span>
          <strong>{risk.target_allocation_gap_score}</strong>
        </article>
      </div>

      <div className="risk-explanation-list">
        {risk.explanations.map((explanation) => (
          <p key={explanation}>{explanation}</p>
        ))}
      </div>
    </section>
  );
}

function TargetGapTable({ analysis }) {
  const gapAnalysis = analysis.risk_score?.target_allocation_gap_analysis || [];

  if (gapAnalysis.length === 0) {
    return null;
  }

  return (
    <section className="dashboard-section">
      <h2>Target Allocation Gap</h2>

      <table>
        <thead>
          <tr>
            <th>Asset Class</th>
            <th>Current Weight</th>
            <th>Target Weight</th>
            <th>Difference</th>
            <th>Status</th>
          </tr>
        </thead>

        <tbody>
          {gapAnalysis.map((gap) => (
            <tr key={gap.asset_class}>
              <td>{gap.asset_class}</td>
              <td>{gap.current_weight}%</td>
              <td>{gap.target_weight}%</td>
              <td>{gap.difference}%</td>
              <td>{gap.status}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </section>
  );
}

function FutureAiSummaryPanel({ analysis }) {
  const aiSummary = analysis.ai_summary;

  if (!aiSummary) {
    return (
      <section className="dashboard-section ai-panel">
        <h2>AI Summary Panel</h2>

        <p className="disclaimer">
          Educational information only; not financial advice.
        </p>

        <p>AI summary unavailable; deterministic metrics still shown.</p>
      </section>
    );
  }

  return (
    <section className="dashboard-section ai-panel">
      <h2>AI Summary Panel</h2>

      <p className="disclaimer">{aiSummary.disclaimer}</p>

      {aiSummary.is_fallback && (
        <p className="fallback-message">{aiSummary.message}</p>
      )}

      <div className="ai-summary-grid">
        <article>
          <h3>Portfolio Overview</h3>
          <p>{aiSummary.sections.portfolio_overview}</p>
        </article>

        <article>
          <h3>Concentration Observations</h3>
          <p>{aiSummary.sections.concentration_observations}</p>
        </article>

        <article>
          <h3>Allocation Observations</h3>
          <p>{aiSummary.sections.allocation_observations}</p>
        </article>

        <article>
          <h3>Educational Note</h3>
          <p>{aiSummary.sections.educational_note}</p>
        </article>

        <article>
          <h3>Limitations</h3>
          <p>{aiSummary.sections.limitations}</p>
        </article>
      </div>
    </section>
  );
}

function OptimizerPanel({ analysis }) {
  const optimizer = analysis.optimizer;
  const recommendations = optimizer?.recommendations || [];

  const sellTrimRecommendations = recommendations.filter((recommendation) =>
    ["reduce_exposure", "review"].includes(recommendation.action) &&
    ["OVERWEIGHT_HOLDING", "OVERWEIGHT_SECTOR"].includes(recommendation.reason_code)
  );

  const buyReallocateRecommendations = recommendations.filter(
    (recommendation) => recommendation.action === "add_exposure",
  );

  const holdRecommendations = recommendations.filter(
    (recommendation) =>
      recommendation.action === "no_action" ||
      recommendation.reason_code === "BELOW_CASH_TARGET",
  );

  function renderRecommendationGroup(title, groupedRecommendations) {
    return (
      <article className="summary-card">
        <h3>{title}</h3>

        {groupedRecommendations.length === 0 ? (
          <p>No recommendations in this group.</p>
        ) : (
          groupedRecommendations.map((recommendation, index) => (
            <div key={`${recommendation.reason_code}-${index}`}>
              <strong>{recommendation.reason_code}</strong>
              <p>{recommendation.human_reason}</p>
              <p>Action: {recommendation.action}</p>
              <p>Priority: {recommendation.priority}</p>
            </div>
          ))
        )}
      </article>
    );
  }

  return (
    <section className="dashboard-section">
      <h2>Optimizer Panel</h2>

      <p className="disclaimer">
        {optimizer?.disclaimer || "Educational information only; not financial advice."}
      </p>

      <div className="summary-grid">
        {renderRecommendationGroup("Sell / Trim", sellTrimRecommendations)}
        {renderRecommendationGroup("Buy / Reallocate", buyReallocateRecommendations)}
        {renderRecommendationGroup("Hold / No Action", holdRecommendations)}
      </div>
    </section>
  );
}

function Dashboard({ analysis, hasAnalysis }) {
  const dashboardAnalysis = analysis || sampleAnalysis;
  const isSample = !hasAnalysis;

  return (
    <>
      <SummaryCards analysis={dashboardAnalysis} isSample={isSample} />
      <AllocationCharts analysis={dashboardAnalysis} isSample={isSample} />
      <TopHoldingsTable topHoldings={dashboardAnalysis.top_holdings} />
      <TopHoldings topHoldings={dashboardAnalysis.top_holdings} />
      <ConcentrationCards analysis={dashboardAnalysis} />
      <RiskCards analysis={dashboardAnalysis} />
      <TargetGapTable analysis={dashboardAnalysis} />
      <OptimizerPanel analysis={dashboardAnalysis} />
      <FutureAiSummaryPanel analysis={dashboardAnalysis} />
    </>
  );
}

function SavedPortfolios({
  savedPortfolios,
  refreshSavedPortfolios,
  handleSelectPortfolio,
}) {
  return (
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
              {portfolio.name} — {formatCurrency(portfolio.cash)} cash
            </button>
          ))}
        </div>
      )}
    </section>
  );
}

function SavedPortfolioDetails({
  selectedPortfolio,
  setSelectedPortfolio,
  handleUpdateSelectedPortfolio,
  handleDeleteSelectedPortfolio,
  handleDeleteSavedHolding,
}) {
  if (!selectedPortfolio) {
    return null;
  }

  return (
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
        <button type="button" onClick={handleUpdateSelectedPortfolio}>
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
                <td>{formatCurrency(holding.price)}</td>
                <td>{holding.asset_class}</td>
                <td>{holding.sector}</td>
                <td>
                  <button
                    type="button"
                    className="danger-button"
                    onClick={() => handleDeleteSavedHolding(holding.id)}
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
  );
}

function App() {
  const [portfolioName, setPortfolioName] = useState("");
  const [cash, setCash] = useState(0);
  const [targetAllocation, setTargetAllocation] = useState({
    ...defaultTargetAllocation,
  });
  const [holdings, setHoldings] = useState([{ ...emptyHolding }]);
  const [portfolioAnalysis, setPortfolioAnalysis] = useState(null);

  const [savedPortfolios, setSavedPortfolios] = useState([]);
  const [selectedPortfolio, setSelectedPortfolio] = useState(null);

  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  const hasAnalysis = useMemo(
    () => Boolean(portfolioAnalysis),
    [portfolioAnalysis],
  );

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

  function updateTargetAllocation(assetClass, value) {
    setTargetAllocation({
      ...targetAllocation,
      [assetClass]: value,
    });
  }

  function addHoldingInput() {
    setHoldings([...holdings, { ...emptyHolding }]);
  }

  function removeHoldingInput(index) {
    if (holdings.length === 1) {
      return;
    }

    setHoldings(holdings.filter((_, currentIndex) => currentIndex !== index));
  }

  function buildPortfolioPayload() {
    return {
      cash: Number(cash),
      target_allocation: Object.fromEntries(
        Object.entries(targetAllocation).map(([assetClass, targetWeight]) => [
          assetClass,
          Number(targetWeight),
        ]),
      ),
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
    setTargetAllocation(samplePortfolio.target_allocation);
    setHoldings(samplePortfolio.holdings);
    setPortfolioAnalysis(null);
    setError("");
    setSuccess("Sample portfolio loaded.");
  }

  function clearPortfolioForm() {
    setPortfolioName("");
    setCash(0);
    setTargetAllocation({ ...defaultTargetAllocation });
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
        Analyze portfolios, save them to PostgreSQL, and understand allocation,
        sector exposure, top holdings, and concentration at a glance.
      </p>

      <PortfolioForm
        portfolioName={portfolioName}
        setPortfolioName={setPortfolioName}
        cash={cash}
        setCash={setCash}
        targetAllocation={targetAllocation}
        updateTargetAllocation={updateTargetAllocation}
        holdings={holdings}
        updateHoldingInput={updateHoldingInput}
        addHoldingInput={addHoldingInput}
        removeHoldingInput={removeHoldingInput}
        loadSamplePortfolio={loadSamplePortfolio}
        clearPortfolioForm={clearPortfolioForm}
        handleAnalyze={handleAnalyze}
        handleSavePortfolio={handleSavePortfolio}
        isLoading={isLoading}
      />

      <StatusArea
        isLoading={isLoading}
        error={error}
        success={success}
        hasAnalysis={hasAnalysis}
      />

      <Dashboard analysis={portfolioAnalysis} hasAnalysis={hasAnalysis} />

      <SavedPortfolios
        savedPortfolios={savedPortfolios}
        refreshSavedPortfolios={refreshSavedPortfolios}
        handleSelectPortfolio={handleSelectPortfolio}
      />

      <SavedPortfolioDetails
        selectedPortfolio={selectedPortfolio}
        setSelectedPortfolio={setSelectedPortfolio}
        handleUpdateSelectedPortfolio={handleUpdateSelectedPortfolio}
        handleDeleteSelectedPortfolio={handleDeleteSelectedPortfolio}
        handleDeleteSavedHolding={handleDeleteSavedHolding}
      />
    </main>
  );
}

export default App;