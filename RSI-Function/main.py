import yfinance as yf
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import datetime as dt

ohlcv_data = {}
tickers = ['AAPL', 'AMZN', 'GOOG', 'IBM', 'MSFT', 'EURUSD=X', "GBPJPY=X"]
start = dt.datetime.today() - dt.timedelta(days=3650)
end = dt.datetime.today()

for ticker in tickers:
    ohlcv_data[ticker] = yf.download(ticker, start=start, end=end)

def RSI(DF, len=14):
    df = DF.copy()
    df["Change"] = df["Adj Close"] - df["Adj Close"].shift(1)
    df["Gain"] = np.where(df["Change"] >= 0, df["Change"], 0)
    df["Loss"] = np.where(df["Change"] < 0, -1*df["Change"], 0)
    df["Avg Gain"] = df["Gain"].ewm(min_periods=len, alpha=1/len).mean()
    df["Avg Loss"] = df["Loss"].ewm(min_periods=len, alpha=1 / len).mean()
    df["RS"] = df["Avg Gain"].div(df["Avg Loss"])
    df["RSI"] = 100 - (100/(1+df["RS"]))
    return df["RSI"]

for ticker in tickers:
    ohlcv_data[ticker]["RSI"] = RSI(ohlcv_data[ticker])

print(ohlcv_data["AAPL"]["RSI"])


