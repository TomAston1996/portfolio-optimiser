from datetime import datetime
from unittest.mock import MagicMock, patch

import pandas as pd
import pytest

from portfoliooptimiser.market_api import PriceType, YFinanceAPI


@patch("yfinance.download")
def test_get_historical_ticker_data_returns_dataframe(mock_download: MagicMock) -> None:
    # Arrange
    mock_df = pd.DataFrame(
        {
            "Open": [100, 101],
            "High": [102, 103],
            "Low": [99, 100],
            "Close": [101, 102],
            "Adj Close": [101, 102],
            "Volume": [1_000_000, 1_200_000],
        },
        index=pd.date_range("2025-01-01", periods=2),
    )

    mock_download.return_value = mock_df

    api = YFinanceAPI()
    tickers = ["AAPL"]

    # Act
    result = api.get_historical_ticker_data(tickers, PriceType.CLOSE, datetime(2025, 1, 1), datetime(2025, 1, 2))

    # Assert
    assert isinstance(result, pd.DataFrame)
    assert not result.empty
    assert list(result.index) == list(mock_df.index)

    squeezed = result.squeeze()  # If single ticker, result should be a Series
    assert isinstance(squeezed, pd.Series)
    pd.testing.assert_series_equal(squeezed, mock_df["Close"], check_names=False)


@patch("yfinance.download")
def test_get_historical_ticker_data_multiple_tickers(mock_download: MagicMock) -> None:
    # Arrange
    tickers = ["AAPL", "MSFT"]
    dates = pd.date_range("2025-01-01", periods=2)

    # Mock yfinance MultiIndex-style return
    mock_df = pd.concat(
        {
            "Open": pd.DataFrame({"AAPL": [100, 101], "MSFT": [200, 201]}, index=dates),
            "High": pd.DataFrame({"AAPL": [102, 103], "MSFT": [202, 203]}, index=dates),
            "Low": pd.DataFrame({"AAPL": [99, 100], "MSFT": [199, 200]}, index=dates),
            "Close": pd.DataFrame({"AAPL": [101, 102], "MSFT": [201, 202]}, index=dates),
            "Adj Close": pd.DataFrame({"AAPL": [101, 102], "MSFT": [201, 202]}, index=dates),
            "Volume": pd.DataFrame({"AAPL": [1_000_000, 1_200_000], "MSFT": [2_000_000, 2_100_000]}, index=dates),
        },
        axis=1,
    )
    mock_download.return_value = mock_df
    api = YFinanceAPI()

    # Act
    result = api.get_historical_ticker_data(tickers, PriceType.CLOSE, datetime(2025, 1, 1), datetime(2025, 1, 2))

    # Assert
    assert isinstance(result, pd.DataFrame)
    assert not result.empty
    assert list(result.columns) == tickers
    assert list(result.index) == list(mock_df.index)
    pd.testing.assert_series_equal(result["AAPL"], mock_df["Close"]["AAPL"])
    pd.testing.assert_series_equal(result["MSFT"], mock_df["Close"]["MSFT"])


@patch("yfinance.download")
def test_get_historical_ticker_data_raises_value_error_if_empty(mock_download: MagicMock) -> None:
    # Arrange
    mock_download.return_value = pd.DataFrame()
    api = YFinanceAPI()
    tickers = ["AAPL"]

    # Act & Assert
    with pytest.raises(ValueError):
        api.get_historical_ticker_data(tickers, PriceType.CLOSE, datetime(2025, 1, 1), datetime(2025, 1, 2))
