import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import argrelextrema

data = pd.read_csv('EURUSD_ohlc.csv', parse_dates=[0], index_col=0)

# EURUSD Close plot
# data[["Close"]].plot(figsize=(12,8))
# plt.show()

# Higher High
order = 70
trading_cost = 0.00007
# position of local max in the index
local_max = argrelextrema(data["High"].values, np.greater_equal, order=order)
local_min = argrelextrema(data["Low"].values, np.less_equal, order=order)

# Index number of local min / max
# print(local_max)
# print(local_min)

# Dates for local max
# print(data.index[local_max])
# print(data.index[local_min])

# Value points (price) of local max and min
# print(data["High"].values[local_max])
# print(data["Low"].values[local_min])

# EURUSD close plot
# data[["Close"]].plot(figsize=(12, 8))
# # X is the "Date" the local max is created, ymin is the lowest low of all the data and ymax is the highest high of all
# # the data
# plt.vlines(x=data.index[local_max], ymin=data["Low"].min(), ymax=data["High"].max(), color='green')
# plt.vlines(x=data.index[local_min], ymin=data["Low"].min(), ymax=data["High"].max(), color='red')
# # plt.hlines(y=data["Low"].iloc[local_min], xmin=data.index[0], xmax=data.index[-1], color='red')
# plt.show()


data["HH"] = np.nan
data["HH_Date"] = np.nan
data["LL"] = np.nan
data["LL_Date"] = np.nan

for bar in range(len(data)):
    # Set date variable to the date of the current data point in the index
    date = data.index[bar]
    # This line of code takes the HIGH of all the bars from the start of the data till now
    hh = data.iloc[: bar+1]["High"]
    ll = data.iloc[: bar+1]["Low"]
    # Local max returns index number
    # This line of code then takes all the datas before and evaluates it until a local_max is reached or evaluated
    local_max = argrelextrema(hh.values, np.greater_equal, order=order)
    local_min = argrelextrema(ll.values, np.less_equal, order=order)
    # The right side of the = sign here indicates that the column data["High"] is first accessed
    # Then its values are accessed ONLY, then we get the index from the LAST NUMBER in the local max array
    # Because it represents the LATEST Higher high index which is the latest HH.
    # So the column "HH" will be filled with the latest HH repeatedly till a new HH index is added to the local_max
    # Then the column "HH" will be filled with the new HH repeatedly till a new HH index is added and repeat
    data.loc[date, "HH"] = data["High"].values[local_max][-1]
    # Same idea as the above line of code but this time accessing the date of the HH and when it is made
    data.loc[date, "HH_Date"] = data.index[local_max][-1]

    data.loc[date, "LL"] = data["Low"].values[local_min][-1]
    data.loc[date, "LL_Date"] = data.index[local_min][-1]

# Visualizing HH / LL
# data.loc["2010":"2011", ["HH", "LL", "Close"]].plot(figsize=(12,8), title="EURUSD LL HH")
# plt.show()

# Go long/short
data["Trend"] = np.where(data["HH_Date"] > data["LL_Date"], "Long", "Short")
# Levels for long
data["23.6"] = np.where(data["Trend"] == "Long",
                        data["HH"] - (data["HH"] - data["LL"]) * 0.236,
                        data["HH"] - (data["HH"] - data["LL"]) * (1 - 0.236))

data["38.2"] = np.where(data["Trend"] == "Long",
                        data["HH"] - (data["HH"] - data["LL"]) * 0.382,
                        data["HH"] - (data["HH"] - data["LL"]) * (1 - 0.382))

data["61.8"] = np.where(data["Trend"] == "Long",
                        data["HH"] - (data["HH"] - data["LL"]) * 0.618,
                        data["HH"] - (data["HH"] - data["LL"]) * (1 - 0.618))
#
# data["78.6"] = np.where(data["Trend"] == "Long",
#                         data["HH"] - (data["HH"] - data["LL"]) * 0.786,
#                         data["HH"] - (data["HH"] - data["LL"] * (1 - 0.786)))

# Positions

data["Position"] = np.where((data["HH"] != data["HH"].shift()) | (data["LL"] != data["LL"].shift()), 0, np.nan)

# 61.8% Strat Entry Long
data["Position"] = np.where((data["Trend"] == "Long")
                            & (data["Close"].shift(1) < data["38.2"].shift(1))
                            & (data["Close"] > data["38.2"]),
                            1, data["Position"])

# Take Profit (Long)
data["Position"] = np.where((data["Trend"] == "Long")
                            & (data["Close"].shift(1) < data["23.6"].shift(1))
                            & (data["Close"] >= data["23.6"]),
                            0, data["Position"])

# Stop Loss (Long)
data["Position"] = np.where((data["Trend"] == "Long")
                            & (data["Close"].shift(1) > data["LL"].shift(1))
                            & (data["Close"] <= data["LL"]),
                            0, data["Position"])

# 61.8% Strat Entry Short
data["Position"] = np.where((data["Trend"] == "Short")
                            & (data["Close"].shift(1) > data["38.2"].shift(1))
                            & (data["Close"] < data["38.2"]),
                            -1, data["Position"])

# Take Profit (Short)
data["Position"] = np.where((data["Trend"] == "Short")
                            & (data["Close"].shift(1) > data["23.6"].shift(1))
                            & (data["Close"] < data["23.6"]),
                            0, data["Position"])

# Stop Loss (Short)
data["Position"] = np.where((data["Trend"] == "Short")
                            & (data["Close"].shift(1) < data["HH"].shift(1))
                            & (data["Close"] > data["HH"]),
                            0, data["Position"])

data["Position"] = data["Position"].ffill()
print(data["Position"].value_counts())

# Backtesting / Stats

data["Returns"] = np.log(data["Close"] / data["Close"].shift())
data["Strategy"] = data["Position"] * data["Returns"]
data = data.dropna()
data["Trades"] = data["Position"].diff().fillna(0).abs()
data["CReturns"] = data["Returns"].cumsum().apply(np.exp)
data["CStrategy"] = data["Strategy"].cumsum().apply(np.exp)


data[["CReturns", "CStrategy"]].plot(figsize=(12, 8), title="EURUSD FIB Pullback")
plt.show()






