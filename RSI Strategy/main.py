import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

data = pd.read_csv('eurusd.csv', parse_dates=["Date"], index_col="Date")
data.plot(figsize=(12, 8), title="EURUSD Price")
period = 20
rsi_upper = 70
rsi_lower = 30
trading_cost = 0.00007
# Shows EURUSD Price chart
# plt.show()

data["U"] = np.where(data.price.diff() > 0 , data.price.diff(), 0)
data["D"] = np.where(data.price.diff() < 0 , -data.price.diff(), 0)

data["MA_U"] = data["U"].rolling(period).mean()
data["MA_D"] = data["D"].rolling(period).mean()
data["RSI"] = data["MA_U"] / (data["MA_U"] + data["MA_D"]) * 100

data.dropna(inplace=True)

data[["RSI"]].plot(figsize=(12, 8), title="EURUSD - RSI", secondary_y="RSI")
plt.hlines(y=rsi_upper, xmin=data.index[0], xmax=data.index[-1], label="RSI_Upper", color="red")
plt.hlines(y=rsi_lower, xmin=data.index[0], xmax=data.index[-1], label="RSI_Lower", color="green")
# plt.show()

# The following 2 lines of code evaluate the rsi and rsiupper/lower at a row level so if it is evaluated to be -1 first
# which fulfils the condition of it not being lower than rsi lower, we want the value to stay -1
# This is why we do not put np.nan on the rsi oversold condition
data["Position"] = np.where(data["RSI"] > rsi_upper, -1, np.nan)
data["Position"] = np.where(data["RSI"] < rsi_lower, 1, data["Position"])
data["Position"].fillna(0)
data["Position"] = data["Position"].fillna(0)

# Visualizing RSI Position and RSI value
data.loc["2016", ["RSI", "Position"]].plot(figsize=(12,8), title="EURUSD - RSI Position", secondary_y="Position")
plt.show()

# Vectorized Backtest
# Per row values
data["Returns"] = np.log(data["price"]/data["price"].shift(1))
data["Strategy"] = data["Position"].shift(1) * data["Returns"]
data["Trades"] = data["Position"].diff().abs()
data["NStrategy"] = data["Strategy"] - data["Trades"] * trading_cost
data.dropna(inplace=True)
# Cumulative Values
data["CReturns"] = data["Returns"].cumsum().apply(np.exp)
data["CStrategy"] = data["Strategy"].cumsum().apply(np.exp)
data["CNStrategy"] = data["NStrategy"].cumsum().apply(np.exp)

data.loc["2016", ["CReturns", "CStrategy", "CNStrategy"]].plot(figsize=(12,8), title="EURUSD - RSI Strategy")
plt.show()

