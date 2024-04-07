import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import brute

class Backtest():

    def __init__(self, SMA_len, dev, trading_cost, us_t_bill):
        self.SMA_len = SMA_len
        self.dev = dev
        self.trading_cost = trading_cost
        self.risk_free_rate = us_t_bill
        self.results = None

    def get_data(self):
        data = pd.read_csv("intraday.csv", parse_dates=["time"], index_col="time")
        data["Returns"] = np.log(data["price"].div(data["price"].shift(1)))
        data["SMA"] = data["price"].rolling(window=self.SMA_len).mean()
        data["Upper"] = data["SMA"] + data["price"].rolling(window=self.SMA_len).std() * self.dev
        data["Lower"] = data["SMA"] - data["price"].rolling(window=self.SMA_len).std() * self.dev
        self.data = data

    def set_parameters(self, SMA_len, dev):
        if SMA_len is not None:
            self.SMA_len = SMA_len
            self.data["SMA"] = self.data["price"].rolling(window=self.SMA_len).mean()
            self.data["Upper"] = self.data["SMA"] + self.data["price"].rolling(window=self.SMA_len).std() * self.dev
            self.data["Lower"] = self.data["SMA"] - self.data["price"].rolling(window=self.SMA_len).std() * self.dev

        if dev is not None:
            self.dev = dev
            self.data["Upper"] = self.data["SMA"] + self.data["price"].rolling(window=self.SMA_len).std() * self.dev
            self.data["Lower"] = self.data["SMA"] - self.data["price"].rolling(window=self.SMA_len).std() * self.dev
    def test_strategy(self):
        data = self.data.copy().dropna()
        data["Distance"] = data["price"] - data["SMA"]
        data["Position"] = np.where(data["price"] < data["Lower"], 1, np.nan)
        data["Position"] = np.where(data["price"] > data["Upper"], -1, data["Position"])
        data["Position"] = np.where(data["Distance"] * data["Distance"].shift(1) < 0, 0, data["Position"])
        # Highlights all the periods that we are in a long/short position
        data["Position"] = data["Position"].ffill().fillna(0)
        # Specifies the exact entry for our trade
        data["Trades"] = data["Position"].diff().fillna(0).abs()
        # Strategy
        data["Strategy"] = data["Returns"] * data["Position"].shift(1)
        data["Strategy_Net"] = data["Strategy"] - data["Trades"] * self.trading_cost
        # Cumulative values
        data["CReturns"] = data["Returns"].cumsum().apply(np.exp)
        data["CStrategy"] = data["Strategy"].cumsum().apply(np.exp)
        data["CStrategy_Net"] = data["Strategy_Net"].cumsum().apply(np.exp)
        self.results = data
        perf = data["CStrategy"].iloc[-1]
        outperf = data["CStrategy"].iloc[-1] - data["CReturns"].iloc[-1]
        # Annualizing returns
        return round(perf, 2), round(outperf, 2)

    def plot_data(self):
        self.results[["CReturns", "CStrategy", "CStrategy_Net"]].plot(figsize=(12, 8), title="BB Strategy")
        plt.show()

    def update_strategy(self, SMA):
        self.set_parameters(int(SMA[0]), int(SMA[1]))
        return -self.test_strategy()[0]

    def optimize(self, ma_range, dev_range):
        opt = brute(self.update_strategy, (ma_range, dev_range))
        print(opt)
        return(opt), -self.update_strategy(opt)

    def financial_analysis(self):
        data = self.results
        asset_returns = round(data["Returns"].mean() * (4 * 252), 2) * 100
        strat_returns = round(data["Strategy_Net"].mean() * (4 * 252), 2) * 100
        asset_risk = round(data["Returns"].std() * np.sqrt(4 * 252), 2) * 100
        strat_risk = round(data["Strategy_Net"].std() * np.sqrt(4 * 252), 2) * 100
        sharpe = round((asset_risk - self.risk_free_rate) / strat_risk, 2)

        print(f"Asset returns: {asset_returns}%")
        print(f"Strategy returns: {strat_returns}%")
        print(f"Asset risk: {asset_risk}%")
        print(f"Strategy risk: {strat_risk}%")
        print(f"Sharpe ratio: {sharpe}")











