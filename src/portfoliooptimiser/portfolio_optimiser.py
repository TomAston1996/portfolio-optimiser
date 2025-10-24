from dataclasses import dataclass
from datetime import datetime

import numpy as np
import pandas as pd
import scipy.optimize as sco

from numpy.typing import NDArray

from portfoliooptimiser.constants import DEFAULT_NUMBER_MONTE_CARLO_SIMULATIONS, TRADING_DAYS_IN_A_YEAR
from portfoliooptimiser.market_api import IMarketAPI, PriceType


@dataclass
class PortfolioOptimiserContext:
    """Context for Portfolio Optimiser."""

    market_api: IMarketAPI


@dataclass
class PortfolioOptimiserConfig:
    """Configuration for Portfolio Optimiser."""

    number_of_simulations: int = DEFAULT_NUMBER_MONTE_CARLO_SIMULATIONS


@dataclass
class PortfolioResult:
    weights: NDArray[np.float64]
    expected_return: float
    expected_volatility: float
    sharpe_ratio: float


class PortfolioOptimiser:
    def __init__(self, context: PortfolioOptimiserContext, config: PortfolioOptimiserConfig) -> None:
        """'Initialise Portfolio Optimiser with context and configuration."""

        self.market_api = context.market_api
        self.number_of_simulations = config.number_of_simulations

    def _get_log_returns_df(self, tickers: list[str], start_date: datetime, end_date: datetime) -> pd.DataFrame:
        """
        Calculate log returns for given tickers over a specified date range.

        Args:
            tickers (list[str]): List of ticker symbols.
            start_date (datetime): Start date for data retrieval.
            end_date (datetime): End date for data retrieval.

        Returns:
            pd.DataFrame: Log returns for the specified tickers.
        """
        historical_data = self.market_api.get_historical_ticker_data(
            tickers=tickers, price_type=PriceType.ADJUSTED_CLOSE, start_date=start_date, end_date=end_date
        )

        returns = np.log(historical_data / historical_data.shift(1))

        assert isinstance(returns, pd.DataFrame)

        return returns

    def _create_random_weights(self, num_weights: int) -> NDArray[np.float64]:
        """
        Generate a random set of weights that sum to 1 for the given number of assets.

        Args:
            num_weights (int): Number of weights to generate.

        Returns:
            NDArray: Array of random weights summing to 1.
        """
        weights = np.random.random(num_weights)
        weights /= np.sum(weights)
        return weights

    def _get_annualised_portfolio_return(self, weights: NDArray[np.float64], returns: pd.DataFrame) -> np.float64:
        """
        Calculate annualised portfolio returns based on asset weights and individual asset returns.

        Args:
            weights (NDArray): Array of asset weights in the portfolio.
            returns (pd.DataFrame): Array of individual asset returns.

        Returns:
            np.float64: Calculated portfolio returns.
        """
        return np.sum(returns.mean() * weights) * TRADING_DAYS_IN_A_YEAR

    def _get_annualised_portfolio_volatility(self, weights: NDArray[np.float64], returns: pd.DataFrame) -> np.float64:
        """
        Calculate annualised portfolio volatility based on asset weights and individual asset returns.
        The higher the volatility, the riskier the portfolio.


        Args:
            weights (NDArray): Array of asset weights in the portfolio.
            returns (pd.DataFrame): Array of individual asset returns.

        Returns:
            np.float64: Calculated portfolio volatility.
        """
        return np.sqrt(np.dot(weights.T, np.dot(returns.cov() * TRADING_DAYS_IN_A_YEAR, weights)))

    def get_expected_returns_and_volatility(
        self, tickers: list[str], returns_df: pd.DataFrame
    ) -> tuple[NDArray[np.float64], NDArray[np.float64]]:
        """
        Calculate both annualised portfolio returns and volatility based on asset weights and individual asset returns.

        Args:
            weights (NDArray): Array of asset weights in the portfolio.
            returns (NDArray): Array of individual asset returns.
        Returns:
            tuple[NDArray, NDArray]: Calculated portfolio returns and volatility.
        """
        portfolio_rets = []
        portfolio_vols = []

        for _ in range(self.number_of_simulations):
            weights = self._create_random_weights(len(tickers))
            portfolio_rets.append(self._get_annualised_portfolio_return(weights, returns_df))
            portfolio_vols.append(self._get_annualised_portfolio_volatility(weights, returns_df))

        portfolio_rets = np.array(portfolio_rets)
        portfolio_vols = np.array(portfolio_vols)

        return portfolio_rets, portfolio_vols


class MaximumSharpeRatioOptimiser(PortfolioOptimiser):
    """Optimiser to derive the asset weights that maximise the sharpe ratio of the portfolio."""

    def __init__(self, context: PortfolioOptimiserContext, config: PortfolioOptimiserConfig) -> None:
        """Initialise Maximum Sharpe Ratio Optimiser with context and configuration."""
        super().__init__(context, config)

    def optimise_portfolio(self, tickers: list[str], start_date: datetime, end_date: datetime) -> PortfolioResult:
        """
        Optimise portfolio to derive the asset weights that maximise the sharpe ratio

        Args:
            tickers (list[str]): List of ticker symbols.
            start_date (datetime): Start date for data retrieval.
            end_date (datetime): End date for data retrieval.

        Returns:
            PortfolioResult: Result of the portfolio optimisation containing weights, expected return, volatility, and sharpe ratio.
        """

        returns_df = self._get_log_returns_df(tickers, start_date, end_date)
        mean_returns = returns_df.mean() * TRADING_DAYS_IN_A_YEAR
        cov_matrix = returns_df.cov() * TRADING_DAYS_IN_A_YEAR

        def _min_func_sharpe(weights: NDArray[np.float64]) -> float:
            port_return = float(np.sum(weights * mean_returns))
            port_vol = float(np.sqrt(weights.T @ cov_matrix @ weights))
            return -port_return / port_vol

        def _sum_to_one_constraint(x: NDArray[np.float64]) -> float:
            return np.sum(x) - 1

        cons = {"type": "eq", "fun": _sum_to_one_constraint}
        bnds = tuple((0, 1) for _ in range(len(tickers)))
        equal_weights = np.array(len(tickers) * [1.0 / len(tickers)])

        opts = sco.minimize(_min_func_sharpe, equal_weights, method="SLSQP", bounds=bnds, constraints=cons)

        optimal_weights = opts["x"].round(3)

        assert isinstance(optimal_weights, np.ndarray)

        port_return = float(np.sum(optimal_weights * mean_returns))
        port_vol = float(np.sqrt(optimal_weights.T @ cov_matrix @ optimal_weights))
        sharpe_ratio = port_return / port_vol if port_vol != 0 else 0.0

        return PortfolioResult(
            weights=optimal_weights,
            expected_return=port_return,
            expected_volatility=port_vol,
            sharpe_ratio=sharpe_ratio,
        )


class MinimumVolatilityOptimiser(PortfolioOptimiser):
    """Optimiser to derive the asset weights that minimise the volatility of the portfolio."""

    def __init__(self, context: PortfolioOptimiserContext, config: PortfolioOptimiserConfig) -> None:
        """Initialise Minimum Volatility Optimiser with context and configuration."""
        super().__init__(context, config)

    def optimise_portfolio(self, tickers: list[str], start_date: datetime, end_date: datetime) -> PortfolioResult:
        """
        Optimise portfolio to derive the asset weights that minimise the volatility

        Args:
            tickers (list[str]): List of ticker symbols.
            start_date (datetime): Start date for data retrieval.
            end_date (datetime): End date for data retrieval.

        Returns:
            PortfolioResult: Result of the portfolio optimisation containing weights, expected return, volatility, and sharpe ratio.
        """

        returns_df = self._get_log_returns_df(tickers, start_date, end_date)
        mean_returns = returns_df.mean() * TRADING_DAYS_IN_A_YEAR
        cov_matrix = returns_df.cov() * TRADING_DAYS_IN_A_YEAR

        def _sum_to_one_constraint(x: NDArray[np.float64]) -> float:
            return np.sum(x) - 1

        cons = {"type": "eq", "fun": _sum_to_one_constraint}
        bnds = tuple((0, 1) for _ in range(len(tickers)))
        equal_weights = np.array(len(tickers) * [1.0 / len(tickers)])

        optv = sco.minimize(
            self._get_annualised_portfolio_volatility,
            equal_weights,
            args=(returns_df,),
            method="SLSQP",
            bounds=bnds,
            constraints=cons,
        )

        optimal_weights = optv["x"].round(3)

        assert isinstance(optimal_weights, np.ndarray)

        port_return = float(np.sum(optimal_weights * mean_returns))
        port_vol = float(np.sqrt(optimal_weights.T @ cov_matrix @ optimal_weights))
        sharpe_ratio = port_return / port_vol if port_vol != 0 else 0.0

        return PortfolioResult(
            weights=optimal_weights,
            expected_return=port_return,
            expected_volatility=port_vol,
            sharpe_ratio=sharpe_ratio,
        )
