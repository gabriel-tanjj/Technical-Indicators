import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.optimize import brute


class RSIBacktester():

    def __init__(self, symbol, rsi_len, rsi_overbought, rsi_oversold, start_date, end_date, trading_cost):
        self.symbol = symbol
        self.rsi_len = rsi_len
        self.rsi_overbought = rsi_overbought
        self.rsi_oversold = rsi_oversold
        self.start_date = start_date
        self.end_date = end_date
        self.trading_cost = trading_cost
        self.results = None

    def get_data(self):
        data = pd.read_csv("forex_pairs.csv", parse_dates=["Date"], index_col="Date")
        data = data[self.symbol].to_frame().dropna()
        data = data.loc[self.start_date:self.end_date]
        data.rename(columns={self.symbol: "Price"}, inplace=True)
        data["Returns"] = np.log(data["Price"].div(data["Price"].shift(1)))
        data["U"] = np.where(data["Price"].diff() > 0, data["Price"].diff(), 0)
        data["D"] = np.where(data["Price"].diff() < 0, -data["Price"].diff(), 0)
        data["MA-U"] = data["U"].rolling(self.rsi_len).mean()
        data["MA-D"] = data["D"].rolling(self.rsi_len).mean()
        # First method of calculating RSI
        data["RSI"] = data["MA-U"] / (data["MA-U"] + data["MA-D"]) * 100
        # Second method of calculating RSI
        data["RSI2"] = 100 - (100 / (1 + data["MA-U"] / data["MA-D"]))
        self.data = data

        print(data)

    def set_parameters(self, rsi_len, rsi_overbought, rsi_oversold):
        if rsi_len is not None:
            self.rsi_len = rsi_len
            self.data["MA-U"] = self.data["U"].rolling(self.rsi_len).mean()
            self.data["MA-D"] = self.data["D"].rolling(self.rsi_len).mean()
            self.data["RSI"] = self.data["MA-U"] / (self.data["MA-U"] + self.data["MA-D"]) * 100

        if rsi_overbought is not None:
            self.rsi_overbought = rsi_overbought

        if rsi_oversold is not None:
            self.rsi_oversold = rsi_oversold

    def test_strategy(self):
        data = self.data.copy()
        data["CReturns"] = data["Returns"].cumsum().apply(np.exp)
        data["Position"] = np.where(data["RSI"] > self.rsi_overbought, -1, np.nan)
        data["Position"] = np.where(data["RSI"] < self.rsi_oversold, 1, data["Position"])
        data["Position"] = data["Position"].fillna(0)
        data["Trades"] = data["Position"].diff().abs()

        # Strategy
        data["Strategy"] = data["Position"].shift(1) * data["Returns"]
        data["NStrategy"] = data["Strategy"] - data["Trades"] * self.trading_cost

        # Cumulative Values
        data["CReturns"] = data["Returns"].cumsum().apply(np.exp)
        data["CStrategy"] = data["Strategy"].cumsum().apply(np.exp)
        data["CNStrategy"] = data["NStrategy"].cumsum().apply(np.exp)

        # Stats
        perf = data["CStrategy"].iloc[-1]
        outperf = data["CStrategy"].iloc[-1] - data["CReturns"].iloc[-1]

        self.results = data

        return(round(perf,2), round(outperf,2))

    def plot_results(self):
        self.results[["CReturns", "CStrategy", "CNStrategy"]].plot(figsize=(12,8), title="{}, RSI: {}".format(self.symbol, self.rsi_len))
        plt.show()

    def update_for_brute(self, RSI):
        self.set_parameters(int(RSI[0]), int(RSI[1]), int(RSI[2]))
        return -self.test_strategy()[0]

    def optimize(self, period_range, upper_range, lower_range):
        opt = brute(self.update_for_brute, (period_range, upper_range, lower_range))
        print(opt)
        return opt, -self.update_for_brute(opt)
