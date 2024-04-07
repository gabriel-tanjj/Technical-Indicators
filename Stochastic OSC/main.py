import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

period = 14
ma_window = 3
trading_cost = 0.00007

# Making column 0 into the index col
data = pd.read_csv("EURUSD_ohlc.csv", parse_dates=[0], index_col=0)

# data.Close.plot(figsize=(12, 8), title="EURUSD Close")
# plt.show()

data["14d_low"] = data.Low.rolling(window=14).min()
data["14d_high"] = data.High.rolling(window=14).max()

data.loc[: , ["Close", "14d_low", "14d_high"]].plot(figsize=(12, 8))

# Whenever recent close price is = high 1/1 * 100 so Stochastic = 100
# Whenever recent close price is = low 0*100 = 0 so Stochastic = 100
data["SO"] = (data["Close"] - data["14d_low"]) / (data["14d_high"] - data["14d_low"]) * 100
# Moving average based on the Stochastic Osc
data["MA"] = data["SO"].rolling(window=ma_window).mean()
# Strategy test
data["Position"] = np.where(data["SO"] > data["MA"], 1, -1)
data["Returns"] = np.log(data["Close"]/data["Close"].shift(1))
data.dropna(inplace=True)
data["Strategy"] = data["Position"].shift(1) * data["Returns"]
data.dropna(inplace=True)
data["Trades"] = data["Position"].diff().fillna(0).abs()
data["Strategy_Net"] = data["Strategy"] - data["Trades"] * trading_cost

# Cumulative Values
data["CReturns"] = data["Returns"].cumsum().apply(np.exp)
data["CStrategy"] = data["Strategy"].cumsum().apply(np.exp)
data["CStrategy_Net"] = data["Strategy_Net"].cumsum().apply(np.exp)

data["outperf"] = data["CStrategy"] - data["CReturns"]

data[["CReturns", "CStrategy", "CStrategy_Net", "outperf"]].plot(figsize=(12, 8), title="EURUSD Stochastic Osc")
plt.show()
