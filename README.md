# AI-Powered Portfolio Optimizer

> An intelligent investment platform combining sentiment analysis, machine learning price prediction, and algorithmic portfolio optimization.

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Code Coverage](https://img.shields.io/badge/coverage-0%25-red.svg)](https://github.com/yourusername/portfolio-optimizer)

## Overview

This project demonstrates the intersection of AI/ML, Software Engineering, and FinTech by building a production-ready system that:

- Analyzes market sentiment from news and social media using NLP
- Predicts stock prices using LSTM and Transformer models
- Optimizes portfolios using Modern Portfolio Theory and ML
- Backtests strategies with realistic market conditions
- Visualizes insights through an interactive dashboard

## Features

### Current Features

- Real-time data collection from multiple sources
- FinBERT-based sentiment analysis
- LSTM/Transformer price prediction models
- Mean-variance portfolio optimization
- Comprehensive backtesting engine
- REST API with authentication
- Interactive web dashboard
- Risk metrics calculation (Sharpe, VaR, Drawdown)

### Planned Features

- Cryptocurrency support
- Options pricing models
- Reinforcement learning for portfolio management
- ESG scoring integration
- Mobile app
- Multi-user support with saved portfolios

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        Frontend (React)                     │
│  Dashboard │ Sentiment View │ Predictions │ Portfolio │ BT  │
└────────────────────────────┬────────────────────────────────┘
                             │ REST API
┌────────────────────────────┴────────────────────────────────┐
│                     Backend (FastAPI)                       │
├──────────────────┬──────────────────┬──────────────────────-┤
│   Sentiment API  │  Prediction API  │     Portfolio API     │
└────────┬─────────┴────────┬─────────┴──────────┬───────────-┘
         │                  │                    │
┌────────┴─────────┬────────┴─────────┬──────────┴───────────┐
│    Sentiment     │     ML Models    │      Optimizer       │
│      Engine      │   (LSTM/Trans.)  │       (MPT/RL)       │
│    (FinBERT)     │                  │                      │
└────────┬─────────┴────────┬─────────┴──────────┬───────────┘
         │                  │                    │
┌────────┴──────────────────┴────────────────────┴──────────--─┐
│              Data Layer (PostgreSQL/TimescaleDB)             │
│  Stock Prices │ News │ Sentiment │ Predictions │ Portfolios  │
└──────────────────────────────────────────────────────────────┘
         │                  │                     │
┌────────┴──────────────────┴─────────────────────┴───────────┐
│                     Data Collection                         │
│        yfinance │ NewsAPI │ Reddit API │ Twitter API        │
└─────────────────────────────────────────────────────────────┘
```

## Quick Start

### Prerequisites
- Python 3.10+
- Node.js 18+
- Docker & Docker Compose
- PostgreSQL 14+

### Installation

1. Clone the repository
```bash
git clone https://github.com/yourusername/portfolio-optimizer.git
cd portfolio-optimizer
```

2. Set up environment variables
```bash
cp .env.example .env
# Edit .env with your API keys
```

3. Start infrastructure services
```bash
docker-compose up -d postgres redis
```

4. Backend setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Initialize database
python scripts/setup_database.py

# Collect historical data
python scripts/collect_historical_data.py

# Run backend
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

5. Frontend setup (in a new terminal)
```bash
cd frontend
npm install
npm run dev
```

6. Access the application
- Frontend: http://localhost:3000
- API Docs: http://localhost:8000/docs
- API Health: http://localhost:8000/health

## API Documentation

### Sentiment Analysis
```bash
POST /api/v1/sentiment/analyze
Content-Type: application/json

{
  "text": "Apple reports record earnings, stock surges 5%",
  "source": "news"
}
```

### Price Prediction
```bash
POST /api/v1/predict/price
Content-Type: application/json

{
  "ticker": "AAPL",
  "days_ahead": 5,
  "model": "lstm"
}
```

### Portfolio Optimization
```bash
POST /api/v1/portfolio/optimize
Content-Type: application/json

{
  "tickers": ["AAPL", "GOOGL", "MSFT", "AMZN"],
  "investment_amount": 10000,
  "risk_tolerance": "moderate",
  "constraints": {
    "max_position_size": 0.3,
    "min_position_size": 0.05
  }
}
```

Full API documentation available at '/docs' when running the backend.

## Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=backend --cov-report=html

# Run specific test file
pytest tests/test_sentiment.py

# Run integration tests
pytest tests/integration/
```

## Model Performance

### Sentiment Analysis
- Model: FinBERT (fine-tuned)
- Accuracy: TBD%
- F1-Score: TBD

### Price Prediction
- Model: LSTM + Attention
- RMSE: TBD
- Directional Accuracy: TBD%

### Portfolio Performance (Backtested)
- Period: TBD
- Sharpe Ratio: TBD
- Max Drawdown: TBD%
- Annual Return: TBD%

## Tech Stack

**Backend**
- FastAPI (API framework)
- PyTorch (Deep learning)
- Hugging Face Transformers (NLP)
- scikit-learn (ML utilities)
- pandas, numpy (Data processing)
- SQLAlchemy (ORM)
- Celery (Task queue)

**Frontend**
- React + TypeScript
- Tailwind CSS
- Chart.js / Recharts
- Axios (API client)

**Infrastructure**
- PostgreSQL + TimescaleDB
- Redis (Caching)
- Docker
- GitHub Actions (CI/CD)

**Data Sources**
- yfinance (Stock data)
- Alpha Vantage (Financial data)
- NewsAPI (News articles)
- Reddit API (Social sentiment)

## Project Structure

## 📁 Project Structure

```
portfolio-optimizer/
├── backend/          # Python backend
│   ├── api/          # FastAPI routes
│   ├── data/         # Data collection & processing
│   ├── ml/           # ML models
│   ├── portfolio/    # Portfolio optimization
│   └── tests/        # Unit & integration tests
├── frontend/         # React frontend
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   └── services/
├── notebooks/        # Jupyter notebooks for exploration
├── scripts/          # Utility scripts
├── docs/             # Documentation
└── docker-compose.yml
```

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines. :)

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Development Log

Track progress in [DEVELOPMENT.md](DEVELOPMENT.md)

## Resources & References

- [Modern Portfolio Theory](https://en.wikipedia.org/wiki/Modern_portfolio_theory)
- [FinBERT Paper](https://arxiv.org/abs/1908.10063)
- [Advances in Financial Machine Learning](https://www.wiley.com/en-us/Advances+in+Financial+Machine+Learning-p-9781119482086)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)

## Disclaimer

This project is for educational purposes only. It is not financial advice. Do not use this system for actual trading without proper due diligence and risk management. Past performance does not guarantee future results.

## License

This project is licensed under the MIT License - see [LICENSE](LICENSE) file for details.

## Author

**Deepthi Morusupalli**
- GitHub: [@deepthimor](https://github.com/deepthimor)
- Email: morusupallida@gmail.com
- LinkedIn: [Deepthi Morusupalli](https://linkedin.com/in/deepthimor)

## Acknowledgments

- UT Austin for the education <3
- Open source community
- Financial data providers

**Status**: In Development | Last Updated: May 2026
