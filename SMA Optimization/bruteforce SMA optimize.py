import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import brute
plt.style.use('seaborn-v0_8')

df = pd.read_csv('eurusd.csv', parse_dates=['Date'], index_col='Date')

def strategy_SMA(SMA_Tuple):
    data = df.copy()
    # Returns are calculated by taking the natural log of today's price - yesterday's price,
    # would return NaN for first row
    data["Returns"] = np.log(data.price.div(data.price.shift(1)))

    # We get the variables inside the tuple using indexing 0, 1, converting it to int format for the function to work
    data["SMA-S"] = data.price.rolling(int(SMA_Tuple[0])).mean()
    data["SMA-L"] = data.price.rolling(int(SMA_Tuple[1])).mean()

    # Removes data prior to the short-len/long-len since it'll be NaN
    data.dropna(inplace=True)
    # Returns long position as 1 and short position as -1
    data["Position"] = np.where(data["SMA-S"] > data["SMA-L"], 1, -1)
    # Solves the issue of short positions being captured in the timeframe they triggered, has to be AFTER candle close
    data["Strategy"] = data.Position.shift(1) * data["Returns"]
    # Removes NaN values just to be safe
    data.dropna(inplace=True)

    return print(-data[["Returns", "Strategy"]].sum().apply(np.exp)[-1])

strategy_SMA((10, 50))

brute(strategy_SMA, ((10, 50, 1), (100, 200, 1)))

