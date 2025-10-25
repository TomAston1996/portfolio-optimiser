
from unittest.mock import MagicMock, patch

from portfoliooptimiser.ui import PortfolioOptimiserUI


def test_ui_simple_smoke() -> None:
    mock_market_api = MagicMock()
    mock_plotter = MagicMock()
    ui = PortfolioOptimiserUI(mock_market_api, mock_plotter)

    # Patch all Streamlit calls so nothing tries to render
    with patch("portfoliooptimiser.ui.st", new=MagicMock()):
        ui.run()
