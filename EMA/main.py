import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

EMA_S = 50
EMA_L = 200
SPREADCOST = 0.00007

data = pd.read_csv("eurusd.csv", parse_dates=["Date"], index_col="Date")

# data.plot(y='price', figsize= (12,8), title="EURUSD Price", fontsize=12)

data["EMA_S"] = data.price.ewm(span=EMA_S, min_periods=EMA_S).mean()
data["EMA_L"] = data.price.ewm(span=EMA_L, min_periods=EMA_L).mean()

# EURUSD Price Chart
# data.plot(figsize=(12,8), title= "EURUSD | EMA{}, EMA{}".format(EMA_S, EMA_L), fontsize=12)
# plt.show()

# Filling up our dataframe with values
data["Positions"] = np.where(data["EMA_S"] > data["EMA_L"], 1, -1)
data["Returns"] = np.log(data.price.div(data.price.shift(1)))
data.dropna(inplace=True)
data["Strategy"] = data["Positions"].shift(1) * data["Returns"]
data.dropna(inplace=True)
data["Trades"] = data["Positions"].diff().fillna(0).abs()
data["nStrategy"] = data["Strategy"] - data["Trades"] * SPREADCOST

# Cumulative values
data["cum_Returns"] = data["Returns"].cumsum().apply(np.exp)
data["cum_Strategy"] = data["Strategy"].cumsum().apply(np.exp)
data["cum_nStrategy"] = data["nStrategy"].cumsum().apply(np.exp)

data[["cum_Returns", "cum_Strategy", "cum_nStrategy"]].plot(figsize=(12,8), title= "EURUSD | EMA{}, EMA{}".format(EMA_S, EMA_L), fontsize=12)
plt.show()

