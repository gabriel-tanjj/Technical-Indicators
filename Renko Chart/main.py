import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from stocktrends import Renko

tickers = ["MSFT", "AMZN", "GOOG", "TSLA"]
ohlcv = {}
hour_data = {}
renko_data = {}

for ticker in tickers:
    data = yf.download(ticker, period="1mo", interval="5m")
    data.dropna(inplace=True)
    ohlcv[ticker] = data
    data_h = yf.download(ticker, period="1y", interval="1h")
    data_h.dropna(inplace=True)
    hour_data[ticker] = data_h

def ATR(df, len=14):
    df = df.copy()
    df["H-L"] = df["High"] - df["Low"]
    df["H-PC"] = df["High"] - df["Adj Close"].shift(1)
    df["L-PC"] = df["Low"] - df["Adj Close"].shift(1)
    df["TR"] = df[["H-L", "H-PC", "L-PC"]].max(axis=1, skipna=False)
    df["ATR"] = df["TR"].ewm(min_periods=len, span=len).mean()
    df["ATR"].dropna(inplace=True)
    return df["ATR"]

def renko_df(df, hourly_df):
    df = df.copy()
    df.drop("Close", axis=1, inplace=True)
    df.drop("Volume", axis=1, inplace=True)
    df.reset_index(inplace=True)
    df.columns = ["date", "open", "high", "low", "close"]
    df.dropna(inplace=True)
    df2 = Renko(df)
    df2.brick_size = 3 * round(ATR(hourly_df, len=120).iloc[-1], 0)
    renko_data = df2.get_ohlc_data()
    return renko_data

for ticker in tickers:
    renko_data[ticker] = renko_df(ohlcv[ticker], hour_data[ticker])
    print(renko_data)
    renko_data[ticker][["open", "high", "low", "close"]].plot(title="Renko for {}".format(ticker))
    plt.show()

