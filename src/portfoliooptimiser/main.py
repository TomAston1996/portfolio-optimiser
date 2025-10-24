from portfoliooptimiser.market_api import YFinanceAPI
from portfoliooptimiser.ui import PortfolioOptimiserUI


if __name__ == "__main__":
    market_api = YFinanceAPI()
    ui = PortfolioOptimiserUI(market_api=market_api)
    ui.run()
