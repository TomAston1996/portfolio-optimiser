from datetime import datetime
from unittest.mock import MagicMock, patch

import pandas as pd
import pytest

from portfoliooptimiser.market_api import PriceType, YFinanceAPI


@patch("yfinance.download")
def test_get_historical_ticker_data_returns_dataframe(mock_download: MagicMock) -> None:
    # Arrange
    mock_df = pd.DataFrame({"Open": [100, 101], "Close": [102, 103]}, index=pd.date_range("2025-01-01", periods=2))

    mock_download.return_value = mock_df

    api = YFinanceAPI()
    tickers = ["AAPL"]

    # Act
    result = api.get_historical_ticker_data(tickers, PriceType.CLOSE, datetime(2025, 1, 1), datetime(2025, 1, 2))

    # Assert
    assert isinstance(result, (pd.DataFrame, pd.Series))
    assert not result.empty
    assert list(result.index) == list(mock_df.index)
    assert bool((result == mock_df["Close"]).all())


@patch("yfinance.download")
def test_get_historical_ticker_data_raises_value_error_if_empty(mock_download: MagicMock) -> None:
    # Arrange
    mock_download.return_value = pd.DataFrame()
    api = YFinanceAPI()
    tickers = ["AAPL"]

    # Act & Assert
    with pytest.raises(ValueError):
        api.get_historical_ticker_data(tickers, PriceType.CLOSE, datetime(2025, 1, 1), datetime(2025, 1, 2))
