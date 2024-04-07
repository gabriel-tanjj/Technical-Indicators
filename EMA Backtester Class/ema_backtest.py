import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.optimize import brute

class Backtester():

    def __init__(self, ticker, long_len, short_len, start_date, end_date, trading_cost):
        self.symbol = ticker
        self.long_len = long_len
        self.short_len = short_len
        self.start_date = start_date
        self.end_date = end_date
        self.trading_cost = trading_cost
        self.results = None
        self.get_data()

    def get_data(self):
        data = pd.read_csv("forex_pairs.csv", parse_dates=["Date"], index_col="Date")
        data = data[self.symbol].to_frame().dropna()
        data = data.loc[self.start_date:self.end_date].copy()
        data.rename(columns={self.symbol: "Price"}, inplace=True)
        data["Returns"] = np.log(data["Price"]/data["Price"].shift(1))
        data["EMA-S"] = data["Price"].ewm(min_periods=self.short_len, span=self.short_len, adjust=False).mean()
        data["EMA-L"] = data["Price"].ewm(min_periods=self.long_len, span=self.long_len, adjust=False).mean()
        # Store data in self.data to allow us to reference it in other functiosn in this class
        self.data = data
        return data

    def set_parameters(self, short_len=None, long_len=None):

        if short_len is not None:
            self.short_len = short_len
            self.data["EMA-S"] = self.data["Price"].ewm(min_periods=self.short_len, span=self.short_len, adjust=False).mean()
        if long_len is not None:
            self.long_len = long_len
            self.data["EMA-L"] = self.data["Price"].ewm(min_periods=self.long_len, span=self.long_len, adjust=False).mean()

    def test_strategy(self):
        data = self.data.copy().dropna()
        data["Position"] = np.where(data["EMA-S"] > data["EMA-L"], 1, -1)
        data["Strategy Returns"] = data["Position"].shift(1) * data["Returns"]
        data["Cumulative Returns"] = data["Returns"].cumsum().apply(np.exp)
        data["Cumulative SReturns"] = data["Strategy Returns"].cumsum().apply(np.exp)
        data["Trades"] = data.Position.diff().fillna(0).abs()
        data["Strategy Net"] = data["Strategy Returns"] - data["Trades"] * self.trading_cost
        data["Cumulative Strategy Net"] = data["Strategy Net"].cumsum().apply(np.exp)
        self.results = data
        strategy_perf = data["Cumulative SReturns"].iloc[-1]
        outperform = data["Cumulative SReturns"].iloc[-1] - data["Cumulative Returns"].iloc[-1]
        return round(strategy_perf, 2), round(outperform, 2)

    def plot_data(self):
        # You need to test the strategy before you can plot your data, because only the test_strategy method will
        # give you the stats needed for the plot_data method

        if self.results is None:
            print("No results to plot")

        else:
            title = "{} | SMA-S: {}, SMA-L: {}".format(self.symbol, self.short_len, self.long_len)
            self.results[["Cumulative Returns", "Cumulative SReturns", "Cumulative Strategy Net"]].plot(figsize=(12,8), title=title)
            plt.show()

    def update_strategy_brute(self, EMA):
        self.set_parameters(int(EMA[0]), int(EMA[1]))
        return -self.test_strategy()[0]

    def optimize(self, short_len_range, long_len_range):
        """
        Perform optimization on the given ranges.

        :param short_len_range: The range for the short length optimization.
        :param long_len_range: The range for the long length optimization.
        :return: A tuple containing the optimized result and the negation of the result of the update strategy brute function.
        """
        opt = brute(self.update_strategy_brute, (short_len_range, long_len_range), finish=None)
        optimized_result = opt
        return opt, -self.update_strategy_brute(opt)






