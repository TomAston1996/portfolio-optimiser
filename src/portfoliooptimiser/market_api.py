from abc import ABC, abstractmethod
from datetime import datetime
from enum import Enum

import pandas as pd
import yfinance as yf


class PriceType(Enum):
    OPEN = "Open"
    HIGH = "High"
    LOW = "Low"
    CLOSE = "Close"
    ADJUSTED_CLOSE = "Adj Close"
    VOLUME = "Volume"


class IMarketAPI(ABC):
    """Interface for market data APIs."""

    @abstractmethod
    def get_historical_ticker_data(
        self, tickers: list[str], price_type: PriceType, start_date: datetime, end_date: datetime
    ) -> pd.DataFrame | pd.Series:
        pass


class YFinanceAPI(IMarketAPI):
    """Implementation of IMarketAPI using yFinance as the data source."""

    def get_historical_ticker_data(
        self, tickers: list[str], price_type: PriceType, start_date: datetime, end_date: datetime
    ) -> pd.DataFrame:
        """
        Fetch historical ticker data from yFinance.

        Args:
            tickers (list[str]): List of ticker symbols.
            price_type (PriceType): Type of price data to retrieve.
            start_date (datetime): Start date for data retrieval.
            end_date (datetime): End date for data retrieval.

        Returns:
            pd.DataFrame: Historical price data for the specified tickers and price type
        """
        data = yf.download(tickers, start=start_date, end=end_date, auto_adjust=True)

        if data is None or data.empty:
            raise ValueError("No data retrieved from yFinance for the given tickers and date range.")

        result = data[price_type.value]

        # If only one ticker is requested, ensure the result is a DataFrame as yFinance returns a Series
        if len(tickers) == 1:
            result = result.to_frame(name=tickers[0])

        # Garantee the return type is a DataFrame
        assert isinstance(result, pd.DataFrame)

        return result
