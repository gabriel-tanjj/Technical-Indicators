import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import datetime as dt

tickers = ["GBPJPY=X", "EURUSD=X", "MSFT", "GOOG", "AMZN", "TSLA"]
ohlcv_data = {}
start = dt.datetime.today() - dt.timedelta(days=3650)
end = dt.datetime.today()

for ticker in tickers:
    data = yf.download(ticker, start=start, end=end)
    ohlcv_data[ticker] = data

def atr(df, len=14):
    df = df.copy()
    df["H-L"] = df["High"] - df["Low"]
    df["H-PC"] = abs(df["High"] - df["Adj Close"].shift(1))
    df["L-PC"] = abs(df["Low"] - df["Adj Close"].shift(1))
    df["TR"] = df[["H-L", "H-PC", "L-PC"]].max(axis=1, skipna=False)
    df["ATR"] = df["TR"].ewm(min_periods=len, span=len).mean()
    return df["ATR"]

for ticker in tickers:
    ohlcv_data[ticker]["ATR"] = atr(ohlcv_data[ticker])

def adx(df, len=20):
    df.copy()
    df["ATR"] = atr(df, len=20)
    df["Up"] = df["High"] - df["High"].shift(1)
    df["Down"] = df["Low"].shift(1) - df["Low"]

    df["+DM"] = np.where((df["Up"] > df["Down"]) & (df["Up"] > 0), df["Up"], 0)
    df["-DM"] = np.where((df["Down"] > df["Up"]) & (df["Down"] > 0), df["Down"], 0)

    df["+DI"] = 100 * df["+DM"].div(df["ATR"]).ewm(min_periods=len, span=len).mean()
    df["-DI"] = 100 * df["-DM"].div(df["ATR"]).ewm(min_periods=len, span=len).mean()

    df["ADX"] = 100 * abs((df["+DI"] - df["-DI"]).div(df["+DI"] + df["-DI"])).ewm(min_periods=len, span=len).mean()
    return df["ADX"]

for ticker in tickers:
    ohlcv_data[ticker]["ADX"] = adx(ohlcv_data[ticker])
    ohlcv_data[ticker][["ADX", "+DI", "-DI"]].plot(title="ADX {}".format(ticker))
    plt.show()

print(ohlcv_data["EURUSD=X"]["ADX"])





