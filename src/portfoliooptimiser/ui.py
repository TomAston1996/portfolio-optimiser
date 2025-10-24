from datetime import datetime, time

import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

from portfoliooptimiser.market_api import IMarketAPI
from portfoliooptimiser.portfolio_optimiser import (
    MaximumSharpeRatioOptimiser,
    MinimumVolatilityOptimiser,
    PortfolioOptimiserConfig,
    PortfolioOptimiserContext,
    PortfolioResult,
)


class PortfolioOptimiserUI:
    """Encapsulates the Streamlit UI for portfolio optimisation."""

    def __init__(self, market_api: IMarketAPI) -> None:
        self.context = PortfolioOptimiserContext(market_api=market_api)
        self.config = PortfolioOptimiserConfig()
        self.sharpe_optimiser = MaximumSharpeRatioOptimiser(self.context, self.config)
        self.minvol_optimiser = MinimumVolatilityOptimiser(self.context, self.config)

    def run(self) -> None:
        st.title("Portfolio Optimiser App")

        # Input controls
        tickers_input = st.text_input("Enter tickers (comma separated):", "AAPL,MSFT,GOOG")
        start_date = st.date_input("Start Date", datetime(2023,1,1))
        end_date = st.date_input("End Date", datetime.today())

        tickers = [t.strip().upper() for t in tickers_input.split(",") if t.strip()]

        if st.button("Run Optimisation") and tickers:
            start_datetime = datetime.combine(start_date, time.min)
            end_datetime = datetime.combine(end_date, time.max)
            self._run_optimisation(tickers, start_datetime, end_datetime)

    def _run_optimisation(self, tickers: list[str], start_date: datetime, end_date: datetime) -> None:
        # Run optimisers
        sharpe_result: PortfolioResult = self.sharpe_optimiser.optimise_portfolio(tickers, start_date, end_date)
        minvol_result: PortfolioResult = self.minvol_optimiser.optimise_portfolio(tickers, start_date, end_date)

        # Display results
        st.subheader("Maximum Sharpe Ratio Portfolio")
        st.write(f"Expected Return: {sharpe_result.expected_return:.2%}")
        st.write(f"Expected Volatility: {sharpe_result.expected_volatility:.2%}")
        st.write(f"Sharpe Ratio: {sharpe_result.sharpe_ratio:.2f}")
        st.write(pd.DataFrame(sharpe_result.weights, index=tickers, columns=["Weight"]))

        st.subheader("Minimum Volatility Portfolio")
        st.write(f"Expected Return: {minvol_result.expected_return:.2%}")
        st.write(f"Expected Volatility: {minvol_result.expected_volatility:.2%}")
        st.write(f"Sharpe Ratio: {minvol_result.sharpe_ratio:.2f}")
        st.write(pd.DataFrame(minvol_result.weights, index=tickers, columns=["Weight"]))

        # Plot Efficient Frontier
        returns_df = self.sharpe_optimiser._get_log_returns_df(tickers, start_date, end_date) # type: ignore
        portfolio_rets, portfolio_vols = self.sharpe_optimiser.get_expected_returns_and_volatility(tickers, returns_df)

        fig, ax = plt.subplots(figsize=(10,6))
        ax.scatter(portfolio_vols, portfolio_rets, c=(portfolio_rets/portfolio_vols), cmap='viridis', s=10, alpha=0.5)
        ax.scatter(sharpe_result.expected_volatility, sharpe_result.expected_return, color='r', marker='*', s=500, label='Max Sharpe')
        ax.scatter(minvol_result.expected_volatility, minvol_result.expected_return, color='b', marker='*', s=500, label='Min Vol')
        ax.set_xlabel("Volatility")
        ax.set_ylabel("Expected Return")
        ax.set_title("Efficient Frontier")
        ax.legend()

        st.pyplot(fig)
