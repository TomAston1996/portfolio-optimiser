from datetime import datetime, time

import pandas as pd
import streamlit as st

from portfoliooptimiser.market_api import IMarketAPI
from portfoliooptimiser.plotter import IPlotter
from portfoliooptimiser.portfolio_optimiser import (
    MaximumSharpeRatioOptimiser,
    MinimumVolatilityOptimiser,
    PortfolioOptimiserConfig,
    PortfolioOptimiserContext,
    PortfolioResult,
)


class PortfolioOptimiserUI:
    """Encapsulates the Streamlit UI for portfolio optimisation."""

    def __init__(self, market_api: IMarketAPI, plotter: IPlotter) -> None:
        self.context = PortfolioOptimiserContext(market_api=market_api)
        self.config = PortfolioOptimiserConfig()
        self.sharpe_optimiser = MaximumSharpeRatioOptimiser(self.context, self.config)
        self.minvol_optimiser = MinimumVolatilityOptimiser(self.context, self.config)

        self.plotter = plotter

    def run(self) -> None:
        st.title("📈 Portfolio Optimiser")

        # --- Sidebar Inputs ---
        st.sidebar.header("Input Parameters")
        tickers_input = st.sidebar.text_input("Enter tickers (comma separated):", "AAPL,MSFT,GOOG")
        start_date = st.sidebar.date_input("Start Date", datetime(2023, 1, 1).date())
        end_date = st.sidebar.date_input("End Date", datetime.today().date())

        tickers = [t.strip().upper() for t in tickers_input.split(",") if t.strip()]
        optimise_button = st.sidebar.button("Run Optimisation 🚀")

        # --- Main Display ---
        if optimise_button and tickers:
            start_datetime = datetime.combine(start_date, time.min)
            end_datetime = datetime.combine(end_date, time.max)
            self._run_optimisation(tickers, start_datetime, end_datetime)

    def _run_optimisation(self, tickers: list[str], start_date: datetime, end_date: datetime) -> None:
        """Run portfolio optimisations and display results."""
        st.write(f"### Analysing tickers: {', '.join(tickers)}")

        with st.spinner("Running optimisation... ⏳"):
            sharpe_result: PortfolioResult = self.sharpe_optimiser.optimise_portfolio(tickers, start_date, end_date)
            minvol_result: PortfolioResult = self.minvol_optimiser.optimise_portfolio(tickers, start_date, end_date)

            # Get returns data
            returns_df = self.sharpe_optimiser._get_log_returns_df(  # type: ignore
                tickers, start_date, end_date
            )

        # --- Plot Log Returns for Each Ticker ---
        st.subheader("📊 Log Returns of Individual Tickers")
        fig_returns = self.plotter.get_log_returns_plot(returns_df, tickers)
        st.pyplot(fig_returns)

        # --- Display Results Side by Side ---
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("🏆 Maximum Sharpe Ratio Portfolio")
            st.metric("Expected Return", f"{sharpe_result.expected_return:.2%}")
            st.metric("Volatility", f"{sharpe_result.expected_volatility:.2%}")
            st.metric("Sharpe Ratio", f"{sharpe_result.sharpe_ratio:.2f}")
            st.dataframe(pd.DataFrame(sharpe_result.weights, index=tickers, columns=["Weight"]))

        with col2:
            st.subheader("🛡️ Minimum Volatility Portfolio")
            st.metric("Expected Return", f"{minvol_result.expected_return:.2%}")
            st.metric("Volatility", f"{minvol_result.expected_volatility:.2%}")
            st.metric("Sharpe Ratio", f"{minvol_result.sharpe_ratio:.2f}")
            st.dataframe(pd.DataFrame(minvol_result.weights, index=tickers, columns=["Weight"]))

        # --- Plot Efficient Frontier ---
        portfolio_rets, portfolio_vols = self.sharpe_optimiser.get_expected_returns_and_volatility(tickers, returns_df)

        st.subheader("💡 Efficient Frontier")

        fig_frontier = self.plotter.get_efficient_frontier_plot(
            portfolio_rets, portfolio_vols, sharpe_result, minvol_result
        )
        st.pyplot(fig_frontier)
