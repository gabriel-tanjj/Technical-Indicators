import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

ema_s = 12
ema_l = 26
signal_window = 9
spread_cost = 0.0007

data = pd.read_csv("eurusd.csv", parse_dates=["Date"], index_col="Date")
data.rename(columns={"price": "Close"}, inplace=True)
data.plot(figsize=(12,8), title="EURUSD")
# plt.show()

data["EMA-S"] = data["Close"].ewm(span=ema_s, min_periods=ema_s).mean()
data["EMA-L"] = data["Close"].ewm(span=ema_l, min_periods=ema_l).mean()
data["MACD"] = data["EMA-S"] - data["EMA-L"]
data["MACD-Signal"] = data["MACD"].ewm(span=signal_window, min_periods=signal_window).mean()

data.loc["2016", ["Close", "EMA-S", "EMA-L", "MACD"]].plot(figsize=(12,8), title="EURUSD", secondary_y="MACD")
# plt.show()
data.loc["2016", ["MACD", "MACD-Signal"]].plot(figsize=(12,8), title="EURUSD - MACD")
# plt.show()

# Defining the MACD strategy

data["Position"] = np.where(data["MACD"] > data["MACD-Signal"], 1, -1)
data["Returns"] = np.log(data["Close"]/data["Close"].shift(1))
data["CReturns"] = data["Returns"].cumsum().apply(np.exp)
data.dropna(inplace=True)
data["Strategy"] = data["Position"].shift(1) * data["Returns"]
data["CStrategy"] = data["Strategy"].cumsum().apply(np.exp)
data["Trades"] = data["Position"].diff().fillna(0).abs()
# To check no. of trades
# print(data["Trades"].value_counts())
data["Strategy_Net"] = data["Strategy"] - data["Trades"] * spread_cost
data["CStrategy_Net"] = data["Strategy_Net"].cumsum().apply(np.exp)

data[["CStrategy_Net", "CStrategy", "CReturns"]].plot(figsize=(12, 8), title="EURUSD - MACD: {}, {}".format(ema_s, ema_l))
plt.show()




