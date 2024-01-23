from datetime import datetime

from lumibot.backtesting import YahooDataBacktesting
from lumibot.brokers import Alpaca
from lumibot.strategies.strategy import Strategy
from lumibot.traders import Trader

ALPACA_CONFIG = {
    # Put your own Alpaca key here:
    "API_KEY": "PK8GJMZYIOH50T5I2QV2",
    # Put your own Alpaca secret here:
    "API_SECRET": "DZB7I87LCnHtnofzzOt5mFcp5uDMjEIqL83g3cKt",
    # If you want to go live, you must change this. It is currently set for paper trading
    "PAPER": "https://paper-api.alpaca.markets"
}

class MyStrategy(Strategy):
    # Custom parameters
    parameters = {
        "symbol": "SPY",
        "quantity": 1,
        "side": "buy"
    }

    def initialize(self, symbol=""):
        # Will make on_trading_iteration() run every 180 minutes
        self.sleeptime = "180M"

    def on_trading_iteration(self):
        symbol = self.parameters["symbol"]
        quantity = self.parameters["quantity"]
        side = self.parameters["side"]

        order = self.create_order(symbol, quantity, side)
        self.submit_order(order)


trader = Trader()
broker = Alpaca(ALPACA_CONFIG)
strategy = MyStrategy(
    broker=broker,
    parameters= {
        "symbol": "SPY"
    })

backtesting_start = datetime(2020, 1, 1)
backtesting_end = datetime(2020, 12, 31)
strategy.backtest(
    YahooDataBacktesting,
    backtesting_start,
    backtesting_end,
    parameters= {
        "symbol": "SPY"
    },
)

