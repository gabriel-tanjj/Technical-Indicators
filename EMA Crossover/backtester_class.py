import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import brute

class Backtester():

    def __init__(self, symbol, SMA, EMA, start_date, end_date, trading_cost):
        self.symbol = symbol
        self.SMA = SMA
        self.EMA = EMA
        self.start_date = start_date
        self.end_date = end_date
        self.trading_cost = trading_cost
        self.results = None
    def get_data(self):
        data = pd.read_csv("forex_pairs.csv", parse_dates=["Date"], index_col="Date")
        # By selecting self.symbol we essentially conver the data into a series, use to_frame() to convert it back
        # to a dataframe
        data = data[self.symbol].to_frame().dropna()
        # Select row of data using start date/end date and use the copy function to create an entirely new df
        # so any changes we make will nto affect the original df
        data = data.loc[self.start_date:self.end_date].copy()
        data.rename(columns={self.symbol: "Price"}, inplace=True)
        data["Returns"] = np.log(data["Price"]/data["Price"].shift(1))
        data["SMA"] = data["Price"].rolling(self.SMA).mean()
        data["EMA"] = data["Price"].ewm(span=self.EMA, min_periods=self.EMA).mean()
        self.data = data
        return data

    def set_parameters(self, SMA, EMA):
        if SMA is not None:
            self.SMA = SMA
            self.data["SMA"] = self.data["Price"].rolling(window=SMA).mean()

        if EMA is not None:
            self.EMA = EMA
            self.data["EMA"] = self.data["Price"].ewm(span=self.EMA, min_periods=self.EMA).mean()

    def test_strategy(self):
        data = self.data.copy().dropna()
        data["Position"] = np.where(data["EMA"] > data["SMA"], 1, -1)
        data["Cumulative Returns"] = data["Returns"].cumsum().apply(np.exp)
        data["Strategy Returns"] = data["Returns"] * data["Position"].shift(1)
        data["Cumulative Strategy Returns"] = data["Strategy Returns"].cumsum().apply(np.exp)
        data["Trades"] = data["Position"].diff().fillna(0).abs()
        data["Strategy Net Returns"] = data["Strategy Returns"] - data["Trades"] * self.trading_cost
        data["Cumulative Strategy Net Returns"] = data["Strategy Net Returns"].cumsum().apply(np.exp)
        # Noticed that the number of trades is abnormally low so use the following line of code to check
        # This causes the cumulative strategy net returns and cumulative strategy returns to have
        # little to no difference
        # print(data["Trades"].value_counts())
        self.results = data
        strategy_perf = data["Cumulative Strategy Net Returns"].iloc[-1]
        outperform = data["Cumulative Strategy Net Returns"].iloc[-1] - data["Cumulative Returns"].iloc[-1]
        return round(strategy_perf, 2), round(outperform, 2)

    def plot_data(self):
        if self.results is None:
            print("No Strategy Tested")

        else:
            title = "{} | EMA: {}, SMA: {}".format(self.symbol, self.EMA, self.SMA)
            self.results[["Cumulative Strategy Net Returns","Cumulative Strategy Returns", "Cumulative Returns"]].plot(figsize=(12,8), title=title)
            plt.show()

    def update_strategy_brute(self, param):
        # we put a negative sign infront of the -self.test_strategy()[0] because we want it to be a negative number
        # the brute method will minimize a loss which in turn maximizes the function thereby giving us the best
        # parameters for the timeframe we chose
        self.set_parameters(int(param[0]), int(param[1]))
        return -self.test_strategy()[0]

    def optimize(self, SMA_Range, EMA_Range):
        opt = brute(self.update_strategy_brute, (SMA_Range, EMA_Range), finish=None)
        return opt, -self.update_strategy_brute(param=opt)





