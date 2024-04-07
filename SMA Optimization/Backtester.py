from SMABacktest import SMABacktester
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
plt.style.use("seaborn-v0_8")

# Removes the original indexing, changes the index to the date column, treats the date column as dt objects
data = pd.read_csv("forex_pairs.csv", parse_dates=["Date"], index_col="Date")

sma_test = SMABacktester("EURUSD=X", 50, 200, "2004-01-01", "2010-01-01")
# Method to get creturns / cstrategy
# print(sma_test.test_strategy())
# Method to print results in a df
# print(sma_test.results)
# sma_test.plot_results()

# Brute forcing the most optimal results
# sma_test.optimize_parameters((10,50,1), (100, 200, 1))
# Plotting the results
# sma_test.plot_results()

# Backtesting the training set
training_set = SMABacktester("EURUSD=X", 50, 200, "2004-01-01", "2015-01-01")
print(training_set.optimize_parameters((25, 50, 1), (100, 200, 1)))

# Now using the backtested date we try to forward test it
forward_test_set = SMABacktester("EURUSD=X", 46, 137, "2015-01-01", "2020-01-01")
forward_test_set.test_strategy()
forward_test_set.plot_results()
plt.show()

# Highlights that although you can reference data that worked well in the past it might not work as well in the future

