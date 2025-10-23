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
    @abstractmethod
    def get_historical_ticker_data(
        self, tickers: list[str], price_type: PriceType, start_date: datetime, end_date: datetime
    ) -> pd.DataFrame | pd.Series:
        pass


class YFinanceAPI(IMarketAPI):
    def get_historical_ticker_data(
        self, tickers: list[str], price_type: PriceType, start_date: datetime, end_date: datetime
    ) -> pd.DataFrame | pd.Series:
        data = yf.download(tickers, start=start_date, end=end_date, auto_adjust=True)

        if data is None or data.empty:
            raise ValueError("No data retrieved from yFinance for the given tickers and date range.")

        return data[price_type.value]
