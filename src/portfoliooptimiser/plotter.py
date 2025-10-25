from abc import ABC, abstractmethod

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from matplotlib.figure import Figure
from numpy.typing import NDArray

from portfoliooptimiser.portfolio_optimiser import PortfolioResult


class IPlotter(ABC):
    """Interface for plotting portfolio optimisation results."""

    @abstractmethod
    def get_log_returns_plot(self, returns_df: pd.DataFrame, tickers: list[str]) -> Figure:
        pass

    @abstractmethod
    def get_efficient_frontier_plot(
        self,
        portfolio_rets: NDArray[np.float64],
        portfolio_vols: NDArray[np.float64],
        sharpe_result: PortfolioResult,
        minvol_result: PortfolioResult,
    ) -> Figure:
        pass


class MatplotlibPlotterV1(IPlotter):
    """Matplotlib implementation of the IPlotter interface."""

    def get_log_returns_plot(self, returns_df: pd.DataFrame, tickers: list[str]) -> Figure:
        """Plot log returns for each ticker over time.

        Args:
            returns_df (pd.DataFrame): DataFrame containing log returns for each ticker.
            tickers (list[str]): List of ticker symbols.

        Returns:
            Figure: Matplotlib Figure object containing the log returns plot.
        """
        fig_returns, ax_returns = plt.subplots(figsize=(10, 5))
        for ticker in tickers:
            ax_returns.plot(returns_df.index, returns_df[ticker], label=ticker, alpha=0.8)
        ax_returns.set_title("Log Returns Over Time")
        ax_returns.set_xlabel("Date")
        ax_returns.set_ylabel("Log Return")
        ax_returns.legend()
        return fig_returns

    def get_efficient_frontier_plot(
        self,
        portfolio_rets: NDArray[np.float64],
        portfolio_vols: NDArray[np.float64],
        sharpe_result: PortfolioResult,
        minvol_result: PortfolioResult,
    ) -> Figure:
        """Plot the efficient frontier along with maximum Sharpe ratio and minimum volatility portfolios.

        Args:
            portfolio_rets (NDArray[np.float64]): Numpy array containing portfolio returns.
            portfolio_vols (NDArray[np.float64]): Numpy array containing portfolio volatilities.
            sharpe_result (PortfolioResult): Result of the maximum Sharpe ratio optimisation.
            minvol_result (PortfolioResult): Result of the minimum volatility optimisation.

        Returns:
            Figure: Matplotlib Figure object containing the efficient frontier plot.
        """
        fig_frontier, ax_frontier = plt.subplots(figsize=(10, 6))
        scatter = ax_frontier.scatter(
            portfolio_vols,
            portfolio_rets,
            c=(portfolio_rets / portfolio_vols),
            cmap="viridis",
            s=20,
            alpha=0.6,
        )
        ax_frontier.scatter(
            sharpe_result.expected_volatility,
            sharpe_result.expected_return,
            color="r",
            marker="*",
            s=300,
            label="Max Sharpe",
        )
        ax_frontier.scatter(
            minvol_result.expected_volatility,
            minvol_result.expected_return,
            color="b",
            marker="*",
            s=300,
            label="Min Vol",
        )
        ax_frontier.set_xlabel("Volatility")
        ax_frontier.set_ylabel("Expected Return")
        ax_frontier.legend()
        ax_frontier.set_title("Efficient Frontier")
        plt.colorbar(scatter, ax=ax_frontier, label="Sharpe Ratio (Return / Volatility)")
        return fig_frontier
