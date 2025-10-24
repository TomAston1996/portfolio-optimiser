from datetime import datetime

import numpy as np
import pandas as pd

from portfoliooptimiser.market_api import IMarketAPI, PriceType
from portfoliooptimiser.portfolio_optimiser import (
    MaximumSharpeRatioOptimiser,
    MinimumVolatilityOptimiser,
    PortfolioOptimiser,
    PortfolioOptimiserConfig,
    PortfolioOptimiserContext,
    PortfolioResult,
)


class MockMarketAPI(IMarketAPI):
    """Mock implementation of IMarketAPI for testing purposes."""

    def get_historical_ticker_data(
        self, tickers: list[str], price_type: PriceType, start_date: datetime, end_date: datetime
    ) -> pd.DataFrame:
        dates = pd.date_range(start=start_date, end=end_date, freq="D")
        data = {ticker: pd.Series(100 + np.arange(len(dates)), index=dates) for ticker in tickers}
        return pd.DataFrame(data)


def create_context() -> tuple[PortfolioOptimiserContext, PortfolioOptimiserConfig]:
    api = MockMarketAPI()
    context = PortfolioOptimiserContext(market_api=api)
    config = PortfolioOptimiserConfig(number_of_simulations=1000)
    return context, config


def test_max_sharpe_ratio_optimiser() -> None:
    # Arrange
    context, config = create_context()
    optimiser = MaximumSharpeRatioOptimiser(context, config)

    start = datetime(2025, 1, 1)
    end = datetime(2025, 1, 5)
    tickers = ["AAPL", "MSFT", "GOOG"]

    # Act
    result: PortfolioResult = optimiser.optimise_portfolio(tickers, start, end)

    # Assert
    assert isinstance(result, PortfolioResult)
    assert isinstance(result.weights, np.ndarray)
    assert np.isclose(result.weights.sum(), 1.0, atol=1e-3)
    assert all(0 <= w <= 1 for w in result.weights)
    assert result.expected_volatility > 0
    assert result.sharpe_ratio > 0


def test_min_volatility_optimiser() -> None:
    # Arrange
    context, config = create_context()
    optimiser = MinimumVolatilityOptimiser(context, config)

    start = datetime(2025, 1, 1)
    end = datetime(2025, 1, 5)
    tickers = ["AAPL", "MSFT", "GOOG"]

    # Act
    result: PortfolioResult = optimiser.optimise_portfolio(tickers, start, end)

    # Assert
    assert isinstance(result, PortfolioResult)
    assert isinstance(result.weights, np.ndarray)
    assert np.isclose(result.weights.sum(), 1.0, atol=1e-3)
    assert all(0 <= w <= 1 for w in result.weights)
    assert result.expected_volatility > 0


def test_get_expected_returns_and_volatility() -> None:
    # Arrange
    api = MockMarketAPI()
    context = PortfolioOptimiserContext(market_api=api)
    config = PortfolioOptimiserConfig(number_of_simulations=100)
    optimiser = PortfolioOptimiser(context, config)

    tickers = ["AAPL", "MSFT", "GOOG"]
    start = datetime(2025, 1, 1)
    end = datetime(2025, 1, 10)

    returns_df = optimiser._get_log_returns_df(tickers, start, end)  # type: ignore

    # Act
    portfolio_rets, portfolio_vols = optimiser.get_expected_returns_and_volatility(tickers, returns_df)

    # Assert
    assert isinstance(portfolio_rets, np.ndarray)
    assert isinstance(portfolio_vols, np.ndarray)
    assert portfolio_rets.shape[0] == config.number_of_simulations
    assert portfolio_vols.shape[0] == config.number_of_simulations

    # All volatilities should be non-negative
    assert np.all(portfolio_vols >= 0)

    # Returns and volatilities should be finite numbers
    assert np.all(np.isfinite(portfolio_rets))
    assert np.all(np.isfinite(portfolio_vols))

    # Optional: check that mean return and volatility are reasonable
    assert portfolio_rets.mean() > 0
    assert portfolio_vols.mean() > 0
