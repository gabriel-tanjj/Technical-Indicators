import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import brute

class Backtester():

    def __init__(self, stoch_period, ma_window, start_date, end_date, trading_cost):
        self.stoch_period = stoch_period
        self.ma_window = ma_window
        self.start_date = start_date
        self.end_date = end_date
        self.trading_cost = trading_cost
        self.results = None

    def get_data(self):
        data = pd.read_csv("EURUSD_ohlc.csv", parse_dates=[0], index_col=0)
        data["14d_low"] = data["Low"].rolling(self.stoch_period).min()
        data["14d_high"] = data["High"].rolling(self.stoch_period).max()
        data["%K"] = (data["Close"] - data["14d_low"]) / (data["14d_high"] - data["14d_low"]) * 100
        data["%D"] = data["%K"].rolling(self.ma_window).mean()
        data["Returns"] = np.log(data["Close"]/data["Close"].shift(1))
        data.dropna(inplace=True)
        self.data = data

    def set_parameters(self, stoch_period, ma_window):

        if stoch_period is not None:
            self.stoch_period = stoch_period
            self.data["14d_low"] = self.data["Low"].rolling(self.stoch_period).min()
            self.data["14d_high"] = self.data["High"].rolling(self.stoch_period).max()
            self.data["%K"] = (self.data["Close"] - self.data["14d_low"]) / (self.data["14d_high"] - self.data["14d_low"]) * 100

        if ma_window is not None:
            self.ma_window = ma_window
            self.data["%D"] = self.data["%K"].rolling(self.ma_window).mean()

    def test_strategy(self):
        data = self.data.copy().dropna()
        # Position & Trades
        data["Position"] = np.where(data["%K"] > data["%D"], 1, -1)
        data["Trades"] = data["Position"].diff().fillna(0).abs()
        # Strategy
        data["Strategy"] = data["Position"].shift(1) * data["Returns"]
        data["Strategy_Net"] = data["Strategy"] - data["Trades"] * self.trading_cost
        # Cumulative
        data["CReturns"] = data["Returns"].cumsum().apply(np.exp)
        data["CStrategy"] = data["Strategy"].cumsum().apply(np.exp)
        data["CStrategy_Net"] = data["Strategy_Net"].cumsum().apply(np.exp)
        # Perf/Outperf
        perf = data["CStrategy"].iloc[-1]
        outperf = data["CStrategy_Net"].iloc[-1] - data["CReturns"].iloc[-1]

        self.results = data
        return round(perf, 2), round(outperf, 2)

    def plot_results(self):
        self.results[["CReturns", "CStrategy", "CStrategy_Net"]].plot(figsize=(12, 8), title="EURUSD - Stochastic Osc")
        plt.show()

    def update(self, SO):
        self.set_parameters(int(SO[0]), int(SO[1]))
        return -self.test_strategy()[0]

    def optimize(self, period_range, ma_range):
        opt = brute(self.update, (period_range, ma_range))
        print(opt)
        return opt, -self.update(opt)



