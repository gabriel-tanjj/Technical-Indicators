import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.optimize import brute

class Backtester():

    def __init__(self, symbol, ema_s, ema_l, signal_len, start_date, end_date, trading_cost):
        self.symbol = symbol
        self.ema_s = ema_s
        self.ema_l = ema_l
        self.signal_len = signal_len
        self.start_date = start_date
        self.end_date = end_date
        self.trading_cost = trading_cost
        self.results = None
        self.get_data()


    def get_data(self):
        data = pd.read_csv("eurusd.csv", parse_dates=["Date"], index_col="Date")
        data.loc[self.start_date:self.end_date]
        data["Returns"] = np.log(data["price"]/data["price"].shift(1))
        data["EMA-S"] = data["price"].ewm(span=self.ema_s, min_periods=self.ema_s).mean()
        data["EMA-L"] = data["price"].ewm(span=self.ema_l, min_periods=self.ema_l).mean()
        data["MACD"] = data["EMA-S"] - data["EMA-L"]
        data["Signal"] = data["MACD"].ewm(span=self.signal_len, min_periods=self.signal_len).mean()
        self.data = data
        return data

    def set_parameters(self, ema_s = None, ema_l = None, signal_len = None):
        if ema_s is not None:
            self.ema_s = ema_s
            self.data["EMA-S"] = self.data["price"].ewm(span=self.ema_s, min_periods=self.ema_s).mean()
            self.data["MACD"] = self.data["EMA-S"] - self.data["EMA-L"]
            self.data["Signal"] = self.data["MACD"].ewm(span=self.signal_len, min_periods=self.signal_len).mean()

        if ema_l is not None:
            self.ema_l = ema_l
            self.data["EMA-L"] = self.data["price"].ewm(span=self.ema_l, min_periods=self.ema_l).mean()
            self.data["MACD"] = self.data["EMA-S"] - self.data["EMA-L"]
            self.data["Signal"] = self.data["MACD"].ewm(span=self.signal_len, min_periods=self.signal_len).mean()

        if signal_len is not None:
            self.signal_len = signal_len
            self.data["Signal"] = self.data["MACD"].ewm(span=self.signal_len, min_periods=self.signal_len).mean()

    def test_strategy(self):
        data = self.data.copy().dropna()
        data["CReturns"] = data["Returns"].cumsum().apply(np.exp)

        data["Position"] = np.where(data["MACD"] > data["Signal"], 1, -1)
        data["Trades"] = data["Position"].diff().fillna(0).abs()

        data["StrategyReturns"] = data["Position"].shift(1) * data["Returns"]
        data["CStrategyReturns"] = data["StrategyReturns"].cumsum().apply(np.exp)

        data["NStrategyReturns"] = data["StrategyReturns"] - data["Trades"] * self.trading_cost
        data["CNStrategyReturns"] = data["NStrategyReturns"].cumsum().apply(np.exp)

        perf = data["CStrategyReturns"].iloc[-1]
        outperf = data["CStrategyReturns"].iloc[-1] - data["CReturns"].iloc[-1]

        self.results = data

        return round(perf, 2), round(outperf, 2)

    def plot_results(self):
        title = "EURUSD - MACD:{}, {}, Signal: {}".format(self.ema_s, self.ema_l, self.signal_len)
        self.results.loc["2016", ["CNStrategyReturns", "CStrategyReturns", "CReturns"]].plot(figsize=(12, 6), title=title)
        plt.show()

    def update_brute(self, MACD):

        self.set_parameters(int(MACD[0]), int(MACD[1]), int(MACD[2]))
        return -self.test_strategy()[0]

    def optimize(self, EMA_S_Range, EMA_L_Range, signal_len_range):

        opt = brute(self.update_brute, (EMA_S_Range, EMA_L_Range, signal_len_range))
        print(opt)
        return opt, -self.update_brute(opt)








