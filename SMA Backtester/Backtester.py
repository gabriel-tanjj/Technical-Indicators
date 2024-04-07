import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import brute

class Backtester():
    """Backtesting class for testing trading strategies on financial data.

    Args:
        ticker (str): Ticker symbol for the asset to be backtested.
        short_len (int): Length of the short-term moving average (SMA).
        long_len (int): Length of the long-term moving average (SMA).
        start_date (str): Start date for the backtesting period.
        end_date (str): End date for the backtesting period.

    Attributes:
        ticker (str): Ticker symbol for the asset being backtested.
        short_len (int): Length of the short-term moving average (SMA).
        long_len (int): Length of the long-term moving average (SMA).
        start_date (str): Start date for the backtesting period.
        end_date (str): End date for the backtesting period.
        results (pandas.DataFrame): Results of the backtesting strategy.
        data (pandas.DataFrame): Data used for backtesting.

    """
    def __init__(self, ticker, short_len, long_len, start_date, end_date, trading_cost):
        self.ticker = ticker
        self.trading_cost = trading_cost
        self.short_len = short_len
        self.long_len = long_len
        self.start_date = start_date
        self.end_date = end_date
        self.results = None
        self.get_data()

    def get_data(self):
        """Load and process data for the given ticker within the specified date range.

        This method reads data from a CSV file named 'forex_pairs.csv' and extracts the data for the given ticker.
        It then filters the data based on the start and end dates provided. The method calculates the log returns,
        simple moving average (SMA) with short and long lengths, and renames the ticker column as 'price'.

        """
        data = pd.read_csv("forex_pairs.csv", parse_dates=["Date"], index_col="Date")
        data = data[self.ticker].to_frame().dropna()
        data = data.loc[self.start_date:self.end_date].copy()
        data.rename(columns={self.ticker: "price"}, inplace=True)
        data["returns"] = np.log(data/data.shift(1))
        data["SMA-S"] = data["price"].rolling(self.short_len).mean()
        data["SMA-L"] = data["price"].rolling(self.long_len).mean()
        # The data for the ticker is loaded and stored in self.data, which allows information to be
        # retained and shared among the different methods of the class instance. Without it, data
        # would only exist within the scope of the method that generates it, and would not be
        # accessible by other methods within the same class instance.
        self.data = data
        return data

    def set_parameters(self, short_len = None, long_len = None):
        """
        Sets the parameters for calculating the moving average.

        :param short_len: The window size for the short-term moving average. Defaults to None.
        :type short_len: int, optional
        :param long_len: The window size for the long-term moving average. Defaults to None.
        :type long_len: int, optional
        :return: None
        :rtype: None
        """
        if short_len is not None:
            self.short_len = short_len
            self.data["SMA-S"] = self.data["price"].rolling(self.short_len).mean()
        if long_len is not None:
            self.long_len = long_len
            self.data["SMA-L"] = self.data["price"].rolling(self.long_len).mean()

    def test_strategy(self):
        """
        Calculate the performance and outperformance of a trading strategy.

        """
        data = self.data.copy().dropna()
        data["position"] = np.where(data["SMA-S"] > data["SMA-L"], 1, -1)
        data["strategy"] = data["position"].shift(1) * data["returns"]
        data.dropna(inplace=True)
        data["creturns"] = data["returns"].cumsum().apply(np.exp)
        data["cstrategy"] = data["strategy"].cumsum().apply(np.exp)
        # To get total trades taken we use diff() to find the diff between rows in column position
        # If diff() = 0 , no change in position or no position
        # If -1 to 1 - we need to get the abs value
        # use fillna(0) to fill NaN rows to 0
        data["trades"] = data.position.diff().fillna(0).abs()
        data["net_strategy"] = data["strategy"] - (data["trades"] * self.trading_cost)
        data["cnet_strategy"] = data["net_strategy"].cumsum().apply(np.exp)
        self.results = data
        perf = data["cstrategy"].iloc[-1]
        outperf = data["cstrategy"].iloc[-1] - data["creturns"].iloc[-1]
        return round(perf, 3), round(outperf, 3)
        # return print(f"Strategy Performance: {round(perf, 3)}, "
        #              f"Buy & Hold Performance: {round(data["creturns"].iloc[-1], 3)}, "
        #              f"Strategy Outperformance (If any): {round(outperf, 3)}")

    def plot_data(self):
        """
        Plot the investment returns and strategy returns.

        """
        if self.results is None:
            print("No results to plot")

        else:
            title = "{} | SMA-S: {}, SMA-L: {}".format(self.ticker, self.short_len, self.long_len)
            self.results[["creturns", "cstrategy"]].plot(title=title, figsize=(15, 10))
            plt.show()

    def update_strategy_no_optimize(self, SMA):
        """
        :param SMA: A tuple containing two values representing the parameters for the Simple Moving Average (SMA).

        This method updates the strategy by setting the parameters for the Simple Moving Average (SMA),
        testing the strategy, and plotting the data.
        """
        self.set_parameters(SMA[0], SMA[1])
        self.test_strategy()
        self.plot_data()

    def update_strategy_brute(self, SMA):
        """Updates the strategy using a brute force approach.

        :param SMA: A list of Simple Moving Average (SMA) values.
        :type SMA: list[int]
        :return: The negative value of the test strategy.
        :rtype: int
        """
        self.set_parameters(int(SMA[0]), int(SMA[1]))
        return -self.test_strategy()[0]
    #
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

