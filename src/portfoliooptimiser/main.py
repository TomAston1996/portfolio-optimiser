from portfoliooptimiser.market_api import YFinanceAPI
from portfoliooptimiser.plotter import MatplotlibPlotterV1
from portfoliooptimiser.ui import PortfolioOptimiserUI


if __name__ == "__main__":
    ui = PortfolioOptimiserUI(market_api=YFinanceAPI(), plotter=MatplotlibPlotterV1())
    ui.run()
