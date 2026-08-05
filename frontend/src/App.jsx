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
  askRagQuestion,
  createPortfolio,
  createReportJob,
  deleteHolding,
  deletePortfolio,
  getPortfolio,
  getReportJob,
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
  optimizer_explanation: {
    is_fallback: false,
    message: "Optimizer explanation generated from deterministic recommendations.",
    prompt_rules:
      "Only explain backend-generated optimizer recommendations. Cite reason codes. Do not invent returns or new recommendations.",
    overview:
      "The optimizer explanation is based only on deterministic backend recommendations that were already generated.",
    reason_codes: ["BALANCED_NO_ACTION"],
    recommendation_summaries: [
      {
        reason_code: "BALANCED_NO_ACTION",
        summary:
          "BALANCED_NO_ACTION: The optimizer did not detect a major overweight holding, overweight sector, or underweight asset class signal.",
      },
    ],
    limitations:
      "This explanation is limited to user-provided holdings and deterministic portfolio metrics. It does not use live market data, tax impact, transaction costs, or personal financial goals.",
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

function OptimizerExplanationPanel({ analysis }) {
  const explanation = analysis.optimizer_explanation;

  if (!explanation) {
    return (
      <section className="dashboard-section">
        <h2>Optimizer Explanation</h2>
        <p>Optimizer explanation unavailable. Deterministic recommendations are still shown.</p>
      </section>
    );
  }

  return (
    <section className="dashboard-section">
      <h2>Optimizer Explanation</h2>

      <p className="disclaimer">{explanation.disclaimer}</p>
      <p>{explanation.overview}</p>

      {explanation.is_fallback && (
        <p className="fallback-message">{explanation.message}</p>
      )}

      <div className="risk-explanation-list">
        {explanation.recommendation_summaries.map((item) => (
          <article key={item.reason_code} className="summary-card">
            <strong>{item.reason_code}</strong>
            <p>{item.summary}</p>
          </article>
        ))}
      </div>

      <h3>Limitations</h3>
      <p>{explanation.limitations}</p>
    </section>
  );
}

function getVisibleReportStatus(status) {
  if (status === "running") {
    return "processing";
  }

  if (status === "completed") {
    return "complete";
  }

  return status || "not started";
}

function buildReportPayloadFromAnalysis(analysis) {
  return {
    cash: analysis.cash || 0,
    scenarios: [
      "market_down_25",
      "tech_down_40",
      "rates_up",
      "cash_return",
      "international_underperformance",
      "concentrated_holding_drop",
    ],
    holdings: (analysis.holdings || []).map((holding) => ({
      ticker: holding.ticker,
      quantity: holding.quantity,
      price: holding.price,
      asset_class: holding.asset_class,
      sector: holding.sector,
    })),
  };
}

function buildDeterministicAiReportSummary(reportJob) {
  const results = reportJob?.result_json?.results || [];

  if (results.length === 0) {
    return "AI report summary will appear after the deterministic scenario report is complete.";
  }

  const worstScenario = [...results].sort(
    (firstResult, secondResult) =>
      firstResult.percent_change - secondResult.percent_change,
  )[0];

  const bestScenario = [...results].sort(
    (firstResult, secondResult) =>
      secondResult.percent_change - firstResult.percent_change,
  )[0];

  return (
    `Based only on deterministic scenario outputs, the largest downside case is ` +
    `${worstScenario.scenario_name}, with an estimated portfolio impact of ` +
    `${worstScenario.percent_change}%. The most resilient scenario is ` +
    `${bestScenario.scenario_name}, with an estimated impact of ` +
    `${bestScenario.percent_change}%. This summary explains scenario math only ` +
    `and does not predict future performance.`
  );
}

function ScenarioReportPanel({ analysis }) {
  const [reportJob, setReportJob] = useState(null);
  const [isCreatingReport, setIsCreatingReport] = useState(false);
  const [reportError, setReportError] = useState("");

  const visibleStatus = getVisibleReportStatus(reportJob?.status);
  const isTerminalStatus = ["completed", "failed"].includes(reportJob?.status);

  async function handleGenerateReport() {
    setIsCreatingReport(true);
    setReportError("");

    try {
      const payload = buildReportPayloadFromAnalysis(analysis);
      const createdJob = await createReportJob(payload);
      setReportJob(createdJob);
    } catch (error) {
      setReportError("Could not create scenario report job. Please try again.");
    } finally {
      setIsCreatingReport(false);
    }
  }

  useEffect(() => {
    if (!reportJob?.job_id || isTerminalStatus) {
      return undefined;
    }

    const pollInterval = window.setInterval(async () => {
      try {
        const updatedJob = await getReportJob(reportJob.job_id);
        setReportJob(updatedJob);
      } catch (error) {
        setReportError("Could not refresh scenario report status.");
        window.clearInterval(pollInterval);
      }
    }, 3000);

    return () => window.clearInterval(pollInterval);
  }, [reportJob?.job_id, isTerminalStatus]);

  const reportResults = reportJob?.result_json?.results || [];
  const allImpactedHoldings = reportResults
    .flatMap((result) =>
      (result.most_impacted_holdings || []).map((holding) => ({
        ...holding,
        scenario_name: result.scenario_name,
      })),
    )
    .sort(
      (firstHolding, secondHolding) =>
        Math.abs(secondHolding.dollar_change) -
        Math.abs(firstHolding.dollar_change),
    )
    .slice(0, 5);

  return (
    <section className="dashboard-section">
      <h2>Scenario Report</h2>

      <p className="disclaimer">
        Educational scenario only; not a prediction or financial advice.
      </p>

      <button
        type="button"
        onClick={handleGenerateReport}
        disabled={isCreatingReport}
      >
        {isCreatingReport ? "Creating Report..." : "Generate Scenario Report"}
      </button>

      <div className="summary-grid">
        <article className="summary-card">
          <span>Report Status</span>
          <strong>{visibleStatus}</strong>
        </article>

        {reportJob?.job_id && (
          <article className="summary-card">
            <span>Report Job ID</span>
            <strong>{reportJob.job_id}</strong>
          </article>
        )}
      </div>

      {reportJob?.status === "pending" && (
        <p>
          Report job created and waiting for the worker. Run{" "}
          <code>PYTHONPATH=. python scripts/run_worker.py</code> locally to process it.
        </p>
      )}

      {reportJob?.status === "running" && (
        <p>Report is processing. Status will refresh automatically.</p>
      )}

      {reportJob?.status === "failed" && (
        <div className="summary-card">
          <h3>Report Failed</h3>
          <p>{reportJob.error_message || "The report could not be generated."}</p>
          <button type="button" onClick={handleGenerateReport}>
            Retry Report
          </button>
        </div>
      )}

      {reportJob?.status === "completed" && (
        <>
          <article className="summary-card">
            <h3>Educational Explanation</h3>
            <p>{buildDeterministicAiReportSummary(reportJob)}</p>
          </article>

          <article className="summary-card">
            <h3>Portfolio Impact</h3>
            <table>
              <thead>
                <tr>
                  <th>Scenario</th>
                  <th>Starting Value</th>
                  <th>Scenario Value</th>
                  <th>Dollar Change</th>
                  <th>Percent Change</th>
                </tr>
              </thead>
              <tbody>
                {reportResults.map((result) => (
                  <tr key={result.scenario_name}>
                    <td>{result.scenario_name}</td>
                    <td>{formatCurrency(result.starting_value)}</td>
                    <td>{formatCurrency(result.scenario_value)}</td>
                    <td>{formatCurrency(result.dollar_change)}</td>
                    <td>{result.percent_change}%</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </article>

          <article className="summary-card">
            <h3>Assumptions</h3>
            {reportResults.map((result) => (
              <div key={`${result.scenario_name}-assumptions`}>
                <strong>{result.scenario_name}</strong>
                <ul>
                  {result.assumptions.map((assumption) => (
                    <li key={assumption}>{assumption}</li>
                  ))}
                </ul>
              </div>
            ))}
          </article>

          <article className="summary-card">
            <h3>Largest Losses</h3>
            {allImpactedHoldings.length === 0 ? (
              <p>No holding-level losses were produced by this scenario report.</p>
            ) : (
              <table>
                <thead>
                  <tr>
                    <th>Scenario</th>
                    <th>Ticker</th>
                    <th>Starting Value</th>
                    <th>Scenario Value</th>
                    <th>Dollar Change</th>
                    <th>Percent Change</th>
                  </tr>
                </thead>
                <tbody>
                  {allImpactedHoldings.map((holding, index) => (
                    <tr key={`${holding.scenario_name}-${holding.ticker}-${index}`}>
                      <td>{holding.scenario_name}</td>
                      <td>{holding.ticker}</td>
                      <td>{formatCurrency(holding.starting_value)}</td>
                      <td>{formatCurrency(holding.scenario_value)}</td>
                      <td>{formatCurrency(holding.dollar_change)}</td>
                      <td>{holding.percent_change}%</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </article>
        </>
      )}

      {reportError && <p className="error-message">{reportError}</p>}
    </section>
  );
}

function RagAssistantPanel() {
  const exampleQuestions = [
    "What is diversification?",
    "What is concentration risk?",
    "Why can cash drag matter?",
    "What is rebalancing?",
  ];

  const [ragQuestion, setRagQuestion] = useState("");
  const [ragAnswer, setRagAnswer] = useState(null);
  const [isAskingRag, setIsAskingRag] = useState(false);
  const [ragError, setRagError] = useState("");

  async function handleAskRag(event) {
    event.preventDefault();

    if (!ragQuestion.trim()) {
      setRagError("Please enter a question.");
      return;
    }

    setIsAskingRag(true);
    setRagError("");

    try {
      const result = await askRagQuestion(ragQuestion.trim());
      setRagAnswer(result);
    } catch (error) {
      setRagError("Could not answer the RAG question. Please try again.");
    } finally {
      setIsAskingRag(false);
    }
  }

  function handleExampleQuestion(question) {
    setRagQuestion(question);
    setRagAnswer(null);
    setRagError("");
  }

  return (
    <section className="dashboard-section">
      <h2>Finance Notes Assistant</h2>

      <p className="disclaimer">
        Educational information only; answers come from retrieved finance-note
        sections and are not investment advice.
      </p>

      <form onSubmit={handleAskRag}>
        <label>
          Ask a finance concept question
          <input
            value={ragQuestion}
            onChange={(event) => setRagQuestion(event.target.value)}
            placeholder="Example: What is diversification?"
          />
        </label>

        <button type="submit" disabled={isAskingRag}>
          {isAskingRag ? "Searching Notes..." : "Ask Finance Notes"}
        </button>
      </form>

      <div className="summary-grid">
        {exampleQuestions.map((question) => (
          <button
            type="button"
            key={question}
            onClick={() => handleExampleQuestion(question)}
          >
            {question}
          </button>
        ))}
      </div>

      {ragError && <p className="error-message">{ragError}</p>}

      {ragAnswer && (
        <>
          <article className="summary-card">
            <h3>Answer</h3>

            {ragAnswer.unsupported && (
              <p className="fallback-message">
                Unsupported question. The assistant could not answer safely from
                the retrieved finance-note context.
              </p>
            )}

            <p>{ragAnswer.answer}</p>

            <p>
              <strong>Confidence:</strong> {ragAnswer.confidence}
            </p>

            <p>
              <strong>Unsupported:</strong>{" "}
              {ragAnswer.unsupported ? "yes" : "no"}
            </p>
          </article>

          <article className="summary-card">
            <h3>Cited Sections</h3>

            {ragAnswer.cited_sections.length === 0 ? (
              <p>No cited sections were retrieved.</p>
            ) : (
              <div className="risk-explanation-list">
                {ragAnswer.cited_sections.map((section) => (
                  <article key={section.chunk_id} className="summary-card">
                    <strong>
                      {section.chunk_id} — {section.title}
                    </strong>
                    <p>{section.source_filename}</p>
                    <p>Score: {section.score}</p>
                    <p>{section.text.slice(0, 500)}...</p>
                  </article>
                ))}
              </div>
            )}
          </article>

          <article className="summary-card">
            <h3>Prompt Rules</h3>
            <ul>
              {ragAnswer.prompt_rules.map((rule) => (
                <li key={rule}>{rule}</li>
              ))}
            </ul>
          </article>
        </>
      )}
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
      <OptimizerExplanationPanel analysis={dashboardAnalysis} />
      <ScenarioReportPanel analysis={dashboardAnalysis} />
      <RagAssistantPanel />
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