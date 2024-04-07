import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

SMA = 30
dev = 2
trading_cost = 0.00007

data = pd.read_csv("intraday.csv", parse_dates=["time"], index_col="time")

data["Returns"] = np.log(data["price"].div(data["price"].shift(1)))

data["SMA"] = data["price"].rolling(window=SMA).mean()
data["Lower"] = data["SMA"] - data["price"].rolling(window=SMA).std() * dev
data["Upper"] = data["SMA"] + data["price"].rolling(window=SMA).std() * dev
data.dropna(inplace=True)

# Visualizing the bollinger bands
# data.drop(columns=["Returns"]).plot(figsize=(12, 8))
# plt.show()

# Strategy definition
data["Distance"] = data["price"] - data["SMA"]
# Overbought
data["Position"] = np.where(data["price"] > data["Upper"], -1, np.nan)
# Oversold
data["Position"] = np.where(data["price"] < data["Lower"], 1, data["Position"])
# Neutral - intuition is that when price < sma results in a negative number and it multiplies by a positive number
# Overall result is still negative
# So when the previous row is negative and the current row is positive (cross up) which means we exit long so we flip
# Position to 0. Otherwise, if negative * negative = positive, results in our position sitll being data["Position"]
# This single line solves the "TP" for both oversold longs and overbought shorts
data["Position"] = np.where(data["Distance"] * data["Distance"].shift(1) < 0, 0, data["Position"])
# Important as it shows that we're in a long position / short position even after it has been "triggered". Since 1 will
# be propagated till 0 (tp) is found and -1 will be propagated till 0 (tp) is found
data["Position"] = data["Position"].ffill().fillna(0)
data["Trades"] = data["Position"].diff().fillna(0).abs()
print(data["Position"].value_counts())
print(data["Trades"].value_counts())

# data.drop(columns=["Distance", "Returns"]).loc["2019-01"].plot(figsize=(12, 8), secondary_y="Position")
# plt.show()

# Vectorized backtesting
data["Strategy"] = data["Position"].shift(1) * data["Returns"]
data["Strategy_Net"] = data["Strategy"] - data["Trades"] * trading_cost

# Cumulative values
data["CReturns"] = data["Returns"].cumsum().apply(np.exp)
data["CStrategy"] = data["Strategy"].cumsum().apply(np.exp)
data["CStrategy_Net"] = data["Strategy_Net"].cumsum().apply(np.exp)

# Visualize
data[["CStrategy", "CStrategy_Net", "CReturns"]].plot(figsize=(12, 8), title="Bol Bands Strategy Returns")
plt.show()

# Annulizing return / volatility
print(data[["Returns", "Strategy_Net"]].mean() * (4 * 252))
print(data[["Returns", "Strategy_Net"]].std() * np.sqrt(4 * 252))


