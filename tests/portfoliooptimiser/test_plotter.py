import numpy as np
import pandas as pd

from matplotlib.figure import Figure

from portfoliooptimiser.plotter import MatplotlibPlotterV1
from portfoliooptimiser.portfolio_optimiser import PortfolioResult


def test_get_log_returns_plot() -> None:
    # Arrange
    plotter = MatplotlibPlotterV1()
    tickers = ["AAPL", "GOOG"]
    dates = pd.date_range("2023-01-01", periods=5)
    returns_df = pd.DataFrame(
        np.random.randn(5, 2),
        index=dates,
        columns=tickers,
    )

    # Act
    fig = plotter.get_log_returns_plot(returns_df, tickers)

    # Assert
    assert isinstance(fig, Figure)
    ax = fig.axes[0]
    assert ax.get_title() == "Log Returns Over Time"
    assert ax.get_xlabel() == "Date"
    assert ax.get_ylabel() == "Log Return"
    assert len(ax.get_lines()) == len(tickers)
    assert all(line.get_label() in tickers for line in ax.get_lines())


def test_get_efficient_frontier_plot() -> None:
    # Arrange
    plotter = MatplotlibPlotterV1()
    n_points = 10
    portfolio_vols = np.linspace(0.1, 0.3, n_points)
    portfolio_rets = np.linspace(0.05, 0.15, n_points)

    sharpe_result = PortfolioResult(
        weights=np.array([0.5, 0.5]),
        expected_return=0.14,
        expected_volatility=0.2,
        sharpe_ratio=0.7,
    )
    minvol_result = PortfolioResult(
        weights=np.array([0.6, 0.4]),
        expected_return=0.06,
        expected_volatility=0.1,
        sharpe_ratio=0.6,
    )

    # Act
    fig = plotter.get_efficient_frontier_plot(portfolio_rets, portfolio_vols, sharpe_result, minvol_result)

    # Assert
    assert isinstance(fig, Figure)
    ax = fig.axes[0]
    assert ax.get_title() == "Efficient Frontier"
    assert ax.get_xlabel() == "Volatility"
    assert ax.get_ylabel() == "Expected Return"
