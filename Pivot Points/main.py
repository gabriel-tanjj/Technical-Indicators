import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

data = pd.read_csv("EURUSD_pivot.csv", parse_dates=["time"], index_col="time")
data = data.tz_localize("UTC")
# print(data)
data = data.tz_convert("US/Eastern")
# print(data)

# downsampling to daily close
close = data["Close"].to_frame().copy()


# downsampling OHLC data
agg_data = {"Open": "first", "High": "max", "Low": "min", "Close": "last"}
daily_ohlc = data.resample("D", offset="17h").agg(agg_data).dropna()

# Merging intraday and daily data
# renaming daily ohlc
daily_ohlc.columns = ["Open_D", "High_D", "Low_D", "Close_D"]


new_data = pd.concat([data, daily_ohlc.shift().dropna()], axis=1).ffill().dropna()
print(new_data)

# Pivot Point - arithmetic mean of high/low/close of prev day
new_data["PP"] = (new_data["High_D"] + new_data["Low_D"] + new_data["Close_D"]) / 3

# Support 1 & 2
new_data["S1"] = new_data["PP"] * 2 - new_data["High_D"]
new_data["S2"] = new_data["PP"] - (new_data["High_D"] - new_data["Low_D"])

# Resistance 1 & 2
new_data["R1"] = new_data["PP"] * 2 - new_data["Low_D"]
new_data["R2"] = new_data["PP"] + (new_data["High_D"] - new_data["Low_D"])

new_data[["Open", "PP", "S1", "S2", "R1", "R2"]].plot(figsize=(12, 8))
plt.title("EURUSD PP")
plt.show()












