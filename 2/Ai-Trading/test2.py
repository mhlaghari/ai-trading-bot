from lumibot.brokers import Alpaca
from lumibot.backtesting import YahooDataBacktesting
from lumibot.strategies.strategy import Strategy
from lumibot.traders import Trader
from datetime import datetime
from alpaca_trade_api import REST
from timedelta import Timedelta
from finbert import estimate_sentiment

API_KEY = "YOUR API KEY"
API_SECRET = "YOUR API SECRET"
BASE_URL = "https://paper-api.alpaca.markets"

ALPACA_CONFIG = {
    # Put your own Alpaca key here:
    "API_KEY": "PK8GJMZYIOH50T5I2QV2",
    # Put your own Alpaca secret here:
    "API_SECRET": "DZB7I87LCnHtnofzzOt5mFcp5uDMjEIqL83g3cKt",
    # If you want to go live, you must change this. It is currently set for paper trading
    "PAPER": "https://paper-api.alpaca.markets"
}

class MLTrader(Strategy):
    def initialize(self, symbol: str="SPY", cash_at_risk: float=.5):
        self.symbol = symbol
        self.sleeptime = "24H"
        self.last_trade = None
        self.cash_at_risk = cash_at_risk
        self.api = REST(base_url=ALPACA_CONFIG['PAPER'],
                        key_id=ALPACA_CONFIG['API_KEY'],
                        secret_key=ALPACA_CONFIG['API_SECRET'])

    def position_sizing(self):
        cash = self.get_cash()
        last_price = self.get_last_price(self.symbol)
        quantity = round(cash * self.cash_at_risk / last_price,0)
        return cash, last_price, quantity

    def get_dates(self):
        today = self.get_datetime()
        three_days_prior = today - Timedelta(days=3)
        return today.strftime('%Y-%m-%d'), three_days_prior.strftime('%Y-%m-%d')

    def get_sentiment(self):
        today, three_days_prior = self.get_dates()
        news = self.api.g(symbol=self.symbol,
                                 start=three_days_prior,
                                 end=today)
        news = [ev.__dict__["_raw"]["headline"] for ev in news]
        probability, sentiment = estimate_sentiment(news)
        return probability, sentiment

    def on_trading_iteration(self):
        cash, last_price, quantity = self.position_sizing()
        probability, sentiment = self.get_sentiment()

        if cash > last_price:
            if sentiment == "positive" and probability > .999:
                if self.last_trade == "sell":
                    self.sell_all()
                order = self.create_order(
                    self.symbol,
                    quantity,
                    "buy",
                    type="bracket",
                    take_profit_price=last_price*1.20,
                    stop_loss_price=last_price*.95
                )
                self.submit_order(order)
                self.last_trade = "buy"
            elif sentiment == "negative" and probability > .999:
                if self.last_trade == "buy":
                    self.sell_all()
                order = self.create_order(
                    self.symbol,
                    quantity,
                    "sell",
                    type="bracket",
                    take_profit_price=last_price*.8,
                    stop_loss_price=last_price*1.05
                )
                self.submit_order(order)
                self.last_trade = "sell"

start_date = datetime(2020,1,1)
end_date = datetime(2023,12,31)
broker = Alpaca(ALPACA_CONFIG)
strategy = MLTrader(name='mlstrat', broker=broker,
                    parameters={"symbol":"SPY",
                                "cash_at_risk":.5})
strategy.backtest(
    YahooDataBacktesting,
    start_date,
    end_date,
    parameters={"symbol":"SPY", "cash_at_risk":.5}
)
# trader = Trader()
# trader.add_strategy(strategy)
# trader.run_all()